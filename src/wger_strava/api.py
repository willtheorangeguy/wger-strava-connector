from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import time
from urllib.parse import urlsplit
import httpx


class APIError(RuntimeError):
    def __init__(self, method, path, status=None):
        self.status = status
        super().__init__(f"{method} {urlsplit(path).path}: " + (f"HTTP {status}" if status else "network error"))


class UnknownWrite(APIError):
    pass


class API:
    def __init__(self, base, state=None, headers=None, transport=None):
        self.base, self.state = base, state
        self.client = httpx.Client(headers=headers, transport=transport, timeout=30, follow_redirects=False, trust_env=False)

    def close(self):
        self.client.close()

    def request(self, method, path, **kwargs):
        url = path if path.startswith(("http://", "https://")) else self.base + path
        if urlsplit(url)[:2] != urlsplit(self.base)[:2]:
            raise ValueError("Refusing pagination outside the configured API origin")
        if self.state and self.state.get("cooldown", 0) > time.time():
            raise APIError(method, path, 429)
        try:
            response = self.client.request(method, url, **kwargs)
        except httpx.TransportError:
            raise (UnknownWrite if method != "GET" else APIError)(method, path) from None
        if response.status_code == 429:
            delay = 900
            retry = response.headers.get("Retry-After")
            if retry:
                try:
                    delay = max(delay, float(retry))
                except ValueError:
                    try:
                        delay = max(delay, parsedate_to_datetime(retry).timestamp() - time.time())
                    except (ValueError, TypeError):
                        pass
            # A daily exhaustion must wait until the next UTC day, not 15 minutes.
            for prefix in ["X-RateLimit", "X-ReadRateLimit"]:
                try:
                    limit = [int(x) for x in response.headers[prefix + "-Limit"].split(",")]
                    usage = [int(x) for x in response.headers[prefix + "-Usage"].split(",")]
                    if usage[1] >= limit[1]:
                        delay = max(delay, 86400 - time.time() % 86400 + 1)
                except (KeyError, IndexError, ValueError):
                    pass
            if self.state:
                self.state.set("cooldown", time.time() + delay)
        if not response.is_success:
            error = UnknownWrite if method != "GET" and response.status_code >= 500 else APIError
            raise error(method, path, response.status_code)
        try:
            return response.json()
        except ValueError:
            raise (UnknownWrite if method != "GET" else APIError)(method, path, response.status_code) from None


class Wger(API):
    def __init__(self, config, **kwargs):
        if not config.wger_token:
            raise ValueError("Set WGER_TOKEN to your wger legacy API token")
        super().__init__(config.wger_url, headers={"Authorization": "Token " + config.wger_token}, **kwargs)

    def items(self, route, **filters):
        path = f"/api/v2/{route}/?" + str(httpx.QueryParams({"limit": 100, **filters}))
        seen = set()
        while path:
            if path in seen:
                raise ValueError("Repeated wger pagination link")
            seen.add(path)
            page = self.request("GET", path)
            if isinstance(page, list):
                yield from page
                return
            yield from page["results"]
            path = page.get("next")


class Strava(API):
    def __init__(self, config, state, **kwargs):
        super().__init__(config.strava_url, state, **kwargs)
        self.config = config

    def token(self):
        token = self.state.get("oauth")
        if not token:
            raise ValueError("Authorize Strava first with auth-url and auth-complete")
        self.state.bind("strava_app", {"url": self.base, "client": self.config.client_id})
        if token["expires_at"] > time.time() + 120:
            return token["access_token"]
        if self.state.get("refresh_uncertain"):
            raise ValueError("OAuth refresh outcome is uncertain; authorize again")
        self.state.set("refresh_uncertain", True)
        try:
            result = self.request("POST", "/oauth/token", data={
                "client_id": self.config.client_id, "client_secret": self.config.client_secret,
                "grant_type": "refresh_token", "refresh_token": token["refresh_token"]})
        except UnknownWrite:
            raise
        except APIError:
            self.state.set("refresh_uncertain", False)
            raise
        # Persist the newest token before any other API calls; never reuse .env tokens.
        updated = {**token, **{key: result[key] for key in ("access_token", "refresh_token", "expires_at")}}
        self.state.set("oauth", updated)
        self.state.set("refresh_uncertain", False)
        return updated["access_token"]

    def call(self, method, path, **kwargs):
        return self.request(method, "/api/v3" + path, headers={"Authorization": "Bearer " + self.token()}, **kwargs)

    def authorize(self, code, scopes):
        if not self.config.client_id or not self.config.client_secret:
            raise ValueError("Set STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET")
        if not {"read", "activity:write", "activity:read_all"} <= set(scopes.replace(",", " ").split()):
            raise ValueError("Strava authorization must grant read, activity:write and activity:read_all")
        self.state.bind("strava_app", {"url": self.base, "client": self.config.client_id})
        result = self.request("POST", "/oauth/token", data={
            "client_id": self.config.client_id, "client_secret": self.config.client_secret,
            "grant_type": "authorization_code", "code": code})
        athlete = str(result["athlete"]["id"])
        self.state.bind("strava_athlete", athlete)
        self.state.set("oauth", {key: result[key] for key in ("access_token", "refresh_token", "expires_at")})
        self.state.set("refresh_uncertain", False)
        self.state.set("oauth_scopes", scopes)
        return athlete

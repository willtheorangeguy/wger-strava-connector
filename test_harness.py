"""Run all tests against a dedicated wger harness user and a mock Strava API."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parent


def run(args, **kwargs):
    return subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wger-harness", type=Path, default=ROOT.parent / "wger-addon-harness")
    args = parser.parse_args()
    harness = args.wger_harness.resolve()
    if not (harness / "harness.py").is_file():
        parser.error("Check out wger-addon-harness alongside this repository or use --wger-harness")
    run([sys.executable, str(harness / "harness.py"), "up"])
    for name in ("runtime", "reports"):
        (ROOT / name).mkdir(exist_ok=True)
        (ROOT / name).chmod(0o777)
    username = "strava_connector_it_" + uuid.uuid4().hex[:12]
    command = ["docker", "compose", "-f", str(harness / "compose.yaml"), "exec", "-T", "web",
               "python3", "manage.py", "shell", "-c", "exec(__import__('sys').stdin.read())"]
    credentials = ROOT / "runtime/test-credentials.json"
    compose = ["docker", "compose", "-f", "compose.test.yaml", "-f", "runtime/test-wger.compose.json"]
    try:
        seed = "USERNAME = " + repr(username) + "\n" + (ROOT / "tests/seed_wger.py").read_text(encoding="utf-8")
        result = run(command, input=seed, text=True, capture_output=True)
        fixture = next(line.split("=", 1)[1] for line in result.stdout.splitlines() if line.startswith("CONNECTOR_TEST_JSON="))
        credentials.write_text(fixture, encoding="utf-8")
        config = run(["docker", "compose", "-f", str(harness / "compose.yaml"), "config", "--format", "json"],
                     text=True, capture_output=True)
        network = json.loads(config.stdout)["networks"]["default"]["name"]
        (ROOT / "runtime/test-wger.compose.json").write_text(json.dumps({
            "services": {"test": {"networks": ["default", "wger-harness"]}},
            "networks": {"wger-harness": {"external": True, "name": network}}}), encoding="utf-8")
        run(compose + ["build", "test"])
        run(compose + ["up", "-d", "--wait", "mock-strava"])
        run(compose + ["run", "--rm", "test"])
    finally:
        if (ROOT / "runtime/test-wger.compose.json").exists():
            subprocess.run(compose + ["down"], cwd=ROOT, check=False)
        cleanup = "from django.contrib.auth.models import User\nUser.objects.filter(username=" + repr(username) + ").delete()"
        run(command, input=cleanup, text=True, capture_output=True)
        credentials.unlink(missing_ok=True)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"Test harness failed (exit {error.returncode}); see reports/junit.xml", file=sys.stderr)
        sys.exit(1)

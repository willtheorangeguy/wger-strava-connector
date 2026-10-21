"""Interactive headless-server login; upload proof restricted to the local mock."""
import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import secrets
import signal
import subprocess
import tempfile
import time
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


@contextmanager
def profile_lock(profile):
    profile.mkdir(parents=True, exist_ok=True)
    profile.chmod(0o700)
    with (profile / '.session.lock').open('a+b') as lock:
        try:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Browser profile is busy; stop the login service or worker first') from None
        yield


def login(profile):
    """A real browser displayed through localhost-only noVNC, with manual MFA."""
    processes = []
    with profile_lock(profile), tempfile.TemporaryDirectory() as temp:
        password = secrets.token_urlsafe(8)[:8]
        password_file = Path(temp) / 'vnc-password'
        password_file.write_text(password + '\n', encoding='utf-8')
        password_file.chmod(0o600)
        environment = {**os.environ, 'DISPLAY': ':99'}
        try:
            processes.append(subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1280x900x24', '-nolisten', 'tcp'], env=environment))
            for _ in range(100):
                if Path('/tmp/.X11-unix/X99').exists():
                    break
                if processes[0].poll() is not None:
                    raise ValueError('Virtual display did not start')
                time.sleep(.1)
            else:
                raise ValueError('Virtual display did not become ready')
            processes.append(subprocess.Popen(['x11vnc', '-display', ':99', '-localhost', '-rfbport', '5900',
                '-forever', '-shared', '-passwdfile', str(password_file)], env=environment,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            processes.append(subprocess.Popen(['websockify', '--web=/usr/share/novnc/', '6080', '127.0.0.1:5900'],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
            print('Open http://localhost:6080/vnc.html (remote server: use an SSH tunnel).', flush=True)
            print('Temporary viewer password: ' + password, flush=True)
            print('Sign into Strava manually, then stop this service to save and release the profile.', flush=True)
            with sync_playwright() as p:
                context = p.chromium.launch_persistent_context(str(profile / 'chromium'), channel='chromium', headless=False,
                    env=environment, viewport={'width':1280,'height':900})
                try:
                    page = context.pages[0] if context.pages else context.new_page()
                    page.goto('https://www.strava.com/login', wait_until='domcontentloaded')
                    while True:
                        if any(process.poll() is not None for process in processes):
                            raise ValueError('Login viewer stopped unexpectedly')
                        page.wait_for_timeout(1000)
                finally:
                    context.close()
        finally:
            for process in reversed(processes):
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def attach_mock(page, origin, activity_id, athlete_id, images, journal):
    """Proof of file upload/save/reopen behavior; NOT a verified Strava adapter."""
    parsed = urlsplit(origin)
    if parsed.scheme != 'http' or parsed.hostname not in {'mock-strava-web', '127.0.0.1', 'localhost'}:
        raise ValueError('Upload prototype is restricted to the local mock website')
    activity_id, athlete_id = str(int(activity_id)), str(int(athlete_id))
    if len(images) != 2 or any(not path.is_file() for path in images):
        raise ValueError('Exactly two existing image files are required')
    identity = {'activity_id':activity_id, 'athlete_id':athlete_id,
                'images':{path.name:hashlib.sha256(path.read_bytes()).hexdigest() for path in images}}
    if len(identity['images']) != 2:
        raise ValueError('Image filenames must be different')
    if journal.exists():
        prior = json.loads(journal.read_text())
        if any(prior.get(key) != value for key,value in identity.items()):
            raise ValueError('Journal belongs to a different activity, athlete or image revision')
        if prior['state'] == 'attached':
            return prior
        raise ValueError('Prior upload outcome is uncertain; inspect the activity before another attempt')
    page.goto(origin + '/activities/' + activity_id)
    if urlsplit(page.url).path == '/login':
        raise ValueError('Browser needs login; reconnect using the login viewer')
    if page.locator('[data-athlete-id]').get_attribute('data-athlete-id') != athlete_id:
        raise ValueError('Browser account does not match the expected Strava athlete')
    if page.locator('[data-owner-id]').get_attribute('data-owner-id') != athlete_id:
        raise ValueError('Activity belongs to a different athlete')
    page.get_by_role('link', name='Edit activity', exact=True).click()
    record = {**identity, 'state':'uncertain'}
    journal.parent.mkdir(parents=True, exist_ok=True)
    journal.write_text(json.dumps(record), encoding='utf-8')
    # Record intent before selecting files: even selection can begin remote uploads.
    page.get_by_label('Media', exact=True).set_input_files([str(path) for path in images])
    page.get_by_role('button', name='Save', exact=True).click()
    page.goto(origin + '/activities/' + activity_id)
    for path in images:
        if page.get_by_alt_text(path.name, exact=True).count() != 1:
            raise ValueError('Saved media could not be verified; upload outcome is uncertain')
    record['state'] = 'attached'
    journal.write_text(json.dumps(record), encoding='utf-8')
    return record


def main():
    def shutdown(*_):
        raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, shutdown)
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('login')
    args = parser.parse_args()
    try:
        if args.command == 'login':
            login(Path(os.environ.get('BROWSER_PROFILE', '/browser-profile')))
    except KeyboardInterrupt:
        pass
    except ValueError as error:
        parser.exit(1, str(error)+'\n')


if __name__ == '__main__':
    main()

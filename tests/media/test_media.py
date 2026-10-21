from decimal import Decimal
import json
import os
from pathlib import Path
import struct
from urllib.request import urlopen

import pytest
pytest.importorskip('playwright.sync_api', reason='Media browser tests run in Dockerfile.media')
from playwright.sync_api import sync_playwright
from wger_strava.media.browser import attach_mock, profile_lock
from wger_strava.media.render import html, render
from wger_strava.media.summary import demo, formatted_volume, volume


def test_volume_counts_only_actual_external_load_repetitions():
    sets = [{'weight':100,'repetitions':10}, {'weight':50,'repetitions':4},
            {'repetitions':20}, {'duration':90,'weight':100}, {'weight':0,'repetitions':20}]
    assert volume(sets,'kg') == Decimal(1200)
    assert formatted_volume(sets,'lb') == '2,646'


@pytest.mark.parametrize('item', [{'weight':'NaN','repetitions':1},{'weight':-1,'repetitions':1},{'weight':10,'repetitions':'Infinity'}])
def test_invalid_volume_values(item):
    with pytest.raises(ValueError):
        volume([item])


def test_render_escapes_workout_names_and_rejects_unknown_design():
    summary = {**demo(),'title':'<script>document.cookie</script>'}
    assert '<script>' not in html(summary,'light','summary')
    with pytest.raises(ValueError):
        html(summary,'neon','summary')


def test_profile_has_exclusive_lock(tmp_path):
    with profile_lock(tmp_path):
        with pytest.raises(ValueError,match='busy'):
            with profile_lock(tmp_path):
                pass
    with profile_lock(tmp_path):
        assert tmp_path.stat().st_mode & 0o777 == 0o700


@pytest.fixture(scope='module')
def cards(tmp_path_factory):
    output=tmp_path_factory.mktemp('cards')
    render(output)
    return output


def sign_in(page, origin, athlete='123456'):
    page.goto(origin+'/login')
    page.get_by_label('Athlete ID').fill(athlete)
    page.get_by_role('button',name='Sign in').click()


def test_four_cards_are_exact_size_and_render_deterministically(cards,tmp_path):
    render(tmp_path)
    individual = [path for path in cards.glob('*.png') if path.name != 'concepts.png']
    for path in individual:
        raw=path.read_bytes()
        assert struct.unpack('>II',raw[16:24]) == (1080,1080)
        assert raw == (tmp_path/path.name).read_bytes()
    assert len(individual) == 4
    assert (cards/'concepts.png').read_bytes() == (tmp_path/'concepts.png').read_bytes()


def test_browser_upload_persists_after_restart_and_never_repeats(cards,tmp_path):
    origin=os.environ['MOCK_WEB_URL']
    images=[cards/'light-summary.png',cards/'light-comparison.png']
    journal=tmp_path/'upload.json'
    with sync_playwright() as p:
        context=p.chromium.launch_persistent_context(str(tmp_path/'profile'),headless=True,channel='chromium')
        page=context.new_page()
        sign_in(page,origin)
        record=attach_mock(page,origin,101,123456,images,journal)
        assert record['state']=='attached'
        context.close()
        context=p.chromium.launch_persistent_context(str(tmp_path/'profile'),headless=True,channel='chromium')
        try:
            page=context.new_page()
            page.goto(origin+'/activities/101')
            assert page.locator('#photos img').count()==2
            assert attach_mock(page,origin,101,123456,images,journal)['state']=='attached'
            state=json.load(urlopen(origin+'/state'))
            assert state['posts']['101']==1
            with pytest.raises(ValueError,match='different activity'):
                attach_mock(page,origin,999,123456,images,journal)
        finally:
            context.close()


def test_mismatched_browser_account_cannot_upload(cards,tmp_path):
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chromium')
        try:
            page=browser.new_page()
            sign_in(page,os.environ['MOCK_WEB_URL'],'999')
            with pytest.raises(ValueError,match='Browser account'):
                attach_mock(page,os.environ['MOCK_WEB_URL'],102,123456,
                            [cards/'dark-summary.png',cards/'dark-comparison.png'],tmp_path/'job.json')
            assert not (tmp_path/'job.json').exists()
        finally:
            browser.close()


def test_ambiguous_save_is_held_instead_of_uploading_again(cards,tmp_path):
    journal=tmp_path/'job.json'
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chromium')
        try:
            page=browser.new_page()
            page.set_default_timeout(3000)
            origin=os.environ['MOCK_WEB_URL']
            sign_in(page,origin)
            page.route('**/activities/103',lambda route: route.abort() if route.request.method=='POST' else route.continue_())
            with pytest.raises(Exception):
                attach_mock(page,origin,103,123456,[cards/'light-summary.png',cards/'light-comparison.png'],journal)
            assert json.loads(journal.read_text())['state']=='uncertain'
            with pytest.raises(ValueError,match='uncertain'):
                attach_mock(page,origin,103,123456,[cards/'light-summary.png',cards/'light-comparison.png'],journal)
        finally:
            browser.close()


def test_prototype_will_not_target_live_strava(cards,tmp_path):
    with pytest.raises(ValueError,match='restricted'):
        attach_mock(None,'https://www.strava.com',101,123456,
                    [cards/'light-summary.png',cards/'light-comparison.png'],tmp_path/'job.json')


def test_expired_login_pauses_before_selecting_files(cards,tmp_path):
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='chromium')
        try:
            page=browser.new_page()
            sign_in(page,os.environ['MOCK_WEB_URL'])
            page.context.clear_cookies()
            with pytest.raises(ValueError,match='needs login'):
                attach_mock(page,os.environ['MOCK_WEB_URL'],104,123456,
                            [cards/'light-summary.png',cards/'light-comparison.png'],tmp_path/'job.json')
            assert not (tmp_path/'job.json').exists()
        finally:
            browser.close()

import json
import pytest
from types import SimpleNamespace
from wger_strava.media.muscles import collect, sparky_session
from wger_strava.media.queue import snapshot
from wger_strava.media.summary import from_activity
from wger_strava.media.render import html


def test_normalizes_source_anatomy_and_primary_wins_across_exercises():
    groups = collect([
        {'primary_muscles': ['Quadriceps', 'lower_back'], 'secondary_muscles': ['GLUTES', 'hamstrings']},
        {'primary_muscles': ['gluteus maximus'], 'secondary_muscles': ['quadriceps', 'hip adductors', 'Unknown custom muscle']},
    ])
    assert groups == {'primary': ['glutes', 'lower_back', 'quads'],
                      'secondary': ['adductors', 'hamstrings'], 'unmapped_muscles': ['Unknown custom muscle']}


def test_wger_english_and_latin_names_ignore_ids_and_unknown_regions():
    assert collect([{'muscles': [{'id': 4, 'name_en': '', 'name': 'Pectoralis major'}],
                     'muscles_secondary': [{'name_en': 'Triceps', 'name': 'Triceps brachii'}, 99]}],
                   'muscles', 'muscles_secondary') == {
                       'primary': ['chest'], 'secondary': ['triceps'], 'unmapped_muscles': []}
    assert collect([{'primary_muscles': ['Unrecognized muscle'], 'secondary_muscles': None}]) == {
        'primary': [], 'secondary': [], 'unmapped_muscles': ['Unrecognized muscle']}


def test_only_completed_exercises_reach_snapshot_and_rendered_highlights():
    groups = sparky_session({'exercises': [
        {'exercise_snapshot': {'primary_muscles': ['chest'], 'secondary_muscles': ['triceps']},
         'sets': [{'completed_at': '2026-10-21T15:00:00Z'}]},
        {'exercise_snapshot': {'primary_muscles': ['quadriceps']}, 'sets': [{'completed_at': None}]},
    ]})
    plan = {'name': 'Bench', 'muscles': groups, 'payload': {
        'start_time': '2026-10-21T14:00:00Z', 'elapsed_time': 900,
        'sets': [{'exercise_type': 'BARBELL_BENCH_PRESS', 'weight': 40, 'repetitions': 8}]}}
    job = json.loads(json.dumps(snapshot(plan, SimpleNamespace(timezone='America/Edmonton', media_units='lb'))))
    summary = from_activity(job)
    assert summary['primary'] == ['chest'] and summary['secondary'] == ['triceps']
    markup = html(summary, 'dark', 'summary')
    assert 'class="muscle primary" data-muscle="chest"' in markup
    assert 'class="muscle secondary" data-muscle="triceps"' in markup
    assert 'class="muscle inactive" data-muscle="quads"' in markup


def test_wger_export_fetches_anatomy_once_and_persists_it(tmp_path):
    from test_watch import Source, Destination
    from wger_strava.config import Config
    from wger_strava.engine import Engine
    from wger_strava.state import State
    source = Source(True)
    source.complete = True
    original = source.request
    reads = []
    def request(method, path):
        if path == '/api/v2/exerciseinfo/1/':
            reads.append(path)
            return {'muscles':[{'name':'Pectoralis major', 'name_en':'Chest'}],
                    'muscles_secondary':[{'name':'Triceps brachii','name_en':'Triceps'}]}
        return original(method, path)
    source.request = request
    state = State(tmp_path)
    state.set('mappings', {'1':'BARBELL_BENCH_PRESS'})
    config = Config(tmp_path, 'https://source.test', 'key', 'client', 'secret', since=source.day, media_enabled=True)
    engine = Engine(config, state, source, Destination())
    try:
        assert engine.sync()['submitted'] == 1
        assert engine.sync()['submitted'] == 0
        job = json.loads((tmp_path/'media/outbox/99.json').read_text())
        assert job['primary'] == ['chest'] and job['secondary'] == ['triceps']
        assert reads == ['/api/v2/exerciseinfo/1/']
        assert engine.sync()['submitted'] == 0 and len(reads) == 1
    finally:
        engine.close()
        state.close()


@pytest.mark.parametrize('malformed', [False, True])
def test_wger_missing_optional_exercise_details_does_not_block_export(tmp_path, malformed):
    from wger_strava.api import APIError
    from wger_strava.engine import Engine
    engine = Engine.__new__(Engine)
    engine.config = SimpleNamespace(timezone='UTC', media_units='lb')
    class Missing:
        def request(self, method, path):
            if malformed:
                raise ValueError('Malformed exercise-info response')
            raise APIError(method, path, 404)
    engine.wger = Missing()
    job = engine.media_snapshot({'name':'Deleted exercise','payload':{},'exercise_ids':['7']})
    assert job['primary'] == job['secondary'] == []
    assert job['unavailable_exercises'] == ['7']

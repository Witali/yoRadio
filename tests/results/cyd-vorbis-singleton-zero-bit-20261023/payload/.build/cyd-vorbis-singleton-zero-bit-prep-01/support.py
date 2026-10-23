"""Source identities and ordinary helper loading; no bitstream/codec implementation."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tests/vorbis_format_corpus/generate_books.py').is_file())
INPUT = HERE / 'inputs/original'
OLD = HERE / 'provenance/prior-preparation'
IDS = tuple(f'map1_{kind}_single_d16_seq{seq}' for kind in ('dense', 'sparse') for seq in (0, 1))
MANIFEST_SHA = '3ad3a1f9b466d92b2c701c787bdec42ed708cfa9146a3804dcf3d5cc766aeadf'
MATRIX_SHA = 'aa6aeb079bf7b810e0aee0e251468eddd3fb6bf2049bad6d2f9ba91aca2a1294'
HOST_REPORT_SHA = '5bc50a664ecc5e5cac92119ff6efc9cd211194ac7f43d9f8471e84cde61f68e6'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, filename, expected):
    path = OLD / filename
    need(sha(path.read_bytes()) == expected, 'exact_prior_helper_source')
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fact(path):
    raw = path.read_bytes()
    return dict(path=str(path.resolve()), bytes=len(raw), sha256=sha(raw))


def source_closure(expected):
    raw = (HERE / 'readiness.json').read_bytes()
    need(sha(raw) == expected, 'reviewed_readiness_pin')
    m = json.loads(raw)
    need(m['schema'] == 'singleton-zero-bit-source-only-readiness-v1' and m['runtime_executed'] is False, 'source_only_readiness')
    names = {p.relative_to(HERE).as_posix() for p in HERE.rglob('*') if p.is_file()}
    need(names == set(m['files']) | {'readiness.json'}, 'complete_preparation_file_set')
    for name, x in m['files'].items():
        p = (HERE / name).resolve()
        need(p.is_relative_to(HERE) and p.stat().st_size == x['bytes'] and sha(p.read_bytes()) == x['sha256'], 'preparation_raw_identity')
    origins = json.loads((HERE / 'source-pins.json').read_bytes())['inputs']
    for x in origins:
        need(fact(Path(x['source']))['sha256'] == x['sha256'], 'original_input_identity')
    return [fact(HERE / n) for n in sorted(names)] + [fact(Path(x['source'])) for x in origins]


def originals():
    need(sha((INPUT / 'manifest.json').read_bytes()) == MANIFEST_SHA and sha((INPUT / 'matrix.json').read_bytes()) == MATRIX_SHA,
         'actual_original_generation_pins')
    need(sha((HERE / 'provenance/original-host-report.json').read_bytes()) == HOST_REPORT_SHA, 'actual_original_host_NONPASS_pin')
    matrix = json.loads((INPUT / 'matrix.json').read_bytes()); fields = json.loads((INPUT / 'bitfields.json').read_bytes())
    manifest = json.loads((INPUT / 'manifest.json').read_bytes()); entries = {x['path']: x for x in manifest['files']}
    cases = [c for c in matrix['cases'] if c['id'] in IDS]
    need(matrix['case_count'] == 8 and [c['id'] for c in cases] == list(IDS), 'exact_four_original_map1_cases')
    for name in ('matrix.json', 'bitfields.json', 'pure-checks.json'):
        raw = (INPUT / name).read_bytes(); x = entries[name]
        need(len(raw) == x['bytes'] and sha(raw) == x['sha256'], 'original_metadata_manifest_identity')
    payloads = {}
    for c in cases:
        for k in ('identification', 'comment', 'setup', 'audio', 'ogg'):
            name = c[k]; p = (INPUT / name).resolve(); need(p.is_relative_to(INPUT), 'bounded_original_member')
            raw = p.read_bytes(); x = entries[name]
            need(len(raw) == x['bytes'] and sha(raw) == x['sha256'] and c['files'][k] == dict(bytes=len(raw), sha256=sha(raw)),
                 'original_raw_map1_identity')
            payloads[name] = raw
    return cases, fields, payloads


def fresh_output(path):
    p = path.resolve(); build = ROOT / '.build'
    need(p != build and p.is_relative_to(build) and not p.exists() and
         not p.is_relative_to(HERE) and not HERE.is_relative_to(p), 'fresh_separate_build_output')
    return p

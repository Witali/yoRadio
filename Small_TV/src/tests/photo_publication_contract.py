"""Recheck saved cold-publication images and callback traces without running QEMU."""
import argparse
import copy
import json
from pathlib import Path

from jpeg_lossless_fixtures import load, pixels
from photo_flash_evidence import journal, ready_frame
from photo_publication_qemu import CASES, GRAY_SHA, check_cut, sha
from verify_jpeg_clock_evidence import protected


def validate(report, plan, bundle, read):
    """Require exact cut/cold bytes, physical authority and a successful recovery."""
    assert report['passed'] and not any(report[key] for key in ('all_functionality_verified',
        'network_acceptance', 'lcd_acceptance', 'physical_power_cut_tested', 'hardware_tested'))
    names = [row['name'] for row in report['cases']]
    assert len(names) == len(set(names)) and set(names) <= set(CASES)
    fixtures, _, _ = load(bundle)
    rows = json.loads(bundle.read_text())['fixtures']
    old = next(row for row in rows if row['channels'] == 4)
    new = next(row for row in rows if row['channels'] == 3)
    source = fixtures[new['name']]; reference = pixels(3)
    mutable = [(0x9000, 0xf000), (0x3e7000, 0x3e8000), (0x264000, 0x27d000)]
    owned = [*plan['backing']['extents'], *plan['metadata']['extents'], *plan['caches'][4]['extents']]
    mutable += [(r['offset'], r['offset']+r['bytes']) for r in owned]
    for row in report['cases']:
        case = row['name']; assert row['passed'] and len(row['boots']) == 2
        warm, cold = row['boots']
        assert warm['owners_stopped'] and warm['abrupt'] and cold['owners_stopped'] and not cold['abrupt']
        assert warm['name'] != cold['name']
        initial = read(case+'/warm/initial.bin')
        cut = read(case+'/cut-stopped.bin'); recovered = read(case+'/recovered.bin')
        assert len(initial) == len(cut) == len(recovered) == 0x400000
        assert read(case+'/cut-paused.bin') == read(case+'/warm/flash.bin') == cut
        assert read(case+'/cold/initial.bin') == cut
        assert read(case+'/cold/flash.bin') == recovered
        assert sha(initial) == warm['initial_sha256'] == warm['prepared_sha256']
        assert sha(cut) == row['cut_sha256'] == cold['initial_sha256'] == cold['prepared_sha256']
        assert sha(recovered) == row['recovery_sha256']
        decision = check_cut(case, initial, cut, plan, old, new, source, reference)
        assert row['journal'] == decision['journal']
        assert journal(initial, plan)['entries'][:4] == decision['journal']['entries'][:4]
        assert row['cold_visible'] == row['expected_visible'] == decision['expected_visible']
        assert row['recovery'] == ready_frame(recovered, plan, 4,
            report['recovery_source_sha256'], GRAY_SHA)
        assert journal(initial, plan)['entries'][:4] == journal(recovered, plan)['entries'][:4]
        protected(initial, cut, mutable); protected(initial, recovered, mutable)
        if case not in ('first-chunk', 'complete'):
            trace = row['trace']; assert trace['boundary'] == case and row['interrupted_http_error']
            events = trace['completed_callbacks']; assert events and trace['cut_pc'] == events[-1]['return_pc']
            targets = []
            for event in events:
                name = event['function']; assert event['status'] == 0 and report['entries'][name] == event['pc']
                assert len(event['instruction_sha256']) == 64
                if name == 'flash_program':
                    address, size = event['address'], event['bytes']
                    assert 0 < size <= 256 and address//256 == (address+size-1)//256
                    target = case == 'frame-page' and address == plan['caches'][4]['extents'][0]['offset']
                    for extent in plan['metadata']['extents']:
                        if extent['offset'] <= address < extent['offset']+extent['bytes']:
                            relative = (address-extent['offset']) % 4096
                            target |= (case.endswith('-body') and relative == 0 or
                                       case.endswith('-footer') and relative == 3840)
                else:
                    assert name in ('flash_erase', 'esp_partition_erase_range')
                    target = (case == 'source-erased' and name == 'esp_partition_erase_range'
                              and event['address'] == 4*102400 and event['bytes'] == 102400)
                targets.append(target)
            assert targets[-1] and not any(targets[:-1])
        for boot in ('warm', 'cold'):
            uart = read(case+'/'+boot+'/uart.log')
            assert uart.count(b'ESP-ROM:esp32c2') == 1
            assert not any(text in uart for text in (b'Guru Meditation', b'assert failed',
                b'abort() was called', b'watchdog got triggered'))
            prepared = json.loads(read(case+'/'+boot+'/prepared.json'))
            expected = initial if boot == 'warm' else cut
            assert sha(expected) == prepared['prepared_flash_sha256']
            assert prepared['sources']['source_sha256'] == report['source_sha256']
            app = next(item for item in prepared['sources']['images'] if item['file'] == 'app.bin')
            offset = int(app['offset'], 0)
            assert sha(expected[offset:offset+app['bytes']]) == app['sha256'] == report['app_sha256']
    return dict(passed=True, cases=len(names), complete_boundaries=set(names) == set(CASES),
        cold_boots=len(names), successful_recoveries=len(names), physical_power_cut_tested=False)


def rejection_checks(report, plan, bundle, read):
    """Reject false visibility, skipped completion and corrupted physical evidence."""
    validate(report, plan, bundle, read); rejected = []
    candidates = ('cold-visible', 'owner-running', 'wrong-return', 'cold-reseed', 'recovery-frame')
    for mode in candidates:
        changed = copy.deepcopy(report); first = changed['cases'][0]; case = first['name']
        replacement = {}
        if mode == 'cold-visible': first['cold_visible']['exists'] = not first['cold_visible']['exists']
        elif mode == 'owner-running': first['boots'][0]['owners_stopped'] = False
        elif mode == 'wrong-return':
            target = next(row for row in changed['cases'] if row.get('trace'))
            target['trace']['completed_callbacks'][-1]['status'] = 1
        elif mode == 'cold-reseed':
            key = case+'/cold/initial.bin'; data = bytearray(read(key)); data[0] ^= 1
            replacement[key] = bytes(data)
        elif mode == 'recovery-frame':
            key = case+'/recovered.bin'; data = bytearray(read(key))
            data[plan['caches'][4]['extents'][0]['offset']] ^= 1; replacement[key] = bytes(data)
        def altered(name):
            return replacement[name] if name in replacement else read(name)
        try: validate(changed, plan, bundle, altered)
        except AssertionError: rejected.append(mode)
        else: raise AssertionError('Unsafe publication evidence accepted: '+mode)
    return rejected


def main():
    """Check a completed local run and the exact producer source pins."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True); args = parser.parse_args()
    root = Path(__file__).resolve().parents[3]
    report = json.loads((args.run/'report.json').read_text())
    for name, digest in report['inputs_sha256'].items(): assert sha(Path(name).read_bytes()) == digest, name
    archive = root/'firmware/development/small-tv-esp32c2-reconstructed'
    plan = json.loads((archive/'jpeg-cache-plan.json').read_text())
    bundle = root/'Small_TV/src/tests/fixtures/jpeg_extended/lossless6-manifest.json'
    read = lambda name: (args.run/name).read_bytes()
    result = validate(report, plan, bundle, read)
    result['rejected_controls'] = rejection_checks(report, plan, bundle, read)
    print(json.dumps(result))


if __name__ == '__main__': main()

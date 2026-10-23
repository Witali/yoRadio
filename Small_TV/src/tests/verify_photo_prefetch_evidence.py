"""Verify prefetch timing, complete LCD surfaces and durable cold-cache evidence."""
import argparse
import gzip
import json
from pathlib import Path

from photo_cache_frame_contract import validate, rejection_checks
from verify_photo_cache_evidence import rgb, sha


def verify(path, root):
    """Reconstruct physical bytes and check actual RGB captures, not green flags."""
    proof = json.loads(path.read_text(encoding='utf-8'))
    assert proof['passed'] and not proof['all_functionality_verified']
    blobs = {}
    for row in proof['blobs']:
        file = (path.parent/row['file']).resolve()
        assert file.is_relative_to(path.parent.resolve())
        encoded = file.read_bytes();assert sha(encoded) == row['gzip_sha256']
        data = gzip.decompress(encoded)
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
        assert row['sha256'] not in blobs;blobs[row['sha256']] = data
    raw = {}
    for row in proof['raw']:
        assert row['source'] not in raw;raw[row['source']] = blobs[row['sha256']]
    report = json.loads(raw[proof['report_source']]);assert report == proof['display']
    validate(report);assert rejection_checks(report) == report['contract_rejections']
    stock = json.loads(raw[proof['factory_timing_source']])
    assert stock['passed'] and stock['case'] == dict(name='first-photo',mask=31,cycles=1,day=0,night_mode=0,night=500)
    assert stock['samples'][0]['guest_seconds'] == report['factory_first_photo_seconds']
    prefix = proof['report_source'].rsplit('/',1)[0]
    flows = dict(report['flows']['reconstructed']);flows['cold'] = report['cold']
    count = 0
    for name, flow in flows.items():
        for index, row in enumerate(flow['samples']):
            pixels = rgb(raw[f'{prefix}/reconstructed-{name}/{index}-complete.png'])
            assert len(pixels) == 57600*3
            assert sha(pixels) == row['qemu_rgb_sha256'] == row['replayed_rgb_sha256']
            count += 1
    assert count == sum(len(f['samples']) for f in flows.values()) and count >= 98
    first = flows['all-photos']['samples'][0]['guest_seconds']
    assert proof['startup_latency_matches_factory'] is True and first <= report['factory_first_photo_seconds']
    base = blobs[proof['flash_base_sha256']];assert len(base) == 0x400000
    images = {}
    for row in proof['images']:
        data = bytearray(base);previous = -4096
        for change in row['sectors']:
            offset = change['offset'];sector = blobs[change['sha256']]
            assert offset % 4096 == 0 and previous < offset <= len(data)-4096 and len(sector) == 4096
            data[offset:offset+4096] = sector;previous = offset
        assert sha(data) == row['sha256'];key = (row['profile'],row['when'])
        assert key not in images;images[key] = bytes(data)
    assert len(images) == 10
    plan = json.loads((root/'firmware/development/small-tv-esp32c2-reconstructed/jpeg-cache-plan.json').read_text())
    mutable = sorted([(0x9000,0xf000),(0x3e7000,0x3e8000)]+
        [(r['offset'],r['offset']+r['bytes']) for r in plan['candidate_extents']])
    for name in flows:
        before, after = images[name,'before'],images[name,'after']
        prepared = json.loads(raw[f'{prefix}/reconstructed-{name}/prepared.json'])
        assert sha(before) == prepared['prepared_flash_sha256']
        cursor = 0
        for start, end in mutable:
            assert before[cursor:start] == after[cursor:start];cursor = end
        assert before[cursor:] == after[cursor:]
    cold_before, cold_after = images['cold','before'],images['cold','after']
    assert cold_before == images['all-photos','after']
    assert sha(cold_before) == report['cold']['cold_from_sha256']
    for row in plan['candidate_extents']:
        start, end = row['offset'],row['offset']+row['bytes']
        assert cold_before[start:end] == cold_after[start:end]
    model = json.loads(raw[proof['machine_report_source']])
    assert model['passed'] and model['slideshow']['steps'] == 13440
    for name, address in report['cold']['cold_write_traps'].items():
        assert len(model['callbacks'][name]) == 1 and model['callbacks'][name][0]['address'] == address
    for name, digest in proof['source_pins'].items():assert sha((root/name).read_bytes()) == digest, name
    archive = root/'firmware/development/small-tv-esp32c2-reconstructed'
    manifest = json.loads((archive/'manifest.json').read_text())
    assert manifest['source_sha256'] == report['source_sha256']
    assert manifest['elf_sha256'] == report['native_elf_sha256'] == model['native_elf_sha256']
    for row in manifest['images']:assert sha((archive/row['file']).read_bytes()) == row['sha256']
    assert next(r['sha256'] for r in manifest['images'] if r['file'] == 'app.bin') == report['app_sha256'] == model['app_sha256']
    return dict(passed=True,frames=count,compared_pixels=count*57600,physical_images=len(images),
                first_photo_guest_seconds=first,cold_first_guest_seconds=flows['cold']['samples'][0]['guest_seconds'],
                cold_cache_program_or_erase_attempts=0,cold_complete_flash_unchanged=cold_before==cold_after)


def main():
    """Read the saved evidence without emulation, ELF execution or flash writes."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    args = parser.parse_args();print(json.dumps(verify(args.proof,args.root)))


if __name__ == '__main__':
    main()

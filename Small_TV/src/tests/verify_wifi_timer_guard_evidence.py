"""Replay the guarded candidate's linked paths, source identity and exact CPU tests."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'tools'))
from verify_wifi_timer_guard import verify as verify_links
from wifi_timer_guard_test import verify_behavior
from verify_photo_format_matrix_evidence import source_hashes


def sha(data):
    """Check compressed evidence and every actual firmware input."""
    return hashlib.sha256(data).hexdigest()


def verify(path, root, libraries, rom, revision=None):
    """Keep host guard acceptance distinct from future QEMU and hardware qualification."""
    proof = json.loads(path.read_bytes())
    assert proof['schema'] == 'wifi-timer-guard-evidence-v1' and proof['passed'] is True
    assert proof['h10_checks_passed'] is False and proof['all_functionality_verified'] is False
    assert proof['physical_hardware_tested'] is False and proof['runtime_qualification_completed'] is False
    assert source_hashes(root,proof['source_pins'],revision) == proof['source_pins']
    file = (path.parent / proof['unit']['file']).resolve()
    assert file.is_relative_to(path.parent.resolve())
    packed = file.read_bytes()
    assert sha(packed) == proof['unit']['gzip_sha256']
    raw = gzip.decompress(packed)
    assert sha(raw) == proof['unit']['sha256']
    unit = json.loads(raw)
    variant = root / 'firmware/development/small-tv-esp32c2-reconstructed'
    manifest = json.loads((variant / 'manifest.json').read_bytes())
    app = (variant / 'app.bin').read_bytes()
    elf = (root / '.build/small-tv-esp32c2/small_tv_reconstructed.elf').read_bytes()
    assert sha(app) == proof['app_sha256'] and sha(elf) == proof['elf_sha256'] == manifest['elf_sha256']
    assert manifest['source_sha256'] == proof['source_sha256'] and manifest['debug_logging'] is False
    source = json.loads((variant / 'source-manifest.json').read_bytes())
    canonical = json.dumps(source['files'],separators=(',',':'),sort_keys=True).encode()
    assert sha(canonical) == source['aggregate_sha256'] == proof['source_sha256']
    src = root / 'Small_TV/src'
    for row in source['files']:
        file = root / '.build/small-tv-esp32c2/resources' / row['file'][10:] if row['file'].startswith('generated/') else src / row['file']
        assert sha(file.read_bytes()) == row['sha256'], 'Compiled source changed: ' + row['file']
    link_report = json.loads((variant / 'wifi-timer-guard.json').read_bytes())
    prefix = proof['producer_root'].replace('\\','/').rstrip('/') + '/'
    for report in (unit,link_report):
        for name,digest in report.pop('inputs_sha256').items():
            name = name.replace('\\','/')
            assert name.startswith(prefix) and proof['source_pins'][name[len(prefix):]] == digest
    assert link_report == verify_links(elf,app,libraries,rom.read_bytes())
    assert unit.pop('inputs_unchanged') is True
    assert unit == verify_behavior(elf,app,libraries,rom.read_bytes())
    assert source_hashes(root,proof['source_pins'],revision) == proof['source_pins'], 'Guard analysis source changed during replay'
    return {'passed':True,'behavior_cases':unit['behavior_cases'],'guarded_out_of_table_reads':0,
            'rom_byte_cases':unit['rom_ingress']['rom_event_byte_cases'],
            'sdk_initializer_cases':len(unit['rom_ingress']['sdk_initializer_feature_cases']),
            'unguarded_vendor_control_detected':unit['unguarded_vendor_control_defect_detected'],
            'runtime_qualification_completed':False,'h10_checks_passed':False}


def main():
    """Read only saved candidate inputs and use private host instruction fixtures."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--proof',type=Path,required=True)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[3])
    parser.add_argument('--sdk-libraries',type=Path,required=True)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--source-revision')
    args = parser.parse_args()
    print(json.dumps(verify(args.proof,args.root,args.sdk_libraries,args.rom,args.source_revision)))


if __name__ == '__main__':
    main()

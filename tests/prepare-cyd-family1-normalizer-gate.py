"""Prepare an enabled-normalizer gate and independent goldens; native UNRELEASED.

Only current owned data helpers run. Captured executables/scripts never run.
This command exposes no build/native execution option before root review.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROFILE_ROOT = ROOT / 'tests/target/cyd_family1_normalizer_qemu'
DATA_ROOT = ROOT / 'tests/fixtures/family1_normalizer'
NATIVE_RELEASE = 'UNRELEASED'


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')


def prepare(args):
    out = args.output.resolve(); capture = args.reference_capture.resolve()
    if not out.is_relative_to(ROOT / '.build') or out == ROOT / '.build' or out.exists():
        raise ValueError('fresh contained caller-owned ignored output')
    if not capture.is_relative_to(ROOT / '.build') or not capture.is_dir() or out.is_relative_to(capture):
        raise ValueError('separate original local reference capture')
    out.mkdir(parents=True)
    report = dict(passed=False, prepared_only=True, native_launch=NATIVE_RELEASE, native_executed=False,
                  compiled=False, physical_hardware=False, production_watchdog_equivalence=False)
    try:
        model = module('enabled_normalizer_integer_model', DATA_ROOT / 'model.py')
        reader = module('enabled_normalizer_records', DATA_ROOT / 'records.py')
        pcm, provenance = reader.reference_subphase(capture)
        (out / 'reference-F12.pcm').write_bytes(pcm)
        model_out = out / 'golden'; model_out.mkdir()
        golden = model.prepare(pcm, model_out)
        write(out / 'golden.json', golden); write(out / 'reference-subphase.json', provenance)
        base = module('owned_family1_capture_utilities', ROOT / 'tests/run-cyd-family1-playback-task-qemu.py')
        model.need(provenance['sdk_commit'] == base.SDK_COMMIT and provenance['vendor_commit'] == base.VENDOR_COMMIT and
                   provenance['vendor_archives'] == base.ARCHIVE_PINS, 'original reference uses exact current SDK/vendor archive identities')
        model.need(all(sha(REPO / '.idf/esp-adf-libs/esp_audio_codec/lib/esp32' / name) == digest
                       for name, digest in base.ARCHIVE_PINS.items()), 'current public archive bytes match original direct reference')
        parameters = SimpleNamespace(output=out, source_release=args.source_release.resolve(),
            vendor=REPO / '.idf/esp-adf-libs/esp_audio_codec')
        campaign = base.Campaign(parameters)
        def no_process(*unused, **ignored):
            raise ValueError('process launch forbidden during unreleased pure preparation')
        campaign.run_command = no_process
        # freeze_sources/reference use only file copies/current pure fixture
        # preparation. No run_command, SDK, Git, decoder or archived code runs.
        campaign.freeze_sources()
        entry = next(x for x in campaign.report['pcm_reference']['entries'] if x['id'] == 12)
        model.need(entry['hold_offset'] == 8413 and entry['hold_after_complete_audio_packets'] == 1 and
                   entry['packet_count'] == 2 and entry['pre_skip'] == 312 and entry['raw_frames'] == 10560 and
                   entry['logical_frames'] == 9600, 'fixed original first-complete-packet/page transport boundary')
        for source in sorted(base.HARNESS.rglob('*')):
            if source.is_file():
                campaign.freeze(source, Path('sources/shared-family1') / source.relative_to(base.HARNESS), 'unchanged shared family1 target source')
        # Generated original asset views are shared byte-for-byte. The base
        # component's binary-data directive resolves relative to its own file.
        for name in ('reference.h', 'asset_size.h', 'fixtures.bin'):
            source = out / 'sources/harness/project/main' / name
            destination = out / 'sources/shared-family1/project/main' / name
            destination.write_bytes(source.read_bytes())
        owned = [Path(__file__).resolve(), DATA_ROOT / 'model.py', DATA_ROOT / 'records.py',
                 ROOT / 'tests/test-cyd-family1-normalizer-model.py']
        owned += [p for p in PROFILE_ROOT.rglob('*') if p.is_file()]
        for source in owned:
            campaign.freeze(source, Path('sources/normalizer') / source.relative_to(ROOT), 'new reviewed enabled-normalizer profile/data/control source')
        for name in ('main.cpp', 'CMakeLists.txt'):
            source = PROFILE_ROOT / 'project/main' / name
            campaign.freeze(source, Path('sources/harness/project/main') / name, 'new thin native profile over frozen shared target')
        write(out / 'source-manifest.json', campaign.sources)
        # Includes/CMake aliases are explicit: retained original base files also
        # remain in the prepared project. A future compiler closure must map
        # each actual path via these exact bytes instead of assuming one alias.
        aliases = {}
        for path in sorted((out / 'sources').rglob('*')):
            if path.is_file():
                aliases[path.relative_to(out).as_posix()] = dict(bytes=path.stat().st_size, sha256=sha(path))
        write(out / 'prepared-source-aliases.json', aliases)
        source_current = all(Path(p).is_file() and sha(p) == record['sha256'] and Path(p).stat().st_size == record['bytes']
                             for p, record in campaign.sources.items())
        model.need(source_current, 'every live input unchanged after pure preparation')
        report.update(passed=True, all_bound_inputs_current=True, source_bindings=len(campaign.sources),
            frozen_aliases=len(aliases), production35_release_sha256=base.SOURCE_RELEASE_SHA,
            creator_F12_transport_sha256='c6a06d1bf954c9119f844167d43b3f080bdbe4e7c2a305318109e524cf3b6757',
            source_reference=provenance, profile=model.PROFILE, witnesses=golden['witnesses'],
            transport_plan={k: entry[k] for k in ('original_source_sha256', 'whole_bytes', 'whole_sha256',
                'split_bytes', 'split_sha256', 'hold_offset', 'hold_after_complete_audio_packets', 'packet_count', 'mapping')},
            logical_source_bytes=153600, logical_mono_bytes=19200, final_padding_bytes=256,
            diagnostic_watchdogs=dict(task_seconds=20, panic=True, interrupt_ms=1000, heap='light'),
            remaining_gates=['root source/oracle review', 'fresh actual compiler/link closure and image fit',
                             'root-authorized SDK/QEMU execution', 'strict actual transcript and full golden PCM comparison'],
            artifact_sha256={p.relative_to(out).as_posix(): sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name != 'report.json'})
        return report
    except BaseException as error:
        report.update(failure_type=type(error).__name__)
        raise
    finally:
        write(out / 'report.json', report)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--reference-capture', type=Path, default=ROOT / '.build/cyd-family1-playback-task-20261103-04')
    parser.add_argument('--source-release', type=Path, default=ROOT / '.build/cyd-family1-source-release-20261103-02.json')
    args = parser.parse_args()
    if not args.prepare_only or NATIVE_RELEASE != 'UNRELEASED':
        raise ValueError('native launch is UNRELEASED; only explicit pure --prepare-only is implemented')
    result = prepare(args)
    print(json.dumps({k: result[k] for k in ('passed', 'prepared_only', 'native_launch', 'native_executed', 'source_bindings', 'frozen_aliases', 'logical_source_bytes', 'logical_mono_bytes', 'final_padding_bytes', 'witnesses')}, sort_keys=True))


if __name__ == '__main__':
    main()

"""Negative checks for complete native Opus reference witnesses; no native run."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'tests/run-cyd-espressif-opus-task-qemu.py'
spec = importlib.util.spec_from_file_location('canonical_opus_task_reader', path)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def verify(folder):
    folder = folder.resolve()
    args = SimpleNamespace(idf=reader.REPO / '.idf/v6.0.2',
        vendor=reader.REPO / '.idf/esp-adf-libs/esp_audio_codec',
        qemu=ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe',
        fixture=ROOT / 'tests/fixtures/esp32c3_calibration/opus-510.ogg')
    report = json.loads((folder / 'report.json').read_bytes())
    assert report['passed'] and report['completed'] and report['target_executed']
    reader.validate_reference_witness(report, folder, args)
    rejected = []

    def reject(name, mutate):
        candidate = copy.deepcopy(report)
        mutate(candidate)
        try:
            reader.validate_reference_witness(candidate, folder, args)
        except (ValueError, KeyError, IndexError):
            rejected.append(name)
        else:
            raise AssertionError('Incomplete witness accepted: ' + name)

    reject('empty_commands', lambda r: r.update(commands=[]))
    reject('missing_build_command', lambda r: r.update(commands=[x for x in r['commands'] if x['name'] != 'build']))
    reject('duplicate_command', lambda r: r['commands'][-1].update(name='merge'))
    reject('empty_artifacts', lambda r: r.update(build_outputs={}))
    for name in ('sdk-child.json', 'qemu-flash.bin', 'build/cyd_espressif_opus_qemu.elf', 'build/compile_commands.json'):
        reject('missing_' + name, lambda r, key=name: r['build_outputs'].pop(key))
    reject('empty_inputs', lambda r: r.update(inputs={}))
    for suffix in ('main/main.c', 'main/CMakeLists.txt', 'sdk-build.ps1'):
        key = str((ROOT / 'tests/target/cyd_espressif_opus_qemu' / suffix).resolve())
        reject('missing_harness_' + suffix, lambda r, name=key: r['inputs'].pop(name))
    reject('different_qemu', lambda r: r['commands'][-1]['argv'].__setitem__(0, str(ROOT / '.build/other-qemu.exe')))

    def option(r, name, value):
        argv = r['commands'][-1]['argv']
        argv[argv.index(name) + 1] = value

    reject('different_flash', lambda r: option(r, '-drive', 'file=other.bin,if=mtd,format=raw'))
    reject('single_core', lambda r: option(r, '-smp', '1'))
    reject('network_enabled', lambda r: option(r, '-nic', 'user'))
    reject('persistent_flash', lambda r: r['commands'][-1]['argv'].remove('-snapshot'))
    reject('different_qemu_hash', lambda r: r['tools']['qemu'].update(sha256='0' * 64))
    archive = str((args.vendor / 'lib/esp32/libesp_audio_codec.a').resolve())
    reject('different_vendor_archive', lambda r: r['inputs'][archive].update(sha256='0' * 64))
    return dict(passed=True, valid_native_reference_accepted=True, rejected=len(rejected), cases=rejected,
                native_process_started=False, files_modified=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    print(json.dumps(verify(parser.parse_args().reference)))

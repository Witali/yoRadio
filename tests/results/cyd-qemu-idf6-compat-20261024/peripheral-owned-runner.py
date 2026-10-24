"""Run the existing classic ESP32 peripheral assertions with owned cleanup."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace


def need(value, reason):
    if not value:
        raise RuntimeError(reason)


def fact(path):
    raw = path.read_bytes()
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--qemu', type=Path, required=True)
p.add_argument('--qemu-sha256', required=True)
p.add_argument('--source', type=Path, required=True)
p.add_argument('--rom-source', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
p.add_argument('--input-delay-ns', type=int, choices=(0, 25), default=0)
a = p.parse_args()
qemu, source, rom_source, out = (x.resolve() for x in
                               (a.qemu, a.source, a.rom_source, a.out))
need(sys.flags.optimize == 0, 'Existing assertions require normal Python mode')
need(fact(qemu)['sha256'] == a.qemu_sha256, 'Explicit chosen emulator digest')
need(out.parent.name == '.build' and out.parent.is_dir() and not out.exists(),
     'Fresh direct .build child')
out.mkdir()
inputs = [qemu, Path(__file__).resolve(), *sorted((source / 'tools').glob('*.py')),
          rom_source / 'pc-bios/esp32-v3-rom.bin',
          rom_source / 'pc-bios/esp32-v3-rom-app.bin']
before = {str(x): fact(x) for x in inputs}
report = dict(result='INCOMPLETE', inputs_before=before, errors=[], owned_children=[],
              emulated_spi_input_delay_ns=a.input_delay_ns,
              firmware_used=False, physical_or_full_radio_qualified=False,
              qmp_actual_eof_independently_qualified=False)
instances = []
try:
    sys.path.insert(0, str(source / 'tools'))
    spec = importlib.util.spec_from_file_location('esp_modules_selected',
                                                source / 'tools/test_esp_modules.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original_vm = module.VM

    def spawn_peripheral(argv, *args, **kwargs):
        if a.input_delay_ns:
            argv = [*argv, '-global',
                    f'driver=ssi.esp32.spi,property=input-delay-ns,value={a.input_delay_ns}']
        return subprocess.Popen(argv, *args, **kwargs)

    module.subprocess = SimpleNamespace(Popen=spawn_peripheral,
                                        CREATE_NO_WINDOW=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    class OwnedVM(original_vm):
        def __init__(self, *args, **kwargs):
            instances.append(self)
            super().__init__(*args, **kwargs)

    module.VM = OwnedVM
    module.r = rom_source
    sys.argv = [str(source / 'tools/test_esp_modules.py'), '--soc', 'esp32',
                '--qemu-xtensa', str(qemu), '--state-directory', str(out)]
    module.main()
    result = json.loads((out / 'modular-report.json').read_bytes())
    need(result['passed'] and result['soc'] == 'esp32', 'Selected peripheral report')
    need(set(result['checks']) == {'esp32_dual_spi', 'legacy_cyd_mmio'},
         'Exactly the two classic ESP32 regression groups')
    need(result['qemu_sha256'] == {'xtensa': a.qemu_sha256}, 'Actual emulator report pin')
    report['peripheral_report'] = result
except BaseException as error:
    report['errors'].append(repr(error))
finally:
    for vm in instances:
        process = getattr(vm, 'p', None)
        if process is None:
            continue
        forced = False
        try:
            if process.poll() is None:
                forced = True
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
                report['errors'].append('Fallback cleanup was required')
            need(process.returncode == 0, 'Peripheral QEMU terminal exit')
        except BaseException as error:
            report['errors'].append(repr(error))
        report['owned_children'].append(dict(pid=process.pid, argv=process.args,
                                             returncode=process.returncode, forced=forced))
    try:
        report['inputs_after'] = {str(x): fact(x) for x in inputs}
        report['inputs_unchanged'] = report['inputs_after'] == before
        need(report['inputs_unchanged'], 'Selected sources, ROMs and emulator unchanged')
        need(len(report['owned_children']) == 2, 'Two owned peripheral QEMU children')
    except BaseException as error:
        report['errors'].append(repr(error))
    if not report['errors'] and 'peripheral_report' in report:
        report['result'] = 'CLASSIC_PERIPHERAL_REGRESSIONS_COMPLETED'
    (out / 'owned-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(report['result'])
raise SystemExit(0 if report['result'] == 'CLASSIC_PERIPHERAL_REGRESSIONS_COMPLETED' else 1)

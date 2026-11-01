"""Isolated actual SDK/OpenETH TLS1.2 traffic with local synthetic verified peers.

No production edits, physical device, RF, certificate-store installation, or
external endpoint. Normal user networking is not claimed to be restrict=on.
"""
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import struct
import subprocess
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'tests/target/cyd_tls_traffic_qemu'
MAIN = ROOT/'idf/esp32-cyd2usb-native/main'
SDK_COMMIT = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
PANIC = r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|TLS_TRAFFIC_FAILURE'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8', newline='\n')


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('output', 'sdk', 'tools', 'qemu', 'rom', 'powershell', 'material'):
        parser.add_argument('--'+name, required=True, type=Path)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--freeze-only', action='store_true')
    parser.add_argument('--compile-only', action='store_true')
    args = parser.parse_args()
    out, sdk, tools, qemu, rom, ps, material = [getattr(args, key).resolve() for key in ('output', 'sdk', 'tools', 'qemu', 'rom', 'powershell', 'material')]
    need(not out.exists() and out.is_relative_to(ROOT/'.build') and material.is_relative_to(ROOT/'.build'), 'fresh ignored output and ignored local test material')
    py = tools/'python_env/idf6.0_py3.12_env/Scripts/python.exe'
    toolbin = tools/'tools/xtensa-esp-elf/esp-15.2.0_20251204/xtensa-esp-elf/bin'
    nm, objdump = [toolbin/('xtensa-esp32-elf-'+name+'.exe') for name in ('nm', 'objdump')]
    need(all(p.is_file() for p in (py, ps, qemu, nm, objdump, rom/'esp32-v3-rom.bin', rom/'esp32-v3-rom-app.bin')), 'pinned installed tools')
    contract_path = ROOT/'tests/native/cyd_tls_static_rx/source_contract.py'
    contract = load('traffic_canonical_registry_contract', contract_path).preflight(ROOT, sdk)
    need(subprocess.check_output(['git', '-C', str(sdk), 'rev-parse', 'HEAD']).decode().strip() == SDK_COMMIT, 'exact installed SDK6.0.2 revision')
    need(not subprocess.check_output(['git', '-c', 'core.longpaths=true', '-C', str(sdk), 'status', '--porcelain', '--untracked-files=no']).strip(), 'installed SDK tracked sources clean')
    test_material = json.loads((material/'manifest.json').read_text(encoding='utf-8-sig'))
    need(test_material['ephemeral_test_only'] and not test_material['certificate_store_modified'] and not test_material['ca_private_key_written'], 'fresh disposable CA, no certificate-store change')
    for name, record in test_material['files'].items():
        need(name in ('ca.pem', 'server.pem', 'server-key.pem') and sha(material/name) == record['sha256'] and
             (material/name).stat().st_size == record['bytes'] and record['local_only'], 'whole original local material identity')
    source_paths = [Path(__file__).resolve(), contract_path, ROOT/'tests/test-cyd-tls-traffic-peer.py', ROOT/'tools/patch_cyd_tls_static_rx.py']
    source_paths += [p for p in sorted(TARGET.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
    source_paths += [MAIN/name for name in ('native_tls_rx_reserve.c', 'native_tls_rx_reserve.h',
        'compat/tls_static_rx/enable.cmake', 'compat/tls_static_rx/sdk-source-guards.json',
        'native_input_reclaim.c', 'native_input_reclaim.h', 'compat/input_reclaim/enable.cmake',
        'native_tls_early_mpi.c', 'native_tls_early_mpi.h', 'compat/early_mpi/enable.cmake', 'Kconfig.projbuild')]
    source_paths += [ROOT/'idf/components/native_stream'/name for name in ('adaptive_input.c', 'include/adaptive_input.h')]
    need(all(p.is_file() for p in source_paths), 'complete new target and actual production helper sources')
    if args.preflight_only:
        print(json.dumps(dict(preflight_passed=True, sources=len(source_paths), build_invoked=False, target_executed=False,
                             tls_rx=16384, tls_tx=4096, hardware_crypto_preserved=True, user_network_restrict=False)))
        return 0
    out.mkdir(parents=True)
    report = dict(passed=False, state='preparing', native_mcu_executed=False, qemu_invoked=False, physical_hardware=False,
                  production_sources_changed=False, rf_or_full_radio_qualified=False, physical_headroom_qualified=False,
                  certificate_store_modified=False, insecure_verification=False, external_endpoints=False,
                  user_network_restrict=False, commands=[], sources={}, tools={}, material_identities={})
    for path in source_paths:
        relative = path.relative_to(TARGET) if path.is_relative_to(TARGET) else Path('repository')/path.relative_to(ROOT)
        target = out/'sources'/relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
        report['sources'][path.relative_to(ROOT).as_posix()] = dict(snapshot=target.relative_to(out).as_posix(), sha256=sha(path), bytes=path.stat().st_size)
    report['canonical_source_contract'] = contract
    tool_paths = dict([('sdk-python', py), ('powershell', ps), ('qemu', qemu), ('nm', nm), ('objdump', objdump),
                       ('rom', rom/'esp32-v3-rom.bin'), ('rom-app', rom/'esp32-v3-rom-app.bin')])
    for label, path in tool_paths.items():
        report['tools'][label] = dict(sha256=sha(path), bytes=path.stat().st_size)
    for name in ('ca.pem', 'server.pem', 'server-key.pem', 'manifest.json'):
        report['material_identities'][name] = dict(sha256=sha(material/name), bytes=(material/name).stat().st_size, local_only=True)
    project = out/'project'
    for path in sorted((out/'sources').rglob('*')):
        if not path.is_file() or path.is_relative_to(out/'sources/repository'):
            continue
        relative = path.relative_to(out/'sources')
        if relative.name in ('CMakeLists.txt', 'sdkconfig.defaults', 'partitions.csv', 'main.c', 'Kconfig.projbuild'):
            destination = project/relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(path.read_bytes())
    (project/'ca.pem').write_bytes((material/'ca.pem').read_bytes())
    (project/'main/test_clock.h').write_text('#define TLS_TEST_EPOCH '+str(test_material['guest_epoch_seconds'])+'\n')
    report['generated_project_inputs'] = {p.relative_to(out).as_posix(): dict(sha256=sha(p), bytes=p.stat().st_size,
                                         local_only=p.name == 'ca.pem') for p in project.rglob('*') if p.is_file()}
    write_json(out/'source-manifest.json', dict(sources=report['sources'], generated_project_inputs=report['generated_project_inputs']))

    def save():
        write_json(out/'report.json', report)

    def current():
        return all(sha(ROOT/name) == row['sha256'] == sha(out/row['snapshot']) for name, row in report['sources'].items()) and all(
            sha(out/name) == row['sha256'] for name, row in report['generated_project_inputs'].items()) and all(
            sha(material/name) == row['sha256'] for name, row in report['material_identities'].items()) and all(
            sha(tool_paths[name]) == row['sha256'] for name, row in report['tools'].items())

    def execute(name, argv, timeout=60):
        argv = list(map(str, argv))
        row = dict(name=name, argv=argv, state='starting')
        report['commands'].append(row); save()
        with (out/(name+'.stdout.log')).open('xb') as so, (out/(name+'.stderr.log')).open('xb') as se:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=so, stderr=se, creationflags=subprocess.CREATE_NO_WINDOW)
            row.update(pid=child.pid, state='running'); save()
            try:
                status = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15)
                status = child.wait(timeout=15); row['timed_out'] = True
        row.update(state='complete', exit_status=status)
        for stream in ('stdout', 'stderr'):
            path = out/(name+'.'+stream+'.log')
            row[stream] = dict(path=path.name, sha256=sha(path), bytes=path.stat().st_size)
        save(); need(status == 0 and not row.get('timed_out'), 'terminal zero: '+name)
        return (out/(name+'.stdout.log')).read_text(encoding='utf-8', errors='replace')

    save()
    try:
        need(current(), 'frozen source bindings before build')
        if args.freeze_only:
            report.update(state='frozen_unbuilt_unrun', preparation_passed=True); save(); print(json.dumps(dict(preparation_passed=True, target_executed=False))); return 0
        report['state'] = 'building'; save()
        execute('sdk-driver', [ps, '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', out/'sources/sdk-build.ps1',
            '-Campaign', out, '-SdkDirectory', sdk, '-ToolsDirectory', tools, '-PythonExecutable', py], 1200)
        child = json.loads((out/'sdk-child.json').read_text(encoding='utf-8-sig'))
        need(child['pid'] > 0 and child['exit_status'] == 0, 'actual SDK child terminal zero')
        build = out/'build'
        description = json.loads((build/'project_description.json').read_text())
        elf = build/description['app_elf']
        image = elf.read_bytes()
        need(image[:6] == b'\x7fELF\x01\x01' and struct.unpack_from('<H', image, 18)[0] == 94, 'actual Xtensa ELF94')
        config = json.loads((build/'config/sdkconfig.json').read_text())
        for key in ('MBEDTLS_HARDWARE_MPI', 'MBEDTLS_HARDWARE_AES', 'MBEDTLS_HARDWARE_SHA', 'ETH_USE_OPENETH',
                    'YORADIO_TLS_INPUT_RECLAIM', 'YORADIO_TLS_STATIC_RX_RESERVE', 'YORADIO_TLS_EARLY_MPI_LOCK'):
            need(config[key], 'actual enabled profile: '+key)
        need(config['MBEDTLS_SSL_IN_CONTENT_LEN'] == 16384 and config['MBEDTLS_SSL_OUT_CONTENT_LEN'] == 4096 and not config['FREERTOS_UNICORE'], 'actual original dual-core full-record profile')
        symbols_text = execute('symbols', [nm, '-n', '-S', elf])
        symbols = {m[4]: dict(address=int(m[1], 16), bytes=int(m[2], 16), kind=m[3]) for m in re.finditer(r'^([0-9a-f]+)\s+([0-9a-f]+)\s+([A-Za-z])\s+(.+)$', symbols_text, re.M)}
        need('s_rx' in symbols and symbols['s_rx']['bytes'] >= 16384, 'actual production static RX symbol identity')
        for name, callee in (('mbedtls_ssl_setup', '__wrap_yoradio_tls_static_rx_calloc'), ('mbedtls_ssl_free', '__wrap_yoradio_tls_static_rx_zeroize_free'),
                             ('app_main', '__wrap_native_tls_early_mpi_prepare')):
            asm = execute('asm-'+name, [objdump, '-dwC', '--disassemble='+name, elf])
            need(callee in asm, 'actual forwarding helper reference: '+name)
        rows = json.loads((build/'compile_commands.json').read_text())
        for name in ('main.c', 'native_tls_rx_reserve.c', 'native_input_reclaim.c', 'native_tls_early_mpi.c', 'adaptive_input.c'):
            need(sum(Path(row['file']).name == name for row in rows) == 1, 'one actual selected translation unit: '+name)
        overlay = build/'native-tls-static-rx/ssl_tls.c'
        need(sum(Path(row['file']).resolve() == overlay.resolve() for row in rows) == 1 and
             not any(Path(row['file']).resolve() == (sdk/'components/mbedtls/mbedtls/library/ssl_tls.c').resolve() for row in rows), 'guarded build-local SDK overlay only')
        patcher = load('frozen_traffic_overlay', out/'sources/repository/tools/patch_cyd_tls_static_rx.py')
        need(overlay.read_bytes() == patcher.patch((sdk/'components/mbedtls/mbedtls/library/ssl_tls.c').read_bytes()), 'actual compiled canonical overlay bytes')
        cache = (build/'CMakeCache.txt').read_text()
        ninja = Path(re.search(r'^CMAKE_MAKE_PROGRAM:FILEPATH=(.+)$', cache, re.M)[1].strip())
        deps = execute('dependencies', [ninja, '-C', build, '-t', 'deps'])
        closure = {}
        for line in deps.splitlines():
            if line.startswith('    '):
                path = Path(line.strip())
                path = path.resolve() if path.is_absolute() else (build/path).resolve()
                if path.is_file():
                    closure[str(path)] = sha(path)
        write_json(out/'actual-compiler-closure.json', dict(captured_before_execution=True, dependencies=closure, translation_units=rows))
        report['compiled_profile'] = config
        report['static_rx'] = symbols['s_rx']
        report['actual_compiler_dependencies'] = len(closure)
        if args.compile_only:
            report.update(state='compiled_unrun', compiled=True); save(); return 0
        recipe = json.loads((build/'flasher_args.json').read_text())
        flash = out/'qemu-flash.bin'
        merge = [py, '-m', 'esptool', '--chip', 'esp32', 'merge-bin', '--output', flash,
                 '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        flash_files = [(int(offset, 0), build/name) for offset, name in recipe['flash_files'].items()]
        for offset, path in sorted(flash_files):
            merge += [hex(offset), path]
        execute('merge-flash', merge+['--pad-to-size', '4MB'])
        need(flash.stat().st_size == 0x400000 and all(flash.read_bytes()[at:at+p.stat().st_size] == p.read_bytes() for at, p in flash_files), 'complete exact diagnostic image')
        report['local_binary_identities'] = {str(p.relative_to(out)): dict(sha256=sha(p), bytes=p.stat().st_size, local_only=True)
                                            for p in (elf, build/description['app_bin'], flash)}
        need(current() and all(sha(p) == digest for p, digest in closure.items()), 'all source/dependency bytes frozen before execution')
        write_json(out/'execution-bundle.json', dict(sources=report['sources'], generated_project_inputs=report['generated_project_inputs'],
                   artifacts=report['local_binary_identities'], static_rx=report['static_rx'], actual_compiler_dependencies=len(closure)))
        peer = load('frozen_actual_traffic_peer', out/'sources/loopback_server.py')
        report.update(state='executing'); save()
        qemu_args = [str(p) for p in (qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet', '-smp', '2', '-L', rom, '-display', 'none', '-monitor', 'none',
                     '-serial', 'stdio', '-qmp', 'tcp:127.0.0.1:18446,server=on,wait=off', '-no-reboot', '-snapshot',
                     '-nic', 'user,model=open_eth', '-drive', 'file='+str(flash).replace(',', ',,')+',if=mtd,format=raw')]
        qemu_row = dict(name='qemu', argv=qemu_args, state='starting')
        report['commands'].append(qemu_row); save()
        reached, output = threading.Event(), bytearray()
        with peer.LoopbackTLS(material, out/'server.jsonl'):
            with (out/'qemu.stdout.log').open('xb') as so, (out/'qemu.stderr.log').open('xb') as se:
                guest = subprocess.Popen(qemu_args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=se, creationflags=subprocess.CREATE_NO_WINDOW)
                qemu_row.update(pid=guest.pid, state='running'); report['qemu_invoked']=True; save()
                def reader():
                    while True:
                        data = guest.stdout.read1(4096)
                        if not data:
                            break
                        output.extend(data); so.write(data); so.flush()
                        if b'TLS_TRAFFIC_PASS ' in output or re.search(PANIC.encode(), output, re.I):
                            reached.set()
                thread = threading.Thread(target=reader, daemon=True); thread.start()
                try:
                    deadline = time.monotonic()+240
                    while not reached.wait(0.2) and guest.poll() is None and time.monotonic() < deadline:
                        pass
                    report['native_mcu_executed'] = b'TLS_EARLY_MPI calls=' in output
                    successful_marker = b'TLS_TRAFFIC_PASS ' in output and re.search(PANIC.encode(), output, re.I) is None
                    if successful_marker and guest.poll() is None:
                        with socket.create_connection(('127.0.0.1', 18446), timeout=5) as control:
                            stream = control.makefile('rwb', buffering=0)
                            need('QMP' in json.loads(stream.readline()), 'actual local QMP greeting')
                            stream.write(b'{"execute":"qmp_capabilities"}\r\n')
                            while 'return' not in json.loads(stream.readline()):
                                pass
                            stream.write(b'{"execute":"quit"}\r\n')
                    else:
                        guest.terminate(); qemu_row['controlled_stop_after_failure'] = True
                    try:
                        status = guest.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        guest.kill(); status = guest.wait(timeout=15); qemu_row['forced_kill'] = True
                finally:
                    # A QMP/parser/observer error must not leave the owned guest
                    # live, nor be reclassified as successful target execution.
                    if guest.poll() is None:
                        guest.terminate(); qemu_row['cleanup_after_observer_error'] = True
                        try:
                            guest.wait(timeout=15)
                        except subprocess.TimeoutExpired:
                            guest.kill(); guest.wait(timeout=15); qemu_row['forced_kill'] = True
                    thread.join(timeout=5)
                    qemu_row.update(state='complete', exit_status=guest.returncode)
        for stream in ('stdout', 'stderr'):
            path = out/('qemu.'+stream+'.log'); qemu_row[stream] = dict(path=path.name, sha256=sha(path), bytes=path.stat().st_size)
        save()
        log = output.decode(errors='replace')
        need(successful_marker and status == 0 and not re.search(PANIC, log, re.I), 'actual full target success, clean QMP terminal zero, no generic panic/refusal')
        data_rows = re.findall(r'TLS_DATA case=(\w+) bytes=(\d+) reads=(\d+) full=(\d+) terminal=(-?\d+) sha256=([0-9a-f]{64})', log)
        normal = {row[0]: row for row in data_rows if row[0] != 'truncated_record'}
        need(set(normal) == {'first', 'reopen', 'after_failures', 'parallel_a', 'parallel_b', 'pressure', 'after_pressure'} and
             all(row[1:4] == ('65536', '4', '4') and row[5] == peer.PAYLOAD_SHA256 for row in normal.values()), 'seven full actual plaintext/digest observations')
        need(any(row[0] == 'truncated_record' and row[1:4] == ('0', '0', '0') and int(row[4]) <= 0 for row in data_rows), 'actual truncated-record failure')
        live = re.search(r'TLS_PARALLEL ptr0=(0x[0-9a-f]+) ptr1=(0x[0-9a-f]+) live=2', log)
        need(live and len({int(live[1], 16), int(live[2], 16)}) == 2 and symbols['s_rx']['address'] in (int(live[1], 16), int(live[2], 16)), 'actual static RX owner and distinct heap fallback while both TLS clients live')
        events = [json.loads(line) for line in (out/'server.jsonl').read_text().splitlines()]
        complete = [row for row in events if row['event'] == 'response_complete']
        need(len(complete) == 7 and all(row['bytes'] == 65536 and row['sha256'] == peer.PAYLOAD_SHA256 for row in complete), 'all seven server/client exact response bindings')
        rounds = [row for row in events if row['event'] == 'parallel_round']
        need([row['round'] for row in rounds] == [0, 0, 1, 1, 2, 2, 3, 3] and len({row['connection'] for row in rounds}) == 2, 'actual simultaneous traffic, not serialized TLS API calls')
        for row in complete:
            need(sum(event['event'] == 'server_record' and event['connection'] == row['connection'] and event['content_type'] == 23 and event['record_bytes'] == 16408 for event in events) == 4, 'genuine full TLS1.2 GCM records')
        need(current() and all(sha(p) == digest for p, digest in closure.items()), 'source/dependency bindings unchanged after actual traffic')
        need(not subprocess.check_output(['git', '-c', 'core.longpaths=true', '-C', str(sdk), 'status', '--porcelain', '--untracked-files=no']).strip(), 'installed SDK remains unchanged')
        report.update(passed=True, state='complete', full_responses=7, full_plaintext_records=28, parallel_live_clients=2,
                      genuine_parallel_traffic_rounds=4, real_pressure_recovery=True, all_source_bindings_current=True)
        save(); print(json.dumps(dict(passed=True, full_responses=7, full_plaintext_records=28, actual_live_clients=2, actual_static_rx=symbols['s_rx']['address']))); return 0
    except BaseException as error:
        report.update(passed=False, state='nonpass', error_type=type(error).__name__, error=str(error)); save(); raise


if __name__ == '__main__':
    raise SystemExit(main())

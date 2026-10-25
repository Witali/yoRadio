"""Compile whole canonical setup/ABI and check its lookup1 integer root in QEMU.

No codec archive, stream decoder, Ogg adapter or production firmware is linked.
Only the existing static quantvals helper is exercised by the isolated worker.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'tests/target/vorbis_quantvals_qemu'
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
PUBLIC_HEADERS = ('include/esp_audio_types.h', 'include/decoder/esp_audio_dec.h',
                  'include/decoder/esp_audio_dec_reg.h',
                  'include/decoder/impl/esp_vorbis_dec.h')


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalize(value):
    return str(value).replace('\\', '/').rstrip('/')


def validate_cases(document, header):
    """Check every root by independent bignum inequalities, and read C rows."""
    need(document['schema'] == 'vorbis-quantvals-cases-v1', 'known cases schema')
    rows = document['cases']
    need(isinstance(rows, list) and 1 <= len(rows) <= 10000, 'finite nonempty cases')
    expected = []
    for row in rows:
        need(set(row) == {'entries', 'dimensions', 'expected'} and
             all(type(row[key]) is int for key in row), 'exact integer case fields')
        entries, dimensions, result = (row[key] for key in ('entries', 'dimensions', 'expected'))
        need(1 <= entries <= 2147483647 and 1 <= dimensions <= 65535 and
             1 <= result <= entries, 'positive signed32/unsigned16 arithmetic inputs')
        need(pow(result, dimensions) <= entries < pow(result+1, dimensions),
             'independent exact integer-root oracle')
        expected.append((entries, dimensions, result))
    count = re.findall(r'^#define\s+QUANTVALS_CASE_COUNT\s+(\d+)[Uu]?\s*$',
                       header, re.M)
    need(count == [str(len(rows))], 'exact materialized case count')
    arrays = re.findall(r'\bquantvals_cases\s*\[[^\]]*\]\s*=\s*\{(.*?)\};',
                        header, re.S)
    need(len(arrays) == 1, 'one complete C case array')
    body = re.sub(r'UINT32_C\(\s*(\d+)\s*\)', r'\1', arrays[0])
    pattern = re.compile(r'\{\s*(\d+)[Uu]?\s*,\s*(\d+)[Uu]?\s*,\s*(\d+)[Uu]?\s*\}')
    actual, cursor = [], 0
    for match in pattern.finditer(body):
        separator = r'\s*,\s*' if actual else r'\s*'
        need(re.fullmatch(separator, body[cursor:match.start()]), 'only literal C row separators')
        actual.append(tuple(map(int, match.groups())))
        cursor = match.end()
    need(re.fullmatch(r'\s*,?\s*', body[cursor:]) and actual == expected,
         'every original C entry/dimension/expected value exactly recovered')
    return rows


def validate_log(log, rows, target, data_sha256):
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|'
                       r'watchdog|stack overflow|timed out', log, re.I), 'target failure')
    lines = [line for line in log.splitlines() if line.startswith('QUANTVALS_')]
    core = 1 if target == 'esp32' else 0
    expected = [
        f'QUANTVALS_BEGIN cases={len(rows)} coordinator=0 worker={core} data={data_sha256}',
        f'QUANTVALS_WORKER core={core} priority=3 stack=16384']
    expected += [
        'QUANTVALS_CASE index={index} entries={entries} dimensions={dimensions} '
        'expected={expected} actual={expected} core={core}'.format(index=index, core=core, **row)
        for index, row in enumerate(rows)]
    expected += [f'QUANTVALS_COMPLETE cases={len(rows)} core={core}',
                 'QUANTVALS_STOP status=PASS']
    need(lines == expected, 'every ordered target arithmetic event and controlled stop')
    return dict(cases=len(rows), protocol_lines=len(lines), coordinator_core=0,
                worker_core=core, priority=3, configured_stack=16384,
                every_root_exact=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', choices=SDK_HEAD, required=True)
    for name in ('output', 'cases', 'idf', 'idf-tools', 'codec', 'powershell',
                 'sdk-python', 'qemu', 'rom'):
        p.add_argument('--'+name, type=Path, required=True)
    for name in ('setup', 'abi', 'cases', 'header', 'qemu'):
        p.add_argument('--'+name+'-sha256', required=True)
    a = p.parse_args()
    need(sys.platform == 'win32', 'explicit pinned Windows SDK launcher')
    for name in ('setup', 'abi', 'cases', 'header', 'qemu'):
        need(re.fullmatch(r'[0-9a-f]{64}', getattr(a, name+'_sha256')),
             'explicit lowercase SHA256 '+name)
    out, cases = a.output.resolve(), a.cases.resolve()
    sdk, tools, codec, ps, py, qemu, rom = [
        getattr(a, name).resolve() for name in
        ('idf', 'idf_tools', 'codec', 'powershell', 'sdk_python', 'qemu', 'rom')]
    candidate = ROOT / ('idf/esp32-cyd2usb-native/main' if a.target == 'esp32'
                        else 'idf/esp32c3-oled-native/main')
    setup, abi = candidate/'vorbis_repair/setup.c', candidate/'vorbis_repair_abi.h'
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    required = [setup, abi, cases/'cases.json', cases/'cases.h', sdk/'export.ps1',
                sdk/'tools/idf.py', ps, py, qemu, git, *[codec/path for path in PUBLIC_HEADERS]]
    need(all(path.is_file() for path in required), 'required source/header/runtime missing')
    need(rom.is_dir() and any(rom.glob(a.target+'*rom*.bin')), 'explicit target ROM files')
    need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(),
         'fresh task-local .build output')
    protected = [candidate, PROJECT, cases, sdk, tools, codec, ps.parent, py.parent,
                 qemu.parent, rom]
    need(not any(out == path or out.is_relative_to(path) or path.is_relative_to(out)
                 for path in protected), 'source/runtime/output overlap')
    need(not any((path/'report.json').is_file() for path in out.parents if path != ROOT),
         'nested output campaign')
    for path, pin in ((setup, a.setup_sha256), (abi, a.abi_sha256),
                      (cases/'cases.json', a.cases_sha256),
                      (cases/'cases.h', a.header_sha256), (qemu, a.qemu_sha256)):
        need(sha(path) == pin, 'reviewed source/data/tool identity '+str(path))
    rows = validate_cases(json.loads((cases/'cases.json').read_bytes()),
                          (cases/'cases.h').read_text(encoding='ascii'))
    out.mkdir(parents=True)
    r = dict(completed=False, passed=False, target=a.target, sdk_revision=SDK_HEAD[a.target],
             finite_integer_root_qualified=False, whole_setup_compiled=False,
             codec_archive_linked=False, decoder_executed=False, full_G6_qualified=False,
             production_firmware=False, physical_device=False,
             source_inputs_unchanged=False, commands=[], inputs={}, tools={},
             build_outputs={}, cases_sha256=a.cases_sha256, header_sha256=a.header_sha256)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
               PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')

    def save():
        (out/'report.json').write_text(json.dumps(r, indent=2)+'\n', encoding='utf-8')

    def freeze(path, relative):
        dst = out/'sources'/relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(path.read_bytes())
        r['inputs'][str(path.resolve())] = dict(snapshot=dst.relative_to(out).as_posix(),
                                              bytes=dst.stat().st_size, sha256=sha(dst))

    def current():
        need(all(sha(path) == pin['sha256'] == sha(out/pin['snapshot'])
                 for path, pin in r['inputs'].items()), 'original/frozen source changed')
        need(all(sha(path) == digest for path, digest in r['tools'].items()), 'tool changed')
        need(all(sha(out/path) == digest for path, digest in r.get('project_sources', {}).items()),
             'actual configured project changed')

    def run(name, argv, timeout=60):
        argv = list(map(str, argv))
        row = dict(name=name, argv=argv, cwd=str(out), state='starting',
                   timeout_seconds=timeout, timed_out=False, interrupted=False)
        r['commands'].append(row)
        save()
        so, se = out/(name+'.stdout.log'), out/(name+'.stderr.log')
        child, start = None, time.monotonic()
        try:
            with so.open('xb') as stdout, se.open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=out, stdout=stdout, stderr=stderr,
                                         stdin=subprocess.DEVNULL, env=env,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(pid=child.pid, state='running')
                save()
                child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as exc:
            row.update(state='failed', error=repr(exc),
                       timed_out=isinstance(exc, subprocess.TimeoutExpired),
                       interrupted=isinstance(exc, KeyboardInterrupt))
            raise
        finally:
            if child is not None and child.poll() is None:
                row['state'] = 'forced_stop_nonpass'
                try:
                    stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'],
                                             capture_output=True, timeout=15,
                                             creationflags=subprocess.CREATE_NO_WINDOW)
                    row['tree_stop_returncode'] = stopped.returncode
                except Exception as exc:
                    row['tree_stop_error'] = repr(exc)
                finally:
                    if child.poll() is None:
                        child.kill()
                    child.wait(timeout=15)
            row.update(elapsed_seconds=time.monotonic()-start,
                       stdout_sha256=sha(so) if so.is_file() else None,
                       stderr_sha256=sha(se) if se.is_file() else None)
            if child is not None:
                row['exit_status'] = child.poll()
            save()
        need(row['state'] == 'complete' and row['exit_status'] == 0,
             name+' did not reach a normal successful terminal')
        return so.read_text(encoding='utf-8', errors='replace').replace('\r\n', '\n')

    save()
    try:
        for path in (py, ps, qemu, git):
            r['tools'][str(path)] = sha(path)
        for path in sorted(rom.glob(a.target+'*rom*.bin')):
            r['tools'][str(path)] = sha(path)
        need(run('sdk-head', [git, '-c', 'core.longpaths=true', '-C', sdk,
                              'rev-parse', 'HEAD']).strip() == SDK_HEAD[a.target], 'SDK revision')
        need(not run('sdk-clean', [git, '-c', 'core.longpaths=true', '-C', sdk,
                                  'status', '--porcelain', '--untracked-files=no']).strip(),
             'SDK has tracked changes')
        freeze(setup, Path('candidate/vorbis_repair/setup.c'))
        freeze(abi, Path('candidate/vorbis_repair_abi.h'))
        freeze(candidate/'vorbis_repair/COPYING', Path('candidate/vorbis_repair/COPYING'))
        freeze(Path(__file__), Path('controller.py'))
        for relative in PUBLIC_HEADERS:
            freeze(codec/relative, Path('codec')/relative)
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file():
                freeze(path, Path('project')/path.relative_to(PROJECT))
        freeze(cases/'cases.json', Path('cases/cases.json'))
        freeze(cases/'cases.h', Path('cases/cases.h'))
        shutil.copytree(out/'sources/project', out/'project')
        shutil.copyfile(out/'sources/cases/cases.h', out/'project/main/cases.h')
        shutil.copyfile(out/'sources/project'/('sdkconfig.'+a.target+'.defaults'),
                        out/'project/sdkconfig.defaults')
        r['project_sources'] = {path.relative_to(out).as_posix(): sha(path)
                                for path in (out/'project').rglob('*') if path.is_file()}
        current()
        run('build', [ps, '-NoProfile', '-NonInteractive', '-File',
                      out/'sources/project/sdk-build.ps1', '-Campaign', out,
                      '-SdkDirectory', sdk, '-ToolsDirectory', tools,
                      '-PythonExecutable', py, '-Target', a.target,
                      '-SetupSha256', a.setup_sha256, '-AbiSha256', a.abi_sha256,
                      '-CasesSha256', a.cases_sha256], 1200)
        build = out/'build'
        sdk_child = json.loads((out/'sdk-child.json').read_text(encoding='utf-8-sig'))
        need(type(sdk_child['pid']) is int and sdk_child['pid'] > 0 and
             sdk_child['exit_status'] == 0, 'actual successful SDK child')
        r['sdk_child'] = sdk_child
        for path in (out/'sdk-build.stdout.log', out/'sdk-build.stderr.log', out/'sdk-child.json'):
            r['build_outputs'][path.relative_to(out).as_posix()] = sha(path)
        description = json.loads((build/'project_description.json').read_bytes())
        elf = build/description['app_elf']
        need(elf.resolve().is_relative_to(build), 'ELF path')
        machine = struct.unpack_from('<H', elf.read_bytes(), 18)[0]
        need(machine == (94 if a.target == 'esp32' else 243), 'native ELF machine')
        r['elf_machine'] = machine
        compiler = Path(description['c_compiler'])
        nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        cache = (build/'CMakeCache.txt').read_text(encoding='utf-8')
        make = re.findall(r'^CMAKE_MAKE_PROGRAM:FILEPATH=(.+)$', cache, re.M)
        need(len(make) == 1, 'one actual configured Ninja')
        ninja = Path(make[0].strip())
        for path in (compiler, nm, ninja):
            need(path.is_file(), 'configured tool exists')
            r['tools'][str(path)] = sha(path)
        compile_rows = json.loads((build/'compile_commands.json').read_bytes())
        main_rows = [row for row in compile_rows
                     if Path(row['file']).resolve() == out/'project/main/main.c']
        need(len(main_rows) == 1, 'one actual whole-setup main compile row')
        r['main_compile_row'] = main_rows[0]
        main_object = 'esp-idf/main/CMakeFiles/__idf_main.dir/main.c.obj'
        need((build/main_object).is_file(), 'actual main object')
        dependencies = run('dependencies', [ninja, '-C', build, '-t', 'deps', main_object])
        dep_text = normalize(dependencies).casefold()
        for path in (out/'sources/candidate/vorbis_repair/setup.c',
                     out/'sources/candidate/vorbis_repair_abi.h', out/'project/main/cases.h',
                     *[out/'sources/codec'/relative for relative in PUBLIC_HEADERS]):
            need(normalize(path).casefold() in dep_text, 'actual whole-source/header dependency')
        r['whole_setup_compiled'] = True
        symbols = run('symbols', [nm, '-n', '-S', elf])
        need(re.search(r'\b_book_maptype1_quantvals$', symbols, re.M), 'actual callable canonical helper')
        need(not re.search(r'\b(?:__wrap_)?esp_vorbis_dec_(?:open|decode)$', symbols, re.M),
             'no retained stream decoder')
        map_file = elf.with_suffix('.map')
        need(map_file.is_file() and b'libesp_audio_codec.a' not in map_file.read_bytes(),
             'no codec archive linked')
        recipe = json.loads((build/'flasher_args.json').read_bytes())
        need(recipe['flash_settings'] == dict(flash_mode='dio', flash_size='4MB', flash_freq='40m'),
             'isolated DIO40/4MB profile')
        flash_files = {int(offset, 0): (build/name).resolve()
                       for offset, name in recipe['flash_files'].items()}
        need(set(flash_files) == ({0x1000, 0x8000, 0x10000} if a.target == 'esp32'
                                 else {0, 0x8000, 0x10000}) and
             all(path.is_relative_to(build) for path in flash_files.values()), 'isolated flash recipe')
        flash = out/'qemu-flash.bin'
        argv = [py, '-m', 'esptool', '--chip', a.target, 'merge-bin', '--output', flash,
                '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flash_files.items()):
            argv += [hex(offset), path]
        run('merge', argv+['--pad-to-size', '4MB'])
        config = (out/'sdkconfig').read_text(encoding='utf-8')
        need(('CONFIG_FREERTOS_UNICORE=y' in config) == (a.target == 'esp32c3'),
             'native single/dual-core SDK configuration')
        selected = [elf, map_file, flash, out/'sdkconfig', build/'flasher_args.json',
                    build/'compile_commands.json', build/'project_description.json',
                    build/'CMakeCache.txt', *flash_files.values()]
        for path in selected:
            r['build_outputs'][path.relative_to(out).as_posix()] = sha(path)
        r['build_warning_lines'] = [
            line for path in (out/'sdk-build.stdout.log', out/'sdk-build.stderr.log')
            for line in path.read_text(encoding='utf-8', errors='replace').splitlines()
            if re.search(r'\bwarning:', line)]
        qargs = [qemu]
        if a.target == 'esp32':
            qargs += ['-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet']
        else:
            qargs += ['-M', 'esp32c3']
        qargs += ['-smp', '2' if a.target == 'esp32' else '1', '-L', rom,
                  '-display', 'none', '-monitor', 'none', '-serial', 'stdio', '-no-reboot',
                  '-snapshot', '-nic', 'none', '-drive', 'file='+str(flash)+',if=mtd,format=raw']
        current()
        log = run('qemu', qargs, 300)
        r['observed'] = validate_log(log+'\n'+(out/'qemu.stderr.log').read_text(
            encoding='utf-8', errors='replace'), rows, a.target, a.cases_sha256)
        need(run('sdk-head-after', [git, '-c', 'core.longpaths=true', '-C', sdk,
                                    'rev-parse', 'HEAD']).strip() == SDK_HEAD[a.target],
             'SDK revision changed')
        need(not run('sdk-clean-after', [git, '-c', 'core.longpaths=true', '-C', sdk,
                                        'status', '--porcelain', '--untracked-files=no']).strip(),
             'SDK modified')
        current()
        need(all(sha(out/path) == digest for path, digest in r['build_outputs'].items()),
             'selected actual build bytes changed')
        r.update(completed=True, passed=True, finite_integer_root_qualified=True,
                 source_inputs_unchanged=True, result='FINITE_QUANTVALS_EXACT',
                 limitations='Arithmetic helper only; whole canonical setup/native ABI compile. '
                 'No raw decoder, PCM, full ABI/G6, radio, resource, QMP EOF or physical qualification. '
                 'Selected source/tool identities and build outputs, not full dependency closure.')
        save()
        print(json.dumps(dict(completed=True, passed=True, target=a.target,
                              cases=len(rows), result=r['result'])))
        return 0
    except BaseException as exc:
        r.update(completed=False, passed=False, finite_integer_root_qualified=False,
                 result='NONPASS', error=repr(exc))
        save()
        raise


if __name__ == '__main__':
    sys.exit(main())

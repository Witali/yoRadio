"""Public AAC-Plus configuration: unchanged LX6 decoder, full LC/HE/HEv2 fixtures and split input."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROJECT = ROOT / 'tests/target/cyd_aac_public_config_qemu'
REVISION = '67b8d0e98f58c774b8652480893037273190e8dc'
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
QEMU_SHA = {'esp32': '4fcdc2bef259bdf5c8ea21251e76a0f9d9255996d8c8d2f28d1af3de99f6e45d',
            'esp32c3': 'a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b'}
ARCHIVES = {
    'esp32': ('92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
              'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6'),
    'esp32c3': ('311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909',
                '232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f'),
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture_accounting():
    folder = ROOT / 'tests/fixtures/aac_stream_format'
    manifest = json.loads((folder / 'manifest.json').read_bytes())
    rates = (96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000, 7350)
    entries = []
    for name, info in manifest['files'].items():
        body = (folder / name).read_bytes()
        need(len(body) == info['size_bytes'] and hashlib.sha256(body).hexdigest() == info['sha256'], 'exact complete original fixture')
        pos, count, geometry = 0, 0, set()
        while pos < len(body):
            head = body[pos:pos + 7]
            need(len(head) == 7 and head[0] == 255 and head[1] & 246 == 240, 'independent ADTS header accounting')
            rate_index = (head[2] >> 2) & 15
            need(rate_index < len(rates), 'ADTS rate index')
            size = ((head[3] & 3) << 11) | (head[4] << 3) | (head[5] >> 5)
            need(size >= (7 if head[1] & 1 else 9) and size <= len(body) - pos and not head[6] & 3, 'complete one-block ADTS frame')
            geometry.add((rates[rate_index], ((head[2] & 1) << 2) | (head[3] >> 6)))
            pos += size; count += 1
        need(pos == len(body) and len(geometry) == 1 and count > 0, 'all original ADTS frames accounted')
        core_rate, core_channels = geometry.pop()
        need(info['sample_rate'] in (core_rate, 2 * core_rate), 'original encoded profile/rate distinction')
        entries.append(dict(name=name, size=len(body), sha256=info['sha256'], rate=info['sample_rate'], channels=info['channels'],
                            core_rate=core_rate, core_channels=core_channels, frames=count,
                            pcm=count * 1024 * (info['sample_rate'] // core_rate) * info['channels'] * 2))
    need(len(entries) == 6, 'all six complete original format fixtures')
    return entries


def make_fixture_blob(entries):
    offset = 16 + 6 * 96
    records, bodies = [], []
    for e in entries:
        body = (ROOT / 'tests/fixtures/aac_stream_format' / e['name']).read_bytes()
        records.append(struct.pack('<64s8I', e['name'].encode(), offset, e['size'], e['rate'], e['channels'],
                                   e['core_rate'], e['core_channels'], e['frames'], e['pcm']))
        bodies.append(body); offset += len(body)
    return struct.pack('<4I', 0x41414350, 1, 6, 96) + b''.join(records) + b''.join(bodies)


def validate_log(log, entries=None):
    entries = entries or fixture_accounting()
    need(not re.search(r'AAC_PUBLIC_ERROR|Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow', log, re.I),
         'no native decode error, panic, assertion, watchdog or heap failure')
    log = log.replace('\r\n','\n')
    lines = [line for line in log.splitlines() if line.startswith('AAC_PUBLIC_')]
    need(lines and lines[0] == 'AAC_PUBLIC_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 initial_capacity=12288 fixtures=6',
         'actual diagnostic worker and complete fixture set')
    fields = ('id','name','mode','chunk','input','calls','frames','pcm','sha256','rate','channels','bits','samples',
              'stereo_differences','resizes','coalesces','before','after','stack_free','core','priority')
    pattern = 'AAC_PUBLIC_CASE ' + ' '.join(name + '=' + ('([a-z0-9.-]+)' if name == 'name' else '([a-f0-9]{64})' if name == 'sha256' else '(\\d+)') for name in fields)
    rows=[]
    open_rows=[]
    for line in lines[1:-1]:
        if line.startswith('AAC_PUBLIC_OPEN '):
            match=re.fullmatch(r'AAC_PUBLIC_OPEN instance=(\d+) mode=(\d+) cfg_present=(\d+) original_plus=(\d+) overwritten_plus=(\d+) outer_cleared=1 scope_returned=1',line)
            need(match,'actual owned-config replacement and helper return observation')
            instance,mode,present,original,overwritten=map(int,match.groups())
            need(instance==len(open_rows)+1 and present==int(mode!=0) and original==int(mode==2) and overwritten==int(mode!=2),
                 'original and overwritten valid public preference fields')
            open_rows.append(dict(instance=instance,mode=mode,original_plus=original,overwritten_plus=overwritten))
            continue
        match=re.fullmatch(pattern,line); need(match,'every complete actual native case record')
        row={key:value if key in ('name','sha256') else int(value) for key,value in zip(fields,match.groups())}
        need(row['core']==1 and row['priority']==3 and row['bits']==16 and row['calls']>0 and row['frames']>0 and
             0<row['stack_free']<=16384 and row['before']>0 and row['after']>0,'actual worker, PCM and heap measurements')
        rows.append(row)
    need(len(rows)==len(open_rows)==36 and len(lines)==74,'complete measured case and scoped-config census')
    need([r['mode'] for r in rows]==[r['mode'] for r in open_rows] and
         all(lines[1+2*i].startswith('AAC_PUBLIC_OPEN ') and lines[2+2*i].startswith('AAC_PUBLIC_CASE ') for i in range(36)),
         'each actual returned open scope precedes its own complete decode')
    identity=lambda row: tuple(row[key] for key in ('pcm','sha256','rate','channels','samples'))
    for index,e in enumerate(entries):
        own=rows[index*6:index*6+6]
        need([(r['id'],r['mode'],r['chunk']) for r in own]==[(index,0,e['size']),(index,1,e['size']),(index,2,e['size']),
             (index,2,4096),(index,2,257),(index,2,1)],'NULL, explicit off and production on precede all split schedules')
        need(all(r['name']==e['name'] and r['input']==e['size'] for r in own),'all complete original encoded input consumed')
        need(identity(own[0])==identity(own[1]),'actual NULL/default equals explicit AAC-Plus off')
        for r in own[2:]:
            need(r['pcm']==e['pcm'] and r['rate']==e['rate'] and r['channels']==e['channels'] and
                 r['samples']==e['frames']*1024*(e['rate']//e['core_rate']),'complete full-rate/full-layout output for production preference')
            need(identity(r)==identity(own[2]),'full on-mode PCM identity across input splits')
            if e['channels']==2: need(r['stereo_differences']>0,'actual nonidentical stereo output samples')
        if e['rate']==e['core_rate']: need(identity(own[1])==identity(own[2]),'LC output unchanged by AAC-Plus preference')
        else: need(own[1]['rate']==e['core_rate'] and own[2]['rate']==2*own[1]['rate'] and
                   own[1]['pcm']!=own[2]['pcm'],'actual SBR full rate differs from core-only baseline')
    need(all(r['before']==r['after']==rows[0]['after'] for r in rows[1:]),'stable repeated decoder ownership')
    match=re.fullmatch(r'AAC_PUBLIC_COMPLETE cases=36 core=1 registry_before=(\d+) heap_free=(\d+) retained=(-?\d+) heap_min=(\d+) stack_free=(\d+) capacity=(\d+) scoped_opens=36 heap_integrity=1',lines[-1])
    need(match,'terminal original status with actual heap observations')
    before,after,retained,minimum,stack,capacity=map(int,match.groups())
    need(retained==before-after and 0<minimum<=after and 0<stack<=16384 and capacity>=12288,'actual registry retention, minimum heap and stack')
    return dict(cases=rows,fixture_count=6,public_config_only=True,full_pcm_independent_numeric_oracle=False,
                compact_owner_ported=False,heap_min=minimum,stack_free=stack,retained_after_unregister=retained,
                final_output_capacity=capacity,scoped_config_opens=open_rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', choices=('esp32',), default='esp32')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--qemu-timeout', type=int, default=1200)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    need(sys.platform == 'win32' and 1 <= args.qemu_timeout <= 1200, 'Windows runtime and bounded deadline')
    out = args.output.resolve()
    need(out.is_relative_to(ROOT / '.build') and out != ROOT / '.build' and not out.exists(),
         'fresh campaign strictly inside repository .build')
    target = args.target
    sdk = REPO / ('.idf/v6.0.2' if target == 'esp32' else '.idf/v6.1-9a97f6c54ec6')
    tools = REPO / ('.idf/tools-v6.0.2' if target == 'esp32' else '.idf/tools-v6.1')
    python = tools / ('python_env/idf6.0_py3.12_env/Scripts/python.exe' if target == 'esp32'
                      else 'python_env/idf6.1_py3.12_env/Scripts/python.exe')
    qemu = ROOT / '.build/cyd-qemu-idf6-build-05/qemu-system-xtensa.exe' if target == 'esp32' else Path('C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
    rom = Path('C:/Work/QEMU-ESP32/pc-bios')
    vendor = REPO / '.idf/esp-adf-libs/esp_audio_codec'
    fixture = ROOT / 'tests/fixtures/aac_stream_format/manifest.json'
    entries = fixture_accounting()
    powershell = Path(shutil.which('pwsh.exe') or '')
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    need(all(p.is_file() for p in (python, qemu, powershell, git, fixture, sdk / 'export.ps1')), 'installed native dependencies')
    need(sha(qemu) == QEMU_SHA[target] and sha(fixture) == 'ac18a7e4a990682b3ce9f217408571c794556096571802bac966b5905635bc1c', 'pinned emulator and valid fixture')
    archives = [vendor / f'lib/{target}/libesp_audio_{name}.a' for name in ('codec', 'simple_dec')]
    need(tuple(map(sha, archives)) == ARCHIVES[target], 'pinned target-specific vendor archives')
    if args.preflight_only:
        print(json.dumps(dict(preflight=True, target=target, output_created=False, target_executed=False)))
        return 0
    out.mkdir(parents=True)
    report = dict(target=target, passed=False, completed=False, commands=[], inputs={}, tools={},
                  production_firmware=False, physical_device=False, custom_decoder=False,
                  private_abi_used=False, target_executed=False, full_conformance_qualified=False, compact_owner_ported=False)

    def save():
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    def freeze(path, relative):
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, destination)
        report['inputs'][str(Path(path).resolve())] = dict(snapshot=relative.as_posix(), sha256=sha(path), bytes=Path(path).stat().st_size)

    private_paths = {str(p) for p in (powershell, git, python, qemu) if re.search(r'(?i)[/\\]Users[/\\]', str(p))}

    def run(name, argv, timeout=60):
        argv = list(map(str, argv))
        row = dict(name=name, argv=['runtime-path-redacted:' + Path(v).name if v in private_paths else v for v in argv],
                   state='starting', timeout_seconds=timeout)
        report['commands'].append(row)
        save()
        child = None
        started = time.monotonic()
        try:
            with (out / (name + '.stdout.log')).open('xb') as stdout, (out / (name + '.stderr.log')).open('xb') as stderr:
                child = subprocess.Popen(argv, cwd=out, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr,
                                         creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='running', pid=child.pid)
                if name == 'qemu': report['target_executed'] = True
                save()
                child.wait(timeout=timeout)
                row.update(state='complete', exit_status=child.returncode)
        except BaseException as error:
            row.update(state='failed', error_type=type(error).__name__, winerror=getattr(error, 'winerror', None))
            raise RuntimeError('native command failed: ' + name) from None
        finally:
            if child is not None and child.poll() is None:
                stopped = subprocess.run(['taskkill.exe', '/PID', str(child.pid), '/T', '/F'], capture_output=True,
                                         timeout=15, creationflags=subprocess.CREATE_NO_WINDOW)
                row.update(state='forced_stop_nonpass', tree_stop_returncode=stopped.returncode)
                if child.poll() is None: child.kill()
                child.wait(timeout=15)
            row['elapsed_seconds'] = time.monotonic() - started
            if child is not None: row['exit_status'] = child.poll()
            row['stdout_sha256'] = sha(out / (name + '.stdout.log'))
            row['stderr_sha256'] = sha(out / (name + '.stderr.log'))
            save()
        need(row['state'] == 'complete' and row['exit_status'] == 0, 'command terminal0: ' + name)
        return (out / (name + '.stdout.log')).read_text('utf-8', errors='replace')

    save()
    try:
        for name, path in [('python', python), ('qemu', qemu), ('powershell', powershell), ('git', git)]:
            report['tools'][name] = dict(path='runtime-path-redacted' if str(path) in private_paths else str(path), sha256=sha(path))
        report['roms'] = {p.name: sha(p) for p in sorted(rom.glob(target + '*rom*.bin'))}
        need(report['roms'], 'installed target ROM inputs')
        need(run('vendor-head', [git, '-c', 'core.longpaths=true', '-C', vendor.parent, 'rev-parse', 'HEAD']).strip() == REVISION,
             'pinned vendor repository revision')
        need(not run('vendor-clean', [git, '-c', 'core.longpaths=true', '-C', vendor.parent, 'status', '--porcelain', '--untracked-files=no']).strip(),
             'clean pinned vendor repository')
        need(run('sdk-head', [git, '-c', 'core.longpaths=true', '-C', sdk, 'rev-parse', 'HEAD']).strip() == SDK_HEAD[target], 'pinned SDK revision')
        need(not run('sdk-clean', [git, '-c', 'core.longpaths=true', '-C', sdk, 'status', '--porcelain', '--untracked-files=no']).strip(), 'clean pinned SDK')
        freeze(Path(__file__), Path('sources/controller.py'))
        for path in sorted(PROJECT.rglob('*')):
            if path.is_file(): freeze(path, Path('project') / path.relative_to(PROJECT))
        freeze(fixture, Path('sources/fixtures/manifest.json'))
        for entry in entries:
            freeze(ROOT / 'tests/fixtures/aac_stream_format' / entry['name'], Path('sources/fixtures') / entry['name'])
        (out / 'project/main/fixtures.bin').write_bytes(make_fixture_blob(entries))
        freeze(ROOT / 'idf/esp32-cyd2usb-native/main/aac_public_config.h', Path('project/main/aac_public_config.h'))
        freeze(ROOT / 'idf/esp32-cyd2usb-native/main/Kconfig.projbuild', Path('sources/production-Kconfig.projbuild'))
        for name in ('decoder_registration.c', 'decoder_registration.h'):
            freeze(ROOT / 'idf/esp32-cyd2usb-native/main' / name, Path('project/main') / name)
        freeze(ROOT / 'idf/components/native_stream/include/decoder_pending_input.h',
               Path('project/main/decoder_pending_input.h'))
        for folder in ('include', 'src'):
            for path in sorted((vendor / folder).rglob('*')):
                if path.is_file(): freeze(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor))
        for path in [*archives, *[p for p in vendor.iterdir() if p.is_file()]]:
            freeze(path, Path('sources/vendor/esp_audio_codec') / path.relative_to(vendor))
        common = (out / 'project/sdkconfig.common.defaults').read_text()
        if target == 'esp32':
            profile = 'CONFIG_IDF_TARGET="esp32"\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_240=y\n# CONFIG_FREERTOS_UNICORE is not set\n'
        else:
            common = common.replace('CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y\n', '')
            profile = 'CONFIG_IDF_TARGET="esp32c3"\nCONFIG_ESP32C3_REV_MIN_0=y\nCONFIG_ESP_DEFAULT_CPU_FREQ_MHZ_160=y\nCONFIG_FREERTOS_UNICORE=y\n'
        (out / 'project/sdkconfig.defaults').write_text(profile + common, encoding='utf-8')
        report.update(prepared=True,vendor_revision=REVISION,sdk_revision=SDK_HEAD[target],
                      fixtures=entries,fixture_manifest_sha256=sha(fixture),full_pcm_independent_oracle=False,
                      output_capacity=12288)
        save()
        if args.prepare_only:
            print(json.dumps(dict(prepared=True, target=target, target_executed=False)))
            return 0
        run('build', [powershell, '-NoProfile', '-NonInteractive', '-File', out / 'project/sdk-build.ps1',
                     '-Campaign', out, '-SdkDirectory', sdk, '-ToolsDirectory', tools,
                     '-PythonExecutable', python, '-Target', target], 1200)
        child = json.loads((out / 'sdk-child.json').read_text('utf-8-sig'))
        need(child['exit_status'] == 0 and child['pid'] > 0, 'actual SDK child terminal0')
        build = out / 'build'
        description = json.loads((build / 'project_description.json').read_bytes())
        elf = (build / description['app_elf']).resolve()
        need(elf.is_relative_to(build) and elf.read_bytes()[:6] == b'\x7fELF\x01\x01' and
             int.from_bytes(elf.read_bytes()[18:20], 'little') == (94 if target == 'esp32' else 243), 'actual native ELF32 architecture')
        compiler = Path(description['c_compiler'])
        report['tools']['compiler'] = dict(path=str(compiler), sha256=sha(compiler))
        cache = (build / 'CMakeCache.txt').read_text()
        ninja = Path(re.search(r'^CMAKE_MAKE_PROGRAM:[A-Z_]+=(.+)$', cache, re.M).group(1).strip())
        report['tools']['ninja'] = dict(path=str(ninja), sha256=sha(ninja))
        run('compiler-version', [compiler, '--version'])
        commands = json.loads((build / 'compile_commands.json').read_bytes())
        lookup = {str((out / row['snapshot']).resolve()).casefold(): original for original,row in report['inputs'].items()}
        used, dependencies, selected_objects = [], {}, []
        for row in commands:
            source = Path(row['file']).resolve()
            if not (source.is_relative_to(out / 'project') or source.is_relative_to(out / 'sources/vendor')):
                continue
            dep_text = run('compiler-deps-' + str(len(used)), [ninja, '-C', build, '-t', 'deps', row['output'].replace('\\','/')])
            need('(VALID)' in dep_text and '#deps ' in dep_text, 'actual GCC/Ninja dependency record')
            actual = []
            for line in dep_text.splitlines():
                if not line.startswith('    '): continue
                path = Path(line.strip())
                path = path.resolve() if path.is_absolute() else (build / path).resolve()
                need(path.is_file(), 'actual compiler dependency exists')
                original = lookup.get(str(path).casefold())
                if original is None:
                    original = str(path)
                    if original not in report['inputs']:
                        relative = Path('sources/compiler-dependencies') / hashlib.sha256(str(path).encode()).hexdigest()[:16] / path.name
                        freeze(path, relative)
                dependencies[str(path)] = dict(sha256=sha(path),manifest_original=original)
                actual.append(str(path))
            need(actual, 'nonempty actual compiler dependency closure')
            selected = dict(row,actual_dependency_paths=actual); used.append(selected)
            obj = Path(row['output'])
            if not obj.is_absolute(): obj = build / obj
            need(obj.is_file() and obj.resolve().is_relative_to(build), 'actual selected compiler object')
            selected_objects.append(obj)
            if obj.with_suffix('.su').exists(): selected_objects.append(obj.with_suffix('.su'))
        need(any(Path(row['file']).name=='main.c' for row in used) and
             any(Path(row['file']).name=='decoder_registration.c' for row in used), 'whole harness and unchanged production registration compiled')
        closure = out / 'actual-compiler-closure.json'
        closure.write_text(json.dumps(dict(translation_units=used,dependencies=dependencies),indent=2)+'\n',encoding='utf-8')
        report.update(actual_translation_units=len(used),actual_compiler_dependencies=len(dependencies))
        nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        symbols = run('symbols', [nm, '-n', elf])
        for name in ('decoder_register_codecs', 'esp_aac_dec_open', 'esp_aac_dec_decode', 'esp_audio_simple_dec_process'):
            need(re.search(r'\b' + name + r'$', symbols, re.M), 'actual linked public decoder: ' + name)
        need(not re.search(r'\b(?:__wrap_(?:esp_vorbis_|esp_audio_|esp_ogg_|floor[01]_|media_lib_)|native_vorbis_)[A-Za-z0-9_]*$',
                           symbols, re.M), 'no custom decoder or codec linker wrappers')
        need(not re.search(r'\b(?:compact5_|aac_compact_|aac_high_|aac_smoothing_|__wrap_(?:PVMP4Audio|ps_read_data|getfill|get_sbr_bitstream))[A-Za-z0-9_]*$',
                           symbols,re.M), 'no private AAC owner, metadata, FIL or reset hooks')
        config = (out / 'sdkconfig').read_text()
        for setting in ['CONFIG_COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE=y', 'CONFIG_ESP_TASK_WDT_EN=y',
                        'CONFIG_ESP_TASK_WDT_INIT=y', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y',
                        'CONFIG_AUDIO_DECODER_AAC_SUPPORT=y', 'CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y'] + (
                        ['CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=y'] if target == 'esp32' else []):
            need(re.search(r'^' + re.escape(setting) + r'$', config, re.M), 'checked runtime configuration: ' + setting)
        recipe = json.loads((build / 'flasher_args.json').read_bytes())
        flashes = {int(offset, 0): (build / name).resolve() for offset, name in recipe['flash_files'].items()}
        need(all(p.is_relative_to(build) for p in flashes.values()) and
             set(flashes) == ({4096, 32768, 65536} if target == 'esp32' else {0, 32768, 65536}), 'bounded diagnostic image recipe')
        flash = out / 'qemu-flash.bin'
        merge = [python, '-m', 'esptool', '--chip', target, 'merge-bin', '--output', flash,
                 '--flash-mode', 'dio', '--flash-size', '4MB', '--flash-freq', '40m']
        for offset, path in sorted(flashes.items()): merge += [hex(offset), path]
        run('merge', merge + ['--pad-to-size', '4MB'])
        report['fixture_blob'] = dict(bytes=(out / 'project/main/fixtures.bin').stat().st_size, sha256=sha(out / 'project/main/fixtures.bin'))
        report['build_outputs'] = {p.relative_to(out).as_posix(): sha(p) for p in
            [elf, elf.with_suffix('.map'), flash, out / 'sdkconfig', out / 'sdk-child.json', *flashes.values(),
             build / 'compile_commands.json', build / 'project_description.json', build / 'flasher_args.json']}
        report['build_outputs'].update({path.relative_to(out).as_posix():sha(path) for path in
            [closure, out / 'project/main/fixtures.bin', build / 'config/sdkconfig.json', build / 'config/sdkconfig.h',
             build / 'CMakeCache.txt', build / 'build.ninja', *selected_objects]})
        save()
        qargs = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet'] if target == 'esp32' else [qemu, '-M', 'esp32c3']
        qargs += ['-smp', '2' if target == 'esp32' else '1', '-L', rom, '-display', 'none', '-monitor', 'none',
                  '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
                  '-drive', 'file=' + str(flash) + ',if=mtd,format=raw']
        log = run('qemu', qargs, args.qemu_timeout)
        report['measurements'] = validate_log(log + '\n' + (out / 'qemu.stderr.log').read_text(errors='replace'), entries)
        for path, pin in report['inputs'].items():
            need(sha(path) == pin['sha256'] == sha(out / pin['snapshot']), 'source and frozen input immutability')
        need(all(sha(out / name)==digest for name,digest in report['build_outputs'].items()), 'all measured build artifacts unchanged')
        need(all(sha(pin['path'])==pin['sha256'] for pin in report['tools'].values()
                 if pin['path'] not in ('runtime-path-redacted',)), 'all native tools unchanged')
        report['all_bound_inputs_current'] = True
        report.update(completed=True, passed=True)
        print(json.dumps(dict(passed=True, target=target, measurements=report['measurements'])))
        return 0
    except Exception as error:
        report.update(failure_type=type(error).__name__, failure=str(error), completed=False, passed=False)
        print(json.dumps(dict(passed=False, target=target, failure=str(error))), file=sys.stderr)
        return 1
    finally:
        save()


if __name__ == '__main__':
    sys.exit(main())

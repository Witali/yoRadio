"""Public Espressif Ogg/Opus output-resize observations on pinned LX6 SDK/QEMU."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROJECT = ROOT / 'tests/target/cyd_espressif_opus_resize_qemu'
REVISION = '67b8d0e98f58c774b8652480893037273190e8dc'
FIXTURE_SHA = 'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
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


def case_rows(log):
    fields=('complete','outcome','input','remaining','calls','frames','pcm','sha256','resizes','error_consumed',
            'final_capacity','match','before','after','stack_free','core','priority','last_result')
    pattern=(r'EOR_CASE strategy=([a-z_]+) complete=(\d+) outcome=(\d+) input=(\d+) remaining=(\d+) calls=(\d+) frames=(\d+) pcm=(\d+) '
             r'sha256=([a-f0-9]{64}) resizes=(\d+) error_consumed=(\d+) final_capacity=(\d+) match=(\d+) before=(\d+) after=(\d+) '
             r'stack_free=(\d+) core=(\d+) priority=(\d+) last_result=(-?\d+)')
    result=[]
    for line in log.replace('\r\n','\n').splitlines():
        if not line.startswith('EOR_CASE'): continue
        match=re.fullmatch(pattern,line); need(match,'strict resize-case observation record')
        strategy,*values=match.groups()
        row={name:value if name=='sha256' else int(value) for name,value in zip(fields,values)}
        row['strategy']=strategy
        need(row['complete'] in (0,1) and row['match'] in (0,1) and 0<=row['outcome']<=6 and
             row['input']+row['remaining']==707097 and row['calls']>0 and row['before']>0 and row['after']>0 and
             0<row['stack_free']<=16384 and row['core']==1 and row['priority']==3,
             'explicit outcome, byte accounting and actual worker profile')
        need(bool(row['complete'])==(row['outcome']==0 and not row['remaining'] and row['input']==707097),
             'complete observation means genuine terminal drain')
        result.append(row)
    return result


def baseline_record(log):
    rows=case_rows(log); need(rows and rows[0]['strategy']=='baseline','baseline precedes retry experiments')
    row=rows[0]
    need(row['complete']==row['match']==1 and row['pcm']>0 and row['frames']>0 and row['resizes']==0 and
         row['final_capacity']==24576,'complete unresized public-vendor reference')
    return dict(reference_kind='unchanged_vendor_inline_eos',pcm_bytes=row['pcm'],pcm_sha256=row['sha256'],
                input_consumed=row['input'],sample_rate=48000,channels=2,bits_per_sample=16,
                fixture_sha256=FIXTURE_SHA,output_capacity=24576)


def validate_log(log,target='esp32'):
    need(target=='esp32','LX6 target only')
    log=log.replace('\r\n','\n')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',log,re.I),
         'no native assertion, panic, watchdog or heap failure')
    prefix='EOR_'; lines=[line for line in log.splitlines() if line.startswith(prefix)]
    need(not any(prefix in line and not line.startswith(prefix) for line in log.splitlines()),'no torn observation records')
    need(lines and lines[0]=='EOR_BEGIN target=esp32 coordinator=0 worker=1 stack=16384 priority=3 initial_capacity=12288 baseline_capacity=24576 fixture=707097',
         'expected fixture and original worker profile')
    cases=case_rows(log); reference=baseline_record(log)
    need([row['strategy'] for row in cases]==['baseline','retry_unchanged','honor_consumed'],'three independent decoder-instance strategies')
    events=[]; errors=[]
    for line in lines[1:-1]:
        if line.startswith('EOR_CASE'): continue
        if line.startswith('EOR_RESIZE'):
            match=re.fullmatch(r'EOR_RESIZE strategy=([a-z_]+) call=(\d+) len_before=(\d+) raw_len=(\d+) consumed=(\d+) decoded_size=(\d+) needed_size=(\d+) capacity=(\d+) result=(-?\d+) advance_on_error=(\d+)',line)
            need(match,'complete public resize-field observation')
            strategy,*values=match.groups(); row=dict(zip(('call','len_before','raw_len','consumed','decoded_size','needed_size','capacity','result','advance_on_error'),map(int,values)))
            row['strategy']=strategy
            need(row['result']==-8 and strategy in ('retry_unchanged','honor_consumed') and row['advance_on_error']==int(strategy=='honor_consumed'),
                 'actual BUFFER_NOT_ENOUGH and explicit caller policy')
            events.append(row)
        else:
            match=re.fullmatch(r'EOR_ERROR strategy=([a-z_]+) call=(\d+) raw_len=(\d+) consumed=(\d+) decoded_size=(\d+) needed_size=(\d+) capacity=(\d+) result=(-?\d+)',line)
            need(match,'complete public decoder-error observation')
            strategy,*values=match.groups(); row=dict(zip(('call','raw_len','consumed','decoded_size','needed_size','capacity','result'),map(int,values)))
            row['strategy']=strategy; need(row['result'] not in (0,-8),'error record is a real decoder error'); errors.append(row)
    for row in cases:
        own=[event for event in events if event['strategy']==row['strategy']]
        need(len(own)==row['resizes'] and sum(event['consumed'] for event in own)==row['error_consumed'] and
             all(0<event['call']<=row['calls'] for event in own),'every resize and error-consumption sum retained')
        same=bool(row['complete']) and row['pcm']==reference['pcm_bytes'] and row['sha256']==reference['pcm_sha256']
        need(bool(row['match'])==same,'qualification independently follows full output identity and complete drain')
        if row['strategy']!='baseline': need(row['before']==row['after']==cases[0]['after'],'fresh instance cleanup restores stable post-warmup heap')
    terminal=re.fullmatch(r'EOR_COMPLETE target=esp32 cases=3 core=1 retry_unchanged_qualified=(\d+) honor_consumed_qualified=(\d+) registry_before=(\d+) heap_free=(\d+) retained=(-?\d+) heap_min=(\d+) stack_free=(\d+) heap_integrity=1',lines[-1])
    need(terminal,'terminal real cleanup and resource census')
    unchanged,honor,before,free,retained,minimum,stack=map(int,terminal.groups())
    need(unchanged==cases[1]['match'] and honor==cases[2]['match'] and retained==before-free and
         0<minimum<=free and 0<stack<=16384,'terminal qualification flags agree with independently evaluated cases')
    return dict(baseline=cases[0],cases=cases[1:],reference=reference,resize_events=events,decoder_errors=errors,
                observation_completed=True,production_retry_qualified=bool(unchanged),honor_consumed_qualified=bool(honor),
                all_retries_qualified=bool(unchanged and honor),registry_before=before,heap_free=free,
                retained_after_unregister_bytes=retained,heap_min=minimum,stack_free=stack,
                full_pcm_independent_oracle=False,required_opus_playback_trim_unresolved=True)


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
    fixture = ROOT / 'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg'
    powershell = Path(shutil.which('pwsh.exe') or '')
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    need(all(p.is_file() for p in (python, qemu, powershell, git, fixture, sdk / 'export.ps1')), 'installed native dependencies')
    need(sha(qemu) == QEMU_SHA[target] and sha(fixture) == FIXTURE_SHA, 'pinned emulator and valid fixture')
    archives = [vendor / f'lib/{target}/libesp_audio_{name}.a' for name in ('codec', 'simple_dec')]
    need(tuple(map(sha, archives)) == ARCHIVES[target], 'pinned target-specific vendor archives')
    if args.preflight_only:
        print(json.dumps(dict(preflight=True, target=target, output_created=False, target_executed=False)))
        return 0
    out.mkdir(parents=True)
    report = dict(target=target, passed=False, completed=False, commands=[], inputs={}, tools={},
                  production_firmware=False, physical_device=False, custom_decoder=False,
                  private_abi_used=False, target_executed=False, full_conformance_qualified=False)

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
        freeze(fixture, Path('project/main/fixture.ogg'))
        for name in ('decoder_registration.c', 'decoder_registration.h'):
            freeze(ROOT / 'idf/esp32-cyd2usb-native/main' / name, Path('project/main') / name)
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
                      fixture_sha256=FIXTURE_SHA,fixture_bytes=707097,full_pcm_independent_oracle=False,
                      initial_output_capacity=12288,baseline_output_capacity=24576)
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
        nm = compiler.with_name(compiler.name.replace('gcc', 'nm'))
        symbols = run('symbols', [nm, '-n', elf])
        for name in ('decoder_register_codecs', 'esp_opus_dec_open', 'esp_opus_dec_decode', 'esp_audio_simple_dec_process'):
            need(re.search(r'\b' + name + r'$', symbols, re.M), 'actual linked public decoder: ' + name)
        need(not re.search(r'\b(?:__wrap_(?:esp_vorbis_|esp_audio_|esp_ogg_|floor[01]_|media_lib_)|native_vorbis_)[A-Za-z0-9_]*$',
                           symbols, re.M), 'no custom decoder or codec linker wrappers')
        config = (out / 'sdkconfig').read_text()
        for setting in ['CONFIG_COMPILER_OPTIMIZATION_ASSERTIONS_ENABLE=y', 'CONFIG_ESP_TASK_WDT_EN=y',
                        'CONFIG_ESP_TASK_WDT_INIT=y', 'CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=y',
                        'CONFIG_AUDIO_DECODER_OPUS_SUPPORT=y', 'CONFIG_AUDIO_SIMPLE_DEC_OGG_SUPPORT=y'] + (
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
        report['build_outputs'] = {p.relative_to(out).as_posix(): sha(p) for p in
            [elf, elf.with_suffix('.map'), flash, out / 'sdkconfig', out / 'sdk-child.json', *flashes.values(),
             build / 'compile_commands.json', build / 'project_description.json', build / 'flasher_args.json']}
        save()
        qargs = [qemu, '-audiodev', 'none,id=quiet', '-M', 'esp32,audiodev=quiet'] if target == 'esp32' else [qemu, '-M', 'esp32c3']
        qargs += ['-smp', '2' if target == 'esp32' else '1', '-L', rom, '-display', 'none', '-monitor', 'none',
                  '-serial', 'stdio', '-no-reboot', '-snapshot', '-nic', 'none',
                  '-drive', 'file=' + str(flash) + ',if=mtd,format=raw']
        log = run('qemu', qargs, args.qemu_timeout)
        report['baseline']=baseline_record(log)
        (out/'baseline.json').write_text(json.dumps(report['baseline'],indent=2)+'\n',encoding='utf-8')
        report['measurements'] = validate_log(log + '\n' + (out / 'qemu.stderr.log').read_text(errors='replace'), target)
        for path, pin in report['inputs'].items():
            need(sha(path) == pin['sha256'] == sha(out / pin['snapshot']), 'source and frozen input immutability')
        report.update(completed=True, observation_completed=True, passed=report['measurements']['all_retries_qualified'])
        print(json.dumps(dict(passed=report['passed'], completed=True, target=target, measurements=report['measurements'])))
        return 0 if report['passed'] else 1
    except Exception as error:
        report.update(failure_type=type(error).__name__, failure=str(error), completed=False, passed=False)
        print(json.dumps(dict(passed=False, target=target, failure=str(error))), file=sys.stderr)
        return 1
    finally:
        save()


if __name__ == '__main__':
    sys.exit(main())

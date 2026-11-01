"""Capture complete stock Espressif raw PCM for independent sample-position comparison.

Only a new public-API diagnostic is built. Full PCM/hex logs remain local;
original campaigns, firmware source and vendor archives are unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent.parent if ROOT.parent.name == '.worktree' else ROOT
PROJECT = ROOT / 'tests/target/cyd_opus_position_qemu'
REVISION = '67b8d0e98f58c774b8652480893037273190e8dc'
FIXTURE_SHA = '53b3ee1b3c883d4a282fa88d0ad42361a8d00eddb5d4ebe9e50657336c5b2a11'
LONG_SHA = 'b6237ae8df98d3fabbea252eec82b291a46dfdb537cb5b9f537bf5e00bcd7679'
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


def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def validate_log(log,target='esp32',out=None):
    need(target=='esp32' and out is not None,'new LX6 PCM capture only')
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP|watchdog.*triggered|stack overflow',log,re.I),'no native runtime fault')
    lines=log.replace('\r\n','\n').splitlines()
    need(not any('EOPC_' in line and not line.startswith('EOPC_') for line in lines),'no torn PCM observations')
    lines=[line for line in lines if line.startswith('EOPC_')]
    need(lines[0]=='EOPC_BEGIN coordinator=0 worker=1 priority=3 stack=16384 output_capacity=24576 fixtures=2','original diagnostic task profile')
    cases={}; pcm={'F20':bytearray(),'F120':bytearray()}; records={'F20':0,'F120':0}
    order=[]
    for line in lines[1:-1]:
        if line.startswith('EOPC_DATA'):
            match=re.fullmatch(r'EOPC_DATA id=(F20|F120) seq=(\d+) offset=(\d+) size=(\d+) hex=([0-9a-f]+)',line)
            need(match,'complete labeled raw PCM record')
            name,seq,offset,size,body=match.groups(); raw=bytes.fromhex(body)
            need(int(seq)==records[name] and int(offset)==len(pcm[name]) and int(size)==len(raw) and 0<len(raw)<=256 and len(raw)%4==0,'ordered exact PCM extent')
            need(not cases or name not in cases,'no PCM after case closes')
            if not order or order[-1]!=name: order.append(name)
            pcm[name]+=raw; records[name]+=1
        else:
            match=re.fullmatch(r'EOPC_CASE id=(F20|F120) input=(\d+) calls=(\d+) frames=(\d+) pcm=(\d+) sha256=([0-9a-f]{64}) window_begin=(\d+) window_end=(\d+) window_bytes=(\d+) window_sha256=([0-9a-f]{64}) sample_rate=48000 channels=2 bits=16 heap_before=(\d+) heap_after=(\d+) stack_free=(\d+) core=1 priority=3',line)
            need(match,'complete actual raw/window identity')
            name,*values=match.groups(); fields=('input','calls','frames','pcm','sha256','window_begin','window_end','window_bytes','window_sha256','heap_before','heap_after','stack_free')
            row={key:value if key.endswith('sha256') else int(value) for key,value in zip(fields,values)}
            need(name not in cases and row['input']==(706319 if name=='F20' else 707097),'complete unique source fixture')
            expected=('a773dc8a0db92aebd689c157bb504cd43e6d6544f8249362db57d59176cb316b','b63b58b563d2a20d90a7bef235e5c1099dc52433db19083492d9c7098345469f',2115840) if name=='F20' else ('670f7787b470d0e8bc101856bc16e42ed0cb15ef85abf3a0214db0261f4cb684','4110db997c16a05c329284bb6105468752c25d67818e3a99b8c9d47c5f481fd0',2119680)
            need(row['sha256']==expected[0] and row['window_sha256']==expected[1] and row['pcm']==expected[2],'reproduce complete earlier stock vendor and raw-window identities')
            need(row['window_begin']==312 and row['window_end']==528312 and row['window_bytes']==2112000,'audited fixture timeline window')
            need(len(pcm[name])==row['pcm'] and hashlib.sha256(pcm[name]).hexdigest()==row['sha256'] and hashlib.sha256(pcm[name][312*4:528312*4]).hexdigest()==row['window_sha256'],'all emitted PCM bytes match actual diagnostic hashes')
            path=out/(name+'-vendor-raw.pcm');path.write_bytes(pcm[name]);row['raw_pcm_path']=path.name;row['hex_records']=records[name]
            cases[name]=row
    need(order==list(cases)==['F20','F120'],'two complete stock instances in order')
    need(re.fullmatch(r'EOPC_COMPLETE cases=2 core=1 priority=3 heap_free=\d+ heap_min=\d+ stack_free=\d+ heap_integrity=1',lines[-1]),'final cleanup and heap integrity')
    return dict(cases=cases,public_api_only=True,full_pcm_captured=True,production_trim_implemented=False,independent_alignment_proven=False)


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
    fixture = ROOT / 'tests/fixtures/esp32c3_calibration/opus-510.ogg'
    long_fixture = ROOT / 'tests/fixtures/opus_ogg_long_packets/stereo-510-120ms.ogg'
    powershell = Path(shutil.which('pwsh.exe') or '')
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    need(all(p.is_file() for p in (python, qemu, powershell, git, fixture, sdk / 'export.ps1')), 'installed native dependencies')
    need(sha(qemu) == QEMU_SHA[target] and sha(fixture) == FIXTURE_SHA and sha(long_fixture) == LONG_SHA, 'pinned emulator and both unchanged fixtures')
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
        freeze(fixture, Path('project/main/fixture20.ogg'))
        freeze(long_fixture, Path('project/main/fixture120.ogg'))
        short_auditor=ROOT/'tests/verify-cyd-opus-direct-checkpoint.py'
        long_auditor=ROOT/'tests/fixtures/opus_ogg_long_packets/generate.py'
        need(sha(short_auditor)=='50bb1a2b372629dbe720ba612cbbbcf90977598258278c741192ec0d4ded815c' and
             sha(long_auditor)=='b31791eb3ba1a4f7159db4cfb06358b7cf52e512417e40993f9bc1ca70fc76d6','reviewed canonical fixture timeline auditors')
        audits=dict(short=module(short_auditor,'short_opus_fixture_auditor').fixture_accounting(fixture.read_bytes()),
                    long=module(long_auditor,'long_opus_fixture_auditor').audit(long_fixture.read_bytes()))
        need(audits['short']['pre_skip_frames']==audits['long']['preskip']==312 and
             audits['short']['eos_granule']==audits['long']['eos_granule']==528312 and
             audits['short']['initial_granule_offset']==audits['long']['initial_granule_offset']==0 and
             audits['short']['raw_frames']==528960 and audits['long']['raw_frames']==529920,'independently audited fixture window ranges')
        for name,path in (('short',short_auditor),('long',long_auditor)):
            freeze(path,Path('sources/fixture-auditors')/(name+'.py'))
        report['fixture_audits']=audits
        (out/'project/main/window_ranges.h').write_text('#pragma once\n#define SHORT_WINDOW_BEGIN UINT64_C(312)\n#define SHORT_WINDOW_END UINT64_C(528312)\n#define LONG_WINDOW_BEGIN UINT64_C(312)\n#define LONG_WINDOW_END UINT64_C(528312)\n',encoding='utf-8')
        report['generated_header_sha256']=sha(out/'project/main/window_ranges.h')
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
                      fixture_sha256=FIXTURE_SHA,fixture_bytes=706319,full_pcm_independent_oracle=False,
                      output_capacity=24576)
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
        for name in ('decoder_register_codecs', 'esp_opus_dec_open', 'esp_opus_dec_decode', 'esp_audio_simple_dec_process', 'esp_ogg_parse_frame'):
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
        report['measurements'] = validate_log(log + '\n' + (out / 'qemu.stderr.log').read_text(errors='replace'), target,out)
        for path, pin in report['inputs'].items():
            need(sha(path) == pin['sha256'] == sha(out / pin['snapshot']), 'source and frozen input immutability')
        for name,digest in report['build_outputs'].items():
            need(sha(out/name)==digest,'pre/post bound build artifact immutability')
        need(sha(out/'project/main/window_ranges.h')==report['generated_header_sha256'],'derived window header unchanged')
        report.update(completed=True, passed=True,all_bound_inputs_current=True,
                      public_api_only=True,padding_units_assumed=False,production_trim_implemented=False)
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

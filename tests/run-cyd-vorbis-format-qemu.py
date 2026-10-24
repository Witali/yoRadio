"""Isolated CYD public raw Vorbis format probe; no radio/Ogg/reset/OOM qualification."""
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
from windows_compile_command import macro_command, check_macro_inputs

ARCHIVES = {'libesp_audio_codec.a': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
            'libesp_audio_simple_dec.a': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6'}
FIXTURE_SHA = '839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
SDK_HEAD = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
MODULES = ('vorbis_repair/setup.c', 'vorbis_repair/output.c', 'vorbis_repair/simple.c', 'vorbis_repair/floor1_render.h',
           'vorbis_repair/COPYING', 'vorbis_repair_abi.h', 'compat/vorbis_repair/enable.cmake')


def need(condition, message):
    if not condition: raise RuntimeError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture_accounting(header):
    def values(name):
        body = re.search(r'\b' + name + r'\[\]\s*=\s*\{([^}]+)\}', header).group(1)
        return [int(x) for x in body.split(',') if x.strip()]
    offsets, modes = values('fixture_offsets'), values('fixture_long_mode')
    need(len(offsets) == 69 and len(modes) == 68 and modes.count(1) == 67, 'Pinned fixture packet/mode counts')
    sizes = [b-a for a, b in zip(offsets, offsets[1:])]
    def pcm(long):
        blocks = [long if mode else 256 for mode in modes]
        return [0] + [a+b for a, b in zip(blocks, blocks[1:])]  # /4 samples * 4 stereo bytes.
    need(sum(pcm(8192)) == 1089792 and pcm(8192).count(16384) == 66, 'Pinned 8192 overlap accounting')
    return sizes, pcm


def validate_log(log, scope, control, header):
    """Check every emitted packet and ordered prerequisite, including exact controls."""
    need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP', log), 'Target panic/corruption')
    sizes, pcm = fixture_accounting(header)
    expected = [rf'BEGIN expected_rejection={int(scope == "baseline")} coordinator=0',
                r'VENDOR_OPEN rate=192000 long=8192 result=0 handle=1']
    expected += [rf'VENDOR_PACKET packet={i} consumed={size} pcm={pcm(8192)[i]} sample_rate=192000 channel=2 bits=16 canaries=1 core=1'
                 for i, size in enumerate(sizes)]
    expected += [r'VENDOR_COMPLETE packets=68 pcm=1089792 nonzero=[1-9]\d* full8192=66']
    pairs = [(48000, 2048), (192000, 8192), (64000, 8192)]
    if scope == 'acceptance' and not control: pairs += [(63999, 8192), (48000, 8192)]
    for rate, long in pairs:
        output = pcm(long)
        reference_rate = 192000 if long == 8192 else rate
        expected += [rf'PAIR_PACKET rate={rate} long={long} packet={i} consumed={size} pcm={output[i]} '
                     rf'vendor_expected_rate={reference_rate} vendor_rate={reference_rate} checked_expected_rate={rate} checked_rate={rate} '
                     rf'expected_channel=2 vendor_channel=2 checked_channel=2 expected_bits=16 vendor_bits=16 checked_bits=16 exact=1 canaries=1 core=1'
                     for i, size in enumerate(sizes)]
        expected += [rf'EXACT rate={rate} long={long} packets=68 pcm={sum(output)} full8192={output.count(16384)}']
    if control:
        expected += [r'FAILURE legal_candidate_open_required']
    else:
        nonzero = r'(?:-[1-9]\d*|[1-9]\d*)'
        if scope == 'baseline':
            expected += [rf'LEGAL_REJECT rate={rate} long=8192 result={nonzero} header_error=1' for rate in (63999, 48000)]
        expected += [rf'INVALID_REJECT case={case} result={nonzero} header_error=1'
                     for case in ('zero_rate', 'short32', 'long16384', 'short_exceeds_long')]
        expected += ([r'BASELINE low_rejected=2 high_exact=2 normal_exact=1 invalid_rejected=4 core=1']
                     if scope == 'baseline' else
                     [r'COMPLETE low_exact=2 high_exact=2 normal_exact=1 invalid_rejected=4 core=1'])
    actual = [line.removeprefix('CYD_VORBIS_FORMAT_') for line in log.splitlines()
              if line.startswith('CYD_VORBIS_FORMAT_')]
    need(len(actual) == len(expected), f'Protocol line count: expected {len(expected)}, got {len(actual)}')
    for i, (line, pattern) in enumerate(zip(actual, expected)):
        need(re.fullmatch(pattern, line), f'Protocol line {i}: {line!r}; expected {pattern!r}')
    return {'protocol_lines': len(actual), 'vendor_packets': len(sizes), 'exact_pairs': len(pairs),
            'exact_pair_packets': len(pairs)*len(sizes), 'exact_failure': 'legal_candidate_open_required' if control else None}


def main():
    repo = next(p for p in Path(__file__).resolve().parents if (p / 'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c').is_file())
    nearest = lambda rel: next((p / rel for p in (repo, *repo.parents) if (p / rel).exists()), None)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--scope', choices=('baseline', 'acceptance'), required=True)
    parser.add_argument('--control', choices=('old-guard',))
    parser.add_argument('--candidate', type=Path, default=repo / 'idf/esp32-cyd2usb-native/main')
    parser.add_argument('--idf', type=Path, default=nearest('.idf/v6.0.2'))
    parser.add_argument('--idf-tools', type=Path)
    parser.add_argument('--codec', type=Path)
    parser.add_argument('--qemu', type=Path, default=shutil.which('qemu-system-xtensa.exe'))
    parser.add_argument('--powershell', type=Path, default=shutil.which('pwsh.exe') or shutil.which('pwsh'))
    args = parser.parse_args()
    if sys.platform != 'win32': parser.error('Pinned Windows SDK launcher required')
    if args.control and args.scope != 'acceptance': parser.error('old-guard control requires acceptance scope')
    if not all((args.idf, args.qemu, args.powershell)): parser.error('Specify missing SDK/QEMU/PowerShell paths')
    out, candidate, sdk = args.output.resolve(), args.candidate.resolve(), args.idf.resolve()
    tools = (args.idf_tools or sdk.parent / 'tools-v6.0.2').resolve()
    codec = (args.codec or sdk.parent / 'esp-adf-libs/esp_audio_codec').resolve()
    py, ps, qemu = tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe', args.powershell.resolve(), args.qemu.resolve()
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    taskkill = Path(os.environ['SystemRoot']) / 'System32/taskkill.exe'
    rom = qemu.parent.parent / 'pc-bios'
    # The sibling layout permits review from this scratch prep before promotion.
    harness = Path(__file__).resolve().parent / 'target/cyd_vorbis_format_qemu'
    protected = (candidate, sdk, tools, codec, ps.parent, qemu.parent, rom)
    if (not candidate.is_relative_to(repo) or not out.is_relative_to(repo / '.build') or out == repo / '.build'
        or out.exists() or any((p / 'report.json').is_file() for p in out.parents if p != repo)
        or any(out == p or out.is_relative_to(p) or p.is_relative_to(out) for p in protected)):
        parser.error('Use a fresh .build campaign, separate from source/runtime directories and previous reports')
    required = [py, ps, qemu, git, taskkill, rom/'esp32-v3-rom.bin', rom/'esp32-v3-rom-app.bin',
                sdk/'export.ps1', sdk/'tools/idf.py', *[candidate/x for x in MODULES],
                *[codec/'lib/esp32'/x for x in ARCHIVES]]
    if any(not p.is_file() for p in required): parser.error('Missing required pinned source/runtime')
    out.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, completed=False, scope=args.scope, control=args.control,
                  regression_reproduced=False, format_acceptance_qualified=False, physical_device=False,
                  production_radio_integration=False, commands=[], inputs={}, tools={},
                  pcm_comparison_scope='same-loader handle parity with shared floor1 renderer',
                  unchanged_vendor_pcm_oracle=False, independent_reference_compared=False)
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1', GIT_OPTIONAL_LOCKS='0')
    def save():
        temp = out / 'report.json.tmp'
        temp.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
        temp.replace(out/'report.json')
    def freeze(path, relative):
        dest = out/'sources'/relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(path.read_bytes())
        report['inputs'][str(path.resolve())] = dict(sha256=sha(path), snapshot=str(dest.relative_to(out)))
    def current():
        need(all(sha(path) == row['sha256'] == sha(out/row['snapshot']) for path,row in report['inputs'].items()), 'Input changed')
        need(all(sha(path) == value for path,value in report['tools'].items()), 'Tool/archive changed')
        need(all(sha(out/path) == value for path,value in report.get('variant_sources',{}).items()), 'Frozen variant changed')
    def execute(name, argv, timeout=60, cwd=None):
        row = dict(name=name, argv=list(map(str,argv)), cwd=str(cwd or out), state='starting', exit_status=None)
        report['commands'].append(row); save()
        proc = None
        try:
            with (out/(name+'.stdout.log')).open('wb') as stdout, (out/(name+'.stderr.log')).open('wb') as stderr:
                try:
                    proc = subprocess.Popen(row['argv'], cwd=row['cwd'], stdout=stdout, stderr=stderr,
                        stdin=subprocess.DEVNULL, env=env, creationflags=subprocess.CREATE_NO_WINDOW)
                    row.update(pid=proc.pid, state='running'); save()
                    proc.wait(timeout=timeout)
                    row.update(exit_status=proc.returncode, state='complete')
                except BaseException as exc:
                    row.update(state='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed', error=repr(exc))
                    if proc is not None and proc.poll() is None:
                        try:
                            killed = subprocess.run([str(taskkill),'/PID',str(proc.pid),'/T','/F'],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=15,
                                creationflags=subprocess.CREATE_NO_WINDOW)
                            (out/(name+'.cleanup.log')).write_bytes(killed.stdout)
                            row['tree_cleanup_exit_status'] = killed.returncode
                        except BaseException as cleanup_error:
                            row['cleanup_error'] = repr(cleanup_error)
                        finally:
                            if proc.poll() is None: proc.kill()  # Only this owned direct process.
                            proc.wait(timeout=15)
                    raise
        finally:
            for stream in ('stdout','stderr'):
                path = out/(name+'.'+stream+'.log')
                if path.is_file(): row[stream+'_sha256'] = sha(path)
            if proc is not None: row['exit_status'] = proc.poll()
            save()
        need(row['exit_status'] == 0, name+' nonzero exit; see retained logs')
        return (out/(name+'.stdout.log')).read_text(errors='replace').replace('\r\n','\n')
    save()
    try:
        for name in MODULES: freeze(candidate/name, Path('candidate')/name)
        for path in sorted(harness.rglob('*')):
            if path.is_file(): freeze(path, Path('project')/path.relative_to(harness))
        freeze(Path(__file__).resolve(), Path('helpers/run.py'))
        freeze(Path(__file__).with_name('windows_compile_command.py'), Path('helpers/windows_compile_command.py'))
        for name in ('tools/cmake/version.cmake','tools/cmake/toolchain-esp32.cmake','tools/cmake/toolchain.cmake','export.ps1','tools/idf.py'):
            freeze(sdk/name,Path('sdk')/name)
        for path in sorted((codec/'include').rglob('*.h')): freeze(path,Path('codec/include')/path.relative_to(codec/'include'))
        for name in ('CMakeLists.txt','Kconfig'):
            if (codec/name).is_file(): freeze(codec/name,Path('codec')/name)
        for path in (Path(sys.executable),py,ps,qemu,git,taskkill,rom/'esp32-v3-rom.bin',rom/'esp32-v3-rom-app.bin',
                     *[codec/'lib/esp32'/x for x in ARCHIVES]): report['tools'][str(path.resolve())] = sha(path)
        need({name:sha(codec/'lib/esp32'/name) for name in ARCHIVES} == ARCHIVES, 'Wrong installed vendor archives')
        header = (out/'sources/project/main/fixture.h').read_text()
        need(sha(out/'sources/project/main/fixture.h') == FIXTURE_SHA, 'Wrong public fixture')
        fixture_accounting(header)
        shutil.copytree(out/'sources/candidate',out/'variant')
        if args.control:
            path = out/'variant/vorbis_repair/setup.c'
            text = path.read_bytes()
            newline = b'\r\n' if b'\r\n' in text else b'\n'
            anchor = b'#ifdef LIMIT_TO_64kHz\n  if(vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;\n#endif'.replace(b'\n',newline)
            need(text.count(anchor) == 1, 'old-guard control requires repaired source with exactly the retained optional limit branch')
            insertion = b'\n#else\n  if(vi->rate<64000 && ci->blocksizes[1]>4096)goto err_out;\n#endif'.replace(b'\n',newline)
            path.write_bytes(text.replace(anchor,anchor.replace(newline+b'#endif',insertion)))
        report['variant_sources'] = {str(p.relative_to(out)):sha(p) for p in (out/'variant').rglob('*') if p.is_file()}
        need(execute('sdk-head',[git,'-C',sdk,'rev-parse','HEAD']).strip() == SDK_HEAD,'Wrong SDK commit')
        need(not execute('sdk-clean',[git,'-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'Dirty SDK')
        current(); save()
        try:
            execute('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1',
                '-Campaign',out,'-Repository',repo,'-SdkDirectory',sdk,'-ToolsDirectory',tools,'-CodecDirectory',codec,
                '-ExpectedRejection',int(args.scope == 'baseline')],1200)
        finally:
            report['sdk_build_logs'] = {name:dict(sha256=sha(out/name),bytes=(out/name).stat().st_size)
                if (out/name).is_file() else dict(missing=True)
                for name in ('sdk-build.stdout.log','sdk-build.stderr.log')}
            save()
        need(not any(row.get('missing') for row in report['sdk_build_logs'].values()), 'Missing actual SDK child logs')
        current()
        activated = json.loads((out/'compiler-environment.json').read_text(encoding='utf-8-sig'))
        need(set(activated) == {'PATH','IDF_PATH','IDF_TOOLS_PATH','IDF_PYTHON_ENV_PATH'},'Unexpected compiler environment fields')
        env.update(activated)
        build = out/'build'
        desc = json.loads((build/'project_description.json').read_text())
        elf, app, cc = build/desc['app_elf'], build/desc['app_bin'], Path(desc['c_compiler'])
        nm = cc.with_name(cc.name.replace('gcc','nm'))
        before = json.loads((out/'compiler-identity-before-build.json').read_text(encoding='utf-8-sig'))
        need(Path(before['compiler']).resolve() == cc.resolve() and Path(before['nm']).resolve() == nm.resolve(), 'Actual compiler differs from pre-build identity')
        for path,key in ((cc,'compiler_sha256'),(nm,'nm_sha256')):
            need(sha(path) == before[key], 'Compiler tool changed during build')
            report['tools'][str(path)] = before[key]
        report['build_outputs'] = {str(p.relative_to(out)):sha(p) for p in (elf,app,out/'sdkconfig',build/'compile_commands.json',out/'compiler-environment.json',out/'compiler-identity-before-build.json')}
        report['build_outputs'].update({name:row['sha256'] for name,row in report['sdk_build_logs'].items()})
        need(struct.unpack_from('<H',elf.read_bytes(),18)[0] == 94,'Wrong ELF machine')
        rows = json.loads((build/'compile_commands.json').read_text())
        row_source = lambda row: (Path(row['directory'])/row['file']).resolve()
        actual = [row for row in rows if row_source(row).is_relative_to(out/'variant')]
        need({row_source(r) for r in actual} == {out/'variant'/name for name in MODULES[:3]} and len(actual) == 3,'Actual bridge compile rows')
        setup = next(r for r in actual if Path(r['file']).name == 'setup.c')
        argv,cwd,original,generated = macro_command(setup,cc,out/'variant/vorbis_repair/setup.c')
        report['setup_macro_context'] = dict(row=setup,original_argv=original,probe_argv=argv,cwd=str(cwd))
        report['setup_macro_context']['generated_inputs'] = {}
        for path,data in generated.items():
            need(path.is_relative_to(build), 'Generated compiler input escaped build')
            freeze(path,Path('generated')/path.relative_to(build))
            digest = hashlib.sha256(data).hexdigest()
            need(sha(path) == digest, 'Generated compiler input changed during freeze')
            report['setup_macro_context']['generated_inputs'][str(path)] = dict(sha256_before=digest)
            report['build_outputs'][str(path.relative_to(out))] = digest
        check_macro_inputs(generated); current(); save()
        try:
            macros = execute('setup-macros',argv,cwd=cwd)
        finally:
            for path in generated:
                report['setup_macro_context']['generated_inputs'][str(path)]['sha256_after'] = sha(path) if path.is_file() else None
            save()
            check_macro_inputs(generated); current()
        need(not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M),'Optional 64kHz limit unexpectedly active')
        for name in ('CONFIG_IDF_TARGET_ESP32','CONFIG_YORADIO_VORBIS_REPAIR'):
            need(re.search(r'^#define '+name+r' 1$',macros,re.M),'Expected setup compile context '+name)
        symbols = execute('symbols',[nm,'-n','-S',elf])
        for symbol in ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','__wrap_floor1_inverse2',
                       'esp_vorbis_dec_open','esp_vorbis_dec_decode'):
            need(re.search(r'\b'+symbol+'$',symbols,re.M),'Missing symbol '+symbol)
        recipe = json.loads((build/'flasher_args.json').read_text())
        settings = recipe.get('flash_settings',{})
        need({k:settings.get(k) for k in ('flash_mode','flash_size','flash_freq')} ==
             {'flash_mode':'dio','flash_size':'4MB','flash_freq':'40m'}, 'Unexpected isolated flash settings')
        expected_flash = {0x1000:build/'bootloader/bootloader.bin',
                          0x8000:build/'partition_table/partition-table.bin',0x10000:app}
        need(len(recipe['flash_files']) == 3 and
             {int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()} ==
             {offset:path.resolve() for offset,path in expected_flash.items()}, 'Unexpected isolated flash offsets/files')
        report['build_outputs']['build/flasher_args.json'] = sha(build/'flasher_args.json')
        flash = out/'qemu-flash.bin'
        merge = [py,'-m','esptool','--chip','esp32','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,name in sorted(recipe['flash_files'].items(),key=lambda x:int(x[0],0)):
            path = (build/name).resolve(); need(path.is_relative_to(build),'Flash recipe escaped build')
            report['build_outputs'][str(path.relative_to(out))] = sha(path)
            merge += [offset,path]
        execute('merge',merge+['--pad-to-size','4MB'])
        report['build_outputs'][str(flash.relative_to(out))] = sha(flash)
        current(); save()
        log = execute('qemu',[qemu,'-audiodev','none,id=quiet','-M','esp32,audiodev=quiet','-smp','2','-L',rom,
            '-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none',
            '-drive','file='+str(flash)+',if=mtd,format=raw'],120)
        stderr = (out/'qemu.stderr.log').read_text(errors='replace')
        report['observed'] = validate_log(log+'\n'+stderr,args.scope,args.control,header)
        need(execute('sdk-head-after',[git,'-C',sdk,'rev-parse','HEAD']).strip() == SDK_HEAD,'SDK identity changed')
        need(not execute('sdk-clean-after',[git,'-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK changed')
        current()
        need(all(sha(out/path) == value for path,value in report['build_outputs'].items()),'Build/execution bytes changed')
        report.update(completed=True,regression_reproduced=args.scope == 'baseline',
            control_effective=bool(args.control),format_acceptance_qualified=args.scope == 'acceptance' and not args.control,
            passed=args.scope == 'acceptance' and not args.control,
            result='CONTROL_EFFECTIVE' if args.control else 'REGRESSION_REPRODUCED' if args.scope == 'baseline' else 'FORMAT_ACCEPTED')
        save()
        print(json.dumps({k:report[k] for k in ('result','passed','regression_reproduced','format_acceptance_qualified')}))
        return 0
    except BaseException as exc:
        report.update(passed=False,completed=False,regression_reproduced=False,format_acceptance_qualified=False,
                      result='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'NONPASS',error=repr(exc))
        save()
        raise


if __name__ == '__main__': sys.exit(main())

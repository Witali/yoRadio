"""Isolated C3 public raw uint32 rates; no radio/Ogg/reset/OOM qualification."""
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
from rate_protocol import validate_log

ARCHIVES = {'libesp_audio_codec.a': '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909',
            'libesp_audio_simple_dec.a': '232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f'}
FIXTURE_SHA = '839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378'
HEADER_AUDIT = {'AUDIT.md':'6c1dd5dc25021e4beb551907f1978ebc0399c864a2bcf254e164f2ebcb1a9c8c',
                'sources.json':'c48f10696437b622ddac456d3ed48e2848acea9dd9f26925da0693eb08bb9310'}
CALLER_SHA = '684b668f3a09b970f566bb1a95f7fb22952a6f70b0dde4ddd02d9437b6404f04'
PROTOCOL_SHA = '3440dc6f58e8b8ae7ceaba18a05815321ea60a2a3640f6e681c81100e5d72050'
RAW_HELPER_SHA = '3c1db2f7b44fbbfb8e352d52325dd99518e77c34567080bd226b361b53b5cd76'
SDK_HEAD = '9a97f6c54ec638111ce55cd36581b3c192f15207'
MODULES = ('vorbis_repair/setup.c', 'vorbis_repair/output.c',
           'vorbis_repair/COPYING', 'vorbis_repair_abi.h')
TOOL_SHA = {
    'python':'0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14',
    'compiler':'9a96e8e77c263d4f7f16c084e8a2dfe89dfa8598c31fd3f9b152db35ccbb2a74',
    'nm':'3962a7c898d8dc17c3f0e846ee3b5f5e5c00c2c395d2ae7084dfe57464f75d4e',
    'cmake':'392ab4d6c3c91543fd297ed6c7e7354bf62edcd26fdf2706ad8613ad620cc45e',
    'ninja':'68865c3276d449d746cea5065fdec2baf755d7813e161ab04205b0907b2629b8',
    'qemu':'a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b',
    'rom':'0de1e65020e803bea0d7443dca149d61895e01fca3bb9c82d073234eebd73f99'}


def need(condition, message):
    if not condition: raise RuntimeError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()



def rate_variant(data, mode, control):
    """Only one reviewed guard may be restored, only from the complete fix."""
    signed = {
        'validity': b'  if(vi->rate<1)goto err_out;',
        'policy': b'  if(vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;'}
    unsigned = {
        'validity': b'  if((uint32_t)vi->rate<1)goto err_out;',
        'policy': b'  if((uint32_t)vi->rate>=64000 || ci->blocksizes[1]>4096)goto err_out;'}
    need(mode in ('baseline','acceptance','limited') and
         (control is None or (mode=='acceptance' and control=='signed-validity') or
          (mode=='limited' and control=='signed-policy')), 'Incompatible mode/control')
    expected, forbidden = (signed,unsigned) if mode=='baseline' else (unsigned,signed)
    need(all(data.count(expected[key])==1 and data.count(forbidden[key])==0 for key in signed),
         'Baseline needs both exact signed guards; acceptance/limited/control needs both complete unsigned fixes')
    result = data
    if control:
        key = {'signed-validity':'validity','signed-policy':'policy'}[control]
        result = data.replace(unsigned[key],signed[key],1)
        need(result.replace(signed[key],unsigned[key],1)==data, 'Control changed more than one exact guard')
    return result

def main():
    repo = next(p for p in Path(__file__).resolve().parents if (p / 'idf/esp32c3-oled-native/main/vorbis_repair/setup.c').is_file())
    nearest = lambda rel: next((p / rel for p in (repo, *repo.parents) if (p / rel).exists()), None)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=('baseline','acceptance','limited'), required=True)
    parser.add_argument('--control', choices=('signed-validity','signed-policy'))
    parser.add_argument('--candidate', type=Path, default=repo / 'idf/esp32c3-oled-native/main')
    parser.add_argument('--idf', type=Path, default=nearest('.idf/v6.1-9a97f6c54ec6'))
    parser.add_argument('--idf-tools', type=Path)
    parser.add_argument('--codec', type=Path)
    parser.add_argument('--qemu', type=Path, default=shutil.which('qemu-system-riscv32.exe') or 'C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
    parser.add_argument('--powershell', type=Path, default=shutil.which('pwsh.exe') or shutil.which('pwsh'))
    args = parser.parse_args()
    if args.control and not ((args.mode=='acceptance' and args.control=='signed-validity') or
                             (args.mode=='limited' and args.control=='signed-policy')):
        parser.error('signed-validity requires acceptance; signed-policy requires limited')
    if sys.platform != 'win32': parser.error('Pinned Windows SDK launcher required')
    if not all((args.idf, args.qemu, args.powershell)): parser.error('Specify missing SDK/QEMU/PowerShell paths')
    out, candidate, sdk = args.output.resolve(), args.candidate.resolve(), args.idf.resolve()
    tools = (args.idf_tools or sdk.parent / 'tools-v6.1').resolve()
    codec = (args.codec or sdk.parent / 'esp-adf-libs/esp_audio_codec').resolve()
    py, ps, qemu = tools / 'python_env/idf6.1_py3.12_env/Scripts/python.exe', args.powershell.resolve(), args.qemu.resolve()
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    taskkill = Path(os.environ['SystemRoot']) / 'System32/taskkill.exe'
    rom = qemu.parent.parent / 'share/qemu'
    cc_expected = tools/'tools/riscv32-esp-elf/esp-15.2.0_20251204/riscv32-esp-elf/bin/riscv32-esp-elf-gcc.exe'
    selected_tools = dict(python=py,compiler=cc_expected,nm=cc_expected.with_name('riscv32-esp-elf-nm.exe'),
        cmake=tools/'tools/cmake/4.0.3/bin/cmake.exe',ninja=tools/'tools/ninja/1.12.1/ninja.exe',
        qemu=qemu,rom=rom/'esp32c3-rom.bin')
    # The sibling layout permits review from this scratch prep before promotion.
    harness = Path(__file__).resolve().parent / 'target/c3_vorbis_uint32_rate_qemu'
    fixture = repo/'tests/target/c3_vorbis_format_qemu/main/fixture.h'
    audit = repo/'.build/cyd-vorbis-public-header-audit-01'
    protected = (candidate, harness, audit, sdk, tools, codec, ps.parent, qemu.parent, rom)
    if (not candidate.is_relative_to(repo) or not out.is_relative_to(repo / '.build') or out == repo / '.build'
        or out.exists() or any((p / 'report.json').is_file() for p in out.parents if p != repo)
        or any(out == p or out.is_relative_to(p) or p.is_relative_to(out) for p in protected)):
        parser.error('Use a fresh .build campaign, separate from source/runtime directories and previous reports')
    required = [py, ps, qemu, git, taskkill, rom/'esp32c3-rom.bin',
                sdk/'export.ps1', sdk/'tools/idf.py', *[candidate/x for x in MODULES],
                *[codec/'lib/esp32c3'/x for x in ARCHIVES], fixture,
                *[audit/name for name in HEADER_AUDIT], harness/'main/main.c',
                Path(__file__).with_name('rate_protocol.py'), *selected_tools.values()]
    if any(not p.is_file() for p in required): parser.error('Missing required pinned source/runtime')
    out.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, completed=False, rate_acceptance_qualified=False, limited_policy_qualified=False,
                  regression_reproduced=False, control_effective=False, full_G6_qualified=False, physical_device=False,
                  production_radio_integration=False,mode=args.mode,control=args.control,platform='esp32c3',
                  sdk_revision=SDK_HEAD,elf_machine=243,coordinator_core=0,worker_core=0,commands=[],inputs={},tools={})
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
        row = dict(name=name, argv=list(map(str,argv)), cwd=str(cwd or out), state='starting', exit_status=None, timed_out=False, interrupted=False)
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
                    row.update(state='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed', error=repr(exc),
                               timed_out=isinstance(exc,subprocess.TimeoutExpired), interrupted=isinstance(exc,KeyboardInterrupt))
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
        freeze(Path(__file__).with_name('rate_protocol.py'), Path('helpers/rate_protocol.py'))
        freeze(fixture, Path('canonical-fixture.h'))
        for name in HEADER_AUDIT: freeze(audit/name,Path('header-audit')/name)
        for name in ('tools/cmake/version.cmake','tools/cmake/toolchain-esp32c3.cmake','tools/cmake/toolchain.cmake','export.ps1','tools/idf.py'):
            freeze(sdk/name,Path('sdk')/name)
        for path in sorted((codec/'include').rglob('*.h')): freeze(path,Path('codec/include')/path.relative_to(codec/'include'))
        for name in ('CMakeLists.txt','Kconfig'):
            if (codec/name).is_file(): freeze(codec/name,Path('codec')/name)
        for path in (Path(sys.executable),py,ps,qemu,git,taskkill,rom/'esp32c3-rom.bin',
                     *[codec/'lib/esp32c3'/x for x in ARCHIVES]): report['tools'][str(path.resolve())] = sha(path)
        need({name:sha(codec/'lib/esp32c3'/name) for name in ARCHIVES} == ARCHIVES, 'Wrong installed vendor archives')
        need(all(sha(path)==TOOL_SHA[name] for name,path in selected_tools.items()),'Wrong independently pinned C3 tool/ROM')
        report['tools'].update({str(path.resolve()):TOOL_SHA[name] for name,path in selected_tools.items()})
        need(sha(fixture)==sha(out/'sources/project/main/fixture.h')==FIXTURE_SHA, 'Wrong exact canonical raw fixture')
        need(sha(out/'sources/project/main/main.c')==CALLER_SHA and
             sha(out/'sources/helpers/rate_protocol.py')==PROTOCOL_SHA and
             sha(out/'sources/project/raw-enable.cmake')==RAW_HELPER_SHA, 'Wrong reviewed caller/protocol/raw helper')
        for name,digest in HEADER_AUDIT.items():
            need(sha(out/'sources/header-audit'/name)==digest, 'Wrong pinned public-header source audit '+name)
        report['raw_fixture'] = dict(sha256=FIXTURE_SHA, header_audit=HEADER_AUDIT,
            scope='Existing public raw fixture and source audit; no new host/target qualification implied')
        shutil.copytree(out/'sources/candidate',out/'variant')
        original_setup = (out/'sources/candidate/vorbis_repair/setup.c').read_bytes()
        selected_setup = rate_variant(original_setup,args.mode,args.control)
        (out/'variant/vorbis_repair/setup.c').write_bytes(selected_setup)
        report['guard_variant'] = dict(original_sha256=hashlib.sha256(original_setup).hexdigest(),
            selected_sha256=hashlib.sha256(selected_setup).hexdigest(), control=args.control,
            changed=(selected_setup!=original_setup))
        # The standalone C3 project includes its raw helper; no application helper/hooks are copied.
        report['variant_sources'] = {str(p.relative_to(out)):sha(p) for p in (out/'variant').rglob('*') if p.is_file()}
        need(execute('sdk-head',[git,'-C',sdk,'rev-parse','HEAD']).strip() == SDK_HEAD,'Wrong SDK commit')
        need(not execute('sdk-clean',[git,'-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'Dirty SDK')
        current(); save()
        try:
            execute('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1',
                '-Campaign',out,'-Repository',repo,'-SdkDirectory',sdk,'-ToolsDirectory',tools,'-CodecDirectory',codec,
                '-RateMode',args.mode],1200)
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
        need(Path(before['compiler']).resolve()==cc.resolve()==cc_expected.resolve() and
             Path(before['nm']).resolve()==nm.resolve(),'Actual RV32 compiler differs from pinned/pre-build identity')
        for name in ('cmake','ninja'):
            need(Path(before[name]).resolve()==selected_tools[name].resolve() and
                 before[name+'_sha256']==sha(selected_tools[name])==TOOL_SHA[name],'Activated C3 build tool differs '+name)
        for path,key in ((cc,'compiler_sha256'),(nm,'nm_sha256')):
            need(sha(path) == before[key], 'Compiler tool changed during build')
            report['tools'][str(path)] = before[key]
        report['build_outputs'] = {str(p.relative_to(out)):sha(p) for p in (elf,app,out/'sdkconfig',build/'compile_commands.json',out/'compiler-environment.json',out/'compiler-identity-before-build.json')}
        report['build_outputs'].update({name:row['sha256'] for name,row in report['sdk_build_logs'].items()})
        need(struct.unpack_from('<H',elf.read_bytes(),18)[0] == 243,'Wrong ELF machine')
        rows = json.loads((build/'compile_commands.json').read_text())
        row_source = lambda row: (Path(row['directory'])/row['file']).resolve()
        caller_rows = [row for row in rows if row_source(row).is_relative_to(out/'sources/project')]
        need(len(caller_rows)==1 and row_source(caller_rows[0])==out/'sources/project/main/main.c',
             'Actual compiled project must contain only the frozen public caller')
        actual = [row for row in rows if row_source(row).is_relative_to(out/'variant')]
        need({row_source(r) for r in actual} == {out/'variant'/name for name in MODULES[:2]} and len(actual) == 2,'Actual bridge compile rows')
        setup = next(r for r in actual if Path(r['file']).name == 'setup.c')
        argv,cwd,original,generated = macro_command(setup,cc,out/'variant/vorbis_repair/setup.c')
        need(len(generated)==2 and sum(arg.startswith('@') for arg in original)==1,
             'Require actual preserved four-line RV32 @cflags and picolibc.specs')
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
        if args.mode=='limited':
            need(re.search(r'^#define LIMIT_TO_64kHz 1$',macros,re.M),'Actual optional 64kHz setup policy missing')
        else:
            need(not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M),'Optional 64kHz limit unexpectedly active')
        for name,value in (('RATE_EXPECT_UNSIGNED_REJECTION',int(args.mode=='baseline')),
                           ('RATE_LIMITED_POLICY',int(args.mode=='limited')),
                           ('CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ',160)):
            need(re.search(r'^#define '+name+' '+str(value)+'$',macros,re.M),'Actual setup mode/config macro '+name)
        for name,value in (('CONFIG_FREERTOS_UNICORE',1),('__riscv_xlen',32),('__SIZEOF_LONG__',4),('__SIZEOF_POINTER__',4)):
            need(re.search(r'^#define '+name+' '+str(value)+'$',macros,re.M),'Actual C3 setup ABI/config macro '+name)
        for name in ('CONFIG_IDF_TARGET_ESP32C3','ESP_PLATFORM'):
            need(re.search(r'^#define '+name+r' 1$',macros,re.M),'Expected setup compile context '+name)
        symbols = execute('symbols',[nm,'-n','-S',elf])
        for symbol in ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_open','esp_vorbis_dec_decode'):
            need(re.search(r'\b'+symbol+'$',symbols,re.M),'Missing symbol '+symbol)
        recipe = json.loads((build/'flasher_args.json').read_text())
        settings = recipe.get('flash_settings',{})
        need(recipe.get('extra_esptool_args',{}).get('chip')=='esp32c3','Wrong isolated flash recipe chip')
        need({k:settings.get(k) for k in ('flash_mode','flash_size','flash_freq')} ==
             {'flash_mode':'dio','flash_size':'4MB','flash_freq':'40m'}, 'Unexpected isolated flash settings')
        expected_flash = {0x0:build/'bootloader/bootloader.bin',
                          0x8000:build/'partition_table/partition-table.bin',0x10000:app}
        need(len(recipe['flash_files']) == 3 and
             {int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()} ==
             {offset:path.resolve() for offset,path in expected_flash.items()}, 'Unexpected isolated flash offsets/files')
        report['build_outputs']['build/flasher_args.json'] = sha(build/'flasher_args.json')
        flash = out/'qemu-flash.bin'
        merge = [py,'-m','esptool','--chip','esp32c3','merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,name in sorted(recipe['flash_files'].items(),key=lambda x:int(x[0],0)):
            path = (build/name).resolve(); need(path.is_relative_to(build),'Flash recipe escaped build')
            report['build_outputs'][str(path.relative_to(out))] = sha(path)
            merge += [offset,path]
        execute('merge',merge+['--pad-to-size','4MB'])
        report['build_outputs'][str(flash.relative_to(out))] = sha(flash)
        current(); save()
        log = execute('qemu',[qemu,'-audiodev','none,id=quiet','-M','esp32c3,audiodev=quiet','-smp','1','-L',rom,
            '-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none',
            '-drive','file='+str(flash)+',if=mtd,format=raw'],300)
        stderr = (out/'qemu.stderr.log').read_text(errors='replace')
        qemu_row = report['commands'][-1]
        report['observed'] = validate_log(log+'\n'+stderr,args.mode,args.control,
            returncode=qemu_row['exit_status'],timed_out=qemu_row['timed_out'],interrupted=qemu_row['interrupted'])
        expected_failure = {'signed-validity':'legal_unsigned_rate_open_required',
                            'signed-policy':'limited_rate_rejection_required'}.get(args.control)
        need(report['observed']['exact_failure']==expected_failure, 'Wrong control/normal terminal protocol')
        need(execute('sdk-head-after',[git,'-C',sdk,'rev-parse','HEAD']).strip() == SDK_HEAD,'SDK identity changed')
        need(not execute('sdk-clean-after',[git,'-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK changed')
        current()
        need(all(sha(out/path) == value for path,value in report['build_outputs'].items()),'Build/execution bytes changed')
        report.update(completed=True,passed=True,control_effective=args.control is not None,
            rate_acceptance_qualified=args.mode=='acceptance' and args.control is None,
            limited_policy_qualified=args.mode=='limited' and args.control is None,
            regression_reproduced=args.mode=='baseline' and args.control is None,
            result='CONTROL_EFFECTIVE' if args.control else {'baseline':'REGRESSION_REPRODUCED',
                'acceptance':'UINT32_RATE_ACCEPTED','limited':'LIMITED_POLICY_VERIFIED'}[args.mode])
        save()
        print(json.dumps({k:report[k] for k in ('result','passed','rate_acceptance_qualified',
            'limited_policy_qualified','regression_reproduced','control_effective','observed')}))
        return 0
    except BaseException as exc:
        report.update(passed=False,completed=False,rate_acceptance_qualified=False,limited_policy_qualified=False,
                      regression_reproduced=False,control_effective=False,
                      result='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'NONPASS',error=repr(exc))
        save()
        raise


if __name__ == '__main__': sys.exit(main())

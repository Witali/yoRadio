"""Finite floor1 setup/PCM regression on the ESP32 or ESP32-C3 public raw API.

This isolated fixture does not run the radio, Ogg adapter, deferred work or a
physical board. Each control removes just one guard from a frozen setup copy.
"""
import argparse
import hashlib
import importlib.util
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
PROJECT = ROOT / 'tests/target/vorbis_floor1_positions_qemu'
SDK_HEAD = {'esp32': '7101770dc6db2667b3c477cc31365dd1acd6db4e',
            'esp32c3': '9a97f6c54ec638111ce55cd36581b3c192f15207'}
CODEC_SHA = {'esp32': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
             'esp32c3': '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909'}
COUNT_GUARD = b'  if(count>63)goto err_out;'
UNIQUE_GUARD = b'''  for(j=1;j<info->posts;j++)
    if(info->postlist[(unsigned char)info->forward_index[j-1]]==
       info->postlist[(unsigned char)info->forward_index[j]])goto err_out;'''


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def need(ok, reason):
    if not ok: raise ValueError(reason)


def registration_decode_control(data):
    """Redirect only the frozen public registration table's decode callback."""
    anchor = b'.decode = esp_vorbis_dec_decode,'
    declaration = b'esp_audio_err_t __wrap_esp_vorbis_dec_register(void) {'
    need(data.count(anchor) == data.count(declaration) == 1, 'registration control anchors changed')
    newline = b'\r\n' if b'\r\n' in data else b'\n'
    prototype = (b'extern esp_audio_err_t __real_esp_vorbis_dec_decode(void *, esp_audio_dec_in_raw_t *, '
                 b'esp_audio_dec_out_frame_t *, esp_audio_dec_info_t *);' + newline)
    return data.replace(anchor, b'.decode = __real_esp_vorbis_dec_decode,', 1).replace(
        declaration, prototype + declaration, 1)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', choices=['esp32', 'esp32c3'], required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--idf', type=Path, required=True)
    p.add_argument('--idf-tools', type=Path, required=True)
    p.add_argument('--codec', type=Path, required=True)
    p.add_argument('--powershell', type=Path, required=True)
    p.add_argument('--qemu', type=Path, required=True)
    p.add_argument('--rom', type=Path, required=True)
    p.add_argument('--corpus', type=Path, required=True)
    p.add_argument('--corpus-kind', choices=['positions', 'slopes'], default='positions')
    p.add_argument('--renderer', choices=['on', 'off'], default='off')
    p.add_argument('--dispatch', choices=['direct', 'registered'], default='direct')
    p.add_argument('--reset-cycles', action='store_true')
    p.add_argument('--control', choices=['count', 'unique', 'old-tail', 'register-open', 'register-decode', 'reset-skip'])
    a = p.parse_args()
    need(a.control!='old-tail' or a.renderer=='on','old-tail requires the explicit renderer path')
    need(a.corpus_kind!='slopes' or a.renderer=='on','per-case slope packets require renderer harness')
    binding_control = a.control in ('register-open', 'register-decode')
    need(not binding_control or a.dispatch == 'registered', 'registration controls require registered dispatch')
    need(a.dispatch != 'registered' or (a.renderer == 'on' and a.control in (None, 'register-open', 'register-decode', 'reset-skip')),
         'registered dispatch requires renderer and its own binding controls')
    need(not a.reset_cycles or (a.dispatch == 'registered' and a.control in (None, 'reset-skip')),
         'reset cycles require registered dispatch without binding controls')
    need(a.control != 'reset-skip' or a.reset_cycles, 'reset-skip requires reset cycles')
    out = a.output.resolve()
    runtimes = [getattr(a, name).resolve() for name in ('idf','idf_tools','codec','powershell','qemu','rom')]
    need(out.is_relative_to(ROOT/'.build') and out != ROOT/'.build' and not out.exists(), 'fresh .build output required')
    need(not any(out.is_relative_to(x) or x.is_relative_to(out) for x in runtimes), 'output/runtime overlap')
    need(not any((x/'report.json').is_file() for x in out.parents if x != ROOT), 'nested campaign')
    sdk, tools, codec, ps, qemu, rom = runtimes
    py = tools / ('python_env/idf6.0_py3.12_env/Scripts/python.exe' if a.target=='esp32'
                  else 'python_env/idf6.1_py3.12_env/Scripts/python.exe')
    need(all(x.is_file() for x in (py,ps,qemu,sdk/'export.ps1')), 'missing runtime')
    out.mkdir(parents=True)
    r = dict(completed=False,passed=False,control_effective=False,target=a.target,control=a.control,
        renderer=a.renderer,dispatch=a.dispatch,corpus_kind=a.corpus_kind,target_capture_completed=False,numerical_reference_qualified=False,
        registered_callbacks_qualified=False,reset_cycles=a.reset_cycles,raw_reset_behavior_qualified=False,
        full_G6_qualified=False,production_radio_integration=False,physical_device=False,
        commands=[],inputs={},tools={},build_outputs={},scope=__doc__)
    env = os.environ.copy()
    env.update(PYTHONUTF8='1',PYTHONIOENCODING='utf-8',PYTHONDONTWRITEBYTECODE='1',GIT_OPTIONAL_LOCKS='0')
    def save(): (out/'report.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf-8')
    def freeze(path, relative):
        dst=out/'sources'/relative;dst.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,dst)
        r['inputs'][str(path.resolve())]=dict(snapshot=str(dst.relative_to(out)),sha256=sha(path))
    def current():
        need(all(sha(path)==row['sha256']==sha(out/row['snapshot']) for path,row in r['inputs'].items()),'input changed')
        need(all(sha(path)==digest for path,digest in r['tools'].items()),'selected tool changed')
    def run(name, argv, timeout=60):
        argv=list(map(str,argv));row=dict(name=name,argv=argv,cwd=str(out),state='starting')
        r['commands'].append(row);save();started=time.monotonic();child=None
        so=out/(name+'.stdout.log');se=out/(name+'.stderr.log')
        try:
            with so.open('xb') as stdout,se.open('xb') as stderr:
                child=subprocess.Popen(argv,cwd=out,stdout=stdout,stderr=stderr,stdin=subprocess.DEVNULL,
                    env=env,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                row['pid']=child.pid;save()
                child.wait(timeout=timeout)
                row.update(state='complete',exit_status=child.returncode)
        finally:
            if child is not None and child.poll() is None:
                row['state']='forced_stop_nonpass'
                try:
                    if os.name=='nt':
                        stopped=subprocess.run(['taskkill.exe','/PID',str(child.pid),'/T','/F'],
                            capture_output=True,timeout=15,creationflags=subprocess.CREATE_NO_WINDOW)
                        row['tree_stop_returncode']=stopped.returncode
                except Exception as exc:
                    row['tree_stop_error']=repr(exc)
                finally:
                    if child.poll() is None: child.kill()
                    child.wait(timeout=15)
            row.update(elapsed_seconds=time.monotonic()-started,
                stdout_sha256=sha(so) if so.exists() else None,stderr_sha256=sha(se) if se.exists() else None)
            save()
        need(row.get('state')=='complete' and row.get('exit_status')==0,name+' terminal failure')
        return so.read_text(encoding='utf-8',errors='replace').replace('\r\n','\n')
    def finish(result):
        need(run('sdk-head-after',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD[a.target],
             'SDK identity changed')
        need(not run('sdk-clean-after',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),
             'SDK modified after')
        current()
        need(all(sha(out/path)==digest for group in ('variant_sources','project_sources','build_outputs')
                 for path,digest in r[group].items()),'execution bytes changed')
        r.update(completed=True,result=result,
            limitations='Finite raw fixture only. Renderer captures need independent numerical comparison; no shared-renderer unchanged vendor oracle. Optional reset cycles cover sequential public raw handle reuse only; default registered dispatch does not call reset. No full callback ABI, Ogg, QMP EOF, allocation-failure, radio, hardware or full G6 qualification; selected files/tools, not full dependency closure.')
        save();print(json.dumps({k:r[k] for k in ('completed','passed','control_effective','result')}));return 0
    try:
        save()
        git=shutil.which('git');need(git,'git missing')
        r['tools']={str(path):sha(path) for path in (py,ps,qemu,Path(git))}
        need(run('sdk-head',[git,'-c','core.longpaths=true','-C',sdk,'rev-parse','HEAD']).strip()==SDK_HEAD[a.target],'SDK identity')
        need(not run('sdk-clean',[git,'-c','core.longpaths=true','-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK modified')
        archive=codec/'lib'/a.target/'libesp_audio_codec.a'
        need(sha(archive)==CODEC_SHA[a.target],'codec identity');r['tools'][str(archive)]=sha(archive)
        rom_files=list(rom.glob('esp32-v3-rom*.bin')) if a.target=='esp32' else list(rom.glob('esp32c3-rom*.bin'))
        need(rom_files,'ROMs missing')
        for path in rom_files:r['tools'][str(path)]=sha(path)
        source_main=ROOT/('idf/esp32-cyd2usb-native/main' if a.target=='esp32' else 'idf/esp32c3-oled-native/main')
        for relative in ('vorbis_repair/setup.c','vorbis_repair/output.c','vorbis_repair/floor1_render.h','vorbis_repair_abi.h','vorbis_repair/COPYING'):
            freeze(source_main/relative,Path('main')/relative)
        freeze(Path(__file__),Path('runner.py'))
        if a.dispatch == 'registered':
            freeze(ROOT/'tests/vorbis_registered_protocol.py',Path('registered_protocol.py'))
        if a.reset_cycles:
            freeze(ROOT/'tests/vorbis_reset_protocol.py',Path('reset_protocol.py'))
        freeze(ROOT/'tests/vorbis_format_corpus/generate_floor1_positions.py',Path('generator.py'))
        generator=ROOT/('tests/vorbis_format_corpus/generate_floor1_'+a.corpus_kind+'.py')
        if a.corpus_kind=='slopes':freeze(generator,Path('slopes-generator.py'))
        freeze(ROOT/'tests/vorbis_block_matrix/generate_minimal.py',Path('generate_minimal.py'))
        for path in PROJECT.rglob('*'):
            if path.is_file():freeze(path,Path('project')/path.relative_to(PROJECT))
        defaults=ROOT/('tests/target/cyd_vorbis_qemu/sdkconfig.defaults' if a.target=='esp32'
                      else 'tests/target/c3_vorbis_format_qemu/sdkconfig.defaults')
        freeze(defaults,Path('sdkconfig.defaults'))
        freeze(ROOT/'tests/target/cyd_vorbis_qemu/partitions.csv',Path('partitions.csv'))
        for path in codec.rglob('*.h'):freeze(path,Path('codec')/path.relative_to(codec))
        corpus=a.corpus.resolve();manifest=json.loads((corpus/'manifest.json').read_text())
        need(manifest['generator_sha256']==sha(generator),'corpus generator identity')
        need(all((corpus/row['path']).is_relative_to(corpus) and
                 (corpus/row['path']).stat().st_size==row['bytes'] and
                 sha(corpus/row['path'])==row['sha256'] for row in manifest['files']),'corpus body identity')
        matrix=json.loads((corpus/'matrix.json').read_text())
        need(len(matrix['cases'])==14 and [x['expected_valid'] for x in matrix['cases']]==[True]*8+[False]*6,'exact corpus validity matrix')
        need(manifest['helper']['sha256']==sha(ROOT/'tests/vorbis_block_matrix/generate_minimal.py'),'corpus helper identity')
        spec=importlib.util.spec_from_file_location('floor1_fixture_identity',generator)
        generated=importlib.util.module_from_spec(spec);spec.loader.exec_module(generated)
        expected=generated.payloads()
        need({x.relative_to(corpus).as_posix() for x in corpus.rglob('*') if x.is_file()}==set(expected),'exact generated corpus inventory')
        need(all((corpus/name).read_bytes()==data for name,data in expected.items()),'corpus/header bytes differ from canonical construction')
        # Every corpus body is frozen; construction and reference outcomes remain separate.
        for path in corpus.rglob('*'):
            if path.is_file():freeze(path,Path('corpus')/path.relative_to(corpus))
        r['corpus_manifest_sha256']=sha(corpus/'manifest.json')
        shutil.copytree(out/'sources/main',out/'variant')
        setup=out/'variant/vorbis_repair/setup.c'
        if a.control in ('count','unique'):
            data=setup.read_bytes();guard=COUNT_GUARD if a.control=='count' else UNIQUE_GUARD
            # Preserve each platform's existing line endings outside the selected guard.
            if guard not in data:guard=guard.replace(b'\n',b'\r\n')
            need(data.count(guard)==1,'control anchor changed');setup.write_bytes(data.replace(guard,b'',1))
        elif a.control=='old-tail':
            header=out/'variant/vorbis_repair/floor1_render.h'
            data=header.read_bytes()
            anchor=b'out[j] = repair_floor1_multiply(out[j], repair_floor1_from_db[ly]);'
            need(data.count(anchor)==1,'old-tail anchor changed')
            # Defined product bits reproduce old int32 multiplication without C overflow.
            header.write_bytes(data.replace(anchor,b'out[j] = repair_floor1_multiply(out[j], ly * 32768);',1))
        elif a.control == 'register-decode':
            setup.write_bytes(registration_decode_control(setup.read_bytes()))
        r['variant_sources']={str(x.relative_to(out)):sha(x) for x in (out/'variant').rglob('*') if x.is_file()}
        shutil.copytree(out/'sources/project',out/'project')
        shutil.copyfile(out/'sources/sdkconfig.defaults',out/'project/sdkconfig.defaults')
        shutil.copyfile(out/'sources/partitions.csv',out/'project/partitions.csv')
        shutil.copyfile(out/'sources/corpus/fixture.h',out/'project/main/fixture.h')
        if a.control == 'reset-skip':
            reset_header = out/'project/main/reset_cycles.h'
            data = reset_header.read_bytes()
            anchor = b'#define VORBIS_RESET_SKIP_CONTROL 0'
            need(data.count(anchor) == 1, 'single frozen reset-skip control anchor')
            reset_header.write_bytes(data.replace(anchor, b'#define VORBIS_RESET_SKIP_CONTROL 1', 1))
        r['project_sources']={str(x.relative_to(out)):sha(x) for x in (out/'project').rglob('*') if x.is_file()}
        current();save()
        run('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1',
            '-Campaign',out,'-SdkDirectory',sdk,'-ToolsDirectory',tools,'-CodecDirectory',codec,
            '-PythonExecutable',py,'-Target',a.target,'-Renderer',a.renderer,
            '-Dispatch',a.dispatch,'-BindingControl',a.control if binding_control else 'none',
            '-ResetCycles','on' if a.reset_cycles else 'off'],1200)
        for path in (out/'sdk-build.stdout.log',out/'sdk-build.stderr.log'):
            need(path.is_file(),'missing actual SDK child log')
            r['build_outputs'][str(path.relative_to(out))]=sha(path)
        current()
        build=out/'build';desc=json.loads((build/'project_description.json').read_text())
        elf=build/desc['app_elf'];app=build/desc['app_bin'];machine=struct.unpack_from('<H',elf.read_bytes(),18)[0]
        need(machine==(94 if a.target=='esp32' else 243),'ELF architecture');r['elf_machine']=machine
        cc=Path(desc['c_compiler']);nm=cc.with_name(cc.name.replace('gcc','nm'))
        for tool in (cc,nm):r['tools'][str(tool)]=sha(tool)
        symbols=run('symbols',[nm,'-n','-S',elf])
        required_symbols=['__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_decode']
        required_symbols+=['__wrap_floor1_inverse2'] if a.renderer=='on' else ['esp_vorbis_dec_open']
        if a.dispatch == 'registered':
            required_symbols += ['esp_vorbis_dec_register' if a.control == 'register-open' else '__wrap_esp_vorbis_dec_register', 'esp_audio_dec_get_ops',
                                 'esp_audio_dec_open', 'esp_audio_dec_process', 'esp_audio_dec_get_info',
                                 'esp_audio_dec_close', 'esp_audio_dec_unregister']
        if a.reset_cycles:
            required_symbols += ['esp_audio_dec_reset']
        for symbol in required_symbols:
            need(re.search(r'\b'+symbol+'$',symbols,re.M),'missing symbol '+symbol)
        rows=json.loads((build/'compile_commands.json').read_text())
        r['compile_rows']=[x for x in rows if Path(x['file']).resolve().is_relative_to(out/'variant')]
        need(len(r['compile_rows'])==2,'canonical setup/output rows')
        if a.dispatch == 'registered':
            r['harness_compile_rows'] = [row for row in rows if Path(row['file']).resolve() == out/'project/main/registered.c']
            need(len(r['harness_compile_rows']) == 1, 'actual registered fixture compilation')
            if a.reset_cycles:
                need(re.search(r'(?:^|\s)-DVORBIS_RESET_CYCLES=1(?:\s|$)',
                               r['harness_compile_rows'][0]['command']), 'actual reset-enabled fixture compilation')
            for path in (build/'compile_commands.json', build/'project_description.json'):
                r['build_outputs'][str(path.relative_to(out))] = sha(path)
        config=(out/'sdkconfig').read_text()
        need(('CONFIG_FREERTOS_UNICORE=y' in config)==(a.target=='esp32c3'),'core configuration')
        recipe=json.loads((build/'flasher_args.json').read_text())
        need(recipe['flash_settings']==dict(flash_mode='dio',flash_size='4MB',flash_freq='40m'),'flash settings')
        files={int(offset,0):(build/name).resolve() for offset,name in recipe['flash_files'].items()}
        need(set(files)==({0x1000,0x8000,0x10000} if a.target=='esp32' else {0,0x8000,0x10000}),'flash offsets')
        need(all(x.is_relative_to(build) for x in files.values()),'flash recipe escapes build')
        flash=out/'qemu-flash.bin'
        argv=[py,'-m','esptool','--chip',a.target,'merge-bin','--output',flash,'--flash-mode','dio','--flash-size','4MB','--flash-freq','40m']
        for offset,path in sorted(files.items()):argv.extend([hex(offset),path])
        run('merge',argv+['--pad-to-size','4MB'])
        for path in (elf,app,flash,out/'sdkconfig',build/'flasher_args.json',*files.values()):r['build_outputs'][str(path.relative_to(out))]=sha(path)
        save()
        qargs=[qemu,'-M',a.target,'-smp','2' if a.target=='esp32' else '1','-L',rom,
            '-display','none','-monitor','none','-serial','stdio','-no-reboot','-snapshot','-nic','none',
            '-drive','file='+str(flash)+',if=mtd,format=raw']
        log=run('qemu',qargs,180);stderr=(out/'qemu.stderr.log').read_text(errors='replace')
        need(not re.search(r'Guru Meditation|abort\(\)|Backtrace:|assert failed|CORRUPT HEAP',log+stderr),'target panic')
        failures=re.findall(r'^FLOOR1_FAILURE case=(\d+) reason=(\S+)$',log,re.M)
        summaries=re.findall(r'^FLOOR1_COMPLETE accepted=(\d+) rejected=(\d+) packets=(\d+) pcm=(\d+) core=(\d+)$',log,re.M)
        need(log.count('FLOOR1_CONTROLLED_STOP')==1,'controlled terminal marker')
        core=1 if a.target=='esp32' else 0
        need(re.findall(r'^FLOOR1_START coordinator=0 decoder=(\d+)$',log,re.M)==[str(core)],'task cores')
        if a.reset_cycles:
            from vorbis_reset_protocol import validate_log as validate_reset
            qemu_command = next(row for row in r['commands'] if row['name'] == 'qemu')
            r['observed_reset'] = validate_reset(log, matrix, a.target, a.control,
                returncode=qemu_command['exit_status'], timed_out=qemu_command['state'] != 'complete',
                interrupted=qemu_command['state'] == 'interrupted')
            if a.control == 'reset-skip':
                need(failures == [('0', 'reset_primer_empty')], 'exact reset-skip behavioral witness')
                r['observed'] = dict(exact_failure=failures[0])
                r['control_effective'] = True
                return finish('RESET_SKIP_CONTROL_EFFECTIVE')
            r['raw_reset_behavior_qualified'] = True
        if a.dispatch == 'registered':
            from vorbis_registered_protocol import validate_log
            qemu_command = next(row for row in r['commands'] if row['name'] == 'qemu')
            r['observed_registry'] = validate_log(log, matrix, a.target, a.control,
                returncode=qemu_command['exit_status'], timed_out=qemu_command['state'] != 'complete',
                interrupted=qemu_command['state'] == 'interrupted')
            if binding_control:
                r['observed'] = dict(exact_failure=failures[0])
                r['control_effective'] = True
                return finish('REGISTER_BINDING_CONTROL_EFFECTIVE')
            r['registered_callbacks_qualified'] = True
        marker='renderer_repair=1' if a.renderer=='on' else 'original_exact=1'
        accepted_rows=re.findall(r'^FLOOR1_ACCEPT case=(\d+) name=(\S+) packets=14 pcm=28160 '+marker+r' core=(\d+)$',log,re.M)
        rejected_rows=re.findall(r'^FLOOR1_REJECT case=(\d+) name=(\S+) result=-1 handle=0 core=(\d+)$',log,re.M)
        need(accepted_rows==[(str(i),matrix['cases'][i]['id'],str(core)) for i in range(8)],'complete accepted prefix')
        opens=re.findall(r'^FLOOR1_OPEN case=(\d+) result=(-?\d+) handle=([01])$',log,re.M)
        rejected_end=12 if a.control=='count' else 8 if a.control=='unique' else 14
        need(rejected_rows==[(str(i),matrix['cases'][i]['id'],str(core)) for i in range(8,rejected_end)],'exact rejected prefix')
        expected_opens=[(str(i),'0','1') for i in range(8)]+[(str(i),'-1','0') for i in range(8,rejected_end)]
        if a.control in ('count','unique'):expected_opens.append((str(rejected_end),'0','1'))
        need(opens==expected_opens,'exact setup open outcomes; only accepted malformed setup qualifies a control')
        pcm_rows=re.findall(r'^FLOOR1_PCM case=(\d+) packet=(\d+) consumed=(\d+) bytes=(\d+) hex=([0-9a-f]*)$',log,re.M)
        need(len(pcm_rows)==112 and [(int(x[0]),int(x[1])) for x in pcm_rows]==[(c,p) for c in range(8) for p in range(14)],'complete ordered PCM prefix')
        need(all(int(x[2])==matrix['cases'][int(x[0])]['offsets'][int(x[1])+1]-matrix['cases'][int(x[0])]['offsets'][int(x[1])] and
                 int(x[3])==matrix['cases'][int(x[0])]['expected_packet_bytes'][int(x[1])] and len(bytes.fromhex(x[4]))==int(x[3])
                 for x in pcm_rows),'per-packet consumption and PCM bytes')
        (out/'pcm').mkdir()
        for c in range(8):
            data=b''.join(bytes.fromhex(x[4]) for x in pcm_rows[c*14:(c+1)*14])
            need(len(data)==28160 and any(data),'full nonzero PCM capture')
            (out/'pcm'/f'{c}.s16le').write_bytes(data)
        r['observed']=dict(accepted=accepted_rows,rejected=rejected_rows,opens=opens,
            pcm={str(x.relative_to(out)):sha(x) for x in (out/'pcm').iterdir()})
        if a.control in ('count','unique'):
            expected='12' if a.control=='count' else '8'
            need(failures==[(expected,'invalid_setup_rejected')] and not summaries,'exact guard control')
            r['observed']['exact_failure']=failures[0];r['control_effective']=True
        else:
            need(not failures and summaries==[('8','6','112','225280',str(core))],'complete finite matrix')
            r['observed']['summary']=summaries[0]
            r['target_capture_completed']=True
            r['passed']=a.renderer=='off'
        return finish('CONTROL_EFFECTIVE' if a.control in ('count','unique') else
                      'RENDER_CAPTURED' if a.renderer=='on' else 'FINITE_MATRIX_PASSED')
    except BaseException as exc:
        r.update(completed=False,passed=False,control_effective=False,
                 registered_callbacks_qualified=False,raw_reset_behavior_qualified=False,
                 target_capture_completed=False,result='NONPASS',error=repr(exc));save();raise


if __name__=='__main__':sys.exit(main())

"""Capture a checked-only public raw Vorbis corpus; independent PCM comparison remains separate."""
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
from protocol import load_contract, validate_log
from reference_binding import verify as verify_source_binding

ARCHIVES = {'libesp_audio_codec.a': '92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58',
            'libesp_audio_simple_dec.a': 'ca3b95dfc83b6984ae91c509bf859e4334fcc74654d2fe8b68bfc34f06126cc6'}
MATRIX_INPUTS = (
    ('__FIRST_MATRIX_PATH__', '__FIRST_MATRIX_SHA__'),
    ('__SECOND_MATRIX_PATH__', '__SECOND_MATRIX_SHA__'))
REFERENCE_PROOFS = __REFERENCE_PROOFS__
CONTRACT_ID = '__CONTRACT_ID__'
CONTRACT_FILE_SHA = '__CONTRACT_FILE_SHA__'
DATA_HEADER_SHA = '__DATA_HEADER_SHA__'
# Filled only with the independent caller owner's final reviewed source bytes.
CALLER_SHA = '37eaeb25a272ceadaafe36d6309449d31895b7019523333ed0e4c48226d0d065'
PROTOCOL_SHA = '547655c4fa31a100f29f52b3a142a54442578393b860723b2b1147732578700e'
CASE_HEADER_SHA = '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'
RAW_HELPER_SHA = '5731c1022c8f6ecdb6c03d833f9d2208c675b22e20f71ac7327b3941af8822c5'
SOURCE_MAP_SHA = '__SOURCE_MAP_SHA__'
REFERENCE_BINDING_SHA = '__REFERENCE_BINDING_SHA__'
REFERENCE_HELPER_SHA = '__REFERENCE_HELPER_SHA__'
SOURCE_PINS_SHA = '__SOURCE_PINS_SHA__'
SDK_HEAD = '7101770dc6db2667b3c477cc31365dd1acd6db4e'
MODULES = ('vorbis_repair/setup.c', 'vorbis_repair/output.c',
           'vorbis_repair/COPYING', 'vorbis_repair_abi.h', 'compat/vorbis_repair/enable.cmake')


def need(condition, message):
    if not condition: raise RuntimeError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()



def main():
    repo = next(p for p in Path(__file__).resolve().parents if (p / 'idf/esp32-cyd2usb-native/main/vorbis_repair/setup.c').is_file())
    nearest = lambda rel: next((p / rel for p in (repo, *repo.parents) if (p / rel).exists()), None)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--contract-sha256', required=True)
    parser.add_argument('--data-header', type=Path, required=True)
    parser.add_argument('--data-sha256', required=True)
    parser.add_argument('--candidate', type=Path, default=repo / 'idf/esp32-cyd2usb-native/main')
    parser.add_argument('--idf', type=Path, default=nearest('.idf/v6.0.2'))
    parser.add_argument('--idf-tools', type=Path)
    parser.add_argument('--codec', type=Path)
    parser.add_argument('--qemu', type=Path, default=shutil.which('qemu-system-xtensa.exe'))
    parser.add_argument('--powershell', type=Path, default=shutil.which('pwsh.exe') or shutil.which('pwsh'))
    args = parser.parse_args()
    if not all(re.fullmatch(r'[0-9a-f]{64}',value) for value in (args.contract_sha256,args.data_sha256)):
        parser.error('Require independently reviewed lowercase contract/data SHA256 values')
    if args.contract_sha256!=CONTRACT_FILE_SHA or args.data_sha256!=DATA_HEADER_SHA:
        parser.error('Require the unchanged reviewed12-case contract and materialized data header')
    if not all((CALLER_SHA,PROTOCOL_SHA,CASE_HEADER_SHA)):
        parser.error('Source proposal incomplete: independent caller source freeze is required')
    if sys.platform != 'win32': parser.error('Pinned Windows SDK launcher required')
    if not all((args.idf, args.qemu, args.powershell)): parser.error('Specify missing SDK/QEMU/PowerShell paths')
    out, candidate, sdk = args.output.resolve(), args.candidate.resolve(), args.idf.resolve()
    need(sha(candidate/'vorbis_repair/setup.c') == '6b36d56bf0800cae21e071e194353993237f6bfd93f6ea73ea28c4c480b4903c',
         'Exact reviewed CYD public setup source required')
    tools = (args.idf_tools or sdk.parent / 'tools-v6.0.2').resolve()
    codec = (args.codec or sdk.parent / 'esp-adf-libs/esp_audio_codec').resolve()
    py, ps, qemu = tools / 'python_env/idf6.0_py3.12_env/Scripts/python.exe', args.powershell.resolve(), args.qemu.resolve()
    git = Path(shutil.which('git.exe') or shutil.which('git') or '')
    taskkill = Path(os.environ['SystemRoot']) / 'System32/taskkill.exe'
    rom = qemu.parent.parent / 'pc-bios'
    # The sibling layout permits review from this scratch prep before promotion.
    harness = Path(__file__).resolve().parent / 'target/cyd_vorbis_wide_width12_qemu'
    source_map_path = Path(__file__).with_name('source-map.json')
    binding_path = Path(__file__).with_name('reference-binding12.json')
    binding_helper = Path(__file__).with_name('reference_binding.py')
    source_pins_path = Path(__file__).with_name('source-pins.json')
    contract_path, data_header = args.contract.resolve(), args.data_header.resolve()
    protected = (candidate,harness,contract_path,data_header,source_map_path,binding_path,binding_helper,source_pins_path,sdk,tools,codec,ps.parent,qemu.parent,rom,
                 repo/'.build/cyd-vorbis-wide-width-host-01', repo/'__QUALIFICATION_ROOT__')
    if (not all(path.is_relative_to(repo) for path in (candidate,contract_path,data_header))
        or not out.is_relative_to(repo / '.build') or out == repo / '.build'
        or out.exists() or any((p / 'report.json').is_file() for p in out.parents if p != repo)
        or any(out == p or out.is_relative_to(p) or p.is_relative_to(out) for p in protected)):
        parser.error('Use a fresh .build campaign, separate from source/runtime directories and previous reports')
    required = [py, ps, qemu, git, taskkill, rom/'esp32-v3-rom.bin', rom/'esp32-v3-rom-app.bin',
                sdk/'export.ps1', sdk/'tools/idf.py', *[candidate/x for x in MODULES],
                *[codec/'lib/esp32'/x for x in ARCHIVES], contract_path, data_header,
                *[repo/name for name in REFERENCE_PROOFS], source_map_path, binding_path, binding_helper, source_pins_path, harness/'main/main.c',
                harness/'main/corpus_case.h', Path(__file__).with_name('protocol.py')]
    if any(not p.is_file() for p in required): parser.error('Missing required pinned source/runtime')
    out.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, completed=False, target_capture_completed=False,checked_decode_completed=False,
                  vendor_checked_pcm_equal=False,vendor_comparison_available=False,
                  independent_reference_compared=False,numeric_reference_qualified=False,format_corpus_qualified=False,
                  full_G6_qualified=False,physical_device=False,production_radio_integration=False,
                  commands=[],inputs={},tools={},observed_pcm=[])
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
            if path.is_file():
                relative = path.relative_to(harness)
                freeze(path,Path('templates/data.h') if relative==Path('main/data.h') else Path('project')/relative)
        need(sha(contract_path)==args.contract_sha256 and sha(data_header)==args.data_sha256,
             'Reviewed contract/data header SHA mismatch')
        freeze(contract_path,Path('corpus/contract.json'))
        freeze(data_header,Path('project/main/data.h'))
        need(sha(out/'sources/corpus/contract.json')==args.contract_sha256 and
             sha(out/'sources/project/main/data.h')==args.data_sha256,'Frozen reviewed contract/data bytes differ')
        contract = json.loads((out/'sources/corpus/contract.json').read_text())
        expected_manifests = [dict(path=str((repo/name).resolve()),sha256=digest) for name,digest in MATRIX_INPUTS]
        need(contract['manifest_inputs']==expected_manifests and load_contract(expected_manifests)==contract,
             'Contract differs from exact unchanged original4 plus additive8 width-control source matrices/raw packets')
        model = contract['model']
        need(contract['contract_sha256']==CONTRACT_ID and len(model['cases'])==__CASE_COUNT__ and
             model['total_packets']==__TOTAL_PACKETS__ and model['total_pcm']==__TOTAL_PCM__ and model['case_mask']==__CASE_MASK__,
             'All12 corpus contract shape/identity required')
        for fact in contract['source_facts']:
            path = Path(fact['path']).resolve()
            need(path.is_relative_to(repo) and sha(path)==fact['sha256'] and path.stat().st_size==fact['bytes'],
                 'Actual raw source fact differs')
            freeze(path,Path('corpus/raw')/path.relative_to(repo))
            need(sha(out/'sources/corpus/raw'/path.relative_to(repo))==fact['sha256'],
                 'Frozen raw source fact differs')
        for name,digest in REFERENCE_PROOFS.items():
            need(sha(repo/name)==digest,'Pinned terminal host reference proof differs '+name)
            freeze(repo/name,Path('reference')/Path(name).relative_to('.build'))
            need(sha(out/'sources/reference'/Path(name).relative_to('.build'))==digest,'Frozen reference proof differs')
        freeze(Path(__file__).resolve(), Path('helpers/run.py'))
        freeze(Path(__file__).with_name('windows_compile_command.py'), Path('helpers/windows_compile_command.py'))
        freeze(Path(__file__).with_name('protocol.py'), Path('helpers/protocol.py'))
        for name in ('tools/cmake/version.cmake','tools/cmake/toolchain-esp32.cmake','tools/cmake/toolchain.cmake','export.ps1','tools/idf.py'):
            freeze(sdk/name,Path('sdk')/name)
        for path in sorted((codec/'include').rglob('*.h')): freeze(path,Path('codec/include')/path.relative_to(codec/'include'))
        for name in ('CMakeLists.txt','Kconfig'):
            if (codec/name).is_file(): freeze(codec/name,Path('codec')/name)
        for path in (Path(sys.executable),py,ps,qemu,git,taskkill,rom/'esp32-v3-rom.bin',rom/'esp32-v3-rom-app.bin',
                     *[codec/'lib/esp32'/x for x in ARCHIVES]): report['tools'][str(path.resolve())] = sha(path)
        need({name:sha(codec/'lib/esp32'/name) for name in ARCHIVES} == ARCHIVES, 'Wrong installed vendor archives')
        need(sha(out/'sources/project/main/main.c')==CALLER_SHA and
             sha(out/'sources/project/main/corpus_case.h')==CASE_HEADER_SHA and
             sha(out/'sources/helpers/protocol.py')==PROTOCOL_SHA and
             sha(out/'sources/project/raw-enable.cmake')==RAW_HELPER_SHA,'Wrong reviewed caller/protocol/raw helper')
        need(sha(source_map_path)==SOURCE_MAP_SHA and sha(binding_path)==REFERENCE_BINDING_SHA and
             sha(binding_helper)==REFERENCE_HELPER_SHA and sha(source_pins_path)==SOURCE_PINS_SHA,'WideWidth12 source binding/helper pins')
        freeze(source_map_path,Path('corpus/source-map.json'))
        freeze(binding_path,Path('reference/reference-binding12.json'))
        freeze(binding_helper,Path('helpers/reference_binding.py'))
        freeze(source_pins_path,Path('helpers/source-pins.json'))
        mapping = json.loads(source_map_path.read_bytes())
        binding = json.loads(binding_path.read_bytes())
        verify_source_binding(contract,mapping,binding)
        need(len(binding['cases'])==__CASE_COUNT__ and binding['new_reference_commands_executed'] is False and
             binding['aggregate_reference_campaign_exists'] is False and binding['dual_reference_passed'] is False,
             'Exact coherent12 source bindings required; historical dual NONPASS remains')
        for item in binding['proof_facts']:
            path = Path(item['path'])
            need(path.is_relative_to(repo) and sha(path)==item['sha256'] and path.stat().st_size==item['bytes'],
                 'Actual original/copied raw or frozen historical reference fact differs')
            freeze(path,Path('reference-facts')/path.relative_to(repo))
        report['corpus'] = dict(contract_sha256=CONTRACT_ID,contract_file_sha256=args.contract_sha256,
            data_header_sha256=args.data_sha256,manifest_sha256=model['manifest_sha256'],cases=__CASE_COUNT__,packets=__TOTAL_PACKETS__,
            expected_pcm=__TOTAL_PCM__,source_map_sha256=SOURCE_MAP_SHA,reference_binding_sha256=REFERENCE_BINDING_SHA,
            source_reference_scopes=binding['source_scopes'],new_reference_commands_executed=False,
            aggregate_reference_campaign_exists=False,dual_reference_passed=False)
        shutil.copytree(out/'sources/candidate',out/'variant')
        shutil.copyfile(out/'sources/project/raw-enable.cmake',out/'variant/compat/vorbis_repair/enable.cmake')
        report['variant_sources'] = {str(p.relative_to(out)):sha(p) for p in (out/'variant').rglob('*') if p.is_file()}
        need(execute('sdk-head',[git,'-C',sdk,'rev-parse','HEAD']).strip() == SDK_HEAD,'Wrong SDK commit')
        need(not execute('sdk-clean',[git,'-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'Dirty SDK')
        current(); save()
        try:
            execute('build',[ps,'-NoProfile','-NonInteractive','-File',out/'sources/project/sdk-build.ps1',
                '-Campaign',out,'-Repository',repo,'-SdkDirectory',sdk,'-ToolsDirectory',tools,'-CodecDirectory',codec],1200)
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
        caller_rows = [row for row in rows if row_source(row).is_relative_to(out/'sources/project')]
        need(len(caller_rows)==1 and row_source(caller_rows[0])==out/'sources/project/main/main.c',
             'Actual compiled project must contain only the frozen public caller')
        actual = [row for row in rows if row_source(row).is_relative_to(out/'variant')]
        need({row_source(r) for r in actual} == {out/'variant'/name for name in MODULES[:2]} and len(actual) == 2,'Actual bridge compile rows')
        setup = next(r for r in actual if Path(r['file']).name == 'setup.c')
        argv,cwd,original,generated = macro_command(setup,cc,out/'variant/vorbis_repair/setup.c')
        need(len(generated)==2 and sum(arg.startswith('@') for arg in original)==1,
             'Require actual preserved six-line generated @cflags and picolibc.specs')
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
        need(not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M),'Corpus requires unrestricted actual setup context')
        need(re.search(r'^#define CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ 240$',macros,re.M),'Actual setup must consume240MHz config')
        need(not re.search(r'^#define CONFIG_FREERTOS_UNICORE\b',macros,re.M),'Actual setup must consume two-core config')
        for name in ('CONFIG_IDF_TARGET_ESP32','CONFIG_YORADIO_VORBIS_REPAIR'):
            need(re.search(r'^#define '+name+r' 1$',macros,re.M),'Expected setup compile context '+name)
        symbols = execute('symbols',[nm,'-n','-S',elf])
        for symbol in ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_decode'):
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
            '-drive','file='+str(flash)+',if=mtd,format=raw'],300)
        stderr = (out/'qemu.stderr.log').read_text(errors='replace')
        qemu_row = report['commands'][-1]
        observed = validate_log(log+'\n'+stderr,contract,
            returncode=qemu_row['exit_status'],timed_out=qemu_row['timed_out'],interrupted=qemu_row['interrupted'],
            manifest_hashes=[sha(repo/name) for name,digest in MATRIX_INPUTS])
        captured = observed.pop('case_pcm')
        need(len(captured)==__CASE_COUNT__ and observed['protocol_lines']==__PROTOCOL_EVENTS__ and observed['cases']==__CASE_COUNT__ and observed['decoded_packets']==__TOTAL_PACKETS__ and observed['pcm']==__TOTAL_PCM__ and
             observed['checked_decode_completed'] is True and observed['vendor_checked_pcm_equal'] is False and
             observed['vendor_comparison_available'] is False and observed['independent_reference_compared'] is False,
             'All12 actual PCM observations required')
        pcm_directory = out/'observed-pcm'
        pcm_directory.mkdir()
        report['observed'] = observed
        for index,(item,case) in enumerate(zip(captured,model['cases'])):
            pcm = item['pcm']
            offsets = [0]
            for count in case['pcm']: offsets.append(offsets[-1]+count)
            need(item['case']==index and item['id']==case['id'] and type(pcm) is bytes and
                 len(pcm)==case['total_pcm'] and hashlib.sha256(pcm).hexdigest()==item['sha256'] and
                 item['packet_offsets']==offsets,'Actual case PCM byte/hash/offset binding')
            path = pcm_directory/f"{index:02d}-{case['id']}.s16le"
            with path.open('xb') as stream: stream.write(pcm)
            need(path.read_bytes()==pcm,'PCM persistence changed bytes')
            report['observed_pcm'].append(dict(case=index,id=case['id'],path=str(path.relative_to(out)),
                source_index=case['source_index'],reference_id=binding['cases'][index]['original_reference_id'],
                reference_scope=binding['cases'][index]['original_group'],
                reference_qualification_sha256=binding['cases'][index]['qualification_sha256'],
                bytes=len(pcm),sha256=sha(path),packet_offsets=offsets))
            save()  # Only metadata enters JSON. Raw public output remains in separate files.
        need(execute('sdk-head-after',[git,'-C',sdk,'rev-parse','HEAD']).strip() == SDK_HEAD,'SDK identity changed')
        need(not execute('sdk-clean-after',[git,'-C',sdk,'status','--porcelain','--untracked-files=no']).strip(),'SDK changed')
        current()
        need(all(sha(out/path) == value for path,value in report['build_outputs'].items()),'Build/execution bytes changed')
        need(len(report['observed_pcm'])==__CASE_COUNT__ and sum(row['bytes'] for row in report['observed_pcm'])==__TOTAL_PCM__ and
             set(pcm_directory.iterdir())=={out/row['path'] for row in report['observed_pcm']} and
             all(sha(out/row['path'])==row['sha256'] and (out/row['path']).stat().st_size==row['bytes']
                 for row in report['observed_pcm']),'Observed PCM file set changed/incomplete')
        report.update(completed=True,target_capture_completed=True,checked_decode_completed=True,
                      vendor_checked_pcm_equal=False,vendor_comparison_available=False,result='CHECKED_CORPUS_PCM_CAPTURED')
        save()
        print(json.dumps({k:report[k] for k in ('result','completed','target_capture_completed',
            'checked_decode_completed','vendor_checked_pcm_equal','vendor_comparison_available','independent_reference_compared','numeric_reference_qualified',
            'format_corpus_qualified','observed_pcm')}))
        return 0
    except BaseException as exc:
        report.update(passed=False,completed=False,target_capture_completed=False,checked_decode_completed=False,
                      vendor_checked_pcm_equal=False,vendor_comparison_available=False,
                      independent_reference_compared=False,numeric_reference_qualified=False,format_corpus_qualified=False,
                      result='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'NONPASS',error=repr(exc))
        save()
        raise


if __name__ == '__main__': sys.exit(main())

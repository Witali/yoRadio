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
from reference_binding02 import verify as verify_source_binding

ARCHIVES = {'libesp_audio_codec.a': '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909', 'libesp_audio_simple_dec.a': '232650ec81ae5e10ecbe1b2c86de2d1adf8f1b793f5ef343241c6e510db3e71f'}
MATRIX_INPUTS = (
    ('.build/cyd-vorbis-format-expanded25-prep-01/inputs/books16/matrix.json',
     '16b087d4462f2ef481cb479f3730dc24f17bf195be83812d68819831799c7239'),
    ('.build/cyd-vorbis-floor0-prep-01/generated01/matrix.json',
     'aa1231b8813ac193767c85a2ef339a2da36af52f2af157a16cda9f3d2d438f07'))
REFERENCE_PROOFS = {'.build/cyd-vorbis-format-corpus-qualified-01/qualification.json': 'd269d71ab02568fcb549c5abf39e4daf8ffcd082b1ede3c259351615768e02b0', '.build/cyd-vorbis-format-corpus-host-01/report.json': 'eaf3d8033406d5c6844f5dd6e3f42b26195d6e03b3293c27ea03353d6ca0ae29', '.build/cyd-vorbis-format-corpus-host-01-command.json': '799bb892e5b12e0ccc13fc02607aefe49527f51568d0aecfe8a98ac88c492773', '.build/cyd-vorbis-map2-regression-qualified-01/qualification.json': 'bb78d2478d6e2a191202098443f5d224cda37fe7c44b33052de005ce10662bc4', '.build/cyd-vorbis-map2-regression-host-01/report.json': '5701c50e49118123e059c2a48a152f1fdd2f9def3bffb84053759b51c9a8df88', '.build/cyd-vorbis-map2-regression-host-01-command.json': '829899ce49f473962c2abc838fb9a1c6a6be14cf1ec007e66c464f7cff09bc2f'}
CONTRACT_ID = '660ac01523d3336ccb103f1443e51b870edf1a3d3f50321c5666969b1da634cc'
CONTRACT_FILE_SHA = '717ec7f703295f9851fd9241877cf249ff6f203c436786300a36247f2805218d'
DATA_HEADER_SHA = '4cba27844a6a9018c103e06ac8e505590ae0549ef2dfe6238ebd933b4dfb9757'
# Filled only with the independent caller owner's final reviewed source bytes.
CALLER_SHA = '8c6aff4bb6d43c6b034db799477653e89fff4c9e65ac0b805d99f257672e9f03'
PROTOCOL_SHA = '961b0050f5881e5000116cbf7a598a122407420b0a52da0805d060c7b7e3f7ba'
CASE_HEADER_SHA = '91a040d89f3bc2b7740fa2f175f36d64cebcd92653cd4c2014149bbb11219be3'
RAW_HELPER_SHA = 'b0dfa7bf6c8a01e3082ce58495ae7f0b3c565873d2054b5c2fa427bdb9871b5e'
SOURCE_MAP_SHA = '63f0eccf40044fabcc8d2b31c0a2094859258856e4948fe53a57cf8a9358301a'
REFERENCE_BINDING_SHA = '802d0fe193991cfc40d388ad27594d8d0b632112f223cb6dee68226c07585f2c'
REFERENCE_HELPER_SHA = '3961e32fc5abb5a883260b2932a570908367c46ad2058a210a123336db7638ce'
SDK_HEAD = '9a97f6c54ec638111ce55cd36581b3c192f15207'
MODULES = ('vorbis_repair/setup.c', 'vorbis_repair/output.c', 'vorbis_repair/COPYING', 'vorbis_repair_abi.h')


TOOL_SHA = {'python': '0b471133e110cfb53a061cad528ce8e517d7b9ac41a0a396c39ad795a487fc14', 'compiler': '9a96e8e77c263d4f7f16c084e8a2dfe89dfa8598c31fd3f9b152db35ccbb2a74', 'nm': '3962a7c898d8dc17c3f0e846ee3b5f5e5c00c2c395d2ae7084dfe57464f75d4e', 'cmake': '392ab4d6c3c91543fd297ed6c7e7354bf62edcd26fdf2706ad8613ad620cc45e', 'ninja': '68865c3276d449d746cea5065fdec2baf755d7813e161ab04205b0907b2629b8', 'qemu': 'a74f3324430b306618aa88a52649dbb93c32eac6d0b87926d335754346abbf0b', 'rom': '0de1e65020e803bea0d7443dca149d61895e01fca3bb9c82d073234eebd73f99'}

def need(condition, message):
    if not condition: raise RuntimeError(message)


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()



def main():
    repo = next(p for p in Path(__file__).resolve().parents if (p / 'idf/esp32c3-oled-native/main/vorbis_repair/setup.c').is_file())
    nearest = lambda rel: next((p / rel for p in (repo, *repo.parents) if (p / rel).exists()), None)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--contract', type=Path, required=True)
    parser.add_argument('--contract-sha256', required=True)
    parser.add_argument('--data-header', type=Path, required=True)
    parser.add_argument('--data-sha256', required=True)
    parser.add_argument('--candidate', type=Path, default=repo / 'idf/esp32c3-oled-native/main')
    parser.add_argument('--idf', type=Path, default=nearest('.idf/v6.1-9a97f6c54ec6'))
    parser.add_argument('--idf-tools', type=Path)
    parser.add_argument('--codec', type=Path)
    parser.add_argument('--qemu', type=Path, default=shutil.which('qemu-system-riscv32.exe') or 'C:/Work/QEMU-ESP32/bin/qemu-system-riscv32.exe')
    parser.add_argument('--powershell', type=Path, default=shutil.which('pwsh.exe') or shutil.which('pwsh'))
    args = parser.parse_args()
    if not all(re.fullmatch(r'[0-9a-f]{64}',value) for value in (args.contract_sha256,args.data_sha256)):
        parser.error('Require independently reviewed lowercase contract/data SHA256 values')
    if args.contract_sha256!=CONTRACT_FILE_SHA or args.data_sha256!=DATA_HEADER_SHA:
        parser.error('Require the unchanged reviewed25-case contract and materialized data header')
    if not all((CALLER_SHA,PROTOCOL_SHA,CASE_HEADER_SHA)):
        parser.error('Source proposal incomplete: independent caller source freeze is required')
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
    harness = Path(__file__).resolve().parent / 'target/c3_vorbis_format_expanded25_qemu'
    source_map_path = Path(__file__).with_name('source-map.json')
    binding_path = Path(__file__).with_name('reference-binding02.json')
    binding_helper = Path(__file__).with_name('reference_binding02.py')
    contract_path, data_header = args.contract.resolve(), args.data_header.resolve()
    protected = (candidate,harness,contract_path,data_header,source_map_path,binding_path,binding_helper,sdk,tools,codec,ps.parent,qemu.parent,rom,
                 repo/'.build/cyd-vorbis-format-corpus-qualified-01',repo/'.build/cyd-vorbis-format-corpus-host-01',
                 repo/'.build/cyd-vorbis-map2-regression-qualified-01',repo/'.build/cyd-vorbis-map2-regression-host-01')
    if (not all(path.is_relative_to(repo) for path in (candidate,contract_path,data_header))
        or not out.is_relative_to(repo / '.build') or out == repo / '.build'
        or out.exists() or any((p / 'report.json').is_file() for p in out.parents if p != repo)
        or any(out == p or out.is_relative_to(p) or p.is_relative_to(out) for p in protected)):
        parser.error('Use a fresh .build campaign, separate from source/runtime directories and previous reports')
    required = [py, ps, qemu, git, taskkill, rom/'esp32c3-rom.bin',
                sdk/'export.ps1', sdk/'tools/idf.py', *[candidate/x for x in MODULES],
                *[codec/'lib/esp32c3'/x for x in ARCHIVES], contract_path, data_header,
                *[repo/name for name in REFERENCE_PROOFS], source_map_path, binding_path, binding_helper, harness/'main/main.c',
                harness/'main/corpus_case.h', Path(__file__).with_name('protocol.py'), *selected_tools.values()]
    if any(not p.is_file() for p in required): parser.error('Missing required pinned source/runtime')
    out.mkdir(parents=True, exist_ok=False)
    report = dict(passed=False, completed=False, target_capture_completed=False,checked_decode_completed=False,
                  vendor_checked_pcm_equal=False,vendor_comparison_available=False,
                  independent_reference_compared=False,numeric_reference_qualified=False,format_corpus_qualified=False,
                  full_G6_qualified=False,physical_device=False,production_radio_integration=False,
                  platform='esp32c3',sdk_revision=SDK_HEAD,elf_machine=243,coordinator_core=0,worker_core=0,
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
             'Contract differs from exact merged books16 plus original floor9 source matrices/raw packets')
        model = contract['model']
        need(contract['contract_sha256']==CONTRACT_ID and len(model['cases'])==25 and
             model['total_packets']==350 and model['total_pcm']==623360 and model['case_mask']==33554431,
             'All25 corpus contract shape/identity required')
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
        need(sha(out/'sources/project/main/main.c')==CALLER_SHA and
             sha(out/'sources/project/main/corpus_case.h')==CASE_HEADER_SHA and
             sha(out/'sources/helpers/protocol.py')==PROTOCOL_SHA and
             sha(out/'sources/project/raw-enable.cmake')==RAW_HELPER_SHA,'Wrong reviewed caller/protocol/raw helper')
        need(sha(source_map_path)==SOURCE_MAP_SHA and sha(binding_path)==REFERENCE_BINDING_SHA and
             sha(binding_helper)==REFERENCE_HELPER_SHA,'Expanded25 source binding/helper pins')
        freeze(source_map_path,Path('corpus/source-map.json'))
        freeze(binding_path,Path('reference/reference-binding02.json'))
        freeze(binding_helper,Path('helpers/reference_binding02.py'))
        mapping = json.loads(source_map_path.read_bytes())
        binding = json.loads(binding_path.read_bytes())
        verify_source_binding(contract,mapping,binding)
        need(len(binding['cases'])==25 and binding['new_reference_commands_executed'] is False and
             binding['aggregate_reference_campaign_exists'] is False and binding['dual_reference_passed'] is False,
             'Exact coherent25 source bindings required; historical dual NONPASS remains')
        for item in binding['proof_facts']:
            path = Path(item['path'])
            need(path.is_relative_to(repo) and sha(path)==item['sha256'] and path.stat().st_size==item['bytes'],
                 'Actual original/copied raw or frozen historical reference fact differs')
            freeze(path,Path('reference-facts')/path.relative_to(repo))
        report['corpus'] = dict(contract_sha256=CONTRACT_ID,contract_file_sha256=args.contract_sha256,
            data_header_sha256=args.data_sha256,manifest_sha256=model['manifest_sha256'],cases=25,packets=350,
            expected_pcm=623360,source_map_sha256=SOURCE_MAP_SHA,reference_binding_sha256=REFERENCE_BINDING_SHA,
            source_reference_scopes=binding['source_scopes'],new_reference_commands_executed=False,
            aggregate_reference_campaign_exists=False,dual_reference_passed=False)
        shutil.copytree(out/'sources/candidate',out/'variant')
        report['selected_setup_sha256'] = sha(out/'variant/vorbis_repair/setup.c')
        # Standalone C3 project owns its raw helper; no full-application hook is copied.
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
        need(not re.search(r'^#define LIMIT_TO_64kHz\b',macros,re.M),'Corpus requires unrestricted actual setup context')
        for name,value in (('CONFIG_ESP_DEFAULT_CPU_FREQ_MHZ',160),
                           ('CONFIG_FREERTOS_UNICORE',1),('__riscv_xlen',32),
                           ('__SIZEOF_LONG__',4),('__SIZEOF_POINTER__',4)):
            need(re.search(r'^#define '+name+' '+str(value)+'$',macros,re.M),'Actual C3 setup ABI/config macro '+name)
        for name in ('CONFIG_IDF_TARGET_ESP32C3','ESP_PLATFORM'):
            need(re.search(r'^#define '+name+r' 1$',macros,re.M),'Expected setup compile context '+name)
        symbols = execute('symbols',[nm,'-n','-S',elf])
        for symbol in ('__wrap_esp_vorbis_dec_open','__wrap_esp_vorbis_dec_decode','esp_vorbis_dec_decode'):
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
        observed = validate_log(log+'\n'+stderr,contract,
            returncode=qemu_row['exit_status'],timed_out=qemu_row['timed_out'],interrupted=qemu_row['interrupted'],
            manifest_hashes=[sha(repo/name) for name,digest in MATRIX_INPUTS])
        captured = observed.pop('case_pcm')
        need(len(captured)==25 and observed['protocol_lines']==778 and observed['cases']==25 and observed['decoded_packets']==350 and observed['pcm']==623360 and
             observed['checked_decode_completed'] is True and observed['vendor_checked_pcm_equal'] is False and
             observed['vendor_comparison_available'] is False and observed['independent_reference_compared'] is False,
             'All25 actual PCM observations required')
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
        need(len(report['observed_pcm'])==25 and sum(row['bytes'] for row in report['observed_pcm'])==623360 and
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

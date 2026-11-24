"""Prepare a public static-evidence package. Dry-run is the default.

Standard-library only. No compilers, QEMU, network, Git/index operations or
runtime-result inputs. --write is an explicit later operation for root.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT=next(p for p in Path(__file__).resolve().parents
          if (p/'idf/esp32-cyd2usb-native').is_dir() and (p/'.git').exists())
BASE=ROOT/'.build/cnortc24'
TARGET=ROOT/'tests/results/cyd-openeth-no-rtc-20261124/sdk'
SOURCE='7595a79958b8a2ef56babb24c43259fcf536b6dd'
HOME=re.compile(rb'(?i)([A-Z]:[\\/]+Users[\\/]+|/home/|/Users/)([^\\/\s\x00"\x27:]+)')

def identity(body): return dict(bytes=len(body),sha256=hashlib.sha256(body).hexdigest())
def pin(path): return identity(Path(path).read_bytes())
def load(path): return json.loads(Path(path).read_bytes())
def encoded(value): return (json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode()
def label(path):
    path=Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
def require(value,message):
    if not value: raise RuntimeError(message)

class Elf32:
    """Minimal read-only ELF32/LE section and symbol reader."""
    def __init__(self,path):
        self.body=Path(path).read_bytes()
        require(self.body[:6]==b'\x7fELF\x01\x01','Expected frozen ELF32 little-endian input')
        h=struct.unpack_from('<16sHHIIIIIHHHHHH',self.body)
        require(h[2]==94,'Expected Xtensa ELF')
        self.headers=[struct.unpack_from('<IIIIIIIIII',self.body,h[6]+i*h[11]) for i in range(h[12])]
        strings=self.data(self.headers[h[13]])
        self.names={strings[s[0]:].split(b'\0',1)[0].decode():s for s in self.headers}
    def data(self,header): return self.body[header[4]:header[4]+header[5]]
    def section(self,name): return self.data(self.names[name])
    def symbols(self):
        table=self.names['.symtab']; names=self.data(self.headers[table[6]]); result=set()
        for offset in range(table[4],table[4]+table[5],table[9]):
            index=struct.unpack_from('<I',self.body,offset)[0]
            result.add(names[index:].split(b'\0',1)[0].decode())
        return result

class Package:
    def __init__(self): self.files={}; self.originals={}; self.redactions=[]; self.logs_checked=0
    def original(self,path):
        path=Path(path).resolve(); body=path.read_bytes(); key=label(path)
        value=identity(body)
        require(key not in self.originals or self.originals[key]==value,'Original changed during planning: '+key)
        self.originals[key]=value
        return body
    def put(self,name,body):
        require(name not in self.files,'Duplicate public destination: '+name)
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Unsafe destination')
        require(Path(name).suffix in ('.json','.md','.py','.log'),'Public binary/raw credential output forbidden')
        if Path(name).suffix!='.log':
            require(not any(m.group(2).lower() not in (b'build',b'public',b'default') for m in HOME.finditer(body)),
                    'Non-log personal home path requires separate review: '+name)
        require(b'\0' not in body,'Unexpected binary content: '+name)
        self.files[name]=body
    def copy(self,source,name):
        body=self.original(source)
        if name.endswith('.log'):
            self.logs_checked+=1; replacements=0
            def replace(match):
                nonlocal replacements
                if match.group(2).lower() in (b'build',b'public',b'default'): return match.group()
                replacements+=1; return match.group(1)+b'build'
            public=HOME.sub(replace,body)
            if replacements:
                self.redactions.append(dict(file=name,source=label(source),original=identity(body),published=identity(public),
                    replacements=replacements,category='personal-home-path',placeholder='build',original_retained_locally=True))
            body=public
        self.put(name,body)
    def json(self,name,value): self.put(name,encoded(value))

def catalog(values): return Counter((x['file'],x['severity'],x['message'],x['check']) for x in values)

def plan():
    package=Package()
    summary=load(BASE/'results.json'); prep=load(BASE/'preflight.json')
    require(summary['state']=='TERMINAL_PASS' and summary['source_commit']==SOURCE,'Frozen static summary mismatch')
    require(summary['native_run'] is False and summary['focused_whole_tu_checks']==6,'Static-only scope mismatch')
    require(prep['source_commit']==SOURCE and prep['rtc_probe_enabled'],'Probe/source mismatch')
    package.copy(BASE/'results.json','summary.json')
    inputs=dict(source_commit=SOURCE,project_source_reference=summary['project_source_reference'],scope='Selected immutable static inputs, not full compiler dependency closure or runtime qualification.',
        preflight=pin(BASE/'preflight.json'),results=pin(BASE/'results.json'),packager=pin(Path(__file__)),
        qemu=prep['qemu'],generator=prep['generator'],generated_sdk_source_sha256=prep['generated_sha256'],
        sdk_repositories=prep['sdk_repositories'],protected_inputs=[],recipes={},profiles=[])
    package.original(BASE/'preflight.json')
    for item in prep['protected']:
        path=ROOT/item['path']
        require(identity(package.original(path))==dict(bytes=item['bytes'],sha256=item['sha256']),'Protected input changed: '+label(path))
        inputs['protected_inputs'].append(item)
    recipes=('common.py','prepare.py','create-execute.py','execute.py','qualify-first-attempt.py',
             'qualify-header-corrected-attempt.py','qualify.py','continue-qualification.py',
             'continue-reviewed-qualification.py','summarize-results.py','PLAN.md')
    for name in recipes:
        path=BASE/name; inputs['recipes'][name]=pin(path); package.copy(path,'recipes/'+name)
    for backend in ('legacy','pdm','continuous'):
        directory=BASE/backend; baseline=load(directory/'baseline.json'); qualified=load(directory/'qualification.json')
        rtc_on=ROOT/baseline['rtc_on']; prefix=backend+'/'
        require(qualified['passed'] and qualified['source_commit']==SOURCE,'Qualification mismatch: '+backend)
        package.original(directory/'baseline.json')
        comparison=load(directory/'object-comparison.json')
        require(comparison['objects']==qualified['object_count'],'Object count mismatch')
        changed={item['path']:item['after'] for item in comparison['changed_raw']}
        for item in baseline['objects']:
            require(pin(ROOT/item['path'])==changed.get(item['path'],item['identity']),'Compiled object changed: '+item['path'])
        for unit in baseline['project_units']:
            require(pin(ROOT/unit['file'])==dict(bytes=unit['bytes'],sha256=unit['sha256']),'Project source changed: '+unit['file'])
        before_path=rtc_on/'compiled/config/sdkconfig.json'; after_path=directory/'compiled/config/sdkconfig.json'
        clang_path=directory/'compiled/clang/config/sdkconfig.json'
        before,after=load(before_path),load(after_path)
        delta={k for k in before.keys()|after.keys() if k not in before or k not in after or type(before[k])is not type(after[k]) or before[k]!=after[k]}
        require(delta=={'YORADIO_WS_STATUS_RTC_SLOW'} and before[next(iter(delta))] is True and after[next(iter(delta))] is False,'Configuration delta widened')
        old_header=package.original(directory/'baseline/sdkconfig.h'); header=package.original(directory/'compiled/config/sdkconfig.h')
        removed=b'#define CONFIG_YORADIO_WS_STATUS_RTC_SLOW 1\r\n'
        require(old_header.count(removed)==1 and old_header.replace(removed,b'')==header,'Header delta widened')
        package.json(prefix+'header-delta.json',dict(before=identity(old_header),after=identity(header),
            removed_define='CONFIG_YORADIO_WS_STATUS_RTC_SLOW 1',line_ending='CRLF',removed_bytes=45,all_other_bytes_identical=True))
        for path,name in ((before_path,'config-before.json'),(after_path,'config-after.json'),(clang_path,'config-clang.json')):
            package.copy(path,prefix+name)
        for name in ('qualification.json','execution-status.json','object-comparison.json','rtc-config-delta.json','compiler-config-delta.json','stack-frame.json'):
            package.copy(directory/name,prefix+name)
        commands={}
        gcc_before=json.loads(package.original(directory/'baseline/compile_commands.json'))
        gcc_after=load(directory/'compiled/compile_commands.json')
        require({x['output']:x for x in gcc_before}=={x['output']:x for x in gcc_after},'GCC command set changed')
        for compiler,path in (('gcc',directory/'compiled/compile_commands.json'),('clang',directory/'compiled/clang/compile_commands.json')):
            entries=json.loads(package.original(path)); selected=[x for x in entries if Path(x['file']).name in ('websocket_service.c','esp_eth_mac_openeth.c')]
            require(len(selected)==2,'Expected two actual focused compile entries'); commands[compiler]=selected
        package.json(prefix+'selected-compile-entries.json',commands)
        image=directory/'fixture/yoradio_cyd2usb_native.bin'; elf_path=directory/'compiled/yoradio_cyd2usb_native.elf'
        require(pin(image)==qualified['image'] and pin(elf_path)==qualified['elf'],'Linked artifact changed')
        record=dict(backend=backend,baseline=pin(directory/'baseline.json'),image=pin(image),elf=pin(elf_path),
            map=pin(directory/'compiled/yoradio_cyd2usb_native.map'),project_units=baseline['project_units'],
            descriptor_context=qualified['descriptor_context'],project_version=baseline['project_version'],source_date_epoch=baseline['source_date_epoch'],
            generated_headers=dict(gcc=identity(header),clang=pin(directory/'compiled/clang/config/sdkconfig.h')),
            complete_compile_databases={compiler:pin(directory/('compiled/compile_commands.json' if compiler=='gcc' else 'compiled/clang/compile_commands.json')) for compiler in ('gcc','clang')},
            non_app_fixture_inputs=[])
        record['complete_compile_databases']['gcc_before']=pin(directory/'baseline/compile_commands.json')
        record['gcc_command_set_unchanged']=True
        for path in sorted((directory/'fixture').rglob('*')):
            if path.is_file() and path.name!='yoradio_cyd2usb_native.bin': record['non_app_fixture_inputs'].append(dict(file=path.relative_to(directory/'fixture').as_posix(),**pin(path)))
        for item in qualified['unlinked_bootloader_date_exceptions']:
            source=Path(item['source']); require(source.name=='esp_bootloader_desc.c' and item['section']=='.rodata.esp_bootloader_desc','Unreviewed metadata exception')
            require(item['field_offset']==40 and item['field_bytes']==24 and item['other_56_bytes_identical'],'Metadata field widened')
            obj,=[x for x in baseline['objects'] if Path(x['source']).name=='esp_bootloader_desc.c']
            old=package.original(directory/'baseline/bootloader-descriptor-before.bin')
            new=Elf32(ROOT/obj['path']).section(item['section'])
            require(len(old)==len(new)==80 and old[:40]==new[:40] and old[64:]==new[64:],'Metadata bytes widened')
            require(identity(old)['sha256']==item['before_sha256'] and identity(new)['sha256']==item['after_sha256'],'Metadata section hash mismatch')
            for folder,proof in zip((rtc_on/'compiled',directory/'compiled'),item['map_elf_proofs']):
                ef=folder/'yoradio_cyd2usb_native.elf'; mp=folder/'yoradio_cyd2usb_native.map'
                require(pin(ef)==proof['elf'] and pin(mp)==proof['map'],'Map/ELF proof identity mismatch')
                text=mp.read_bytes(); require(b'esp_bootloader_desc.c.obj' not in text and b'.rodata.esp_bootloader_desc' not in text,'Previously unextracted section linked')
                require(not {'esp_bootloader_desc','esp_bootloader_get_description'}&Elf32(ef).symbols(),'Previously absent symbol linked')
            package.copy(directory/'unlinked-bootloader-date-exception.json',prefix+'unlinked-bootloader-date-exception.json')
            package.json(prefix+'bootloader-date-bytes.json',dict(before_hex=old.hex(),after_hex=new.hex(),date_time_offset=40,date_time_bytes=24,
                before_sha256=item['before_sha256'],after_sha256=item['after_sha256'],other_56_bytes_identical=True,
                before_provenance='Legacy bytes were reconstructed from the pinned SDK date field and verified against the frozen preflight SHA.' if backend=='legacy' else 'Exact section bytes captured before the RTC-off build.'))
        for unit in ('websocket','openeth'):
            output=directory/('lint-'+unit); report=load(output/'report.json')
            require(report['returncode']==0 and report['errors']==0 and report['warning_catalog_unchanged'],'Focused Clang mismatch')
            for name in ('report.json','stdout.log','stderr.log'):
                package.copy(output/name,prefix+'lint-'+unit+'/'+name)
        for phase in ('gcc-reconfigure','gcc-build','stage-fixture','clang-reconfigure','qualify'):
            for stream in ('stdout','stderr'):
                package.copy(directory/(phase+'.'+stream+'.log'),prefix+phase+'.'+stream+'.log')
        if backend=='legacy':
            for name in ('qualification-continuation-status.json','qualification-reviewed-continuation-status.json',
                         'header-comparison-diagnosis.json','unexpected-object-differences.json','bootloader-descriptor-diagnosis.json',
                         'qualify-continuation.stdout.log','qualify-continuation.stderr.log','qualify-reviewed.stdout.log','qualify-reviewed.stderr.log'):
                package.copy(directory/name,prefix+name)
            require(load(directory/'execution-status.json')['state']=='TERMINAL_NONPASS','Original first failure altered')
            require(load(directory/'qualification-continuation-status.json')['state']=='TERMINAL_NONPASS','Original object rejection altered')
            require(load(directory/'qualification-reviewed-continuation-status.json')['state']=='TERMINAL_PASS','Reviewed continuation mismatch')
        else: require(load(directory/'execution-status.json')['state']=='TERMINAL_PASS','Original controller mismatch')
        inputs['profiles'].append(record)
    package.json('input-bindings.json',inputs)
    package.json('redactions.json',dict(scope='Only personal home-directory components in public log copies are replaced with build. Raw local bytes, source, JSON, outcomes and counters remain unchanged.',
        log_files_checked=package.logs_checked,files=package.redactions))
    package.put('README.md',b'''# RTC workspace off: static SDK qualification

Three diagnostic OpenETH fixtures were built at source
`7595a79958b8a2ef56babb24c43259fcf536b6dd`, preserving application TU bytes
from the shared-scheduler implementation. This package covers builds/static
checks and focused Clang only. It contains no native runtime results and does
not close the HE-AAC/two-client resource gate or claim physical acceptance.

The sole effective change from the matched RTC-on fixtures is
`WS_STATUS_RTC_SLOW=true` becoming `false`. The independent 64-byte RTC access
probe stays ON. RTC usage is 104 bytes, plus the separate 24-byte reservation,
with 8,064 free. DRAM BSS and heap-start each increase exactly 6,560 bytes;
every image is 6,560 bytes smaller. TCP11520/10/5760, TLS16384/4096, original
watchdogs/cores/priorities/stacks, channels2 and vendor codecs stay unchanged.

Image/ELF/OTA/header/frame checks and six whole WS/SDK-driver Clang units pass.
Each profile retains 1 WS and 32 SDK warnings, with zero errors/new warnings.
2,855 objects were compared. PDM changes only WS. Legacy and continuous also
have one specifically reviewed SDK bootloader-descriptor date_time change:
only the 24-byte field of its 80-byte section differs, and the archive member,
section and symbols are absent from both linked applications. Exact bytes,
hashes and map/ELF exclusion bindings are included; no generic metadata
exception is allowed. Actual bootloader/partition/SPIFFS/non-app flash inputs
and all 24 production app/metadata files remain unchanged.

The original legacy controller NONPASS (LF expected, SDK header CRLF) and the
first static continuation NONPASS (unextracted descriptor date rejected) are
retained unchanged. The separately named reviewed continuation passes without
rebuilding that image. Source snapshots and all three logs/statuses preserve
the distinction; no original failure is relabeled.

PROJECT_VER and SOURCE_DATE_EPOCH deliberately preserve original diagnostic
A/B descriptor metadata. These are not newly labeled clean production releases.
`summary.json`, per-profile proofs, `input-bindings.json`, and the artifact
manifest bind selected immutable inputs. Full binaries/ELF/maps/databases and
private credentials stay local; this is not full compiler dependency closure.

`recipes/` contains frozen review copies, including the two earlier helpers.
They document the isolated build rather than instructing execution from this
public folder. The packager defaults to dry-run and performs no compiler,
QEMU, network or Git/index operation. Only public log home-path components
are neutralized; `redactions.json` records exact original/published hashes and
counts. Raw local logs and all qualification outcomes remain unchanged.

Native playback, final post-asset/post-close resource health and any NONPASS
runtime result belong to the separate parent package when available. No
default profile promotion or physical Wi-Fi/audio/RTC timing claim is made.
''')
    manifest=[dict(file=name,**identity(body)) for name,body in sorted(package.files.items())]
    package.json('artifact-manifest.json',manifest)
    for name,body in package.files.items():
        if name.endswith('.json'): json.loads(body)
    return package

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    modes=parser.add_mutually_exclusive_group(); modes.add_argument('--dry-run',action='store_true'); modes.add_argument('--write',action='store_true')
    args=parser.parse_args(); package=plan()
    for name,expected in package.originals.items(): require(pin(ROOT/name)==expected,'Original changed after planning: '+name)
    if args.write:
        require(not TARGET.exists(),'Refuse to overwrite existing public SDK directory')
        TARGET.mkdir(parents=True)
        for name,body in sorted(package.files.items()):
            path=TARGET/name; path.parent.mkdir(parents=True,exist_ok=True)
            with path.open('xb') as stream: stream.write(body)
            require(pin(path)==identity(body),'Written bytes differ: '+name)
    result=dict(mode='write' if args.write else 'dry-run',public_writes=bool(args.write),target=label(TARGET),
        files=[dict(file=name,**identity(body)) for name,body in sorted(package.files.items())],
        total_bytes=sum(map(len,package.files.values())),original_files_verified=len(package.originals),
        changed_public_log_files=len(package.redactions),home_replacements=sum(x['replacements'] for x in package.redactions),
        runtime_inputs_copied=0,compilers_run=False,qemu_run=False,network_used=False,git_index_changed=False)
    report=BASE/('package-sdk-write.json' if args.write else 'package-sdk-dry-run.json')
    report.write_bytes(encoded(result))
    print(json.dumps({k:v for k,v in result.items() if k!='files'}))

if __name__=='__main__': main()

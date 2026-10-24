"""Create-only current full31 RAW evidence; launch/import no prepared programs."""
from pathlib import Path
import ast
import gzip
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/'tests/results/vorbis-current-format31-20261024'
VERIFIER = ROOT/'.build/verify-vorbis-current-format31-template-01.py'
CHECKPOINT = ROOT/'.build/vorbis-current-format31-checkpoint-01.md'
GROUPS = {
    'prep': '.build/vorbis-format31-current-prep-01',
    'host': '.build/vorbis-format31-current-host-01',
    'commands': '.build/vorbis-format31-current-validation-20261024-01',
    'history01': '.build/vorbis-format31-current-cyd-01',
    'capture': '.build/vorbis-format31-current-cyd-02',
    'numeric-prep': '.build/vorbis-format31-current-numeric-prep-01',
    'numeric': '.build/vorbis-format31-current-numeric-01',
}
CANONICAL = ['docs/CYD_VORBIS_TRANSFER_DESIGN.md','docs/ESP32_CYD_C3_TRANSFER_PLAN.md','docs/CYD_VORBIS_FLOOR0_REMAINING.md',
    '.build/cyd-vorbis-format-command-01.py','.build/test-vorbis-format31-current-link-01.py',
    '.build/compare-vorbis-format31-current-old-01.py']
CANONICAL += ['idf/esp32-cyd2usb-native/main/'+name for name in (
    'vorbis_repair/setup.c','vorbis_repair/output.c','vorbis_repair/floor1_render.h',
    'vorbis_repair_abi.h','vorbis_repair/COPYING','vorbis_repair/README.md','compat/vorbis_repair/enable.cmake')]
COMMANDS = ('sdk-head','sdk-clean','build','setup-macros','link-recipe','symbols','merge','qemu','sdk-head-after','sdk-clean-after')
OBSERVED = {}


def need(ok,reason):
    if not ok: raise ValueError(reason)


def sha(data): return hashlib.sha256(data).hexdigest()


def norm(path): return str(path).replace('\\','/').rstrip('/')


def safe(base,relative):
    path = (base/norm(relative)).resolve()
    need(path != base and path.is_relative_to(base),'relative selected file boundary')
    return path


def read(path):
    path=path.resolve();need(path.is_relative_to(ROOT) and path.is_file(),'ordinary selected checkout body')
    data=path.read_bytes();pin=(len(data),sha(data))
    need(path not in OBSERVED or OBSERVED[path]==pin,'selected source changed')
    OBSERVED[path]=pin
    return data


def identity(path,refresh=False):
    path=path.resolve();need(path.is_file(),'identity-only file exists')
    if path in OBSERVED and not refresh: return OBSERVED[path]
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for part in iter(lambda:stream.read(1024*1024),b''): h.update(part)
    pin=(path.stat().st_size,h.hexdigest())
    need(path not in OBSERVED or OBSERVED[path]==pin,'identity-only input changed')
    OBSERVED[path]=pin
    return pin


def report(group): return json.loads(read(ROOT/GROUPS[group]/'report.json'))


def outer(path,code):
    r=json.loads(read(path))
    need(r['status']=='TERMINAL' and type(r['returncode']) is int and r['returncode']==code and
         type(r['owned_pid']) is int and r['owned_pid']>0 and not r.get('timed_out') and
         not r.get('interrupted') and not r.get('error_type') and 'returncode_after_stop' not in r,
         'actual ordinary outer terminal: '+str(path))
    return r


def preflight():
    need(not DEST.exists() and DEST.parent.is_dir(),'fresh evidence destination')
    ast.parse(read(VERIFIER),filename=str(VERIFIER))
    need(bool(read(CHECKPOINT)),'root-owned publication checkpoint must exist before destination creation')
    c=report('capture')
    need(c['completed'] is True and c['target_capture_completed'] is True and c['checked_decode_completed'] is True and
         c['passed'] is False and c['result']=='CHECKED_CORPUS_PCM_CAPTURED' and
         (c['corpus']['cases'],c['corpus']['packets'],c['corpus']['expected_pcm'])==(31,434,738560) and
         (c['observed']['cases'],c['observed']['decoded_packets'],c['observed']['pcm'],c['observed']['protocol_lines'])==(31,434,738560,964) and
         len(c['observed_pcm'])==31,'complete current31 actual capture')
    need(tuple(x['name'] for x in c['commands'])==COMMANDS,'actual ten capture commands')
    need(all(x['state']=='complete' and x['exit_status']==0 and type(x['pid']) is int and x['pid']>0 and
         not x['timed_out'] and not x['interrupted'] for x in c['commands']),'actual normal capture children')
    n=report('numeric')
    need(n['measurement_completed'] is True and n['actual_reference_compared'] is True and
         n['policy']['max_abs_error']==2 and n['policy']['required_cases']==31 and len(n['cases'])==31 and
         type(n['bounded_corpus_pcm_qualified']) is bool and
         n['result']==('BOUNDED_CORPUS_PCM_QUALIFIED' if n['bounded_corpus_pcm_qualified'] else 'BOUNDED_CORPUS_PCM_REJECTED') and
         all(len(n['metamorphic_relations'][key])==14 for key in ('xiph','target')) and
         n['passed'] is False and n['retained_reference_outputs_reused'] is True and
         n['new_reference_processes_executed'] is False,'complete numerical measurement; NONPASS is retained')
    need(all(n[key] is False for key in ('format_conformance_qualified','format_corpus_qualified','full_G6_qualified',
         'physical_device','production_radio_integration')),'finite numerical scope')
    h=report('history01')
    need(h['completed'] is False and h['passed'] is False and h['target_capture_completed'] is False and
         h['result']=='NONPASS' and tuple(x['name'] for x in h['commands'])==('sdk-head','sdk-clean','build') and
         h['commands'][-1]['exit_status']==1 and all(x.get('missing') for x in h['sdk_build_logs'].values()),
         'unchanged initial pre-SDK Python/export failure retained')
    host=report('host')
    need(host['passed'] is True and host['tests_run']==8 and len(host['commands'])==8 and host['inputs_unchanged'] is True and
         host['configure_only'] is True and not any(host[k] for k in ('compiler_invoked','SDK_invoked','QEMU_invoked','reference_invoked','prepared_Python_imported')),
         'actual eight CMake-P/AST preparation checks')
    commands=ROOT/GROUPS['commands']
    for name,code in (('preparation-host',0),('link-host',0),('cyd',1),('cyd02',0),('parity',0),
                      ('numeric',0 if n['bounded_corpus_pcm_qualified'] else 1)):
        outer(commands/(name+'.json'),code)
    need(b'Ran 8 tests in ' in read(commands/'link-host.stderr.log') and
         read(commands/'link-host.stderr.log').replace(b'\r\n',b'\n').endswith(b'\nOK\n'),'actual eight link-recipe tests')
    binding=ROOT/GROUPS['numeric-prep']/'host-bindings.json'
    receipt=outer(binding,0)
    logs=[read(Path(path)) for path in receipt['logs']]
    need(any(b'Ran 9 tests in ' in data and data.replace(b'\r\n',b'\n').endswith(b'\nOK\n') for data in logs),
         'actual nine numeric binding host tests')
    parity=json.loads(read(commands/'old-pcm-parity.json'))
    need(parity['comparison_completed'] is True and parity['inputs_unchanged'] is True and
         (parity['total_cases'],parity['total_packets'],parity['total_pcm_bytes'])==(31,434,738560) and
         len(parity['cases'])==31 and parity['new_decoder_or_reference_execution'] is False and
         parity['numerical_qualification'] is False,'actual full old/current PCM parity observation')
    return n,parity


def omission_reason(path):
    path=Path(path)
    if path.suffix.lower() in {'.exe','.elf','.obj','.o','.a','.dll','.pdb','.pyc'} or path.name=='qemu-flash.bin':
        return 'Executable/library/object/merged flash omitted; historical byte identity only, no binary semantics.'
    if 'build' in path.parts:
        tail=Path(*path.parts[path.parts.index('build')+1:]).as_posix()
        if not(path.suffix=='.map' or tail.startswith('log/') or tail in {'compile_commands.json','project_description.json',
                'flasher_args.json','config/sdkconfig.h','CMakeCache.txt','build.ninja','CMakeFiles/rules.ninja'}):
            return 'Replaceable unselected build output omitted; historical byte identity only.'
    return None


def main():
    numeric,parity=preflight()
    inventory={g:sorted(p.relative_to(ROOT/base).as_posix() for p in (ROOT/base).rglob('*') if p.is_file())
               for g,base in GROUPS.items()}
    need(all(inventory.values()),'every selected actual group exists')
    for name in CANONICAL: read(safe(ROOT,name))
    # Validate all consumed numerical inputs before creating the destination.
    for row in numeric['inputs'].values():
        size,digest=identity(Path(row['path']))
        need(size==row['bytes'] and digest==row['sha256'],'consumed numerical input changed')
    for path,row in parity['selected_inputs'].items():
        size,digest=identity(Path(path));need(size==row['bytes'] and digest==row['sha256'],'consumed parity input changed')
    m=dict(schema='vorbis-current-format31-evidence-v1',checkout_root=str(ROOT),groups=GROUPS,
        files={},omissions=[],origins={},numeric_inputs={},parity_inputs={},complete=False,predeclared_max_abs_error=2,
        corpus=dict(cases=31,packets=434,pcm_bytes=738560,relations=14),
        numerical_scope='Independent full original signed16 samples/packets and14 relations; no signal transforms.',
        parser_scope='Independent finite target event replay; explicit exact-hash reuse only of pure owned C-array/link recipe readers.',
        recipe_scope='Owned Ninja recipe query plus successful SDK build and linked ELF identity; no independent dynamic linker execution pin or invented response-file body.',
        binary_scope='Omitted binaries/tools have historical byte identity only; no full dependency or SDK rebuild closure.',
        documentation_scope='Publication-time design/plan and production README; execution sources remain separately pinned.',
        full_G1_qualified=False,full_G4_qualified=False,full_G5_qualified=False,full_G6_qualified=False,
        format_conformance_qualified=False,ogg_qualified=False,production_radio_integration=False,physical_device=False)
    DEST.mkdir();(DEST/'objects').mkdir()
    def put(alias,data):
        need(alias not in m['files'],'unique body alias')
        digest=sha(data);name='objects/'+digest+'.gz';path=DEST/name
        if not path.exists():
            with path.open('xb') as stream: stream.write(gzip.compress(data,mtime=0))
        m['files'][alias]=dict(bytes=len(data),sha256=digest,object=name)
    def remember(path,alias,reason=None):
        path=path.resolve();key=norm(path).casefold()
        if key in m['origins']:
            return m['origins'][key]
        size,digest=identity(path)
        row=dict(path=norm(path),bytes=size,sha256=digest)
        if reason:
            row['omission_reason']=reason;m['omissions'].append(dict(row))
        else:
            data=read(path);need((len(data),sha(data))==(size,digest),'body/identity race')
            put(alias,data);row['alias']=alias
        m['origins'][key]=row
        return row
    for group,base in GROUPS.items():
        for name in inventory[group]:
            remember(safe(ROOT/base,name),group+'/'+name,omission_reason(name))
    for name in CANONICAL: remember(safe(ROOT,name),'canonical/'+name)
    for index,(role,pin) in enumerate(numeric['inputs'].items()):
        path=Path(pin['path']).resolve();key=norm(path).casefold()
        reason=None
        if key not in m['origins']:
            reason=omission_reason(path)
            if not path.is_relative_to(ROOT):
                need(path.suffix.lower() in {'.exe','.a','.dll','.elf','.bin'},'external consumed input must be tool identity only')
                reason='External tool/ROM/library omitted; historical byte identity only, no executable semantics.'
        row=remember(path,'numeric-inputs/'+str(index).zfill(5),reason)
        need(row['bytes']==pin['bytes'] and row['sha256']==pin['sha256'],'saved consumed numeric identity')
        m['numeric_inputs'][role]=dict(row)
    for index,(original,pin) in enumerate(parity['selected_inputs'].items()):
        path=Path(original).resolve();need(path.is_relative_to(ROOT),'selected parity body stays inside checkout')
        row=remember(path,'parity-inputs/'+str(index).zfill(3))
        need(row['bytes']==pin['bytes'] and row['sha256']==pin['sha256'],'saved selected parity identity')
        m['parity_inputs'][original]=dict(row)
    put('collector.py',read(Path(__file__)))
    verifier=read(VERIFIER);put('verifier.py',verifier);(DEST/'verifier.py').write_bytes(verifier)
    readme=b'''Current-source finite31 RAW Vorbis evidence, 2026-10-24

Run python verifier.py offline. It launches no external program and executes
only exact-hash owned pure C-array/link-recipe reader definitions. Target events,
every signed16 sample/packet and all14 relations are independently replayed.
Integrity success preserves the actual bounded numeric PASS or NONPASS; it never
means full codec conformance. The predeclared engineering bound is2 S16 LSB.
No gain, trim, shift, channel swap, resampling or subset is applied.

Historical17+8+full12 Xiph evidence and actual native lookup2 refusals remain
unchanged. The initial current31 attempt is a host-Python SDK export invocation
failure before compiler/QEMU; it is preserved and never qualified. The separate
current02 capture requires all31 cases/434 packets/738560 bytes and10 owned
terminal commands. Ninja's queried link recipe is not a dynamic linker receipt.

Tools/ELF/libraries/flash/build junk are explicit historical hash-only omissions.
This bundle is not full SDK/dependency closure, production-radio/QIO boot,
full G1/G4/G5/G6, Ogg, private AAC, hardware or real-time/audio qualification.
Publication documentation is collected after execution; runtime source snapshots
remain separately hash-bound. No archived SDK/decoder/runner/checker executes.
'''
    attrs=b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n'
    for name,data in (('README.md',readme),('.gitattributes',attrs),('CHECKPOINT.md',read(CHECKPOINT))):
        put(name,data);(DEST/name).write_bytes(data)
    for group,base in GROUPS.items():
        need(inventory[group]==sorted(p.relative_to(ROOT/base).as_posix() for p in (ROOT/base).rglob('*') if p.is_file()),
             'selected group inventory changed')
    for path,pin in tuple(OBSERVED.items()): need(identity(path,refresh=True)==pin,'selected input changed before publication')
    m.update(complete=True,collection_sources_unchanged=True,logical_files=len(m['files']),
        unique_objects=len(list((DEST/'objects').iterdir())),selected_uncompressed_bytes=sum(x['bytes'] for x in m['files'].values()))
    output=DEST/'manifest.json';output.write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(path=str(DEST),manifest_sha256=sha(output.read_bytes()),aliases=m['logical_files'],
        objects=m['unique_objects'],omissions=len(m['omissions']))))


if __name__=='__main__': main()

"""Pack standalone actual public-curve evidence; never run any proposed verifier."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path, PurePosixPath
import struct

SELF=('pack.py','verify.py','protocol.py','readback.py','curve_fields_formula.py','compile_context_base.py',
      'README.md','plan.template.json','source-origins.json','source-relation.json','pack-adaptation.diff',
      'verify-adaptation.diff','source-checks.json','readiness.json','provenance/base-pack.py')
BINARY={'.elf','.bin','.a','.o','.obj','.exe','.dll','.rom','.lib','.zip','.pyc'}
TEXT_BUILD=('compile_commands.json','project_description.json','CMakeCache.txt','build.ninja','CMakeFiles/rules.ninja',
    'flasher_args.json','flash_args','config/sdkconfig.h','toolchain/cflags','specs/picolibc.specs','cyd_public_tremor_floor0_curve.map')


def need(ok,reason):
    if not ok:raise RuntimeError(reason)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def safe(value):
    value=str(value).replace('\\','/');path=PurePosixPath(value)
    need(value and not path.is_absolute() and '..' not in path.parts and ':' not in value,'Unsafe relative archive key')
    return path.as_posix()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--plan',type=Path,required=True);parser.add_argument('--plan-sha256',required=True)
    args=parser.parse_args();here=Path(__file__).resolve().parent;repo=args.repository.resolve();out=args.output.resolve()
    plan_raw=args.plan.resolve().read_bytes();need(sha(plan_raw)==args.plan_sha256,'Independently reviewed actual root plan required')
    plan=json.loads(plan_raw)
    need(plan['schema']=='public-floor0-curve-archive-plan-v1' and plan['state']=='ACTUAL_PARENT_TERMINALS_PINNED' and
         Path(plan['repository']).resolve()==repo and plan['archive_data_dependencies']==[] and
         plan['canonical_destination']=='tests/results/cyd-vorbis-public-floor0-curve-20261023','Standalone actual public-curve plan')
    roots=[Path(row['path']).resolve() for row in plan['preparations']+plan['roles']]+[Path(plan['public_download']['path']).resolve()]
    need(out.is_relative_to(repo/'.build') and out!=repo/'.build' and not out.exists() and
         all(root.is_dir() and root.is_relative_to(repo/'.build') and not out.is_relative_to(root) and not root.is_relative_to(out) for root in roots)
         and not out.is_relative_to(here) and not here.is_relative_to(out),'Fresh independent worktree .build stage')
    need([row['role'] for row in plan['roles']]==['failed01','failed02','capture03'],'All three actual histories required')
    out.mkdir(parents=True,exist_ok=False)
    m=dict(schema='cyd-public-floor0-curve-archive-v1',plan_sha256=args.plan_sha256,files={},omitted={},preparations={},campaigns={},
        diagnostics={},extra_receipts=[],extra_files=[],archive_data_dependencies=[],standalone=True,
        public_source_variant='PORTED_PUBLIC_TREMOR_FLOOR0',vendor_backend_qualified=False,target_codec_executed=False,
        reference_decoder_executed=False,PCM_computed=False,PCM_qualified=False,full_G6_qualified=False,physical_qualified=False,
        production_radio_integration=False,omitted_binary_bytes_replayable=False,
        QMP_EOF_direct_boolean_recorded=False,QMP_EOF_enforced_by_exact_captured_helper=True)
    originals={}

    def put(raw,key,origin,derived=None):
        key=safe(key);need(key not in m['files'] and key not in m['omitted'],'Unique stored archive key')
        compress=len(raw)>=16384 and Path(key).suffix.lower() not in ('.py','.c','.h','.ps1','.cmake','.diff','.gz')
        encoded=gzip.compress(raw,compresslevel=9,mtime=0) if compress else raw;stored=key+('.gz' if compress else '')
        path=out/safe(stored);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(encoded)
        row=dict(origin=str(origin).replace('\\','/'),bytes=len(raw),sha256=sha(raw),stored=stored,stored_bytes=len(encoded),
            stored_sha256=sha(encoded),compression='gzip' if compress else 'none')
        if derived is not None:row['derived_from_full_sha256']=derived
        m['files'][key]=row

    def add(path,key,expected=None,tool=False):
        need(not Path(path).is_symlink(),'No symlink input')
        path=Path(path).resolve();key=safe(key)
        need(path.is_file() and not path.is_symlink() and (tool or path.is_relative_to(repo)),'Regular retained input within repository; external tools hash-only')
        raw=path.read_bytes();digest=sha(raw);need(expected is None or digest==expected,'Pinned source/evidence changed: '+str(path))
        if key in m['files'] or key in m['omitted']:
            row=m['files'].get(key,m['omitted'].get(key));need(row['sha256']==digest and row['bytes']==len(raw),'Repeated identity differs');return key
        originals[str(path)]=digest
        fixture=path.name in ('identification.bin','setup.bin','audio.bin','comment.bin')
        if tool or (path.suffix.lower() in BINARY and not fixture):
            need(path.suffix.lower() not in ('.o','.obj','.pyc'),'Intermediate object/cache not selected')
            row=dict(origin=str(path).replace('\\','/'),bytes=len(raw),sha256=digest,reason='Actual declared runtime/tool binary body omitted; identity only')
            if path.suffix.lower()=='.elf':
                need(raw[:7]==b'\x7fELF\x01\x01\x01' and len(raw)>=64 and struct.unpack_from('<H',raw,18)[0]==94,'Actual ELF32/Xtensa header')
                header=key+'.header64';put(raw[:64],header,str(path)+'[0:64]',derived=digest)
                row.update(elf_header_key=header,elf_machine=94,elf_header_bytes=64)
            m['omitted'][key]=row
        else:put(raw,key,path)
        return key

    def receipt(path,key,expected,code):
        raw=Path(path).read_bytes();need(sha(raw)==expected,'Exact actual root receipt')
        r=json.loads(raw);actual=r.get('exit_code',r.get('returncode'))
        need(type(actual) is int and actual==code and (r.get('schema')=='direct-exec-tool-terminal-v1' or r.get('status')=='TERMINAL'),'Actual outer terminal outcome')
        entry=dict(key=add(path,key,expected),log_keys={},tool_key=None)
        for index,(origin,row) in enumerate(r.get('logs',{}).items()):
            target=key+'.streams/'+f'{index:02d}-'+Path(origin).name;entry['log_keys'][origin]=add(origin,target,row['sha256'])
        if 'executable_sha256' in r:
            entry['tool_key']=add(r['argv'][0],key+'.tool/'+Path(r['argv'][0]).name,r['executable_sha256'],tool=True)
        return entry

    put(plan_raw,'plan.json',args.plan.resolve())
    for name in SELF:add(here/name,name)
    add(plan['checkpoint']['path'],'CHECKPOINT.md',plan['checkpoint']['sha256'])
    put(b'* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol,-space-before-tab\n','.gitattributes','literal raw-byte policy')
    for row in plan['preparations']:
        root=Path(row['path']);index_raw=(root/row['index']).read_bytes();need(sha(index_raw)==row['index_sha256'],'Preparation/runtime index pin')
        index=json.loads(index_raw);names={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
        need(names==set(index['files'])|{row['index']},'Complete historical preparation/runtime index')
        prefix='preparations/'+safe(row['name'])
        for name in sorted(names):add(root/name,prefix+'/'+name,row['index_sha256'] if name==row['index'] else index['files'][name]['sha256'])
        m['preparations'][row['name']]=dict(prefix=prefix,index=row['index'],index_sha256=row['index_sha256'])
    public=plan['public_download'];root=Path(public['path']);raw_index=(root/public['index']).read_bytes();need(sha(raw_index)==public['index_sha256'],'Complete original public SOURCE record')
    index=json.loads(raw_index);names={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    need(names=={public['index'],index['archive']['path']}|{row['path'] for row in index['files']},'Exact full downloaded public source tree/archive')
    published={row['path']:row['sha256'] for row in index['files']};published[public['index']]=public['index_sha256'];published[index['archive']['path']]=index['archive']['sha256']
    for name in sorted(names):add(root/name,'public-download/'+name,published[name])
    m['public_download']=dict(prefix='public-download',index=public['index'],index_sha256=public['index_sha256'])
    for role in plan['roles']:
        name=role['role'];root=Path(role['path']);prefix='campaigns/'+name;report_raw=(root/'report.json').read_bytes()
        need(sha(report_raw)==role['report_sha256'],'Root-reviewed actual capture report')
        report=json.loads(report_raw);need(report['result']==role['expected_result'],'Preserved actual role result')
        outer=receipt(role['terminal_path'],prefix+'/parent-terminal.json',role['terminal_sha256'],role['expected_exit_code'])
        for path in sorted(root.iterdir()):
            if path.is_file() and path.suffix.lower() not in BINARY and path.name!='report.json.tmp':add(path,prefix+'/'+path.name)
        for folder in ('sources','observed-curves'):
            for path in sorted((root/folder).rglob('*')):
                if path.is_file():add(path,prefix+'/'+path.relative_to(root).as_posix())
        inputs={}
        for origin,fact in report['inputs'].items():
            path=(root/safe(fact['snapshot'])).resolve();need(path.is_relative_to(root/'sources') and path.stat().st_size==fact['bytes'],'Bounded complete actual input snapshot')
            inputs[origin]=add(path,prefix+'/'+safe(fact['snapshot']),fact['sha256'])
            original=Path(origin).resolve();need(sha(original.read_bytes())==fact['sha256'],'Original declared input differs from frozen snapshot');originals[str(original)]=fact['sha256']
        for rel,digest in report['build_outputs'].items():add(root/safe(rel),prefix+'/'+safe(rel),digest)
        for rel in TEXT_BUILD:
            if (root/'build'/rel).is_file():add(root/'build'/rel,prefix+'/build/'+rel)
        tools={}
        for index,(origin,digest) in enumerate(report['tools'].items()):tools[origin]=add(origin,prefix+'/tools/'+f'{index:02d}-'+Path(origin).name,digest,tool=True)
        m['campaigns'][name]=dict(prefix=prefix,historical_root=role['path'],prep=role['prep'],report_sha256=role['report_sha256'],
            terminal_sha256=role['terminal_sha256'],expected_exit_code=role['expected_exit_code'],expected_result=role['expected_result'],input_keys=inputs,tool_keys=tools,outer=outer)
    for index,row in enumerate(plan['extra_receipts']):m['extra_receipts'].append(receipt(row['path'],'root-receipts/'+f'{index:02d}-'+Path(row['path']).name,row['sha256'],row['expected_exit_code']))
    for row in plan['extra_files']:m['extra_files'].append(add(row['path'],'root-sources/'+Path(row['path']).name,row['sha256']))
    for row in plan['diagnostics']:
        name=safe(row['name']);prefix='diagnostics/'+name
        add(row['report_path'],prefix+'/report.json',row['report_sha256']);report=json.loads(Path(row['report_path']).read_bytes())
        outer=receipt(row['terminal_path'],prefix+'/parent-terminal.json',row['terminal_sha256'],row['expected_exit_code'])
        inputs={}
        for index,(origin,fact) in enumerate(report['validated_inputs'].items()):
            inputs[origin]=add(origin,prefix+'/validated-inputs/'+f'{index:04d}-'+Path(origin).name,fact['sha256'])
        m['diagnostics'][name]=dict(prefix=prefix,prep=row['prep'],report_sha256=row['report_sha256'],outer=outer,input_keys=inputs)
    for origin,digest in originals.items():need(sha(Path(origin).read_bytes())==digest,'Source changed during archive assembly')
    with (out/'manifest.json').open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(m,indent=2)+'\n')
    print(json.dumps(dict(result='PUBLIC_CURVE_EVIDENCE_PACKED_UNVERIFIED',files=len(m['files']),omitted=len(m['omitted']),
        manifest_sha256=sha((out/'manifest.json').read_bytes()),verifier_executed=False,PCM_qualified=False,full_G6_qualified=False)))


if __name__=='__main__':main()

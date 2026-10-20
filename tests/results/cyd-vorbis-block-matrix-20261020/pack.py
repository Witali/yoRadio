"""Copy selected completed block-matrix evidence; never runs a tool or verifier."""
import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import struct
import wave

def need(ok, message):
    if not ok: raise RuntimeError(message)
def sha(data): return hashlib.sha256(data).hexdigest()
def norm(path): return str(path).replace('\\', '/')
def load(path): return json.loads(Path(path).read_bytes())

ROOTS = {
    'dual':'cyd-vorbis-block-host-01', 'xiph':'cyd-vorbis-block-xiph-01',
    'rate':'cyd-vorbis-block-rate-host-01', 'banks':'cyd-vorbis-block-banks-01',
    'design':'cyd-vorbis-block-matrix-design-01', 'candidates':'cyd-vorbis-block-candidates-01',
    'minimal':'cyd-vorbis-minimal-block-prep-01', 'rebound':'cyd-vorbis-minimal-block-rate-prep-01',
    'generator_prep':'cyd-vorbis-block-generators-canonical-prep-01',
    'generator_check':'cyd-vorbis-block-generators-canonical-check-01',
    'protocol_prep':'cyd-vorbis-block-target-prep-01', 'sdk_prep':'cyd-vorbis-block-sdk-prep-01',
    'normative':'cyd-vorbis-floor-range-audit-01',
    'canonical_protocol':'cyd-vorbis-block-protocol-canonical-check-01'}
BINARY = {'.elf','.bin','.a','.o','.obj','.exe','.dll','.rom','.lib','.zip','.wav','.pcm','.s16le','.f32le','.pyc'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('repository','target','target-terminal','output'): p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--extra',action='append',default=[],type=Path)
    args = p.parse_args(); repo,target,out = (getattr(args,n).resolve() for n in ('repository','target','output'))
    roots = {name:repo/'.build'/rel for name,rel in ROOTS.items()}; roots['target'] = target
    need(all(x.is_relative_to(repo) and x.is_dir() for x in roots.values()) and not out.exists() and
         out.parent == repo/'tests/results' and all(not out.is_relative_to(x) for x in roots.values()), 'Fresh results output and selected repository roots required')
    reports = {name:load(roots[name]/'report.json') for name in ('dual','xiph','rate','target')}
    need(all(reports[n].get('completed') is True for n in ('dual','xiph','rate')), 'Host corpus not completed')
    outer = args.target_terminal.resolve(); terminal = load(outer)
    need(terminal.get('status') == 'TERMINAL' and type(terminal.get('exit_code')) is int and
         type(terminal.get('session_id')) is int and terminal.get('chunk_id') and
         terminal.get('argv') and terminal.get('cwd') and
         terminal.get('report_sha256')==sha((target/'report.json').read_bytes()),
         'Explicit final direct-tool receipt and report identity required')
    need(reports['target']['commands'] and all(c['state'] in ('complete','failed','interrupted') and
         type(c['exit_status']) is int for c in reports['target']['commands']), 'Live/incomplete target commands')
    out.mkdir(parents=True,exist_ok=False)
    manifest = dict(schema='cyd-public-block-matrix-archive-v1',repository_original=norm(repo),
        roots={k:v.relative_to(repo).as_posix() for k,v in roots.items()},target_terminal=norm(outer),
        files={},scope='isolated public raw block matrix; no full G6/radio/physical qualification',
        omitted_bytes_replayable=False)
    seen = {}
    def add(path, expected=None, size=None, destination=None):
        path=Path(path); need(not path.is_symlink(),'Symlink input'); path=path.resolve()
        need(path.is_file(),'Missing evidence '+str(path))
        key=norm(path)
        if key in seen:
            need(expected is None or seen[key]==expected,'Repeated pin differs '+key)
            need(size is None or manifest['files'][key]['bytes']==size,'Repeated size differs '+key)
            return  # Every unique source is rehashed before manifest publication.
        data=path.read_bytes(); digest=sha(data)
        need(expected is None or digest==expected,'Pinned input changed '+str(path))
        need(size is None or len(data)==size,'Pinned size changed '+str(path))
        key=norm(path); need(key not in seen or seen[key]==digest,'Conflicting source identity')
        if key in seen: return
        seen[key]=digest; row=dict(sha256=digest,bytes=len(data),stored=None)
        encoded = (('/generated01/' in key or '/cyd-vorbis-block-generators-canonical-check-01/minimal-' in key) and
                   path.suffix=='.bin' and len(data)<65536)
        if path.suffix.lower() in BINARY and not encoded:
            row['omission']='Identity only; omitted bytes cannot be replayed offline'
            if path.suffix.lower()=='.elf':
                need(data[:6]==b'\x7fELF\x01\x01' and struct.unpack_from('<H',data,18)[0]==94,'Expected ELF32LE Xtensa94')
                row['elf_header_hex']=data[:52].hex(); row['elf_machine']=94
            if path.suffix.lower()=='.wav':
                try:
                    with wave.open(io.BytesIO(data),'rb') as stream:
                        pcm=stream.readframes(stream.getnframes())
                        row['pcm']=dict(sha256=sha(pcm),bytes=len(pcm),rate=stream.getframerate(),channels=stream.getnchannels(),sample_width=stream.getsampwidth())
                except (wave.Error,EOFError) as exc: row['incomplete_wav']=str(exc)
        else:
            destination=destination or ('records/'+path.relative_to(repo).as_posix() if path.is_relative_to(repo) else 'external/'+sha(key.encode())[:16]+'/'+path.name)
            compressed=len(data)>65536 and path.suffix!='.py'
            blob=gzip.compress(data,mtime=0) if compressed else data
            dest=out/(destination+('.gz' if compressed else ''))
            need(dest.resolve().is_relative_to(out) and not dest.exists(),'Unsafe/duplicate archive path')
            dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(blob)
            row.update(stored=dest.relative_to(out).as_posix(),encoding='gzip' if compressed else 'raw',stored_sha256=sha(blob),stored_bytes=len(blob))
            if encoded: row['encoded_source_bytes']=True
        manifest['files'][key]=row
    def tree(folder):
        for path in sorted(folder.rglob('*')):
            if path.is_file(): add(path)
    def captured(path):
        r=load(path); add(path)
        for name,row in r.get('logs',{}).items():
            value=Path(name); value=value if value.is_absolute() else Path(path).parent/value
            add(value,row['sha256'],row['bytes'])
        if 'executable_sha256' in r: add(r['argv'][0],r['executable_sha256'])
    for name,folder in roots.items():
        if name!='target': tree(folder)
    tree(repo/'tests/vorbis_block_matrix')
    for name in ('design','protocol_prep'):
        for row in load(roots[name]/'input-pins.json')['inputs']:
            add(repo/norm(row['path']),row['sha256'],row['bytes'])
    for path,row in load(roots['canonical_protocol']/'host-tests.command.json')['inputs'].items():
        add(path,row['sha256'],row['bytes'])
    for path in sorted(target.iterdir()):
        if path.is_file(): add(path)
    for name in ('sources','variant'): tree(target/name)
    for name in ('CMakeCache.txt','compile_commands.json','build.ninja','project_description.json','flasher_args.json','config/sdkconfig.h','config/sdkconfig.json'):
        add(target/'build'/name)
    tr=reports['target']
    for path,row in tr['inputs'].items(): add(path,row['sha256']); add(target/norm(row['snapshot']),row['sha256'])
    for path,digest in tr['tools'].items(): add(path,digest)
    for mapping in ('variant_sources','build_outputs'):
        for path,digest in tr[mapping].items(): add(target/norm(path),digest)
    for path,row in tr['setup_macro_context']['generated_inputs'].items(): add(path,row['sha256_before'])
    for command in tr['commands']:
        for stream in ('stdout','stderr'): add(target/(command['name']+'.'+stream+'.log'),command[stream+'_sha256'])
    captured(outer)
    for name in ('host','xiph','rate-host'): captured(repo/'.build'/('cyd-vorbis-block-'+name+'-01-command.json'))
    for name in ('candidates-generate','rate-generate'): captured(repo/'.build'/('cyd-vorbis-block-'+name+'-01.json'))
    for name in ('host-driver','xiph-complete','freeze-banks','sdk-materialize'):
        add(repo/'.build'/('cyd-vorbis-block-'+name+'-01.py'))
    add(repo/'.build/cyd-vorbis-format-command-01.py')
    for name in ('dual','rate'):
        r=reports[name]
        for path,digest in r['tools'].items(): add(path,digest)
        for c in r['commands']: captured(roots[name]/c['receipt'])
        for c in r['cases']:
            matrix=Path(c['source_matrix']); add(matrix,c['source_matrix_sha256'])
            source=Path(c['input'].get('path',matrix.parent/c['input']['ogg'])); add(source,c['ogg_sha256'])
    # Reused78 point to original receipts; added30 receipts live in xiph's tree.
    for path in roots['xiph'].rglob('*.json'):
        r=load(path)
        if isinstance(r,dict) and r.get('status')=='TERMINAL': captured(path)
    relation=load(roots['generator_prep']/'source-relation.json')
    for row in relation['source_inputs']: add(row['path'],row['sha256'],row['bytes'])
    for row in relation['files']:
        add(roots['generator_prep']/row['path'],row['sha256'],row['bytes'])
        add(repo/'tests/vorbis_block_matrix'/Path(row['path']).name,row['sha256'],row['bytes'])
    check=load(roots['generator_check']/'report.json')
    for row in check['commands']:
        receipt=load(row['path']); add(row['path'],row['sha256']); add(receipt['argv'][0])
        for stream in ('stdout','stderr'):
            entry=receipt[stream]; add(entry['path'],entry['sha256'],entry['bytes'])
    for row in check['files']:
        add(row['historical'],row['historical_sha256'],row['historical_bytes'])
        add(row['canonical_output'],row['canonical_sha256'],row['canonical_bytes'])
    for path in args.extra: add(path if path.is_absolute() else repo/path)
    here=Path(__file__).resolve().parent
    for name in ('pack.py','verify.py','README.md'): add(here/name,destination=name)
    attrs=b'* -text\n** -text\n'; (out/'.gitattributes').write_bytes(attrs)
    manifest['attributes_sha256']=sha(attrs)
    for key,digest in seen.items(): need(sha(Path(key).read_bytes())==digest,'Input changed while collecting '+key)
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(dict(collected=True,verified=False,files=len(seen),output=str(out))))


if __name__=='__main__': main()

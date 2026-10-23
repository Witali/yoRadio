"""Pure source AST/hash checks only; never import another proposed module."""
import argparse
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def need(ok,reason):
    if not ok:raise ValueError(reason)


def sha(data):return hashlib.sha256(data).hexdigest()


def check():
    origins=json.loads((HERE/'source-origins.json').read_bytes())
    for row in origins['inputs']:
        before=Path(row['source']).read_bytes();after=(HERE/row['snapshot']).read_bytes()
        need(before==after and len(after)==row['bytes'] and sha(after)==row['sha256'],'Exact original source copy')
    source=json.loads((HERE/'provenance/public-download/SOURCE.json').read_bytes())
    need(source['revision']=='0ad0141e864cfbb130db4f22e279d421832e7336' and
         source['archive']['sha256']=='d5e655ab1ad537049ade9703477200a6ec15d7919cae11678ea841f018936743' and
         sha((HERE/'provenance/public-download/Tremor.tar.gz').read_bytes())==source['archive']['sha256'],'Public download source/archive identity')
    published={row['path']:row for row in source['files']}
    public=[]
    port=json.loads((HERE/'public-portability.json').read_bytes())
    need(sha((HERE/'public-floor0-portability.diff').read_bytes())==port['exact_diff_sha256'],'Explicit public-C portability diff bytes')
    for path in sorted((HERE/'project/main/public').iterdir()):
        row=published['source/'+path.name];raw=path.read_bytes()
        if path.name=='floor0.c':
            original=(HERE/'provenance/public-port/floor0.original.c').read_bytes()
            need(len(original)==row['bytes'] and sha(original)==row['sha256']==port['original_floor0_sha256'] and
                 sha(raw)==port['ported_floor0_sha256'],'Explicit original and ported public floor0 identities')
            expected=original.replace(b'(-140<<12)',b'-(140<<12)').replace(b'  ogg_uint32_t inyq= (1UL<<31) / toBARK(nyq);\n',b'')
            need(expected==raw,'Only approved public-C portability changes')
        else:
            need(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'Unchanged other public C/header/COPYING source')
        public.append(dict(path=path.relative_to(HERE).as_posix(),bytes=len(raw),sha256=sha(raw),ported=path.name=='floor0.c'))
    AST=[]
    for path in sorted(HERE.rglob('*.py')):
        raw=path.read_bytes();tree=ast.parse(raw,filename=path.as_posix())
        AST.append(dict(path=path.relative_to(HERE).as_posix(),bytes=len(raw),sha256=sha(raw),AST_parsed=True))
    need(not any(path.suffix.lower() in {'.a','.elf','.bin','.exe'} for path in (HERE/'project').rglob('*')),'No binary/vendor archive input in public source project')
    return dict(schema='public-floor0-curve-source-checks-v1',raw_copies=len(origins['inputs']),public_sources=public,AST=AST,
        scope='Raw bytes and AST only; proposed functions/materializer/protocol/unit/math not executed',
        materializer_executed=False,semantic_controls_executed=False,public_function_evaluated=False,target_codec_executed=False,
        reference_decoder_executed=False,SDK_executed=False,QEMU_executed=False,PCM_computed=False,numeric_qualified=False,full_G6_qualified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    out=args.output.resolve()
    need(not out.exists() and not out.is_relative_to(HERE),'Use a fresh independent source-check result file')
    result=check();out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8',newline='\n') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(source_AST_hash_checks=True,public_function_evaluated=False)))

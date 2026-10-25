"""Additional owned-codebook malformed and maximum-metadata host assertions.

No frozen prior campaign is changed. This runner launches no SDK or QEMU.
The separate C adapter generates finite packets and captures actual assertions.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
ROOT=Path(__file__).resolve().parents[1]
COMPONENT=ROOT/'idf/components/native_vorbis_numeric'
DRIVER=ROOT/'tests/native/vorbis_codebook_boundaries_test.c'
POLICY=dict(schema='native-vorbis-codebook-boundaries-policy-v1',kind='Finite additional C parser/metadata assertions',
    preserved_prior_campaigns=True,host_only=True,not_exhaustive_conformance=True,selected_before_measurement=True,
    full24_sparse_packet_bytes=2097162,full24_word_storage_count=1,entries_sized_stack=False)
EXPECTED=dict(schema='native-vorbis-codebook-boundaries-capture-v1',passed=True,status_checks=290,negative_cases=140,
    ordered_overrun=1,ordered_length33=32,reserved_lookup=13,bad_singleton=62,wrong_sync=24,unordered_flag_truncations=7,
    lookup1_zero_dimension=1,wide_complete_entries=32768,wide_complete_dimensions=65535,wide_complete_used=32768,
    wide_complete_maximum_length=15,full24_sparse_entries=0xffffff,full24_sparse_dimensions=65535,full24_sparse_used=1,
    full24_sparse_last_entry=0xfffffe,full24_packet_bits=66+0xffffff+5+4,full24_packet_bytes=2097162,full24_decoded_bits=2)
def need(ok,reason):
    if not ok:raise ValueError(reason)
def sha(data):return hashlib.sha256(data).hexdigest()
def validate_capture(capture):
    need(set(capture)==set(EXPECTED) and capture['passed']is True and all(type(capture[k])is type(v) and capture[k]==v for k,v in EXPECTED.items()),'complete actual boundary assertion capture')
    return dict(passed=True,status_checks=capture['status_checks'],negative_cases=capture['negative_cases'])
def host(path):
    value=Path(path).resolve().as_posix()
    return '/mnt/'+value[0].lower()+value[2:]if sys.platform=='win32'else value

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--prepare-only',action='store_true');args=parser.parse_args()
    out=args.output.resolve();need(out.is_relative_to(ROOT/'.build') and out!=ROOT/'.build' and not out.exists(),'fresh task-local supplement output')
    out.mkdir(parents=True);(out/'sources').mkdir()
    report=dict(completed=False,passed=False,prepared=False,component_executed=False,source_inputs_unchanged=False,policy=POLICY,
        commands=[],sources={},SDK_or_QEMU_executed=False,decoder_executed=False,full_floor0_qualified=False,full_G6_qualified=False,PCM_qualified=False,physical_device=False)
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def freeze(path,name):
        body=path.read_bytes();(out/'sources'/name).write_bytes(body);report['sources'][str(path.resolve())]=dict(snapshot='sources/'+name,bytes=len(body),sha256=sha(body));return body
    def current():need(all(sha(Path(path).read_bytes())==pin['sha256']==sha((out/pin['snapshot']).read_bytes())for path,pin in report['sources'].items()),'whole source/header/supervisor inputs unchanged')
    save()
    try:
        freeze(Path(__file__),'test-vorbis-codebook-boundaries.py');freeze(DRIVER,'driver.c')
        for name in ('floor0.c','quant.c','codebook.c','CMakeLists.txt'):freeze(COMPONENT/name,name)
        for name in ('native_vorbis_floor0.h','native_vorbis_quant.h','native_vorbis_codebook.h'):freeze(COMPONENT/'include'/name,name)
        owner=freeze(ROOT/'tests/test-vorbis-floor1-render.py','supervisor-owner.py')
        nodes=[node for node in ast.parse(owner).body if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='SUPERVISOR'for t in node.targets)]
        need(len(nodes)==1,'one existing owned supervisor literal');(out/'supervisor.py').write_text(ast.literal_eval(nodes[0].value),encoding='utf-8',newline='\n')
        report.update(prepared=True);current();save()
        if args.prepare_only:print(json.dumps(dict(prepared=True,passed=False,component_executed=False)));return 0
        def run(name,argv):
            nonce=uuid.uuid4().hex;request=out/(name+'.request.json');receipt=out/(name+'.receipt.json');stop=out/(name+'.stop')
            request.write_text(json.dumps(dict(nonce=nonce,argv=argv,timeout=60,receipt=host(receipt),stop=host(stop))),encoding='utf-8')
            command=(['wsl.exe','--exec','python3']if sys.platform=='win32'else[sys.executable])+[host(out/'supervisor.py'),host(request)]
            row=dict(name=name,argv=command,child_argv=argv,nonce=nonce);report['commands'].append(row);save();child=None;error=None;start=time.monotonic()
            stdout=out/(name+'.stdout.log');stderr=out/(name+'.stderr.log')
            try:
                with stdout.open('xb')as so,stderr.open('xb')as se:
                    child=subprocess.Popen(command,stdin=subprocess.DEVNULL,stdout=so,stderr=se,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt'else 0)
                    row['transport_pid']=child.pid;save();child.wait(timeout=80)
            except BaseException as exc:error=exc
            finally:
                if child is not None and child.poll()is None:
                    stop.write_text(nonce,encoding='utf-8')
                    try:child.wait(timeout=15)
                    except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5);row['forced_transport_stop']=True
                actual=json.loads(receipt.read_bytes())if receipt.exists()else{}
                row.update(supervisor=actual,transport_returncode=None if child is None else child.poll(),elapsed_seconds=time.monotonic()-start,
                    stdout_sha256=sha(stdout.read_bytes())if stdout.exists()else None,stderr_sha256=sha(stderr.read_bytes())if stderr.exists()else None);save()
            need(actual.get('nonce')==nonce and actual.get('request_sha256')==sha(request.read_bytes())and all(actual.get(k)is True for k in ('final','new_session','child_reaped','group_gone'))and
                actual.get('state')=='terminal'and actual.get('child_returncode')==0 and row['transport_returncode']==0 and not row.get('forced_transport_stop')and 'cleanup_error'not in actual,'owned boundary child terminal/cleanup '+name)
            if error is not None:raise error
            return stdout.read_bytes(),stderr.read_bytes()
        run('compiler-version',['gcc','--version']);run('compiler-machine',['gcc','-dumpmachine'])
        flags=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer','-fno-pie','-no-pie']
        so,se=run('compile',flags+['-I'+host(out/'sources'),host(out/'sources/driver.c'),host(out/'sources/floor0.c'),host(out/'sources/quant.c'),host(out/'sources/codebook.c'),'-lm','-o',host(out/'test')])
        need(not so and not se,'strict clean whole-component compile');current()
        so,se=run('execute',[host(out/'test'),host(out/'capture.json')]);report['component_executed']=True;need(not so and not se,'clean actual sanitized supplement run')
        body=(out/'capture.json').read_bytes();capture=json.loads(body);result=validate_capture(capture);current()
        report.update(completed=True,passed=result['passed'],source_inputs_unchanged=True,assertion_capture=capture,capture_sha256=sha(body),
            status_checks=result['status_checks'],negative_cases=result['negative_cases'],result='HOST_CODEBOOK_BOUNDARIES_QUALIFIED')
        save();print(json.dumps(dict(completed=True,passed=True,status_checks=result['status_checks'],negative_cases=result['negative_cases'],result=report['result'])));return 0
    except BaseException as error:report.update(completed=False,passed=False,error=repr(error));save();raise

if __name__=='__main__':sys.exit(main())

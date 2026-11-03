"""Read-only Git clean-CRLF identity controls; never stage/write Git objects or sources."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / 'tests/run-cyd-flac-ordinary-task-qemu.py'


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); out=args.output.resolve(); out.mkdir(parents=True,exist_ok=False)
    report=dict(passed=False,SDK_or_compiler_started=False,production_modified=False,git_objects_written=False,commands=[],cases=[])
    def save(): (out/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    def run(label, command, input_bytes=None):
        command=list(map(str,command)); assert '-w' not in command
        result=subprocess.run(command,input=input_bytes,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30)
        (out/(label+'.stdout.log')).write_bytes(result.stdout); (out/(label+'.stderr.log')).write_bytes(result.stderr)
        report['commands'].append(dict(name=label,command=command,returncode=result.returncode,
                    input_bytes=len(input_bytes) if input_bytes is not None else None,
                    input_sha256=hashlib.sha256(input_bytes).hexdigest() if input_bytes is not None else None))
        assert result.returncode==0,label
        return result.stdout.decode('utf-8').replace('\r\n','\n')
    try:
        for source in (CONTROLLER,Path(__file__).resolve()):
            data=source.read_bytes(); target=out/'sources'/source.relative_to(ROOT)
            target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        spec=importlib.util.spec_from_file_location('ordinary_flac_identity_controller',CONTROLLER)
        controller=importlib.util.module_from_spec(spec); spec.loader.exec_module(controller)
        for index,relative in enumerate(('idf/esp32-cyd2usb-native/main/board_config.h','idf/esp32-cyd2usb-native/sdkconfig.defaults')):
            source=ROOT/relative; data=source.read_bytes(); assert b'\r\n' in data,'actual clean CRLF checkout required'
            snapshot=out/'sources'/relative; snapshot.parent.mkdir(parents=True,exist_ok=True); snapshot.write_bytes(data)
            expected=run('expected-'+str(index),['git','-C',ROOT,'rev-parse','HEAD:'+relative]).strip()
            canonical=controller.canonical_git_blob(relative,data,run,'clean-'+str(index)); assert canonical==expected
            changed=controller.canonical_git_blob(relative,data+b'\r\n// real-edit identity control\r\n',run,'edited-'+str(index))
            assert changed!=expected and source.read_bytes()==data
            raw_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            assert raw_blob!=expected,'control must reproduce original unfiltered-identity defect'
            report['cases'].append(dict(path=relative,clean_CRLF_matches_commit=True,real_edit_refused=True,
                original_source_unchanged=True,canonical_git_blob=canonical,raw_compiler_input_sha256=hashlib.sha256(data).hexdigest(),
                raw_blob_identity_differs=True))
        calls=[]
        def forbidden_filter(label,command,**kwargs):
            calls.append(list(map(str,command))); return 'model.h: filter: forbidden-model\n'
        try: controller.canonical_git_blob('model.h',b'model',forbidden_filter,'filter-model')
        except AssertionError: pass
        else: raise AssertionError('Configured external filter must be refused before hash-object')
        assert len(calls)==1 and 'check-attr' in calls[0]
        report['external_filter_refusal_is_model']=True
        executable=Path(shutil.which('git')).resolve()
        report.update(passed=True,git=dict(path=str(executable),sha256=hashlib.sha256(executable.read_bytes()).hexdigest()),
                      python=dict(path=sys.executable,version=sys.version),source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (CONTROLLER,Path(__file__).resolve())})
    finally: save()
    print(json.dumps(dict(passed=report['passed'],actual_clean_CRLF_cases=len(report['cases']),
                         real_source_edit_negatives=len(report['cases']),external_filter_model_refused=True,
                         SDK_or_compiler_started=False,production_modified=False,git_objects_written=False),indent=2))


if __name__=='__main__': main()

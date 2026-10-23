"""Require real native assertions to reject unsafe integrated photo write policies."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

PROJECT=Path(__file__).resolve().parents[1]
ROOT=PROJECT.parents[1]


def sha(path):
    """Pin compiler inputs and every executed binary, including copied mutants."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    """Reuse the successful native link recipe; never modify production sources."""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    native=ROOT/'.build/small-tv-esp32c2/native-tests'
    recipe=(native/'compile.cmd').read_text()
    cases={
        'ignore_user_limit':('app/media/photo_codec.c',
            '(uint64_t)settings_jpeg_write_limit_kib()*1024u','UINT64_C(16000000)'),
        'erase_at_zero':('app/media/photo_codec.c',
            'program_limit,program_limit ? 4096:0,','program_limit,4096,'),
        'forget_invalidation_traffic':('app/media/photo_upload.c',
            'upload.cache_program_bytes=diagnostic->program_bytes;','upload.cache_program_bytes=0;'),
        'lose_cumulative_diagnostic':('app/media/photo_codec.c',
            'codec.prior_program_bytes=prior_program_bytes;','codec.prior_program_bytes=0;'),
        'retry_failed_budget_forever':('app/media/photo_worker.c',
            'bool permanent=diagnostic.write_limit ||','bool permanent=false ||'),
        'never_retry_after_increase':('app/media/photo_worker.c',
            'write_limit<=failed_write_limits[slot]','true'),
    }
    files=[p for name in ('app','codec','storage','tests/stubs') for p in (PROJECT/name).rglob('*') if p.is_file()]
    files += [PROJECT/'tests/native_test.c',PROJECT/'tests/native_photo_platform.c',*[p for p in (PROJECT/'tests').glob('*.inc')],Path(__file__),native/'compile.cmd']
    files += [p for p in (native/'resources').glob('*') if p.is_file()]
    selection=native/'jpeg-library/selection.json'
    library=Path(json.loads(selection.read_text())['build_directory'])/'library/jpeg-static.lib'
    files += [selection,library]
    report=dict(passed=False,cases=[],inputs_sha256={str(p.resolve()):sha(p) for p in files})
    try:
        for name,mutation in [('control',None),*cases.items()]:
            folder=(args.output/name).resolve();folder.mkdir()
            command=recipe.replace(str(native.resolve()),str(folder))
            # Keep original generated headers/library paths while directing
            # intermediate .obj/.lib and the executable to this isolated folder.
            command=command.replace(str(folder/'resources'),str(native/'resources'))
            command=command.replace(str(folder/'jpeg-library'),str(native/'jpeg-library'))
            command=command.replace('cl ',f'cl /I"{PROJECT / "app/media"}" ',1)
            command=command.replace('\ncl ','\nwhere cl > compiler-path.txt\ncl ',1)
            if mutation:
                relative,before,after=mutation;source=PROJECT/relative;text=source.read_text()
                expected=2 if name in ('never_retry_after_increase','ignore_user_limit') else 1
                assert text.count(before)==expected,name
                copied=folder/source.name;copied.write_text(text.replace(before,after),encoding='utf-8',newline='\n')
                original='"'+str(source.resolve())+'"';assert command.count(original)==1
                command=command.replace(original,'"'+str(copied)+'"')
            batch=folder/'compile.cmd';batch.write_text(command,encoding='utf-8',newline='\r\n')
            compiled=subprocess.run(['cmd.exe','/d','/c',str(batch)],capture_output=True,timeout=120)
            (folder/'compile.log').write_bytes(compiled.stdout+compiled.stderr)
            assert compiled.returncode==0,'Compile failure is not mutant rejection: '+name
            executable=folder/'native_test.exe'
            ran=subprocess.run([str(executable),str(native/'resources/assets.bin'),str(folder/'native-report.json'),
                str(PROJECT/'tests/fixtures/jpeg_extended')],capture_output=True,timeout=90)
            (folder/'run.log').write_bytes(ran.stdout+ran.stderr)
            if mutation:assert ran.returncode==1 and b'Check failed at ' in ran.stderr,'Unsafe policy escaped: '+name
            else:assert ran.returncode==0 and b'PASS:' in ran.stdout
            report['cases'].append(dict(name=name,exit_code=ran.returncode,executable_sha256=sha(executable),
                compiler_sha256=sha(Path((folder/'compiler-path.txt').read_text().splitlines()[0])),
                assertion=ran.stderr.decode(errors='replace').strip()))
            print('REJECTED integrated write-budget mutant:' if mutation else 'PASS integrated control:',name,flush=True)
        report['passed']=True
    finally:
        report['inputs_unchanged']=all(sha(Path(p))==digest for p,digest in report['inputs_sha256'].items())
        report['passed'] &= report['inputs_unchanged']
        (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':main()

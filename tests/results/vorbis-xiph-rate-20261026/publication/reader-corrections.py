"""Prove the exact reader-only fixes while retaining the immutable captures."""
import hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'tests/results/vorbis-xiph-rate-20261026'
PUBLICATION=ROOT/'.build/vorbis-xiph-rate-publication-20261026-01'
sha=lambda body:hashlib.sha256(body).hexdigest()
archive=RESULT/'captures.zip';pin=json.loads((RESULT/'archive.json').read_bytes())
assert sha(archive.read_bytes())==pin['sha256']
with zipfile.ZipFile(archive)as saved:initial=saved.read('sources/tests/verify-vorbis-xiph-rate-checkpoint.py')
current=(ROOT/'tests/verify-vorbis-xiph-rate-checkpoint.py').read_bytes();body=initial;steps=[]
def group(label,replacements,receipt):
    global body
    before_hash=sha(body)
    for before,after in replacements:
        before,after=before.encode(),after.encode();assert body.count(before)==1,(label,before)
        body=body.replace(before,after,1)
    observed=json.loads((PUBLICATION/(receipt+'.json')).read_bytes())
    steps.append(dict(label=label,before_sha256=before_hash,after_sha256=sha(body),preceding_failure_receipt=receipt+'.json',preceding_failure_exit=observed['returncode']))
group('Correct one transcribed ABI runner hash',[
    ('5c0dc723d0d6e125c5fa13023bff5c32acdd5942fc2654815fb241f9fb93879e4','5c0dc723d0d6e125c5fa13023bff5c32acd5942fc2654815fb241f9fb93879e4')], 'verify')
group('Parse the sdkconfig CRLF text view consistently',[
    ("    config = read('native/sdkconfig').decode()",r"    config = read('native/sdkconfig').decode().replace('\r\n', '\n')")], 'verify-final')
group('Keep generated-record path distinct from later tool-path loop variable',[
    ("    path = report['generated_porting']['path']","    porting_path = report['generated_porting']['path']"),
    ("    need(canonical(path) and path.endswith('/PORTING.json') and sha(read('native/' + path)) == report['generated_porting']['sha256'],","    need(canonical(porting_path) and porting_path.endswith('/PORTING.json') and sha(read('native/' + porting_path)) == report['generated_porting']['sha256'],"),
    ("    generated = 'native/' + path.rsplit('/', 1)[0] + '/'","    generated = 'native/' + porting_path.rsplit('/', 1)[0] + '/'"),
    ("    gen_directory = directory + '/' + path.rsplit('/', 1)[0]","    gen_directory = directory + '/' + porting_path.rsplit('/', 1)[0]")], 'verify-crlf')
group('Parse the nm CRLF text view consistently',[
    ("    symbols = read('native/symbols.stdout.log').decode()",r"    symbols = read('native/symbols.stdout.log').decode().replace('\r\n', '\n')")], 'verify-path')
assert body==current and all(step['preceding_failure_exit']==1 for step in steps)
final=json.loads((PUBLICATION/'verify-text.json').read_bytes());assert final['status']=='TERMINAL'and final['returncode']==0
record=dict(completed=True,archive_unchanged=True,archive_sha256=pin['sha256'],archived_initial_reader_sha256=sha(initial),corrected_local_reader_sha256=sha(current),exact_reader_only_transform=True,steps=steps,final_pass_receipt='verify-text.json',qualification_data_changed=False,diagnostics_removed=False,numerical_limits_changed=False)
(PUBLICATION/'reader-corrections.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
(PUBLICATION/'reader-corrections.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({key:record[key]for key in('completed','archive_unchanged','archived_initial_reader_sha256','corrected_local_reader_sha256','exact_reader_only_transform','qualification_data_changed')}))

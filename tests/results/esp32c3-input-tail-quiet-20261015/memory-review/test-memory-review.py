import hashlib,json,shutil,subprocess,sys
from pathlib import Path
dest=Path('tests/results/esp32c3-input-tail-quiet-20261015/memory-review')
assert not dest.exists();dest.mkdir()
tests=['test-heap-trend.py','test-sustained-output.py','test-public-file-acceptance.py',
       'test-production-health.py','test-quiet-file-gates.py','test-quiet-public-gates.py']
tmp=Path('.build/c3-input-tail-quiet-20261015/tmp').resolve();tmp.mkdir(exist_ok=True)
results=[]
for name in tests:
    code='import tempfile,runpy; tempfile.tempdir='+repr(str(tmp))+';runpy.run_path('+repr('tests/'+name)+',run_name="__main__")'
    p=subprocess.run([sys.executable,'-B','-c',code],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (dest/(name+'.log')).write_bytes(p.stdout)
    results.append(dict(test=name,exit_code=p.returncode));print(name,p.returncode,flush=True)
assert all(r['exit_code']==0 for r in results)
(dest/'host-tests.json').write_text(json.dumps(results,indent=2)+'\n')
shutil.copyfile('.build/c3-input-tail-quiet-20261015/memory-review.json',dest/'review.json')
names=['tools/esp32c3_tests/'+n for n in ('heap_trend.py','review_finite_memory.py','sustained_output.py')]+['tests/'+n for n in tests]
for name in names:
    target=dest/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(name,target)
shutil.copyfile(__file__,dest/'test-memory-review.py')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
hashes={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()}
(dest/'sha256.json').write_text(json.dumps(hashes,indent=2)+'\n')

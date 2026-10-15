import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-read512-20261015');dest=Path('tests/results/esp32c3-read512-20261015/host')
assert not dest.exists();dest.mkdir(parents=True)
sources=set()
for name in ('reader','task512','task2048'):
    folder=base/name;report=json.loads((folder/'report.json').read_text())
    assert report.get('passed') or report.get('result')=='PASS'
    for key in ('source_sha256','sources_sha256'):
        for filename,digest in report.get(key,{}).items():
            p=Path(filename);assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,p;sources.add(p)
    target=dest/name;target.mkdir()
    for p in folder.iterdir():
        if p.suffix in ('.log','.json'):shutil.copyfile(p,target/p.name)
sources.add(Path('idf/esp32c3-oled-native/main/Kconfig.projbuild'))
for p in sources:
    target=dest/'sources'/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
shutil.copyfile(__file__,dest/'freeze-host.py')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Saved exact host-test sources and results')

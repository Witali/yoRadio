import hashlib,json,shutil,subprocess,sys
from pathlib import Path
base=Path('.build/c3-decode-probe-20261015')
dest=Path('tests/results/esp32c3-decode-probe-20261015/host')
assert not dest.exists();dest.mkdir(parents=True)
sources=set()
for name in ('health-native','terminal','drain','reader','output'):
    folder=base/name;report=json.loads((folder/'report.json').read_text())
    for key in ('sources','source_sha256','sources_sha256'):
        for filename,digest in report.get(key,{}).items():
            p=Path(filename);assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,p
            sources.add(p)
    target=dest/name;target.mkdir()
    for p in folder.iterdir():
        if p.suffix in ('.log','.json'):shutil.copyfile(p,target/p.name)
for name in ('test-pipeline-health.py','test-production-health.py'):
    p=Path('tests')/name
    run=subprocess.run([sys.executable,'-B',str(p)],capture_output=True)
    (dest/(name+'.log')).write_bytes(run.stdout+run.stderr);assert run.returncode==0
    sources.add(p)
for name in ('production_health.py','pipeline_probe.py','common.py'):
    sources.add(Path('tools/esp32c3_tests')/name)
for p in sources:
    target=dest/'sources'/p;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
shutil.copyfile(__file__,dest/'freeze-host.py')
(dest/'README.md').write_text('''# Decoder work diagnostic host verification

Six health-handler configurations pass ASan/UBSan (watchdog, diagnostics,
adaptive input and optional shared arena). Maximal serialized event durations
and optional counters fit the bounded JSON buffer. Twenty custom-decoder
terminal cases, thirty generic drain cases, twenty output boundary cases and
89 HTTP/TLS reader cases pass. Python validation: seven pipeline and thirteen
health tests pass. No physical timing or audio-quality claim follows.

The initial sandboxed WSL launch was denied by the host environment; rerunning
with host access passed. An initial reader invocation omitted its required
--idf argument and was corrected before the recorded test run.
''')
(dest/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(dest/'sha256.json').write_text(json.dumps({p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(dest.rglob('*')) if p.is_file()},indent=2)+'\n')
print('Host evidence and exact sources saved')

import hashlib,json,shutil
from pathlib import Path
base=Path('.build/c3-raw-tail-quiet-20261015')
out=Path('tests/results/esp32c3-raw-tail-quiet-20261015/final-deployment-import-failure')
assert not out.exists()
c=json.loads((base/'final-deployment/controller.json').read_text())
assert c['restored']['stopped'] and all(c['restored']['settings'].values())
assert c['restored']['identity']['app_elf_sha256']==c['original']['app_elf_sha256']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(base/'final-deploy.py')==c['controller_sha256']
assert sha(base/'final-smoke.py')==c['smoke_sha256']
shutil.copytree(base/'final-deployment',out)
for name in ('final-deploy.py','final-smoke.py','prepare-final-retry.py'):shutil.copyfile(base/name,out/name)
(out/'failure.json').write_text(json.dumps(dict(stage='Smoke runner import, before playback',
    error='ModuleNotFoundError: No module named audio_test_server',
    cause='common imports the tools directory; the new runner imported audio_test_server before common',
    firmware_fault_observed=False,scope='Test harness failure; no playback qualification was executed. Rollback succeeded.'),indent=2)+'\n')
(out/'.gitattributes').write_text('* -text whitespace=cr-at-eol,-blank-at-eof,-blank-at-eol\n')
(out/'sha256.json').write_text(json.dumps({p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*')) if p.is_file()},indent=2)+'\n')
s=(base/'final-smoke.py').read_text().replace("sys.path.insert(0,'tools/esp32c3_tests')", "sys.path.insert(0,'tools/esp32c3_tests')\nimport common  # Adds the shared tools directory before server imports.")
s=s.replace("base/'final-deployment'", "base/'final-deployment-repeat'")
(base/'final-smoke-v2.py').write_text(s)
s=(base/'final-deploy.py').read_text().replace("base/'final-deployment'", "base/'final-deployment-repeat'")
s=s.replace('final-smoke.py','final-smoke-v2.py')
(base/'final-deploy-v2.py').write_text(s)
print('Archived failed harness and verified rollback; prepared corrected retry')

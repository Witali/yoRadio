from pathlib import Path
root=Path('.build/c3-production-radio-opus')
s=(root/'review.py').read_text(encoding='utf-8')
s=s.replace("sys.path.insert(0,'tools/esp32c3_tests')", "sys.path.insert(0,str(Path(__file__).resolve().parent/'test-sources/tools/esp32c3_tests'))")
s=s.replace("assert sha(Path(name).read_bytes())==digest and sha((ROOT/'test-sources'/name).read_bytes())==digest,name", "assert sha((ROOT/'test-sources'/name).read_bytes())==digest,name")
s=s.replace("spec=fixtures(ROOT/'fixtures/manifest.json')['stress-opus-48000-2ch-16bit-90s']", "spec=json.loads((ROOT/'fixtures/manifest.json').read_text())['fixtures'][0]\nspec['label']='OGG'")
s=s.replace("(ROOT/'review.json').write_text(json.dumps(review,indent=2)+'\\n');print(json.dumps(review,indent=2))", "assert review==json.loads((ROOT/'review.json').read_text()),'Offline replay differs'\n(ROOT/'offline-review.json').write_text(json.dumps(review,indent=2)+'\\n');print('Offline replay matches original review')")
(root/'offline_replay.py').write_text(s,encoding='utf-8')
for name in ('freeze.py','verify_commit.py'):
    s=Path('.build/c3-production-radio-mp3-http',name).read_text(encoding='utf-8').replace('tests/results/esp32c3-production-radio-mp3-http','tests/results/esp32c3-production-radio-opus')
    (root/name).write_text(s,encoding='utf-8')

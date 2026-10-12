from pathlib import Path
root=Path(__file__).resolve().parent
s=(root/'review.py').read_text(encoding='utf-8')
s=s.replace("sys.path.insert(0,'tools/esp32c3_tests')", "sys.path.insert(0,str(Path(__file__).resolve().parent/'test-sources/tools/esp32c3_tests'))")
s=s.replace("    assert sha(Path(name).read_bytes())==digest,name\n",'')
s=s.replace("(ROOT/'review.json').write_text(json.dumps(result,indent=2)+'\\n')", "assert result==json.loads((ROOT/'review.json').read_text()),'Offline replay differs'\n(ROOT/'offline-review.json').write_text(json.dumps(result,indent=2)+'\\n')")
(root/'offline_replay.py').write_text(s,encoding='utf-8')
print('Prepared frozen-source replay')

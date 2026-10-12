from pathlib import Path
root=Path('.build/c3-production-radio-regression');old=Path('.build/c3-http-buffer-regression')
text=(old/'run.py').read_text().replace('esp32c3-idf-6.1-r9a97-quiet-http-txrelease','esp32c3-idf-6.1-r9a97-production-radio')
text=text.replace("require(not OUT.exists(),'Preserve evidence')", "require(not OUT.exists(),'Preserve evidence')\nrequire(json.loads(Path('.build/c3-production-radio/production-radio/build-audit.json').read_text())['result']=='PASS','Build audit missing')")
(root/'run.py').write_text(text)
(root/'review.py').write_text((old/'review.py').read_text())
print('Prepared production-candidate 33-case controller and replay; not started')

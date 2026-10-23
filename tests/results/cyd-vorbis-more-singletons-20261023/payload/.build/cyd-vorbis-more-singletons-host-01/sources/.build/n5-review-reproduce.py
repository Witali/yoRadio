import hashlib,json,pathlib,os,subprocess
root=pathlib.Path.cwd();out=root/'.build/n5-independent-review-01'
source=root/'tests/cyd-native-page.test.js';raw=source.read_bytes()
snapshot=out/'sources/tests/cyd-native-page.test.js';snapshot.parent.mkdir(parents=True,exist_ok=True);snapshot.write_bytes(raw)
report=json.loads((out/'review.json').read_text(encoding='utf-8'))
report['source_sha256']['tests/cyd-native-page.test.js']=hashlib.sha256(raw).hexdigest()
test=out/'stale-timer-reproduction.test.js'
suffix="""
test('independent review: successful timer save cannot leave disabled status after refresh failure', async () => {
  const h=harness(false,networkSettingsCaps);await tick();
  assert.match(h.element('network-timeout-status').textContent,/перезапуск отключён/);
  h.element('network-hostname').value='yoradio';h.element('network-ap-timeout').value='1';
  h.element('network-settings-form').listeners.input();h.failNetworkSettingsGet('Snapshot busy');
  submit(h,'network-settings');
  await waitFor(()=>h.element('network-settings-status').textContent==='Настройки сохранены; состояние пока недоступно');
  assert.equal(h.networkSettings.ap_timeout_minutes,1);
  assert.doesNotMatch(h.element('network-timeout-status').textContent,/перезапуск отключён/);
});
"""
test.write_text(raw.decode('utf-8')+suffix,encoding='utf-8')
env=os.environ.copy();env['CYD_NATIVE_PAGE_SOURCE']=str(out/'sources/idf/esp32-cyd2usb-native/main/web_pages.cpp')
command=['C:/Program Files/nodejs/node.exe','--test','--test-reporter=tap','--test-name-pattern','^independent review:',str(test)]
result=subprocess.run(command,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=30)
(out/'stale-timer-reproduction.log').write_bytes(result.stdout)
assert result.returncode!=0 and b'AssertionError' in result.stdout and b'undisabled' not in result.stdout,result.stdout
report['findings']=[{'id':'N5-UI-01','priority':'P2','file':'idf/esp32-cyd2usb-native/main/web_pages.cpp','line':439,'end_line':442,'title':'Invalidate prior AP timer status when the post-save refresh fails','scenario':'Boot desired AP timeout is 0 and the UI shows automatic restart disabled. Save timeout=1 (or another nonzero value), POST succeeds durably, then its forced GET fails. The catch changes only network-settings-status; network-timeout-status continues to claim automatic restart is disabled even though the owner can arm and restart. The reverse transition can retain an old active countdown.','requested_change':'For the matching request epoch, clear or replace the separate timer label with an unavailable/pending status in this catch, and add an actual page-script regression for a successful timeout change followed by failed refresh.','evidence':'stale-timer-reproduction.log','reproduction_exit_status':result.returncode,'status':'reported to parent; web agent fixing'}]
report['reproduction']={'command':command,'source':'stale-timer-reproduction.test.js','sha256':hashlib.sha256(test.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(result.stdout).hexdigest(),'exit_status':result.returncode}
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Reproduced stale timer label after successful durable save and failed forced GET')

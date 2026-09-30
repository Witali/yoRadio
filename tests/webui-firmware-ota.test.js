const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const vm = require('node:vm'), zlib = require('node:zlib');
const source = zlib.gunzipSync(fs.readFileSync(path.join(__dirname,
  '../yoRadio/data/www/script.js.gz'))).toString();
const code = source.slice(source.indexOf('var firmwareUploading = false;'),
  source.indexOf('/** UPDATE **/', source.indexOf('var firmwareUploading = false;')));
function setup(capabilities={}) {
  const nodes = {}, timers=[], requests=[], fields=[], hidden=[];
  for(const id of ['uploadtype1','uploadtype2','uploadstatus','binfile',
      'updateform','updateprogress','update_cancel_button','version']) {
    nodes[id]={checked:id==='uploadtype1',files:[{size:1024}],hidden:false,
      attr(key,value){this[key]=value;},closest(){return {classList:{add:n=>hidden.push(n)}}}};
  }
  class XHR {
    constructor(){this.handlers={};this.upload={addEventListener:()=>{}};requests.push(this);}
    addEventListener(event,fn){this.handlers[event]=fn;}
    open(...args){this.opened=args;}
    send(form){this.form=form;}
    finish(status,responseText){this.status=status;this.responseText=responseText;this.handlers.load({target:this});}
  }
  const context={...capabilities,getId:id=>nodes[id], XMLHttpRequest:XHR,
    FormData:class {append(...pair){fields.push(pair)}},alert:msg=>{context.alerted=msg},
    pathname:'/update.html',location:{}, uiResource:s=>s,
    setTimeout:(fn,ms)=>timers.push({fn,ms}), clearTimeout:()=>{}, AbortSignal,
    fetch:async()=>({ok:true,json:async()=>({version:'test-v2',max_size:1900544})})};
  vm.createContext(context); vm.runInContext(code,context);
  return {context,nodes,timers,requests,fields,hidden};
}
test('original Arduino/CYD firmware and SPIFFS choices keep the shared POST contract',()=>{
  for(const firmware of [true,false]) {
    const t=setup(); t.context.configureFirmwareUpdate(); assert.equal(t.hidden.length,0);
    t.nodes.uploadtype1.checked=firmware; t.context.doUpdate();
    assert.deepEqual(t.fields.map(x=>x[0]),['updatetarget','update']);
    assert.equal(t.fields[0][1],firmware?'firmware':'spiffs');
    assert.deepEqual(t.requests[0].opened,['POST','/update',true]);
    t.requests[0].finish(200,'OK');
    assert.match(t.nodes.uploadstatus.textContent,/rebooting/);
    assert.ok(t.timers.some(x=>x.ms===200));
  }
});
test('native C3 and ESP8266 use the same form with their own app.bin label',()=>{
  for(const board of [undefined,'ESP32-C3 OLED native']) {
    const t=setup({nativeFirmwareOnly:true,...(board?{nativeFirmwareName:board}:{})});
    t.context.configureFirmwareUpdate();
    assert.equal(t.hidden.length,1); assert.equal(t.nodes.uploadtype1.checked,true);
    assert.equal(t.nodes.binfile.accept,'.bin');
    assert.ok(t.nodes.uploadstatus.textContent.includes(board || 'ESP8266 native'));
  }
});
test('HTTP failures, legacy Arduino errors, network errors, aborts and timeouts allow retry',()=>{
  for(const failure of ['status','legacy','error','abort','timeout']) {
    const t=setup(); t.context.doUpdate();
    if(failure==='status') t.requests[0].finish(500,'OK');
    else if(failure==='legacy') t.requests[0].finish(200,'<b>Invalid image</b>');
    else t.requests[0].handlers[failure]({target:t.requests[0]});
    assert.equal(t.context.firmwareUploading,false);
    assert.equal(t.nodes.updateform.class,'');
    assert.equal(t.nodes.update_cancel_button.hidden,false);
    assert.equal(t.nodes.updateprogress.hidden,true);
    assert.equal(t.timers.length,0);
    if(failure==='legacy') assert.equal(t.nodes.uploadstatus.textContent,'<b>Invalid image</b>');
    t.context.doUpdate(); assert.equal(t.requests.length,2);
  }
});
test('C3 polling keeps the selection page awake and pauses during upload',async()=>{
  const t=setup({nativeFirmwareOnly:true,nativeFirmwareName:'ESP32-C3 OLED native',
    nativeFirmwareInfo:'/api/native/ota'});
  let calls=0; t.context.fetch=async(url)=>{
    assert.equal(url,'/api/native/ota'); ++calls;
    return {ok:true,json:async()=>({version:'test-v2',max_size:1900544})};
  };
  t.context.configureFirmwareUpdate(); await new Promise(setImmediate);
  assert.equal(calls,1); assert.equal(t.nodes.version.textContent,' | test-v2');
  assert.equal(t.timers[0].ms,5000);
  t.context.doUpdate(); t.timers[0].fn(); await new Promise(setImmediate);
  assert.equal(calls,1);
});
test('empty or too-large files are rejected before sending',()=>{
  for(const size of [0,1900545]) {
    const t=setup(); t.context.firmwareInfo={max_size:1900544};
    t.nodes.binfile.files[0].size=size; t.context.doUpdate();
    assert.equal(t.requests.length,0); assert.match(t.nodes.uploadstatus.textContent,/non-empty app.bin/);
  }
});

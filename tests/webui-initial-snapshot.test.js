const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
const script=zlib.gunzipSync(fs.readFileSync(path.join(root,'yoRadio/data/www/script.js.gz'))).toString();
function context(enabled,pathname='/') {
  const received=[],sent=[],urls=[];
  const c={window:{location:{pathname}},hostname:'radio',playerUiReady:false,
    initialPlayerMessages:[],initialPlayerOverflow:false,clearTimeout(){},wstimeout:null,
    console:{log(){}},websocket:{send:x=>sent.push(x)},onOpen(){},onClose(){},
    WebSocket:class {constructor(url){urls.push(url);}send(x){sent.push(x);}}};
  if(enabled!==undefined)c.webSocketInitialState=enabled;
  const functions=script.slice(script.indexOf('function websocketBootstrapEnabled'),script.indexOf('function onLoad'));
  // Execute the actual queue guard independently of the unchanged DOM renderer.
  const receive=script.slice(script.indexOf('function onMessage(event)'),script.indexOf('  try{',script.indexOf('function onMessage(event)')));
  c.capture=x=>received.push(x);
  vm.createContext(c);vm.runInContext(functions+receive+'capture(event.data);}',c);
  return {c,received,sent,urls};
}
test('opted-in player receives a real bootstrap without an extra getindex round trip',()=>{
  const {c,received,sent,urls}=context(true);
  c.initWebSocket();assert.equal(urls[0],'ws://radio/ws?initial=1');
  c.onMessage({data:'status'});c.onMessage({data:'current'});
  assert.deepEqual(received,[]);c.initialPlayerStateReady();
  assert.deepEqual(received,['status','current']);assert.deepEqual(sent,[]);
  c.onMessage({data:'next'});assert.deepEqual(received,['status','current','next']);
});
test('late bootstrap, reconnect and bounded early-message overflow are handled',()=>{
  const {c,received,sent}=context(true);
  c.initialPlayerStateReady();c.onMessage({data:'late'});
  assert.deepEqual(received,['late']);assert.deepEqual(sent,[]);
  c.initWebSocket();c.onMessage({data:'reconnected'});
  assert.deepEqual(received,['late','reconnected']);assert.deepEqual(sent,[]);
  c.playerUiReady=false;
  for(let i=0;i<20;++i)c.onMessage({data:String(i)});
  assert.equal(c.initialPlayerMessages.length,16);assert.equal(c.initialPlayerOverflow,true);
  c.initialPlayerStateReady();assert.deepEqual(sent,['getindex=1']);
  assert.equal(c.initialPlayerMessages.length,0);
});
test('Arduino, other boards and settings retain the legacy request-driven protocol',()=>{
  for(const [enabled,pathname] of [[undefined,'/'],[false,'/'],[true,'/settings.html']]) {
    const {c,received,sent,urls}=context(enabled,pathname);c.initWebSocket();
    assert.equal(urls[0],'ws://radio/ws');c.onMessage({data:'legacy'});
    assert.deepEqual(received,['legacy']);c.initialPlayerStateReady();assert.deepEqual(sent,['getindex=1']);
  }
});
test('server enables snapshots only after upgrade and explicit opt-in; gzip migration is idempotent',()=>{
  const uri=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/components/esp_http_server/src/httpd_uri.c'),'utf8');
  assert.match(uri,/ws_handshake_done = true;[\s\S]*?return uri->handler\(req\)/);
  const web=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/web_service.c'),'utf8');
  const handler=web.slice(web.indexOf('static esp_err_t websocket_handler'),web.indexOf('static FILE *open_nonempty'));
  assert.match(handler,/request->method == HTTP_GET[\s\S]*?httpd_query_key_value\(query, "initial"[\s\S]*?strcmp\(initial, "1"\) == 0[\s\S]*?subscribe_socket[\s\S]*?return send_initial_state\(request\)/);
  const bytes=fs.readFileSync(path.join(root,'yoRadio/data/www/script.js.gz'));
  const run=require('node:child_process').spawnSync(process.execPath,[path.join(root,'tools/update_webui_initial_snapshot.cjs')]);
  assert.equal(run.status,0,run.stderr.toString());assert.deepEqual(fs.readFileSync(path.join(root,'yoRadio/data/www/script.js.gz')),bytes);
});

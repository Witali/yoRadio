// Idempotent migration of the shared WebUI used by Arduino/CYD and native ports.
const fs = require('node:fs'), path = require('node:path'), zlib = require('node:zlib');
const file = path.join(__dirname, '../yoRadio/data/www/script.js.gz');
let source = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
const oldSetup = `        if(typeof nativeFirmwareOnly !== 'undefined' && nativeFirmwareOnly === true){
          getId('uploadtype2').closest('label').classList.add('hidden');
          getId('uploadstatus').innerText='Choose ESP8266 native app.bin. For WebUI files use Board.';
        }`;
if (!source.includes('function configureFirmwareUpdate()')) {
  if (!source.includes(oldSetup)) throw Error('Missing shared OTA setup');
  source = source.replace(oldSetup, '        configureFirmwareUpdate();');
  const start = source.indexOf('function doUpdate(el) {');
  const end = source.indexOf('/** UPDATE **/', start);
  if (start < 0 || end < 0) throw Error('Missing shared OTA handlers');
  source = source.slice(0, start) + `var firmwareUploading = false;
var firmwareInfo = null;
function configureFirmwareUpdate(){
  if(typeof nativeFirmwareOnly !== 'undefined' && nativeFirmwareOnly === true){
    getId('uploadtype2').closest('label').classList.add('hidden');
    getId('uploadtype1').checked=true;
    const board = typeof nativeFirmwareName === 'string' ? nativeFirmwareName : 'ESP8266 native';
    getId('uploadstatus').textContent='Choose '+board+' app.bin. For WebUI files use Board.';
    getId('binfile').accept='.bin';
  }
  // C3 refreshes its idle timer while this page is open. No saved setting is
  // changed. Pause these requests during the upload, which has its own guard.
  if(typeof nativeFirmwareInfo === 'string') refreshFirmwareInfo();
}
function refreshFirmwareInfo(){
  if(firmwareUploading || pathname !== '/update.html') return;
  fetch(nativeFirmwareInfo, {cache:'no-store', signal:AbortSignal.timeout(5000)})
    .then(response => { if(!response.ok) throw Error('Radio unavailable'); return response.json(); })
    .then(info => { firmwareInfo=info; getId('version').textContent=' | '+info.version; })
    .catch(() => { if(!firmwareUploading) getId('uploadstatus').textContent='Radio unavailable. If asleep, hold BOOT for over 500 ms, release it and retry.'; })
    .finally(() => { if(!firmwareUploading) setTimeout(refreshFirmwareInfo, 5000); });
}
function firmwareUploadFailed(message){
  uploadWithError=true;
  firmwareUploading=false;
  getId('updateform').attr('class','');
  getId('updateprogress').hidden=true;
  getId('updateprogress').value=0;
  getId('update_cancel_button').hidden=false;
  getId('uploadstatus').textContent=message;
  if(typeof nativeFirmwareInfo === 'string') setTimeout(refreshFirmwareInfo, 5000);
}
function doUpdate(el) {
  const binfile = getId('binfile').files[0];
  if(!binfile){ alert('Choose something first'); return; }
  if(firmwareUploading) return;
  if(!binfile.size || (firmwareInfo && binfile.size > firmwareInfo.max_size)){
    firmwareUploadFailed('Choose a non-empty app.bin that fits this board.'); return;
  }
  firmwareUploading=true;
  getId('updateform').attr('class','hidden');
  getId('updateprogress').value=0;
  getId('updateprogress').hidden=false;
  getId('update_cancel_button').hidden=true;
  const formData = new FormData();
  formData.append('updatetarget', getId('uploadtype1').checked?'firmware':'spiffs');
  formData.append('update', binfile);
  const xhr = new XMLHttpRequest();
  uploadWithError=false;
  xhr.upload.addEventListener('progress', progressHandler, false);
  xhr.addEventListener('load', completeHandler, false);
  xhr.addEventListener('error', errorHandler, false);
  xhr.addEventListener('abort', abortHandler, false);
  xhr.addEventListener('timeout', () => firmwareUploadFailed('Upload timed out. Check the radio before retrying.'), false);
  xhr.open('POST', '/update', true);
  xhr.timeout=210000;
  xhr.send(formData);
}
function progressHandler(event) {
  if(!event.lengthComputable) return;
  const percent = Math.round(event.loaded / event.total * 100);
  getId('updateprogress').value=percent;
  getId('uploadstatus').textContent=percent >= 100 ?
    'Upload sent. Please wait for firmware verification...' : percent+'% uploaded | please wait...';
}
var tickcount=0;
function rebootingProgress(){
  getId('updateprogress').value=Math.round(tickcount/7);
  tickcount+=14;
  if(tickcount>700) location.href=uiResource('/');
  else setTimeout(rebootingProgress, 200);
}
function completeHandler(event) {
  const xhr=event.target;
  if(xhr.status < 200 || xhr.status >= 300 || xhr.responseText.trim() !== 'OK'){
    firmwareUploadFailed(xhr.responseText || 'Upload failed (HTTP '+xhr.status+').');
    return;
  }
  getId('uploadstatus').textContent='Upload complete, rebooting...';
  tickcount=0;
  rebootingProgress();
}
function errorHandler(event) { firmwareUploadFailed('Upload failed. Check the connection and retry.'); }
function abortHandler(event) { firmwareUploadFailed('Upload aborted.'); }
` + source.slice(end);
}
if (!source.includes('var firmwareInfoTimer = null;')) {
  source = source.replace('var firmwareInfo = null;', `var firmwareInfo = null;
var firmwareInfoTimer = null;
function scheduleFirmwareInfo(){
  clearTimeout(firmwareInfoTimer);
  firmwareInfoTimer=setTimeout(refreshFirmwareInfo, 5000);
}`);
  source = source.replaceAll('if(!firmwareUploading) setTimeout(refreshFirmwareInfo, 5000);',
    'if(!firmwareUploading) scheduleFirmwareInfo();');
  source = source.replaceAll("if(typeof nativeFirmwareInfo === 'string') setTimeout(refreshFirmwareInfo, 5000);",
    "if(typeof nativeFirmwareInfo === 'string') scheduleFirmwareInfo();");
  source = source.replace('  firmwareUploading=true;',
    '  firmwareUploading=true;\n  clearTimeout(firmwareInfoTimer);');
}
fs.writeFileSync(file, zlib.gzipSync(source, {level:9}));

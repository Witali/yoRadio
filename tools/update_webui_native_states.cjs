// Idempotent migration of the shared gzip-only WebUI asset.
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const file = path.join(__dirname, '../yoRadio/data/www/script.js.gz');
let source = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
const before = 'function setupElement(id,value){';
const after = before + '\n  if(id=="connecting"){ setPlaybackPending(!!value); return; }';
if(!source.includes(after)) {
  if(!source.includes(before)) throw Error('Missing setupElement');
  source = source.replace(before, after);
}
const stateHook = '  if(id=="connecting"){ setPlaybackPending(!!value); return; }';
if(!source.includes('if(id=="nativeAppearance")')) {
  source = source.replace(stateHook, stateHook + `
  if(id=="commandError"){ alert(value); return; }
  if(id=="nativeAppearance"){
    const row = getId('upst')?.closest('.flex-row');
    const system = getId('group_system');
    if(value && row && system){ row.classList.remove('hidden'); system.appendChild(row); }
    return;
  }`);
}
fs.writeFileSync(file, zlib.gzipSync(source, {level:9}));

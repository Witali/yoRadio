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
  fs.writeFileSync(file, zlib.gzipSync(source, {level:9}));
}

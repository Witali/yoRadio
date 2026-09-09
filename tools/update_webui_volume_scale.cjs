// Shared gzip-only WebUI migration. Boards opt in via volumeMax; legacy
// firmware without that capability retains its 0..254 slider/protocol.
const fs = require('node:fs');
const path = require('node:path');
const zlib = require('node:zlib');
const file = path.join(__dirname, '../yoRadio/data/www/script.js.gz');
let source = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
const anchor = 'function applyPlayerCapabilities() {';
if (!source.includes('function applyVolumeScale()')) {
  if (!source.includes(anchor)) throw Error('Missing player capabilities hook');
  source = source.replace(anchor, `function applyVolumeScale() {
  const slider = getId('volume');
  if(!slider) return;
  slider.min = '0';
  slider.max = typeof volumeMax !== 'undefined' && volumeMax === 100 ? '100' : '254';
  slider.step = '1';
}
${anchor}
  applyVolumeScale();`);
  fs.writeFileSync(file, zlib.gzipSync(source, {level: 9}));
}

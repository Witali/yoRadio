// Mechanical update of the canonical compressed shared WebUI.
const fs = require('node:fs'), zlib = require('node:zlib'), path = require('node:path');
const file = path.join(__dirname, '../yoRadio/data/www/script.js.gz');
let source = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
const original = source;
const before = 'if(typeof data.mdns !== \'undefined\'){';
const after = 'if(typeof data.mdns !== \'undefined\' && getId("radiolink")){';
if (!source.includes(after)) {
  if (source.split(before).length !== 2) throw new Error('Settings link anchor changed');
  source = source.replace(before, after);
}
const playlistBefore = 'const playlist = getId("playlist");\n  let activeItem';
const playlistAfter = 'const playlist = getId("playlist");\n  if(!playlist) return;\n  let activeItem';
if (!source.includes(playlistAfter)) {
  if (!source.includes(playlistBefore)) throw new Error('Current station anchor changed');
  source = source.replace(playlistBefore, playlistAfter);
}
if (source !== original) fs.writeFileSync(file, zlib.gzipSync(Buffer.from(source), {level: 9}));

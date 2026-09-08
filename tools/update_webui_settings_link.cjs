// Mechanical update of the canonical compressed shared WebUI.
const fs = require('node:fs'), zlib = require('node:zlib'), path = require('node:path');
const file = path.join(__dirname, '../yoRadio/data/www/script.js.gz');
const source = zlib.gunzipSync(fs.readFileSync(file)).toString('utf8');
const before = 'if(typeof data.mdns !== \'undefined\'){';
const after = 'if(typeof data.mdns !== \'undefined\' && getId("radiolink")){';
if (!source.includes(after)) {
  if (source.split(before).length !== 2) throw new Error('Settings link anchor changed');
  fs.writeFileSync(file, zlib.gzipSync(Buffer.from(source.replace(before, after)), {level: 9}));
}

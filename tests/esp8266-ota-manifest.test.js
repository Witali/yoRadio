const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {readManifest} = require('../tools/esp8266_audio_profile/check_prefill_board.cjs');

test('OTA accepts UTF-8 manifests with and without PowerShell BOM', t => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-ota-manifest-'));
  t.after(() => fs.rmSync(dir, {recursive:true, force:true}));
  const file = path.join(dir, 'manifest.json');
  const expected = {web_audio_pause:'short', bytes:760800, app_sha256:'123456'};
  for (const prefix of ['', '\uFEFF']) {
    fs.writeFileSync(file, prefix+JSON.stringify(expected));
    assert.deepEqual(readManifest(file), expected);
  }
  fs.writeFileSync(file, '\uFEFF{broken');
  assert.throws(() => readManifest(file), SyntaxError);
});

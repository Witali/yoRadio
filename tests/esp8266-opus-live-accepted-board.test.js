// Offline evidence checks. Never opens a connection to the board.
const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {summarize} = require('../tools/esp8266_opus_profile/run_stage_wall.cjs');
const {root} = require('../tools/esp8266_opus_asm/export.cjs');
const {variant} = require('../tools/esp8266_opus_asm/live_accepted.cjs');
const directory = path.join(root, 'firmware/development', variant);
const read = name => JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8'));

test('all ten ordinary radio attempts are retained and independently classified', () => {
  const rows = read('board/stations/series.json');
  assert.equal(rows.length, 10);
  for (let i = 1; i <= 10; i++) {
    const row = rows[i - 1], start = read(`board/stations/start${i}.json`);
    const window = read(`board/stations/window${i}.json`);
    const station = i % 2 ? 512 : 513;
    assert.equal(row.attempt, i); assert.equal(row.station, station);
    if (start.command) assert.equal(start.command.value, `play=${station}`);
    else assert.ok(start.error); // A failed WebSocket handshake is not a decoder failure.
    const confirmed = !!start.command?.messages.some(m => m.current === station);
    assert.equal(row.current_confirmed, confirmed);
    const result = summarize(window.samples, window.seconds);
    assert.deepEqual(window.result, result); assert.deepEqual(row.result, result);
    const audioPass = !!(result.continuity.pass && !result.profile_error);
    assert.equal(row.audio_pass, audioPass);
    assert.equal(row.pass, !!(confirmed && audioPass && !start.error));
    assert.match(result.timing_kind, /NOT CPU/);
  }
});

test('OTA used the accepted ordinary ASM image and retained playlist and final stopped state', () => {
  const ota = read('board/ota.json'), manifest = read('manifest.json');
  const initial = read('board/initial.json'), restored = read('board/restored.json');
  assert.equal(ota.sha256, manifest.app_sha256); assert.equal(ota.pass, true);
  assert.equal(ota.upload.http, 200); assert.equal(ota.upload.body, 'OK');
  assert.notEqual(ota.before.app_address, ota.after.app_address);
  assert.equal(restored.status.app_address, ota.after.app_address);
  assert.equal(restored.status.playing, false);
  const current = snapshot => snapshot.index.messages.find(m => m.current !== undefined)?.current;
  assert.equal(current(initial), 167); assert.equal(current(restored), 167);
  assert.equal(initial.playlist.wire_sha256, restored.playlist.wire_sha256);
  assert.equal(manifest.opus_benchmark, false);
});

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {report} = require('../tools/esp8266_opus_profile/report_live_stations.cjs');
const directory = path.join(__dirname, 'results/esp8266-opus-live-stations-20260917');
test('ordinary-radio results preserve every failure and recompute cumulative continuity', () => {
  const actual = report(directory);
  const saved = JSON.parse(fs.readFileSync(path.join(directory, 'report.json'), 'utf8'));
  assert.deepEqual(actual, saved);
  assert.equal(actual.windows_total, 7);
  assert.equal(actual.uninterrupted_windows, 0);
  assert.ok(actual.results.every(r => r.starts.length === 2 && r.host_decode_exit === 0));
  assert.equal(actual.restoration.station_after, 167);
  const failure = actual.results[0].diagnostic.find(r => r.route.endsWith('/opus-stream')).body;
  assert.equal(failure.stage, 10);
  assert.ok(failure.free_dram < failure.reserve_bytes);
});

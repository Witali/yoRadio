// Offline report only: never connects to or changes the board.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const {summarize} = require('./run_stage_wall.cjs');
function report(directory) {
  const read = name => JSON.parse(fs.readFileSync(path.join(directory, name), 'utf8'));
  const initial = read('initial.json'), restored = read('restored.json');
  const station = snapshot => snapshot.index.messages.find(m => m.current !== undefined)?.current;
  const results = [];
  for (const [name, ids] of [['r2rock', [2, 3]], ['plaza', [1, 2, 3, 4]]]) {
    const windows = ids.map(id => {
      const file = `${name}-sparse${id}.json`, input = read(file);
      const result = summarize(input.samples, input.seconds);
      assert.deepEqual(result, input.result, `stale result: ${file}`);
      return {file, ...result};
    });
    const starts = [1, 2].map(id => {
      const file = `${name}-start${id}.json`, input = read(file);
      return {file, command: input.command?.value, error: input.error ?? null,
        status: input.status ?? null};
    });
    const diag = read(`${name}-diagnostic.json`);
    const source = read(`${name}-stream.json`), host = read(`${name}-host-decode.json`);
    assert.equal(host.decode_exit, 0);
    results.push({name, starts, windows, source,
      host_decode_exit: host.decode_exit,
      diagnostic: diag,
      uninterrupted_windows: windows.filter(w => w.continuity.pass && !w.profile_error).length});
  }
  // Preserve the failed, more intrusive first probe. A failed status request
  // does not erase its partial health counters, but cannot qualify a window.
  const first = read('r2rock-sample1.json');
  assert.equal(first.pass, false);
  const restoration = {
    station_before: station(initial), station_after: station(restored),
    stopped: restored.status.playing === false,
    slot_unchanged: initial.status.app_address === restored.status.app_address,
    playlist_unchanged: initial.playlist.wire_sha256 === restored.playlist.wire_sha256,
    free_heap: restored.status.free_heap, minimum_heap_since_boot: restored.status.min_heap,
  };
  assert.equal(restoration.station_before, restoration.station_after);
  assert.ok(restoration.stopped && restoration.slot_unchanged && restoration.playlist_unchanged);
  return {date: initial.date, firmware: 'existing ordinary radio, C Opus backend, not raw benchmark',
    note: 'Stage percentages are elapsed wall time, not CPU utilization. No acoustic recording. Underruns are events, not silence duration.',
    results, first_probe: {file: 'r2rock-sample1.json', pass: first.pass,
      observations: first.samples.length, failures: first.samples.filter(s => s.error).length},
    windows_total: 1 + results.reduce((n, r) => n + r.windows.length, 0),
    uninterrupted_windows: results.reduce((n, r) => n + r.uninterrupted_windows, 0), restoration};
}
module.exports = {report};
if (require.main === module) {
  const directory = process.argv[2];
  if (!directory) throw Error('result directory required');
  const result = report(directory);
  fs.writeFileSync(path.join(directory, 'report.json'), JSON.stringify(result, null, 2) + '\n');
  console.log(JSON.stringify(result, null, 2));
}

const assert = require('node:assert/strict');
function verifyStates(reference, candidate, mixed = false) {
  const fields = ['samples', 'reset_exact', 'scratch_byte_peak_bytes', 'scratch_word_peak_bytes', 'scratch_byte_capacity_bytes',
    ...(mixed ? ['persistent_bytes', 'sequence_packets', 'plc_frames'] :
      ['mono_state_bytes', 'stereo_state_bytes', 'packets', 'output_channels', 'sample_rate', 'scratch_word_capacity_bytes', 'arena_guards_ok', 'oom_reinitialized_exact'])];
  for (const key of fields) {
    for (const value of [reference, candidate]) {
      assert.ok(Object.hasOwn(value, key), 'Missing host state field: ' + key);
      if (['reset_exact', 'arena_guards_ok', 'oom_reinitialized_exact'].includes(key)) assert.equal(value[key], true, key);
      else assert.ok(Number.isFinite(value[key]) && value[key] >= 0, 'Invalid host field: ' + key);
    }
    assert.deepEqual(candidate[key], reference[key], 'Changed host state: ' + key);
  }
  if (mixed) assert.ok(reference.plc_frames > 0);
  else {assert.ok(reference.mono_state_bytes > 0); assert.ok(reference.stereo_state_bytes > 0);}
}
module.exports = {verifyStates};

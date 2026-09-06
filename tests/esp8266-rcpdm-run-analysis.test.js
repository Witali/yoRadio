// Research-only model for the user's proposed constant-bit runs.
// Not compiled into firmware; speed on LX106 has NOT been measured.
const test = require('node:test');
const assert = require('node:assert/strict');
const MAX = 0xffffffff, STEP = 0x0fffffff, HALF = STEP >>> 1;
function original(state, pcm) {
  const target = (pcm + 32768) * 65536;
  let word = 0;
  for (let i = 0; i < 32; ++i) {
    const down = state - (state >>> 4);
    const high = target > down + HALF;
    state = down + (high ? STEP : 0);
    word = ((word << 1) | Number(high)) >>> 0;
  }
  return [state, word];
}
function grouped(state, pcm, count) {
  const target = (pcm + 32768) * 65536;
  const guard = count * STEP - HALF;
  let left = 32, word = 0;
  while (left) {
    const high = target >= state;
    const difference = high ? target - state : state - target;
    if (left >= count && difference >= guard) {
      let distance = high ? MAX - state : state;
      for (let i = 0; i < count; ++i) distance -= distance >>> 4;
      state = high ? MAX - distance : distance;
      word = ((word << count) | (high ? 2 ** count - 1 : 0)) >>> 0;
      left -= count;
    } else {
      const down = state - (state >>> 4);
      const bit = target > down + HALF;
      state = down + (bit ? STEP : 0);
      word = ((word << 1) | Number(bit)) >>> 0;
      --left;
    }
  }
  return [state, word];
}
test('sufficient bounds for 2/4/8 constant bits preserve every word and RC state', () => {
  let checked = 0;
  function check(state, pcm) {
    const expected = original(state, pcm);
    for (const count of [2, 4, 8]) {
      const actual = grouped(state, pcm, count);
      assert.ok(actual[0] === expected[0] && actual[1] === expected[1]);
      ++checked;
    }
    return expected[0];
  }
  for (const state of [0, 1, 15, 0x80000000, MAX - 15, MAX])
    for (let pcm = -32768; pcm < 32768; ++pcm) check(state, pcm);
  let state = 0x80000000, random = 1;
  for (let i = 0; i < 100000; ++i) {
    random = (Math.imul(random, 1664525) + 1013904223) >>> 0;
    state = check(state, (random & 65535) - 32768);
  }
  assert.equal(checked, 1479648);
  assert.equal(4 * STEP - HALF, 939524093);
});

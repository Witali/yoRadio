const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const root = path.resolve(__dirname, "..");
const read = (...parts) => fs.readFileSync(path.join(root, ...parts), "utf8");

const signed32 = (value) => BigInt.asIntN(32, BigInt(value));
const unsigned64 = (value) => BigInt.asUintN(64, value);

function optimizedHigh(x, y) {
  const sx = Number(BigInt.asIntN(32, BigInt(x)));
  const sy = Number(BigInt.asIntN(32, BigInt(y)));
  const xHi = sx >> 16;
  const yHi = sy >> 16;
  const xLo = sx & 0xffff;
  const yLo = sy & 0xffff;
  const low = Math.imul(xLo, yLo) >>> 0;
  const cross0 = (Math.imul(xHi, yLo) + (low >>> 16)) | 0;
  const cross1 = (Math.imul(yHi, xLo) + (cross0 & 0xffff)) | 0;
  return (Math.imul(xHi, yHi) + (cross0 >> 16) + (cross1 >> 16)) | 0;
}

function optimizedUnsignedHigh(x, y) {
  const ux = x >>> 0;
  const uy = y >>> 0;
  const xHi = ux >>> 16;
  const yHi = uy >>> 16;
  const xLo = ux & 0xffff;
  const yLo = uy & 0xffff;
  const low = Math.imul(xLo, yLo) >>> 0;
  const cross0 = (Math.imul(xHi, yLo) + (low >>> 16)) >>> 0;
  const cross1 = (Math.imul(yHi, xLo) + (cross0 & 0xffff)) >>> 0;
  return (Math.imul(xHi, yHi) + (cross0 >>> 16) + (cross1 >>> 16)) >>> 0;
}

function reciprocalDivide(value, divisor) {
  const reciprocal = Number((2n ** 32n) / BigInt(divisor) + 1n);
  let quotient = optimizedUnsignedHigh(value, reciprocal);
  if (quotient * divisor > (value >>> 0)) --quotient;
  return quotient >>> 0;
}

test("LX106 high-half multiply is exact for edge and deterministic random inputs", () => {
  const values = [
    -0x80000000, -0x7fffffff, -0x10001, -0x10000, -1, 0, 1,
    0x7fff, 0x8000, 0xffff, 0x10000, 0x7fffffff,
  ];
  let state = 0x8266c0de;
  for (let index = 0; index < 20000; ++index) {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    values.push(state | 0);
  }

  for (let index = 0; index + 1 < values.length; index += 2) {
    const x = values[index];
    const y = values[index + 1];
    const reference = Number(BigInt.asIntN(32, (signed32(x) * signed32(y)) >> 32n));
    assert.equal(optimizedHigh(x, y), reference, `${x} * ${y}`);

    const sum = unsigned64(BigInt(index) * 0x9e3779b97f4a7c15n);
    const optimizedProduct =
      (BigInt(optimizedHigh(x, y) >>> 0) << 32n) |
      BigInt(Math.imul(x, y) >>> 0);
    assert.equal(
      unsigned64(sum + optimizedProduct),
      unsigned64(sum + signed32(x) * signed32(y)),
      `madd ${x} * ${y}`,
    );
  }
});

test("LX106 Q32 reciprocal division is exact for MP3 divisors", () => {
  const values = [
    0, 1, 2, 3, 4, 5, 6, 17, 18, 35, 36, 37,
    0x7fffffff, 0xfffffffe, 0xffffffff,
  ];
  let state = 0x1d1f1de;
  for (let index = 0; index < 50000; ++index) {
    state = (Math.imul(state, 1664525) + 1013904223) >>> 0;
    values.push(state);
  }

  for (const divisor of [3, 5, 6, 18, 36]) {
    for (const value of values) {
      assert.equal(
        reciprocalDivide(value, divisor),
        Math.floor((value >>> 0) / divisor),
        `${value >>> 0} / ${divisor}`,
      );
    }
  }
});

test("ESP8266 Helix decoders use the shared non-64-bit multiply helper", () => {
  const helper = read("yoRadio", "src", "audioI2S", "helix_lx106_fixed.h");
  const mp3 = read("yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.h");
  const mp3Source = read(
    "yoRadio", "src", "audioI2S", "mp3_decoder", "mp3_decoder.cpp",
  );
  const aac = read("yoRadio", "src", "audioI2S", "aac_decoder", "aac_decoder.cpp");
  const cmake = read(
    "esp8266", "rtos-sdk-native", "components", "helix_codecs", "CMakeLists.txt",
  );

  assert.match(helper, /helix_lx106_mulshift32/);
  assert.match(helper, /helix_lx106_madd64/);
  assert.match(helper, /helix_lx106_udiv_recip/);
  assert.doesNotMatch(helper, /int64_t\)x\s*\*/);
  assert.match(mp3, /YORADIO_ESP8266_NATIVE[\s\S]*helix_lx106_mulshift32/);
  assert.match(cmake, /YORADIO_ESP8266_HELIX_RECIPROCAL_DIVIDE[\s\S]*ON/);
  assert.match(mp3Source, /YORADIO_ESP8266_HELIX_RECIPROCAL_DIVIDE/);
  assert.match(aac, /YORADIO_ESP8266_NATIVE[\s\S]*helix_lx106_mulshift32/);
  assert.match(
    aac,
    /YORADIO_ESP8266_NATIVE[\s\S]*m_AACDecInfo->sampRate[\s\S]*frameBytes\) \/ 128U/,
  );
});

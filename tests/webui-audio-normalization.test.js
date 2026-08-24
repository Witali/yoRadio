const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const optionsPath = path.join(
  __dirname,
  "..",
  "yoRadio",
  "data",
  "www",
  "options.html.gz"
);

function optionsHtml() {
  return zlib.gunzipSync(fs.readFileSync(optionsPath)).toString("utf8");
}

test("settings expose automatic sound normalization", () => {
  const html = optionsHtml();

  assert.match(
    html,
    /id="normalize"[^>]*data-command="normalization"/,
    "normalization toggle is missing"
  );
});

test("settings constrain maximum normalization boost to 0..20 dB", () => {
  const html = optionsHtml();
  const gainInput = html.match(/<input[^>]*id="normgain"[^>]*>/)?.[0];

  assert.ok(gainInput, "maximum boost input is missing");
  assert.match(gainInput, /data-command="normgain"/);
  assert.match(gainInput, /min="0"/);
  assert.match(gainInput, /max="20"/);
  assert.match(gainInput, /step="1"/);
});

test("settings expose target peak level and symmetric time constant", () => {
  const html = optionsHtml();
  const targetInput = html.match(/<input[^>]*id="normtarget"[^>]*>/)?.[0];
  const timeInput = html.match(/<input[^>]*id="normtime"[^>]*>/)?.[0];

  assert.ok(targetInput, "normalization target input is missing");
  assert.match(targetInput, /data-command="normtarget"/);
  assert.match(targetInput, /value="-3"/);
  assert.match(targetInput, /min="-20"/);
  assert.match(targetInput, /max="0"/);

  assert.ok(timeInput, "normalization time input is missing");
  assert.match(timeInput, /data-command="normtime"/);
  assert.match(timeInput, /value="5000"/);
  assert.match(timeInput, /min="100"/);
  assert.match(timeInput, /max="10000"/);
});

test("normalizer precomputes one smoothing interval for both directions", () => {
  const source = fs.readFileSync(
    path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "AudioNormalizer.cpp"),
    "utf8"
  );

  assert.match(source, /m_targetPeak/);
  assert.match(source, /m_smoothingBlocks/);
  assert.match(source, /moveTowards\(m_gainQ12, targetGain, m_smoothingBlocks\)/);
  assert.doesNotMatch(source, /targetGain < m_gainQ12 \?/);
  assert.doesNotMatch(source, /attackSamples/);
});

test("normalizer hot path uses a division-free inline fixed-point limiter", () => {
  const source = fs.readFileSync(
    path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "AudioNormalizer.cpp"),
    "utf8"
  );
  const header = fs.readFileSync(
    path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "AudioNormalizer.h"),
    "utf8"
  );
  const processBody = header.match(
    /void processEnabled\(int16_t sample\[2\]\) \{([\s\S]*?)\n    \}/
  )?.[1];
  const limiterBody = header.match(
    /static int16_t softLimit\(int32_t value\) \{([\s\S]*?)\n    \}/
  )?.[1];
  const targetBody = source.match(
    /void AudioNormalizer::updateGainTarget\(\) \{([\s\S]*?)\n\}/
  )?.[1];

  assert.ok(processBody, "normalizer inline process body is missing");
  assert.ok(limiterBody, "inline soft limiter body is missing");
  assert.ok(targetBody, "gain target body is missing");
  assert.match(processBody, /\* m_gainQ12\) >> 12/);
  assert.doesNotMatch(processBody, /int64_t/);
  assert.doesNotMatch(limiterBody, /int64_t/);
  assert.doesNotMatch(limiterBody, /\//);
  assert.match(limiterBody, /kSoftLimitLutStepShift/);
  assert.match(limiterBody, /\* fraction \+ rounding\) >>/);
  assert.match(source, /soft limiter numerator must fit in int32_t/);
  assert.match(source, /std::make_index_sequence<kSoftLimitLutEntries>/);
  assert.doesNotMatch(targetBody, /uint64_t/);
  assert.match(source, /enabled == m_enabled[\s\S]*return;/);
  assert.match(source, /AudioNormalizer::processBlock/);
  assert.match(source, /processEnabled\(stereo\)/);
});

test("soft limiter LUT interpolation stays within 13 PCM levels", () => {
  const knee = 28672;
  const remaining = 32767 - knee;
  const maximum = 327680;
  const step = 1 << 9;
  const exact = magnitude => magnitude <= knee
    ? magnitude
    : knee + Math.floor(
        (magnitude - knee) * remaining /
        (magnitude - knee + remaining)
      );
  const lut = [];
  for(let magnitude = knee; magnitude <= maximum; magnitude += step) {
    lut.push(exact(magnitude));
  }
  assert.equal(lut.length, 585);
  let maximumError = 0;
  for(let magnitude = knee; magnitude <= maximum; ++magnitude) {
    const over = magnitude - knee;
    const index = over >> 9;
    const fraction = over & (step - 1);
    const approximated = index >= lut.length - 1
      ? lut.at(-1)
      : lut[index] +
        (((lut[index + 1] - lut[index]) * fraction + step / 2) >> 9);
    maximumError = Math.max(
      maximumError,
      Math.abs(approximated - exact(magnitude))
    );
  }
  assert.equal(maximumError, 13);
});
test("settings page requests and applies current normalization values", () => {
  const scriptPath = path.join(
    __dirname,
    "..",
    "yoRadio",
    "data",
    "www",
    "script.js.gz"
  );
  const script = zlib.gunzipSync(fs.readFileSync(scriptPath)).toString("utf8");
  const optionsLoaded = script.indexOf("getId('content').innerHTML = options");
  const request = script.indexOf("websocket.send('getsystem=1')", optionsLoaded);

  assert.ok(optionsLoaded >= 0 && request > optionsLoaded);
  assert.match(script, /Object\.keys\(data\)\.forEach\(key=>\{/);
  assert.match(script, /setupElement\(key, data\[key\]\)/);
  assert.match(script, /classList\.contains\("checkbox"\)/);
});

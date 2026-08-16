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
  assert.match(timeInput, /value="2000"/);
  assert.match(timeInput, /min="100"/);
  assert.match(timeInput, /max="10000"/);
});

test("normalizer uses one time constant for gain increase and decrease", () => {
  const source = fs.readFileSync(
    path.join(__dirname, "..", "yoRadio", "src", "audioI2S", "AudioNormalizer.cpp"),
    "utf8"
  );

  assert.match(source, /m_targetPeak/);
  assert.match(source, /m_timeConstantMs/);
  assert.match(source, /moveTowards\(m_gainQ16, targetGain, smoothingBlocks\)/);
  assert.doesNotMatch(source, /targetGain < m_gainQ16 \?/);
  assert.doesNotMatch(source, /attackSamples/);
});

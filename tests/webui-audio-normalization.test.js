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

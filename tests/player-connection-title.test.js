const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");

const config = fs.readFileSync(
  path.join(__dirname, "..", "yoRadio", "src", "core", "config.cpp"),
  "utf8",
);

test("successful web playback clears a stale connecting title", () => {
  assert.match(
    config,
    /configPostPlaying[\s\S]*getMode\(\)==PM_WEB[\s\S]*strcmp\(station\.title, LANG::const_PlConnect\) == 0[\s\S]*setTitle\(station\.name\)/,
  );
});

const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");

test("clock redraw keeps existing digits visible without a framebuffer", () => {
  const source = fs.readFileSync(
    path.join(root, "yoRadio", "src", "displays", "widgets", "widgets.cpp"),
    "utf8"
  );

  assert.match(
    source,
    /incrementalClockRedraw\s*=\s*CLOCKFONT_MONO\s*&&\s*!_fb->ready\(\)/
  );
  assert.match(source, /if\(!incrementalClockRedraw\)\s*_clearClock\(\)/);
  assert.match(
    source,
    /if\(incrementalClockRedraw\)[\s\S]*gfx\.print\('8'\)[\s\S]*gfx\.print\(\*digit\)/
  );
});

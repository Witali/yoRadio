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

test("clock advances before the first network time synchronization", () => {
  const source = fs.readFileSync(
    path.join(root, "yoRadio", "src", "core", "timekeeper.cpp"),
    "utf8"
  );

  assert.match(
    source,
    /TimeKeeper::_upClock\(\)[\s\S]*network\.timeinfo\.tm_sec\+\+[\s\S]*mktime\(&network\.timeinfo\)/
  );
  assert.doesNotMatch(source, /network\.timeinfo\.tm_year\s*>\s*100/);
});

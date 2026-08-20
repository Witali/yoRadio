const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const repository = path.join(__dirname, "..");

function readAsset(name) {
  return zlib
    .gunzipSync(
      fs.readFileSync(path.join(repository, "yoRadio", "data", "www", name)),
    )
    .toString("utf8");
}

test("long song metadata is clipped without widening the player", () => {
  const player = readAsset("player.html.gz");
  const style = readAsset("style.css.gz");

  assert.match(
    player,
    /id="trackinfo"[\s\S]*id="nameset"[\s\S]*id="meta"/,
  );
  assert.match(
    style,
    /#trackinfo \{[^}]*width: 100%[^}]*min-width: 0[^}]*max-width: 100%[^}]*overflow: hidden/,
  );
  assert.match(style, /#meta \{[^}]*overflow: hidden/);
  assert.match(style, /#meta \{[^}]*white-space: nowrap/);
  assert.match(style, /#meta \{[^}]*text-overflow: clip/);
});

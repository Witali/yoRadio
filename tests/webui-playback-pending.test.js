const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const repository = path.join(__dirname, "..");

function readAsset(name) {
  return zlib.gunzipSync(
    fs.readFileSync(path.join(repository, "yoRadio", "data", "www", name)),
  ).toString("utf8");
}

test("Play is disabled visually until playback actually starts", () => {
  const script = readAsset("script.js.gz");
  const style = readAsset("style.css.gz");

  assert.match(script, /function setPlaybackPending\(pending\)/);
  assert.match(script, /classList\.toggle\('connecting', pending\)/);
  assert.match(script, /attr\('aria-disabled', pending \? 'true' : 'false'\)/);
  assert.match(script, /setTimeout\(\(\) => setPlaybackPending\(false\), 15000\)/);
  assert.match(
    script,
    /const startingPlayback = player && player\.classList\.contains\('stopped'\)/,
  );
  assert.match(
    script,
    /if\(startingPlayback\) \{[\s\S]*?setCurrentItem\(currentItem, true\);[\s\S]*?setPlaybackPending\(true\);[\s\S]*?\}/,
  );
  assert.match(
    script,
    /id=="playerwrap" && value=="playing"\) setPlaybackPending\(false\)/,
  );
  assert.match(script, /classList\.contains\('connecting'\)\) return/);
  assert.match(
    style,
    /#playbutton\.connecting \{[^}]*opacity: \.45;[^}]*cursor: wait;[^}]*pointer-events: none;/,
  );
});

test("Pause leaves the playlist scroll position unchanged", () => {
  const script = readAsset("script.js.gz");
  const playButtonHandler = script.slice(
    script.indexOf("if(target.id === 'playbutton')"),
    script.indexOf("if(target.id === 'prevbutton'"),
  );

  assert.match(playButtonHandler, /const startingPlayback =/);
  assert.match(playButtonHandler, /if\(startingPlayback\)/);
  assert.doesNotMatch(
    playButtonHandler,
    /setCurrentItem\(currentItem, true\);[\s\S]*?const startingPlayback/,
  );
});

test("live WebUI test covers remote and physical control status", () => {
  const integration = fs.readFileSync(
    path.join(repository, "tools", "test_webui_controls.mjs"),
    "utf8",
  );
  const packageJson = JSON.parse(
    fs.readFileSync(path.join(repository, "package.json"), "utf8"),
  );

  assert.match(integration, /Play reaches actual playing state/);
  assert.match(integration, /Pause reaches stopped state/);
  assert.match(integration, /Next publishes a different current station/);
  assert.match(integration, /Previous publishes a different current station/);
  assert.match(integration, /physical Play reaches WebUI/);
  assert.match(integration, /physical Stop reaches WebUI/);
  assert.match(integration, /physical Next changes the WebUI station/);
  assert.match(integration, /physical Previous changes the WebUI station/);
  assert.equal(
    packageJson.scripts["test:webui-physical"],
    "node tools/test_webui_controls.mjs --physical",
  );
});

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const repository = path.join(__dirname, "..");

test("WebUI responses are not cached for a year", () => {
  const server = fs.readFileSync(
    path.join(repository, "yoRadio", "src", "core", "netserver.cpp"),
    "utf8"
  );

  assert.doesNotMatch(server, /max-age=31536000/);
  assert.match(server, /no-store, no-cache, must-revalidate, max-age=0/);
});

test("content-derived UI revision propagates to shell assets", () => {
  const shell = fs.readFileSync(
    path.join(repository, "yoRadio", "src", "core", "netserver.h"),
    "utf8"
  );

  assert.match(shell, /variables\.js\?boot=\$\{bootToken\}/);
  assert.match(shell, /encodeURIComponent\(webUiRevision\)/);
  for (const asset of ["theme.css", "style.css", "script.js", "dragpl.js"]) {
    assert.match(shell, new RegExp(`${asset.replace(".", "\\.")}\\$\\{uiSuffix\\}`));
  }
});

test("UI revision propagates to dynamically loaded settings", () => {
  const compressed = fs.readFileSync(
    path.join(repository, "yoRadio", "data", "www", "script.js.gz")
  );
  const script = zlib.gunzipSync(compressed).toString("utf8");

  assert.match(script, /typeof webUiRevision === 'undefined'/);
  assert.match(script, /fetch\(uiResource\('options\.html'\), \{cache: 'no-store'\}\)/);
  assert.match(script, /fetch\(uiResource\('player\.html'\), \{cache: 'no-store'\}\)/);
});

test("UI revision survives navigation between player and settings", () => {
  const compressed = fs.readFileSync(
    path.join(repository, "yoRadio", "data", "www", "script.js.gz")
  );
  const script = zlib.gunzipSync(compressed).toString("utf8");

  assert.match(script, /window\.location\.href=uiResource\('\/settings\.html'\)/);
  assert.match(script, /window\.location\.href=uiResource\('\/'\)/);
  assert.doesNotMatch(script, /window\.location\.href=`http:\/\/\$\{hostname\}\/(?:settings\.html)?`/);
});

test("firmware serves the index shell for a versioned root URL", () => {
  const server = fs.readFileSync(
    path.join(repository, "yoRadio", "src", "core", "netserver.cpp"),
    "utf8"
  );

  assert.match(server, /request->params\(\) == 1 && request->hasParam\("ui"\)/);
  assert.match(server, /request->params\(\) == 0 \|\| isVersionedIndex/);
});

test("firmware computes the UI revision from SPIFFS file contents", () => {
  const server = fs.readFileSync(
    path.join(repository, "yoRadio", "src", "core", "netserver.cpp"),
    "utf8"
  );

  assert.match(server, /refreshWebUiRevision\(\)/);
  assert.match(server, /\/www\/options\.html\.gz/);
  assert.match(server, /hash \^= buffer\[index\]/);
  assert.match(server, /var webUiRevision='%s'/);
});

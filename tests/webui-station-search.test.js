const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const zlib = require("node:zlib");

const repository = path.join(__dirname, "..");

function readAsset(name) {
  return zlib.gunzipSync(
    fs.readFileSync(path.join(repository, "yoRadio", "data", "www", name))
  ).toString("utf8");
}

test("player shows station search immediately above playlist", () => {
  const player = readAsset("player.html.gz");
  const searchIndex = player.indexOf('id="playlistfilter"');
  const playlistIndex = player.indexOf('id="playlist"');

  assert.ok(searchIndex >= 0, "station search input is missing");
  assert.ok(playlistIndex > searchIndex, "search must be above the playlist");
  assert.match(player, /type="search"/);
  assert.match(player, /aria-label="Search stations by name"/);
  assert.match(player, /id="playlistempty"[^>]*>No stations found</);
});

test("station search filters rendered rows by normalized name", () => {
  const script = readAsset("script.js.gz");

  assert.match(script, /function normalizeStationName\(value\)/);
  assert.match(script, /\.normalize\('NFKD'\)/);
  assert.match(script, /function filterPlaylist\(value\)/);
  assert.match(script, /item\.dataset\.name/);
  assert.match(script, /terms\.every\(term => name\.includes\(term\)\)/);
  assert.match(script, /item\.classList\.toggle\('filtered', !matches\)/);
  assert.match(script, /target\.id === 'playlistfilter'/);
  assert.match(script, /filterPlaylist\(filter \? filter\.value : ''\)/);
});

test("current-station updates preserve the active filter", () => {
  const script = readAsset("script.js.gz");
  const setCurrentItem = script.slice(
    script.indexOf("function setCurrentItem"),
    script.indexOf("function normalizeStationName")
  );

  assert.match(setCurrentItem, /querySelectorAll\('li\.play'\)/);
  assert.match(setCurrentItem, /classList\.toggle\('active', active\)/);
  assert.doesNotMatch(setCurrentItem, /attr\('class','play'\)/);
});

test("station search has compact responsive styling", () => {
  const style = readAsset("style.css.gz");

  assert.match(style, /#playlistsearch \{/);
  assert.match(style, /#playlistfilter \{/);
  assert.match(style, /#playlist li\.filtered \{ display: none; \}/);
});

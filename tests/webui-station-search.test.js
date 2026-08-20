const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
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

test("current station stays selectable without unsolicited scrolling", () => {
  const script = readAsset("script.js.gz");
  const setCurrentItem = script.slice(
    script.indexOf("function setCurrentItem"),
    script.indexOf("function normalizeStationName")
  );

  assert.match(setCurrentItem, /querySelectorAll\('li\[attr-id\]'\)/);
  assert.match(setCurrentItem, /classList\.add\('play'\)/);
  assert.match(setCurrentItem, /classList\.toggle\('active', active\)/);
  assert.doesNotMatch(setCurrentItem, /attr\('class','play'\)/);
  assert.match(script, /class="play\$\{active\}"/);
  assert.doesNotMatch(script, /<li\$\{active\}[^>]*class="play"/);

  const makeRow = (id, classes, offsetTop) => {
    const values = new Set(classes);
    return {
      offsetTop,
      offsetHeight: 20,
      attr: (name) => (name === "attr-id" ? String(id) : null),
      classList: {
        add: (name) => values.add(name),
        contains: (name) => values.has(name),
        toggle: (name, enabled) =>
          enabled ? values.add(name) : values.delete(name),
      },
      classes: values,
    };
  };
  const oldRow = makeRow(1, ["play", "active"], 0);
  // This reproduces the former duplicate-class HTML result: the current row
  // had only `active`, so a `li.play` query could never find it.
  const currentRow = makeRow(42, ["active"], 420);
  let scrollOptions = null;
  const playlist = {
    offsetHeight: 200,
    querySelectorAll: (selector) => {
      assert.equal(selector, "li[attr-id]");
      return [oldRow, currentRow];
    },
    scrollTo: (options) => {
      scrollOptions = options;
    },
  };

  vm.runInNewContext(`${setCurrentItem}\nsetCurrentItem(42);`, {
    getId: (id) => {
      assert.equal(id, "playlist");
      return playlist;
    },
  });

  assert.deepEqual([...oldRow.classes].sort(), ["play"]);
  assert.deepEqual([...currentRow.classes].sort(), ["active", "play"]);
  assert.equal(scrollOptions, null);

  vm.runInNewContext(`${setCurrentItem}\nsetCurrentItem(42, true);`, {
    getId: () => playlist,
  });
  assert.equal(scrollOptions.top, 330);
  assert.equal(scrollOptions.behavior, "smooth");
});

test("playlist scroll is requested only by playback navigation", () => {
  const script = readAsset("script.js.gz");

  assert.match(script, /function setCurrentItem\(item, shouldScroll=false\)/);
  assert.match(script, /if\(activeItem && shouldScroll\)/);
  assert.match(
    script,
    /setCurrentItem\(data\.current, shouldScrollCurrentItem\(data\.current\)\)/,
  );
  assert.match(script, /id=='meta' \|\| id=='nameset'\) setCurrentItem\(currentItem, false\)/);
  assert.match(script, /setCurrentItem\(currentItem, true\)/);
  assert.match(
    script,
    /target\.id === 'nameset'\) \{ setCurrentItem\(currentItem, true\); return; \}/,
  );
  assert.match(script, /setCurrentItem\(item, false\)/);
  assert.match(
    script,
    /target\.id === 'prevbutton' \|\| target\.id === 'nextbutton'\) requestStationChangeScroll\(\)/,
  );
  assert.match(
    script,
    /const changed = currentItemSynchronized && Number\(item\) !== Number\(currentItem\)/,
  );
  assert.match(script, /currentItemSynchronized = true/);
});

test("a physical station change scrolls once after initial synchronization", () => {
  const script = readAsset("script.js.gz");
  const helpers = script.slice(
    script.indexOf("function requestStationChangeScroll"),
    script.indexOf("function setupElement"),
  );
  const context = {
    currentItem: 11,
    currentItemSynchronized: false,
    stationChangeScrollFrom: null,
  };

  vm.runInNewContext(helpers, context);
  assert.equal(context.shouldScrollCurrentItem(11), false);
  assert.equal(context.shouldScrollCurrentItem(11), false);
  assert.equal(context.shouldScrollCurrentItem(12), true);
  context.currentItem = 12;
  assert.equal(context.shouldScrollCurrentItem(12), false);
});

test("station search has compact responsive styling", () => {
  const style = readAsset("style.css.gz");

  assert.match(style, /#playlistsearch \{/);
  assert.match(style, /#playlistfilter \{/);
  assert.match(style, /#playlist li\.filtered \{ display: none; \}/);
  assert.match(
    style,
    /#playlistfilter::-webkit-search-cancel-button[^}]*width: 22px[^}]*height: 22px/,
  );
  assert.match(
    style,
    /#playlistfilter::-webkit-search-cancel-button[\s\S]*?background:[^}]*var\(--accent-color\)/,
  );
});

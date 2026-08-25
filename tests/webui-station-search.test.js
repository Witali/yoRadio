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

test("playlist scroll is requested after initial load or by user navigation", () => {
  const script = readAsset("script.js.gz");

  assert.match(script, /function setCurrentItem\(item, shouldScroll=false\)/);
  assert.match(script, /if\(activeItem && shouldScroll\)/);
  assert.match(
    script,
    /setCurrentItem\(data\.current, shouldScrollCurrentItem\(data\.current\)\)/,
  );
  assert.match(script, /id=='meta' \|\| id=='nameset'\) setCurrentItem\(currentItem, false\)/);
  assert.match(
    script,
    /if\(startingPlayback\) \{[\s\S]*?setCurrentItem\(currentItem, true\)/,
  );
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
  assert.match(script, /const initial = initialPlaylistScrollPending && playlistLoaded/);
  assert.match(script, /currentItemSynchronized = true/);
});

test("playlist reload preserves the user's scroll position", async () => {
  const script = readAsset("script.js.gz");
  const playlistFunctions = script.slice(
    script.indexOf("function handlePlaylistData"),
    script.indexOf("function plAdd"),
  );
  let html = "existing playlist";
  const playlist = {
    scrollTop: 4321,
    get innerHTML() {
      return html;
    },
    set innerHTML(value) {
      html = value;
      this.scrollTop = 0;
    },
  };

  vm.runInNewContext(
    `${playlistFunctions}\ngeneratePlaylist("http://source/playlist.csv");`,
    {
      bigplaylist: true,
      currentItem: 1,
      initialPlaylistScrollPending: false,
      playlistLoaded: true,
      playlistRequestSerial: 0,
      fetch: async () => ({
        ok: true,
        text: async () => "Station\tstream\t0",
      }),
      filterPlaylist: () => {},
      getId: (id) =>
        id === "playlist" ? playlist : { value: "" },
      hostname: "device",
      modesd: true,
      setCurrentItem: () => {},
    },
  );
  await new Promise((resolve) => setImmediate(resolve));
  await new Promise((resolve) => setImmediate(resolve));

  assert.equal(playlist.scrollTop, 4321);
});

test("WebSocket reconnect resynchronizes without rebuilding the player page", () => {
  const script = readAsset("script.js.gz");
  const reconnectFunctions = script.slice(
    script.indexOf("function resyncCurrentPage"),
    script.indexOf("function onClose"),
  );
  const sent = [];
  let pageLoads = 0;
  const context = {
    continueLoading: () => pageLoads++,
    loaded: false,
    pingUp: () => {},
    playMode: "player",
    websocket: { send: (message) => sent.push(message) },
    window: { location: { pathname: "/" } },
    wserrcnt: 4,
    console: { log: () => {} },
  };

  vm.runInNewContext(`${reconnectFunctions}\nonOpen(); onOpen();`, context);

  assert.equal(pageLoads, 1, "reconnect must not replace the page DOM");
  assert.deepEqual(sent, ["getindex=1"]);
  assert.equal(context.wserrcnt, 0);
});

test("playlist remains visible while transient HTTP failures are retried", async () => {
  const script = readAsset("script.js.gz");
  const playlistFunctions = script.slice(
    script.indexOf("function handlePlaylistData"),
    script.indexOf("function plAdd"),
  );
  let html = "existing playlist";
  let attempts = 0;
  const playlist = {
    scrollTop: 77,
    get innerHTML() { return html; },
    set innerHTML(value) { html = value; },
  };
  const context = {
    bigplaylist: false,
    currentItem: 1,
    initialPlaylistScrollPending: false,
    playlistLoaded: true,
    playlistRequestSerial: 0,
    fetch: async () => {
      attempts++;
      if(attempts < 3) return { ok: false, status: 503, text: async () => "" };
      return { ok: true, text: async () => "Recovered\tstream\t0" };
    },
    filterPlaylist: () => {},
    getId: (id) => id === "playlist" ? playlist : { value: "" },
    hostname: "device",
    initPLEditor: () => {},
    modesd: true,
    setCurrentItem: () => {},
    setTimeout: (callback) => callback(),
    console: { log: () => {} },
    result: null,
  };

  vm.runInNewContext(
    `${playlistFunctions}\nresult = generatePlaylist("http://source/playlist.csv");`,
    context,
  );
  assert.equal(html, "existing playlist", "loading must not erase existing rows");
  assert.equal(await context.result, true);
  assert.equal(attempts, 3);
  assert.match(html, /Recovered/);
  assert.equal(playlist.scrollTop, 77);
  assert.equal(context.bigplaylist, false);
});

test("failed playlist refresh keeps the last successfully rendered list", async () => {
  const script = readAsset("script.js.gz");
  const playlistFunctions = script.slice(
    script.indexOf("function handlePlaylistData"),
    script.indexOf("function plAdd"),
  );
  const playlist = { innerHTML: "last good playlist", scrollTop: 91 };
  const context = {
    bigplaylist: false,
    currentItem: 1,
    playlistRequestSerial: 0,
    fetch: async () => ({ ok: false, status: 500, text: async () => "" }),
    getId: () => playlist,
    hostname: "device",
    setTimeout: (callback) => callback(),
    console: { log: () => {} },
    result: null,
  };

  vm.runInNewContext(
    `${playlistFunctions}\nresult = generatePlaylist("http://source/playlist.csv");`,
    context,
  );
  assert.equal(await context.result, false);
  assert.equal(playlist.innerHTML, "last good playlist");
  assert.equal(playlist.scrollTop, 91);
  assert.equal(context.bigplaylist, false);
});

test("repeated player status does not rebuild the station list", () => {
  const script = readAsset("script.js.gz");
  const helper = script.slice(
    script.indexOf("function shouldReloadPlaylist"),
    script.indexOf("function setupElement"),
  );
  const context = { loadedPlaylistMode: null, results: null };

  vm.runInNewContext(
    `${helper}\nresults = [shouldReloadPlaylist('modeweb'), shouldReloadPlaylist('modeweb'), shouldReloadPlaylist('modesd')];`,
    context,
  );

  assert.deepEqual(Array.from(context.results), [true, false, true]);
  assert.match(
    script,
    /if\(shouldReloadPlaylist\(data\.playermode\)\) \{[\s\S]*?generatePlaylist/,
  );
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
    initialPlaylistScrollPending: false,
    playlistLoaded: true,
  };

  vm.runInNewContext(helpers, context);
  assert.equal(context.shouldScrollCurrentItem(11), false);
  assert.equal(context.shouldScrollCurrentItem(11), false);
  assert.equal(context.shouldScrollCurrentItem(12), true);
  context.currentItem = 12;
  assert.equal(context.shouldScrollCurrentItem(12), false);
});

test("initial playlist rendering scrolls to the current station once", async () => {
  const script = readAsset("script.js.gz");
  const playlistFunctions = script.slice(
    script.indexOf("function handlePlaylistData"),
    script.indexOf("function plAdd"),
  );
  let shouldScroll = null;
  const playlist = { innerHTML: "", scrollTop: 0 };
  const context = {
    bigplaylist: false,
    currentItem: 2,
    initialPlaylistScrollPending: true,
    playlistLoaded: false,
    playlistRequestSerial: 0,
    fetch: async () => ({
      ok: true,
      text: async () => "First\tstream-1\t0\nSecond\tstream-2\t0",
    }),
    filterPlaylist: () => {},
    getId: (id) => id === "playlist" ? playlist : { value: "" },
    hostname: "device",
    modesd: true,
    setCurrentItem: (item, scroll) => {
      assert.equal(item, 2);
      shouldScroll = scroll;
    },
    console: { log: () => {} },
    result: null,
  };

  vm.runInNewContext(
    `${playlistFunctions}\nresult = generatePlaylist("http://source/playlist.csv");`,
    context,
  );
  assert.equal(await context.result, true);
  assert.equal(shouldScroll, true);
  assert.equal(context.initialPlaylistScrollPending, false);
  assert.equal(context.playlistLoaded, true);
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

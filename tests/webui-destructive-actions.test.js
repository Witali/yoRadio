const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");
const zlib = require("node:zlib");

const webUiScriptPath = path.join(
  __dirname,
  "..",
  "yoRadio",
  "data",
  "www",
  "script.js.gz"
);

function classList(initial = []) {
  const values = new Set(initial);
  return {
    add: (...names) => names.forEach((name) => values.add(name)),
    contains: (name) => values.has(name),
    remove: (...names) => names.forEach((name) => values.delete(name)),
    toggle: (name) => {
      if (values.has(name)) {
        values.delete(name);
        return false;
      }
      values.add(name);
      return true;
    },
  };
}

function loadWebUi(confirmResponses) {
  const clickListeners = [];
  const commands = [];
  const prompts = [];
  const elements = {
    navigation: { classList: classList() },
    settingscontent: { innerHTML: "" },
    settingsdone: { classList: classList() },
  };
  const neverResolve = {
    catch() {
      return this;
    },
    then() {
      return this;
    },
  };

  class HTMLElement {}

  const window = {
    addEventListener() {},
    confirm(message) {
      prompts.push(message);
      return confirmResponses.shift();
    },
    location: {
      hostname: "yoradio.local",
      pathname: "/settings.html",
      search: "",
    },
    open() {},
  };
  const document = {
    body: {
      addEventListener(type, listener) {
        if (type === "click") clickListeners.push(listener);
      },
    },
    createElement() {
      return {};
    },
    getElementById(id) {
      return elements[id] || null;
    },
    querySelectorAll() {
      return [];
    },
  };

  const context = vm.createContext({
    URLSearchParams,
    WebSocket: class WebSocket {},
    clearTimeout() {},
    console,
    document,
    fetch() {
      return neverResolve;
    },
    HTMLElement,
    setTimeout() {
      return 1;
    },
    window,
    yoVersion: "test",
  });

  const source = zlib.gunzipSync(fs.readFileSync(webUiScriptPath), "utf8");
  vm.runInContext(source, context, { filename: "script.js" });
  context.websocket = { send: (command) => commands.push(command) };
  context.continueLoading("access-point");

  assert.equal(clickListeners.length, 1, "WebUI click handler was not registered");

  function click(command) {
    const parentElement = { classList: classList() };
    const target = {
      classList: classList(["local"]),
      closest: () => target,
      dataset: { command },
      parentElement,
    };
    clickListeners[0]({
      preventDefault() {},
      stopPropagation() {},
      target,
    });
  }

  return { click, commands, elements, prompts };
}

test("format does nothing when the first confirmation is cancelled", () => {
  const ui = loadWebUi([false]);

  ui.click("format");

  assert.deepEqual(ui.commands, []);
  assert.equal(ui.prompts.length, 1);
  assert.match(ui.prompts[0], /erase ALL SPIFFS data/);
});

test("format does nothing when the final confirmation is cancelled", () => {
  const ui = loadWebUi([true, false]);

  ui.click("format");

  assert.deepEqual(ui.commands, []);
  assert.equal(ui.prompts.length, 2);
  assert.match(ui.prompts[1], /FINAL CONFIRMATION/);
});

test("format is sent only after both confirmations are accepted", () => {
  const ui = loadWebUi([true, true]);

  ui.click("format");

  assert.deepEqual(ui.commands, ["format=1"]);
  assert.equal(ui.prompts.length, 2);
  assert.match(ui.elements.settingscontent.innerHTML, /Format SPIFFS/);
});

test("settings reset does nothing when its confirmation is cancelled", () => {
  const ui = loadWebUi([false]);

  ui.click("reset");

  assert.deepEqual(ui.commands, []);
  assert.equal(ui.prompts.length, 1);
  assert.match(ui.prompts[0], /Reset all radio settings/);
});

test("settings reset is sent after its confirmation is accepted", () => {
  const ui = loadWebUi([true]);

  ui.click("reset");

  assert.deepEqual(ui.commands, ["reset=1"]);
  assert.equal(ui.prompts.length, 1);
  assert.match(ui.elements.settingscontent.innerHTML, /Reset settings/);
});

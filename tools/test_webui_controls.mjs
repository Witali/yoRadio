#!/usr/bin/env node

import process from "node:process";
import { createInterface } from "node:readline/promises";

const args = process.argv.slice(2);
const physical = args.includes("--physical");
const hostIndex = args.indexOf("--host");
const host = hostIndex >= 0 ? args[hostIndex + 1] : "192.168.100.4";
const timeoutIndex = args.indexOf("--timeout");
const timeoutMs = timeoutIndex >= 0 ? Number(args[timeoutIndex + 1]) : 20000;
const stationIndex = args.indexOf("--station");
const selectedStation = stationIndex >= 0 ? Number(args[stationIndex + 1]) : null;

if(args.includes("--help") || !host || !Number.isFinite(timeoutMs) ||
   (selectedStation !== null &&
    (!Number.isInteger(selectedStation) || selectedStation < 1 ||
     selectedStation > 65535))) {
  console.log(`Usage: node tools/test_webui_controls.mjs [options]

Options:
  --host ADDRESS     Board address (default: 192.168.100.4)
  --timeout MS       Per-step timeout (default: 20000)
  --physical         Also verify short, double and long BOOT gestures
  --station INDEX    Known working station used for the playlist-row Play test;
                     defaults to station 1 or 2, whichever is not current
  --help             Show this help

The default run verifies the same WebSocket status flow used by WebUI for
Play, connecting/playing, Stop, Next and Previous. The physical run pauses
for BOOT-button gestures and verifies their status reaches WebUI.`);
  process.exit(args.includes("--help") ? 0 : 2);
}

const url = `ws://${host}/ws`;
const socket = new WebSocket(url);
const state = {
  revision: 0,
  playing: null,
  current: null,
  station: "",
};
const waiters = new Set();
const messageWaiters = new Set();

function describeState(value = state) {
  return `playing=${value.playing} current=${value.current} station="${value.station}"`;
}

function settleWaiters() {
  for(const waiter of [...waiters]) {
    if(state.revision > waiter.afterRevision && waiter.predicate(state)) {
      clearTimeout(waiter.timer);
      waiters.delete(waiter);
      waiter.resolve({...state});
    }
  }
}

function applyMessage(raw) {
  const data = JSON.parse(raw);
  for(const waiter of [...messageWaiters]) {
    if(waiter.predicate(data)) {
      clearTimeout(waiter.timer);
      messageWaiters.delete(waiter);
      waiter.resolve(data);
    }
  }
  if(Array.isArray(data.payload)) {
    for(const item of data.payload) {
      if(item.id === "playerwrap") state.playing = item.value === "playing";
      if(item.id === "nameset") state.station = String(item.value ?? "");
    }
  }
  if(typeof data.current !== "undefined") state.current = Number(data.current);
  state.revision++;
  settleWaiters();
}

function waitFor(description, predicate, afterRevision = state.revision) {
  return new Promise((resolve, reject) => {
    const waiter = {description, predicate, afterRevision, resolve, reject};
    waiter.timer = setTimeout(() => {
      waiters.delete(waiter);
      reject(new Error(`Timed out waiting for ${description}; ${describeState()}`));
    }, timeoutMs);
    waiters.add(waiter);
    settleWaiters();
  });
}

function waitForJson(description, predicate) {
  return new Promise((resolve, reject) => {
    const waiter = {description, predicate, resolve, reject};
    waiter.timer = setTimeout(() => {
      messageWaiters.delete(waiter);
      reject(new Error(`Timed out waiting for ${description}`));
    }, timeoutMs);
    messageWaiters.add(waiter);
  });
}

async function query(commandText, description, predicate) {
  const response = waitForJson(description, predicate);
  socket.send(commandText);
  const data = await response;
  console.log(`PASS ${description}`);
  return data;
}

async function command(command, description, predicate) {
  const afterRevision = state.revision;
  socket.send(command);
  const result = await waitFor(description, predicate, afterRevision);
  console.log(`PASS ${description}: ${describeState(result)}`);
  return result;
}

function delay(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function ensureStopped() {
  if(!state.playing) {
    console.log(`PASS WebUI is already stopped: ${describeState()}`);
    return;
  }
  await command("stop=1", "WebUI receives stopped state", value => !value.playing);
  await delay(1000);
  if(state.playing) {
    await command(
      "stop=1",
      "late stream startup is stopped before the next scenario",
      value => !value.playing,
    );
  }
}

async function testSettingsResponses() {
  await query(
    "getactive=1",
    "client mode exposes the full settings groups",
    data => Array.isArray(data.act) && data.act.includes("group_system") &&
            data.act.includes("group_display"),
  );
  await query("getsystem=1", "system settings are returned",
              data => "normalize" in data && "normtime" in data);
  await query("getscreen=1", "display settings are returned",
              data => "br" in data && "scrt" in data);
  await query("gettimezone=1", "timezone settings are returned",
              data => "sntp1" in data && "timeint" in data);
  await query("getcontrols=1", "control settings are returned",
              data => "vols" in data && "enca" in data);
}

async function testRemoteControls() {
  await ensureStopped();
  const clickedStation = selectedStation ?? (state.current === 1 ? 2 : 1);
  await command(
    `play=${clickedStation}`,
    "playlist row click selects and starts that station",
    value => value.current === clickedStation && value.playing,
  );
  await command("stop=1", "clicked station can be stopped", value => !value.playing);
  await command("toggle=1", "Play reaches actual playing state", value => value.playing);
  await command("stop=1", "Stop reaches stopped state", value => !value.playing);
  await command("toggle=1", "Play resumes after Stop", value => value.playing);
  await command("toggle=1", "Pause reaches stopped state", value => !value.playing);

  const beforeNext = state.current;
  await command(
    "next=1",
    "Next publishes a different current station",
    value => value.current !== null && value.current !== beforeNext,
  );

  const beforePrevious = state.current;
  await command(
    "prev=1",
    "Previous publishes a different current station",
    value => value.current !== null && value.current !== beforePrevious,
  );
  await ensureStopped();
}

async function physicalStep(prompt, description, predicate) {
  const afterRevision = state.revision;
  await input.question(`${prompt}\nPress Enter after completing the gesture... `);
  const result = await waitFor(description, predicate, afterRevision);
  console.log(`PASS ${description}: ${describeState(result)}`);
  return result;
}

async function testPhysicalControls() {
  await ensureStopped();
  await physicalStep(
    "Short-press BOOT once to start playback.",
    "physical Play reaches WebUI",
    value => value.playing,
  );
  await physicalStep(
    "Short-press BOOT once to stop playback.",
    "physical Stop reaches WebUI",
    value => !value.playing,
  );

  const beforeNext = state.current;
  await physicalStep(
    "Double-click BOOT to select the next station.",
    "physical Next changes the WebUI station",
    value => value.current !== null && value.current !== beforeNext,
  );

  const beforePrevious = state.current;
  await physicalStep(
    "Hold BOOT for about one second to select the previous station.",
    "physical Previous changes the WebUI station",
    value => value.current !== null && value.current !== beforePrevious,
  );
}

let input;
try {
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, {once: true});
    socket.addEventListener("error", () => reject(new Error(`Cannot connect to ${url}`)), {once: true});
  });
  socket.addEventListener("message", event => {
    try { applyMessage(String(event.data)); }
    catch(error) { console.error(`Ignoring invalid WebSocket message: ${error.message}`); }
  });
  socket.send("getindex=1");
  await waitFor(
    "initial WebUI state",
    value => value.playing !== null && value.current !== null,
    -1,
  );
  console.log(`Connected to ${url}: ${describeState()}`);

  await testSettingsResponses();
  await testRemoteControls();
  if(physical) {
    input = createInterface({input: process.stdin, output: process.stdout});
    await testPhysicalControls();
  }
  console.log("All requested WebUI control scenarios passed.");
} catch(error) {
  console.error(`FAIL ${error.message}`);
  process.exitCode = 1;
} finally {
  input?.close();
  socket.close();
}

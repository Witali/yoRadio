#!/usr/bin/env node

import process from "node:process";
import { createInterface } from "node:readline/promises";

const args = process.argv.slice(2);
const physical = args.includes("--physical");
const hostIndex = args.indexOf("--host");
const host = hostIndex >= 0 ? args[hostIndex + 1] : "192.168.100.4";
const timeoutIndex = args.indexOf("--timeout");
const timeoutMs = timeoutIndex >= 0 ? Number(args[timeoutIndex + 1]) : 20000;

if(args.includes("--help") || !host || !Number.isFinite(timeoutMs)) {
  console.log(`Usage: node tools/test_webui_controls.mjs [options]

Options:
  --host ADDRESS     Board address (default: 192.168.100.4)
  --timeout MS       Per-step timeout (default: 20000)
  --physical         Also verify short, double and long BOOT gestures
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

async function testRemoteControls() {
  await ensureStopped();
  await command("toggle=1", "Play reaches actual playing state", value => value.playing);
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

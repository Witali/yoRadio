#!/usr/bin/env node
// Opt-in physical RAM workload. Requires the memory-profile firmware and a
// separate UART TX capture. Does not upload files, edit Wi-Fi or reset the MCU.
const fs = require('node:fs');
const { chromium } = require('playwright');
const args = process.argv.slice(2);
const opt = (key, fallback) => args.includes(key) ? args[args.indexOf(key) + 1] : fallback;
const host = opt('--host', '192.168.100.6');
const output = opt('--output', '.build/esp8266-memory-workload.jsonl');
const aacStation = Number(opt('--aac-station', '2'));
if (!Number.isInteger(aacStation) || aacStation < 1)
  throw new Error('Invalid --aac-station');
const original = {
  station: Number(opt('--restore-station', '0')),
  volume: Number(opt('--restore-volume', '-1')),
  playing: opt('--restore-playing', '')
};
if (!Number.isInteger(original.station) || original.station < 1 ||
    !Number.isInteger(original.volume) || original.volume < 0 || original.volume > 254 ||
    !['true', 'false'].includes(original.playing)) {
  throw new Error('Read the original state first; supply --restore-station, --restore-volume and --restore-playing');
}
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const log = (event, data = {}) => {
  const line = JSON.stringify({ time: new Date().toISOString(), event, ...data });
  fs.appendFileSync(output, line + '\n');
  console.log(line);
};
let browser;
const pages = [];
async function rawCommand(command) {
  await new Promise((resolve, reject) => {
    const ws = new WebSocket(`ws://${host}/ws`);
    let finished = false;
    const finish = error => {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      // Undici can emit error synchronously from close() on a failed socket.
      ws.onerror = null;
      if (ws.readyState === WebSocket.OPEN) ws.close();
      if (error) reject(error); else resolve();
    };
    const timer = setTimeout(() => finish(new Error('command timeout: ' + command)), 12000);
    ws.onopen = () => {
      ws.send(command);
      setTimeout(() => finish(), 1200);
    };
    ws.onerror = () => finish(new Error('command connection: ' + command));
  });
}
async function command(value) {
  for (const page of pages) {
    if (page.isClosed()) continue;
    const sent = await page.evaluate(value => {
      if (typeof websocket !== 'undefined' && websocket.readyState === 1) {
        websocket.send(value); return true;
      }
      return false;
    }, value).catch(() => false);
    if (sent) { await sleep(1200); return; }
  }
  return rawCommand(value);
}
async function status(label) {
  const start = Date.now();
  try {
    const response = await fetch(`http://${host}/api/native/status`, {signal: AbortSignal.timeout(10000)});
    log('status', {label, ms: Date.now() - start, http: response.status, status: await response.json()});
  } catch (error) { log('status_error', {label, error: error.message}); }
}
async function phase(label, cmd, seconds) {
  log('phase_start', {label, command: cmd, seconds});
  try { if (cmd) await command(cmd); }
  catch (error) { log('command_error', {label, error: error.message}); }
  // The UART sampler does not create extra HTTP/TCP load during this interval.
  await sleep(seconds * 1000);
  await status(label);
  log('phase_end', {label});
}
async function openTab(label) {
  const page = await browser.newPage({viewport: {width: 1000, height: 800}});
  pages.push(page);
  let frames = 0;
  page.on('websocket', ws => {
    log('ws_open', {label});
    ws.on('framereceived', () => ++frames);
    ws.on('close', () => log('ws_close', {label, frames}));
  });
  page.on('requestfailed', r => log('resource_error', {label, path: new URL(r.url()).pathname, error: r.failure()?.errorText}));
  const started = Date.now();
  try {
    await page.goto(`http://${host}/?ui=memory-profile`, {waitUntil: 'domcontentloaded', timeout: 45000});
    await page.waitForFunction(() => document.querySelectorAll('#playlist li[attr-id]').length > 0 &&
      typeof websocket !== 'undefined' && websocket.readyState === 1, {}, {timeout: 45000});
    log('tab_ready', {label, ms: Date.now() - started, frames,
      rows: await page.locator('#playlist li[attr-id]').count()});
  } catch (error) { log('tab_error', {label, ms: Date.now() - started, error: error.message}); }
}
async function reloadTab(index, label) {
  log('reload_start', {label});
  try {
    await pages[index].reload({waitUntil: 'domcontentloaded', timeout: 45000});
    await pages[index].waitForFunction(() => document.querySelectorAll('#playlist li[attr-id]').length > 0 &&
      typeof websocket !== 'undefined' && websocket.readyState === 1, {}, {timeout: 45000});
    log('reload_ready', {label});
  } catch (error) { log('reload_error', {label, error: error.message}); }
  await phase(label, null, 15);
}
(async () => {
  log('begin', {host, original});
  try {
    await phase('stopped-no-tabs', 'stop=1', 30);
    if (!args.includes('--aac-followup')) {
      await phase('MP3-128-no-tabs', 'play=498', 50);
      await phase('MP3-256-no-tabs', 'play=502', 50);
    } else {
      await phase('AAC-low-no-tabs', 'play=1', 35);
    }
    await phase('AAC-no-tabs', `play=${aacStation}`, 50);
    await phase('switch-AAC-to-MP3', 'play=510', 25);
    await phase('switch-MP3-to-AAC', `play=${aacStation}`, 25);
    await phase('stop-after-switches', 'stop=1', 20);
    browser = await chromium.launch({channel: opt('--channel', 'msedge'), headless: true});
    log('tabs_loading');
    await openTab('first');
    await phase('one-tab-stopped', null, 20);
    await openTab('second');
    await phase('two-tabs-stopped', null, 20);
    await phase('two-tabs-MP3', 'play=498', 45);
    if (args.includes('--reload-during-audio')) await reloadTab(0, 'reload-during-MP3');
    await phase('two-tabs-AAC', `play=${aacStation}`, 45);
    if (args.includes('--reload-during-audio')) await reloadTab(1, 'reload-during-AAC');
    await phase('two-tabs-stopped-after', 'stop=1', 20);
  } finally {
    if (browser) await browser.close().catch(error => log('close_error', {error: error.message}));
    let restored = false;
    for (let attempt = 1; attempt <= 3 && !restored; ++attempt) {
      try {
        await rawCommand(`play=${original.station}`);
        if (original.playing === 'false') await rawCommand('stop=1');
        await rawCommand(`volume=${original.volume}`);
        restored = true;
        log('restore_commands_sent', {attempt, original});
      } catch (error) { log('restore_error', {attempt, error: error.message}); await sleep(2000); }
    }
    await status('restored-check');
    if (!restored) throw new Error('Original state could not be restored; manual recovery required');
  }
  log('end');
})().then(() => process.exit(0), error => { log('fatal', {error: error.stack}); process.exit(1); });

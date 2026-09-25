import assert from 'node:assert/strict';
import fs from 'node:fs';
import net from 'node:net';
import os from 'node:os';
import path from 'node:path';
import process from 'node:process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const fixtures = {
  mp3: {
    route: '/stream.mp3',
    contentType: 'audio/mpeg',
    bitrateKbps: 64,
    data: fs.readFileSync(path.join(root, 'tests', 'webradio', 'fixtures', 'mono-64.mp3')),
  },
  aac: {
    route: '/stream.aac',
    contentType: 'audio/aac',
    bitrateKbps: 64,
    data: fs.readFileSync(path.join(root, 'tests', 'webradio', 'fixtures', 'mono-64.aac')),
  },
};

function argument(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

function defaultHost() {
  for (const addresses of Object.values(os.networkInterfaces())) {
    for (const address of addresses ?? []) {
      if (address.family === 'IPv4' && !address.internal) return address.address;
    }
  }
  throw new Error('No non-loopback IPv4 address found; pass --host explicitly');
}

const board = new URL(argument('board', 'http://192.168.100.6/'));
const host = argument('host', defaultHost());
const port = Number(argument('port', '18080'));
const durationMs = Number(argument('duration-ms', '8000'));
const counters = { mp3: 0, aac: 0 };

function codecForRequest(line) {
  for (const [codec, fixture] of Object.entries(fixtures)) {
    if (line.startsWith(`GET ${fixture.route} `)) return codec;
  }
  return null;
}

const streamServer = net.createServer((socket) => {
  socket.setNoDelay(true);
  socket.once('data', (request) => {
    const codec = codecForRequest(request.toString('latin1').split('\r\n', 1)[0]);
    if (!codec) {
      socket.end('HTTP/1.0 404 Not Found\r\nContent-Length: 0\r\n\r\n');
      return;
    }

    const fixture = fixtures[codec];
    socket.write(`HTTP/1.0 200 OK\r\nContent-Type: ${fixture.contentType}\r\nConnection: close\r\n\r\n`);
    let offset = 0;
    const pump = () => {
      if (socket.destroyed) return;
      const remaining = fixture.data.length - offset;
      const chunkLength = Math.min(1024, remaining);
      const chunk = fixture.data.subarray(offset, offset + chunkLength);
      offset = (offset + chunkLength) % fixture.data.length;
      counters[codec] += chunk.length;
      const intervalMs = Math.ceil((chunk.length * 8) / fixture.bitrateKbps);
      const schedule = () => setTimeout(pump, intervalMs);
      if (socket.write(chunk)) schedule();
      else socket.once('drain', schedule);
    };
    pump();
  });
  socket.on('error', () => {});
});

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function api(route, parameters = {}) {
  const url = new URL(route, board);
  for (const [key, value] of Object.entries(parameters)) url.searchParams.set(key, value);
  const response = await fetch(url, { cache: 'no-store', signal: AbortSignal.timeout(10000) });
  const body = await response.text();
  assert.ok(response.ok, `${url.pathname} returned ${response.status}: ${body}`);
  return body ? JSON.parse(body) : null;
}

async function waitFor(predicate, description, timeoutMs = 12000) {
  const deadline = Date.now() + timeoutMs;
  let last;
  while (Date.now() < deadline) {
    last = await api('/api/status');
    if (predicate(last)) return last;
    await delay(250);
  }
  throw new Error(`${description}; last status=${JSON.stringify(last)}`);
}

async function testCodec(codec) {
  counters[codec] = 0;
  const streamUrl = `http://${host}:${port}${fixtures[codec].route}`;
  console.log(`${codec.toUpperCase()}: play ${streamUrl}`);
  await api('/api/play', { url: streamUrl, codec });
  const started = await waitFor(
    (status) => status.playing && status.codec === codec && status.samples > 0,
    `${codec} decoder did not start`,
  );
  const initialSamples = started.samples;
  await delay(durationMs);
  const completed = await api('/api/status');
  assert.equal(completed.playing, true, `${codec} decoder stopped unexpectedly: ${completed.status}`);
  assert.equal(completed.codec, codec);
  assert.ok(completed.samples > initialSamples, `${codec} sample count did not advance`);
  assert.ok(completed.sample_rate > 0, `${codec} sample rate was not reported`);
  assert.ok(completed.channels > 0, `${codec} channel count was not reported`);
  assert.ok(counters[codec] >= 16384, `${codec} decoder consumed only ${counters[codec]} HTTP bytes`);
  console.log(
    `${codec.toUpperCase()}: PASS, samples +${completed.samples - initialSamples}, ` +
      `${completed.sample_rate} Hz, ${completed.channels} channel(s), HTTP ${counters[codec]} bytes, heap ${completed.free_heap}`,
  );
  await api('/api/stop');
  await waitFor((status) => !status.playing && !status.pending, `${codec} decoder did not stop`);
}

await new Promise((resolve, reject) => {
  streamServer.once('error', reject);
  streamServer.listen(port, '0.0.0.0', resolve);
});

try {
  await api('/api/status');
  await testCodec('mp3');
  await testCodec('aac');
  console.log('WebRadio physical MP3/AAC playback test: PASS');
} finally {
  await api('/api/stop').catch(() => {});
  await new Promise((resolve) => streamServer.close(resolve));
}

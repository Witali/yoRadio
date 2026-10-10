import assert from 'node:assert/strict';
import process from 'node:process';

function argument(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const board = new URL(argument('board', 'http://192.168.4.1/'));
const host = argument('host', '192.168.4.2');
const port = Number(argument('port', '18080'));
const durationMs = Number(argument('duration-ms', '8000'));

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function api(route, parameters = {}, timeoutMs = 10000) {
  const url = new URL(route, board);
  for (const [key, value] of Object.entries(parameters)) url.searchParams.set(key, value);
  const response = await fetch(url, { cache: 'no-store', signal: AbortSignal.timeout(timeoutMs) });
  const body = await response.text();
  assert.ok(response.ok, `${url.pathname} returned ${response.status}: ${body}`);
  return body ? JSON.parse(body) : null;
}

async function statusUntil(predicate, description, timeoutMs = 20000) {
  const deadline = Date.now() + timeoutMs;
  let last;
  while (Date.now() < deadline) {
    try {
      last = await api('/api/status');
      if (predicate(last)) return last;
    } catch (error) {
      if (Date.now() >= deadline) throw error;
    }
    await delay(250);
  }
  throw new Error(`${description}; last status=${JSON.stringify(last)}`);
}

async function serverStats() {
  const response = await fetch(`http://127.0.0.1:${port}/stats`, {
    cache: 'no-store',
    signal: AbortSignal.timeout(3000),
  });
  assert.equal(response.ok, true);
  return response.json();
}

async function testCodec(codec) {
  const before = await serverStats();
  const streamUrl = `http://${host}:${port}/stream.${codec}`;
  console.log(`${codec.toUpperCase()}: play ${streamUrl}`);
  await api('/api/play', { url: streamUrl, codec });
  const started = await statusUntil(
    (status) => status.playing && status.codec === codec && status.samples > 0,
    `${codec} decoder did not start`,
  );
  const initialSamples = started.samples;
  await delay(durationMs);
  const completed = await api('/api/status');
  const after = await serverStats();
  assert.equal(completed.playing, true, `${codec} decoder stopped unexpectedly: ${completed.status}`);
  assert.equal(completed.codec, codec);
  assert.ok(completed.samples > initialSamples, `${codec} sample count did not advance`);
  assert.ok(completed.sample_rate > 0, `${codec} sample rate was not reported`);
  assert.ok(completed.channels > 0, `${codec} channel count was not reported`);
  assert.ok(after[codec] - before[codec] >= 16384, `${codec} consumed too few HTTP bytes`);
  console.log(
    `${codec.toUpperCase()}: PASS, samples +${completed.samples - initialSamples}, ` +
      `${completed.sample_rate} Hz, ${completed.channels} channel(s), ` +
      `HTTP ${after[codec] - before[codec]} bytes, heap ${completed.free_heap}`,
  );
  await api('/api/stop');
  await statusUntil((status) => !status.playing && !status.pending, `${codec} decoder did not stop`);
}

try {
  await api('/api/status');
  await testCodec('mp3');
  await testCodec('aac');
  console.log('WebRadio physical MP3/AAC playback test: PASS');
} finally {
  await api('/api/stop').catch(() => {});
}

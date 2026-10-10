import assert from 'node:assert/strict';
import process from 'node:process';

function argument(name, fallback) {
  const index = process.argv.indexOf(`--${name}`);
  return index >= 0 ? process.argv[index + 1] : fallback;
}

const board = new URL(argument('board', 'http://192.168.100.6/'));
const durationMs = Number(argument('duration-ms', '8000'));
const streams = [
  ['mp3', argument('mp3-url', '')],
  ['aac', argument('aac-url', '')],
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function api(route, parameters = {}) {
  const url = new URL(route, board);
  for (const [key, value] of Object.entries(parameters)) url.searchParams.set(key, value);
  const response = await fetch(url, { cache: 'no-store', signal: AbortSignal.timeout(15000) });
  const body = await response.text();
  assert.ok(response.ok, `${url.pathname} returned ${response.status}: ${body}`);
  return body ? JSON.parse(body) : null;
}

async function waitFor(predicate, description, timeoutMs = 30000) {
  const deadline = Date.now() + timeoutMs;
  let last;
  while (Date.now() < deadline) {
    try {
      last = await api('/api/status');
      if (predicate(last)) return last;
    } catch (error) {
      if (Date.now() >= deadline) throw error;
    }
    await delay(500);
  }
  throw new Error(`${description}; last status=${JSON.stringify(last)}`);
}

async function testStream(codec, streamUrl) {
  assert.ok(streamUrl.startsWith('http://'), `${codec} requires an unencrypted HTTP URL`);
  console.log(`${codec.toUpperCase()}: play ${streamUrl}`);
  await api('/api/play', { url: streamUrl, codec });
  const started = await waitFor(
    (status) => status.playing && status.codec === codec && status.samples > 0,
    `${codec} decoder did not produce PCM samples`,
  );
  const initialSamples = started.samples;
  await delay(durationMs);
  const completed = await api('/api/status');
  assert.equal(completed.playing, true, `${codec} stopped unexpectedly: ${completed.status}`);
  assert.ok(completed.samples > initialSamples, `${codec} sample count did not advance`);
  assert.ok(completed.sample_rate > 0, `${codec} sample rate was not reported`);
  assert.ok(completed.channels > 0, `${codec} channel count was not reported`);
  console.log(
    `${codec.toUpperCase()}: PASS, samples +${completed.samples - initialSamples}, ` +
      `${completed.sample_rate} Hz, ${completed.channels} channel(s), heap ${completed.free_heap}`,
  );
  await api('/api/stop');
  await waitFor((status) => !status.playing && !status.pending, `${codec} decoder did not stop`);
}

try {
  await api('/api/status');
  for (const [codec, url] of streams) await testStream(codec, url);
  console.log('WebRadio public MP3/AAC playback test: PASS');
} finally {
  await api('/api/stop').catch(() => {});
}

// Opt-in physical MP3/AAC DMA workload. No Wi-Fi/settings uploads or UART RX.
// Pair with monitor_esp8266.py and an AUDIO_PROFILE firmware (30 s window).
const args = process.argv.slice(2);
const opt = (k, d) => args.includes(k) ? args[args.indexOf(k) + 1] : d;
const host = opt('--host', '192.168.100.6');
const restore = {station: Number(opt('--restore-station', '0')),
  volume: Number(opt('--restore-volume', '-1')), playing: opt('--restore-playing', '')};
if (!Number.isInteger(restore.station) || restore.station < 1 ||
    !Number.isInteger(restore.volume) || restore.volume < 0 || restore.volume > 254 ||
    !['true', 'false'].includes(restore.playing)) throw new Error('Read original state and provide all --restore-* options');
const seconds = Number(opt('--seconds', '45'));
const stations = opt('--stations', '498,2').split(',').map(Number);
if (!Number.isInteger(seconds) || seconds < 1 || seconds > 60 ||
    stations.some(n => !Number.isInteger(n) || n < 1)) throw new Error('Invalid cases');
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
const log = (event, data) => console.log(JSON.stringify({time: new Date().toISOString(), event, ...data}));
async function command(value) {
  await new Promise((resolve, reject) => {
    const ws = new WebSocket(`ws://${host}/ws`);
    let done = false;
    const finish = error => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      ws.onerror = null;
      if (ws.readyState === WebSocket.OPEN) ws.close();
      error ? reject(error) : resolve();
    };
    const timer = setTimeout(() => finish(new Error('WS timeout')), 10000);
    ws.onopen = () => { ws.send(value); setTimeout(() => finish(), 800); };
    ws.onerror = () => finish(new Error('WS error'));
  });
}
async function status(label) {
  const start = Date.now();
  const response = await fetch(`http://${host}/api/native/status`, {signal: AbortSignal.timeout(8000)});
  if (!response.ok) throw new Error('HTTP ' + response.status);
  const state = await response.json();
  log('status', {label, ms: Date.now() - start, state});
  return state;
}
(async () => {
  const before = await status('before');
  if (before.playing !== (restore.playing === 'true')) throw new Error('Restore playing state disagrees with board');
  try {
    for (const station of stations) {
      log('phase', {station, seconds});
      await command('play=' + station);
      await sleep(seconds * 1000);
      const state = await status('station-' + station);
      if (!state.playing || state.connecting || state.error)
        throw new Error(`Station ${station} is not playing at the checkpoint`);
    }
  } finally {
    let restored = false;
    for (let attempt = 0; attempt < 3 && !restored; ++attempt) {
      try {
        await command('play=' + restore.station);
        if (restore.playing === 'false') await command('stop=1');
        await command('volume=' + restore.volume);
        const state = await status('restored');
        restored = state.playing === (restore.playing === 'true');
      } catch (error) { log('restore_error', {error: error.message}); }
    }
    if (!restored) throw new Error('Restoration failed; board recovery required');
  }
})().catch(error => { log('fatal', {error: error.stack}); process.exitCode = 1; });

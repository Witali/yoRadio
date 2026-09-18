#!/usr/bin/env node
// Finite, LAN-only reconnect test: short valid Opus, HTTP 503, repeat;
// then the original long stream. No playlist, adapter, serial or OTA writes.
const fs = require('node:fs'), http = require('node:http'), path = require('node:path');
const crypto = require('node:crypto');
const {pages, crc, createStation} = require('./local_radio.cjs');

function prefix(data, milliseconds = 3000) {
  if (!Number.isInteger(milliseconds) || milliseconds < 1) throw Error('Invalid duration');
  const parsed = pages(data);
  const end = parsed.findIndex(p => p.endMs >= milliseconds &&
    p.bytes[26] && p.bytes[26 + p.bytes[26]] !== 255);
  if (end < 0) throw Error('No complete-packet page at requested duration');
  const selected = parsed.slice(0, end + 1).map(p => Buffer.from(p.bytes));
  const last = selected.at(-1);
  last[5] |= 4; // EOS; do not alter any encoded packet or granule.
  last.writeUInt32LE(crc(last), 22);
  const result = Buffer.concat(selected);
  pages(result); // Revalidate the checksum/framing of the shortened stream.
  return result;
}

function createReconnectStation(data, {cycles = 10, durationMs = 3000,
  leadMs = 1000, log = () => {}} = {}) {
  if (!Number.isInteger(cycles) || cycles < 1 || cycles > 10) throw Error('Invalid cycles');
  const short = createStation(prefix(data, durationMs),
    {leadMs, log: x => log({stream: 'short', ...x})});
  const full = createStation(data, {leadMs, log: x => log({stream: 'full', ...x})});
  let requests = 0;
  return http.createServer((req, res) => {
    if (req.url !== '/live.opus' && req.url !== '/buffered.opus') {
      res.writeHead(404, {'Content-Length': 0, Connection: 'close'}); res.end(); return;
    }
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.writeHead(405, {Allow: 'GET, HEAD', 'Content-Length': 0, Connection: 'close'});
      res.end(); return;
    }
    // Probes must not consume the fault schedule.
    if (req.method === 'HEAD') { full.emit('request', req, res); return; }
    const ordinal = ++requests;
    if (ordinal <= cycles * 2 && ordinal % 2 === 0) {
      log({event: 'fault', ordinal, status: 503, remote: req.socket.remoteAddress});
      res.writeHead(503, {'Content-Length': 0, Connection: 'close', 'Cache-Control': 'no-store'});
      res.end(); return;
    }
    const stream = ordinal <= cycles * 2 ? 'short' : 'full';
    log({event: 'dispatch', ordinal, stream});
    (stream === 'short' ? short : full).emit('request', req, res);
  });
}
module.exports = {prefix, createReconnectStation};

if (require.main === module) {
  const args = process.argv.slice(2), opt = (k, d) => args.includes(k) ? args[args.indexOf(k) + 1] : d;
  const file = opt('--file'), output = opt('--output'), host = opt('--host', '127.0.0.1');
  const port = Number(opt('--port', '8765')), seconds = Number(opt('--seconds', '600'));
  if (!file || !output || fs.existsSync(output) || !Number.isInteger(port) || port < 1024 ||
      port > 65535 || !Number.isInteger(seconds) || seconds < 60 || seconds > 900 ||
      !/^(127\.0\.0\.1|192\.168\.\d+\.\d+)$/.test(host))
    throw Error('Explicit file, new output, bounded LAN listener required');
  const data = fs.readFileSync(file);
  fs.mkdirSync(path.dirname(output), {recursive: true});
  const log = row => {
    const line = JSON.stringify({utc: new Date().toISOString(), ...row});
    fs.appendFileSync(output, line + '\n'); console.log(line);
  };
  const server = createReconnectStation(data, {log});
  const timer = setTimeout(() => {server.closeAllConnections(); server.close();}, seconds * 1000);
  server.once('close', () => clearTimeout(timer));
  server.once('error', error => {clearTimeout(timer); console.error(error); process.exitCode = 1;});
  server.listen(port, host, () => log({event: 'listen', host, port, cycles: 10,
    file: path.basename(file), sha256: crypto.createHash('sha256').update(data).digest('hex'),
    short_duration_ms: pages(prefix(data)).at(-1).endMs, lifetime_seconds: seconds}));
}

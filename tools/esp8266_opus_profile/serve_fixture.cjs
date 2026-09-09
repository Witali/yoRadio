#!/usr/bin/env node
// Explicit local fixture server; never modifies board state or network adapters.
const fs = require('node:fs');
const http = require('node:http');
const path = require('node:path');

function createFixtureServer(file, log = () => {}) {
  const bytes = fs.statSync(file).size;
  if (!fs.statSync(file).isFile() || !bytes) throw Error('Expected nonempty fixture file');
  return http.createServer((req, res) => {
    if (req.url !== '/test.opus') { res.writeHead(404, {'Content-Length': 0, Connection: 'close'}); res.end(); return; }
    if (!['GET', 'HEAD'].includes(req.method)) {
      res.writeHead(405, {Allow: 'GET, HEAD', 'Content-Length': 0, Connection: 'close'}); res.end(); return;
    }
    const started = performance.now(), socket = req.socket, initialBytes = socket.bytesWritten;
    const fields = {at: new Date().toISOString(), remote: socket.remoteAddress, method: req.method, fixture: path.basename(file), bytes};
    log({...fields, event: 'request'});
    res.writeHead(200, {'Content-Type': 'audio/ogg', 'Content-Length': bytes, Connection: 'close'});
    let source;
    res.once('finish', () => log({...fields, event: 'finish', ms: performance.now() - started, socket_bytes: socket.bytesWritten - initialBytes}));
    res.once('close', () => {
      if (source) source.destroy();
      log({...fields, event: 'close', complete: res.writableFinished, ms: performance.now() - started, socket_bytes: socket.bytesWritten - initialBytes});
    });
    if (req.method === 'HEAD') { res.end(); return; }
    source = fs.createReadStream(file);
    source.once('error', error => { log({...fields, event: 'read_error', error: error.message}); res.destroy(error); });
    source.pipe(res);
  });
}

if (require.main === module) {
  const args = process.argv.slice(2), opt = (key, fallback) => args.includes(key) ? args[args.indexOf(key) + 1] : fallback;
  const file = opt('--file'), host = opt('--host', '127.0.0.1'), port = Number(opt('--port', '8765'));
  if (!file || !Number.isInteger(port) || port < 1 || port > 65535) throw Error('--file is required; --port must be 1..65535');
  const output = opt('--output');
  if (output) fs.mkdirSync(path.dirname(output), {recursive: true});
  const log = data => { const line = JSON.stringify(data); console.log(line); if (output) fs.appendFileSync(output, line + '\n'); };
  const server = createFixtureServer(path.resolve(file), log);
  server.listen(port, host, () => log({event: 'listening', host, port, file: path.resolve(file)}));
  server.on('error', error => { console.error(error.message); process.exitCode = 1; });
}
module.exports = {createFixtureServer};

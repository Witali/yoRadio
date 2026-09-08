#!/usr/bin/env node
// Bounded LAN source; paced radio traffic or unpaced throughput control.
const http = require('node:http'), fs = require('node:fs');
const sources = {
  '/mp3-128': ['tests/fixtures/mp3_composite/mix-128.mp3', 'audio/mpeg'],
  '/mp3-320': ['tests/fixtures/mp3_composite/mix-320.mp3', 'audio/mpeg'],
  '/aac-64': ['tests/fixtures/aac_composite/mix-064.aac', 'audio/aac'],
};
function createServer() {
  return http.createServer(async (req, res) => {
    const url = new URL(req.url, 'http://localhost');
    const source = sources[url.pathname], rate = Number(url.searchParams.get('rate'));
    if (req.method !== 'GET' || !source || ![0,64,128,320].includes(rate)) {
      res.writeHead(404, {'Connection':'close'}); res.end(); return;
    }
    const input = fs.readFileSync(source[0]);
    const loops = rate ? Math.ceil(rate*1000/8*35/input.length) : Math.ceil(128*1024*1024/input.length);
    const length = loops*input.length;
    res.writeHead(200, {'Content-Type':source[1], 'Content-Length':length, 'Connection':'close'});
    res.socket.setNoDelay(true);
    const started = performance.now();
    let bytes = 0, closed = false;
    res.on('close', () => { closed = true; });
    try {
      while (!closed && bytes < length) {
        const offset = bytes % input.length;
        const n = Math.min(1024, input.length-offset, length-bytes);
        if (!res.write(input.subarray(offset, offset+n))) {
          await new Promise(resolve => {
            const done = () => { res.off('drain',done); res.off('close',done); resolve(); };
            res.once('drain',done); res.once('close',done);
          });
          if (closed) break;
        }
        bytes += n;
        if (rate) {
          const wait = started + bytes*8/rate - performance.now();
          if (wait > 0) await new Promise(resolve => setTimeout(resolve,wait));
        }
      }
    } catch (error) {
      if (!['ECONNRESET','EPIPE'].includes(error.code)) console.error(error.message);
    } finally {
      res.end();
      console.log(JSON.stringify({path:url.pathname,rate_kbps:rate,bytes_written:bytes,
        elapsed_ms:Math.round(performance.now()-started),peer_closed:closed}));
    }
  });
}
module.exports={createServer};
if (require.main === module) {
  const server=createServer();
  server.listen(8765,'192.168.100.253',()=>console.log('LAN audio source on 192.168.100.253:8765'));
}

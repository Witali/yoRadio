const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const {createFixtureServer} = require('../tools/esp8266_opus_profile/serve_fixture.cjs');

test('fixture server streams exact file with bounded HTTP lifecycle and no directory exposure', async t => {
  const file = path.resolve(__dirname, 'fixtures/opus_native/mono-12.opus'), events = [];
  const server = createFixtureServer(file, event => events.push(event));
  t.after(() => new Promise(resolve => server.close(resolve)));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  async function request(method, url = '/test.opus') {
    return new Promise((resolve, reject) => {
      const req = http.request({host: '127.0.0.1', port: server.address().port, path: url, method, agent: false}, res => {
        const chunks = [];
        res.on('data', chunk => chunks.push(chunk)); res.on('error', reject);
        res.on('end', () => resolve({status: res.statusCode, headers: res.headers, body: Buffer.concat(chunks)}));
      });
      req.on('error', reject); req.end();
    });
  }
  const get = await request('GET');
  assert.equal(get.status, 200); assert.deepEqual(get.body, fs.readFileSync(file));
  assert.equal(get.headers.connection, 'close'); assert.equal(get.headers['content-type'], 'audio/ogg');
  assert.equal(Number(get.headers['content-length']), get.body.length);
  const head = await request('HEAD'); assert.equal(head.status, 200); assert.equal(head.body.length, 0);
  assert.equal(Number(head.headers['content-length']), get.body.length);
  assert.equal((await request('GET', '/../../wifi.csv')).status, 404);
  const post = await request('POST'); assert.equal(post.status, 405); assert.equal(post.headers.allow, 'GET, HEAD');
  assert.ok(events.some(event => event.event === 'close' && event.complete));
  assert.ok(events.some(event => event.event === 'finish' && event.socket_bytes > get.body.length));
});

test('optional FIN hold preserves payload and can be cancelled by the client', async t => {
  const file = path.resolve(__dirname, 'fixtures/opus_native/mono-12.opus'), events = [];
  assert.throws(() => createFixtureServer(file, undefined, {holdOpenMs: -1}));
  const server = createFixtureServer(file, event => events.push(event), {holdOpenMs: 200});
  t.after(() => new Promise(resolve => server.close(resolve)));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const body = await new Promise((resolve, reject) => {
    // Retain the client socket until the test explicitly closes it.
    const req = http.get({host: '127.0.0.1', port: server.address().port, path: '/test.opus', agent: false}, res => {
      const chunks = []; res.on('data', data => chunks.push(data)); res.on('error', reject);
      res.on('end', () => { resolve(Buffer.concat(chunks)); req.destroy(); });
    }); req.on('error', reject);
  });
  assert.deepEqual(body, fs.readFileSync(file));
  await new Promise(resolve => setTimeout(resolve, 30));
  assert.ok(events.some(event => event.event === 'close' && !event.complete));
  assert.ok(!events.some(event => event.event === 'finish'));
});

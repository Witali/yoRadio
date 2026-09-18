const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const {prefix, createReconnectStation} = require('../tools/esp8266_opus_profile/reconnect_radio.cjs');
const {pages} = require('../tools/esp8266_opus_profile/local_radio.cjs');
const data = fs.readFileSync(path.join(__dirname, 'fixtures/opus_local_radio/mono-12-20ms.opus'));

test('short stream changes only final EOS/checksum, preserving Opus packets and granules', () => {
  const before = Buffer.from(data), result = prefix(data), original = pages(data), short = pages(result);
  assert.deepEqual(data, before);
  assert.ok(short.at(-1).endMs >= 3000 && short.at(-1).endMs < 5000);
  assert.ok(result.length < data.length);
  short.forEach((p, i) => {
    const source = Buffer.from(original[i].bytes), actual = Buffer.from(p.bytes);
    if (i === short.length - 1) {
      source[5] &= ~4; actual[5] &= ~4; source.fill(0, 22, 26); actual.fill(0, 22, 26);
    }
    assert.deepEqual(actual, source);
  });
  assert.throws(() => prefix(data, 400000), /No complete/);
  assert.throws(() => createReconnectStation(data, {cycles: 11}), /Invalid cycles/);
});

test('ten finite valid streams alternate with ten well-framed 503s, then full stream', async t => {
  const log = [], server = createReconnectStation(data, {log: row => log.push(row)});
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => {server.closeAllConnections(); server.close();});
  const get = (method = 'GET', route = '/buffered.opus') => new Promise((resolve, reject) => {
    const req = http.request({host: '127.0.0.1', port: server.address().port,
      path: route, method, agent: false}, res => {
      const parts = []; res.on('data', p => parts.push(p)); res.on('error', reject);
      res.on('end', () => resolve({status: res.statusCode, headers: res.headers, data: Buffer.concat(parts)}));
    });
    req.setTimeout(5000, () => req.destroy(Error('timeout'))); req.on('error', reject); req.end();
  });
  assert.equal((await get('GET', '/other')).status, 404);
  assert.equal((await get('POST')).status, 405);
  const short = prefix(data);
  for (let i = 0; i < 10; i++) {
    assert.equal((await get('HEAD')).data.length, 0);
    const success = await get();
    assert.equal(success.status, 200); assert.deepEqual(success.data, short);
    const failure = await get();
    assert.equal(failure.status, 503); assert.equal(failure.headers['content-length'], '0');
    assert.equal(failure.headers.connection, 'close');
    assert.equal(failure.headers['transfer-encoding'], undefined); assert.equal(failure.data.length, 0);
  }
  assert.deepEqual((await get()).data, data);
  assert.equal(log.filter(row => row.event === 'fault').length, 10);
  assert.equal(log.filter(row => row.event === 'dispatch').at(-1).ordinal, 21);
});

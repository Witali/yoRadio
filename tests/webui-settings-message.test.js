const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), zlib = require('node:zlib'), vm = require('node:vm');
const source = zlib.gunzipSync(fs.readFileSync(require('node:path').join(__dirname,
  '../yoRadio/data/www/script.js.gz'))).toString();
const handler = source.slice(source.indexOf('function onMessage('), source.indexOf('function escapeData('));
for (const hasLink of [false, true]) {
  test(`system snapshot is processed on ${hasLink ? 'settings' : 'player'} page`, () => {
    const seen = {}, errors = [], link = {innerHTML: ''};
    const context = {JSON, Object, hostname: '192.168.100.6', escapeData: s => s,
      getId: id => id === 'radiolink' && hasLink ? link : null,
      setupElement: (id, value) => {seen[id] = value;}, console: {log: (...args) => errors.push(args)}};
    vm.runInNewContext(handler, context);
    context.onMessage({data: JSON.stringify({mdns:'yoradio', ipaddr:'192.168.100.6', normtime:5000, normalize:1})});
    assert.deepEqual(errors, []);
    assert.equal(seen.normtime, 5000);
    assert.equal(seen.normalize, 1);
    if (hasLink) assert.equal(link.innerHTML, '<a href="http://yoradio.local/settings.html">http://yoradio.local/</a>');
  });
}

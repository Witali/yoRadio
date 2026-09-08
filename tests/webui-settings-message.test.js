const test = require('node:test'), assert = require('node:assert/strict');
const fs = require('node:fs'), zlib = require('node:zlib'), vm = require('node:vm');
const source = zlib.gunzipSync(fs.readFileSync(require('node:path').join(__dirname,
  '../yoRadio/data/www/script.js.gz'))).toString();
const bootstrap = source.slice(source.indexOf('function websocketBootstrapEnabled('), source.indexOf('function initialPlayerStateReady('));
const handler = bootstrap+'\n'+source.slice(source.indexOf('function onMessage('), source.indexOf('function escapeData('));
test('station broadcasts update current state without requiring the player DOM', () => {
  const select = source.slice(source.indexOf('function setCurrentItem('), source.indexOf('function normalizeStationName('));
  const errors = [];
  const context = {JSON, currentItem:0, getId:()=>null, shouldScrollCurrentItem:()=>false,
    escapeData:s=>s, console:{log:(...args)=>errors.push(args)}};
  vm.runInNewContext(select+'\n'+handler, context);
  context.onMessage({data:'{"current":176}'});
  assert.deepEqual(errors, []);
  assert.equal(context.currentItem, 176);
});
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

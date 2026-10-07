const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const zlib = require('node:zlib');
const test = require('node:test');
const source = zlib.gunzipSync(fs.readFileSync(path.join(__dirname,
  '../yoRadio/data/www/script.js.gz'))).toString('utf8');
const start = source.indexOf('function setupElement(');
const end = source.indexOf('\nfunction ', start + 1);
assert.ok(start >= 0 && end > start);

function setup(withSettings = true) {
  const elements = new Map();
  const rows = [];
  if (withSettings) elements.set('group_system', {appendChild: row => {
    rows.push(row);
    assert.match(row.innerHTML, /data-command="stationtimeout"/);
    assert.match(row.innerHTML, /min="1" max="120" step="1"/);
    elements.set('stationtimeout', {});
  }});
  const context = {getId: id => elements.get(id), document: {createElement: () => ({})}};
  vm.runInNewContext(source.slice(start, end), context);
  return {rows, elements, update: context.setupElement};
}

test('timeout appears only when firmware advertises it and updates without duplicate rows', () => {
  const ui = setup();
  ui.update('abuffmax', 14);
  assert.equal(ui.rows.length, 0);
  ui.update('stationtimeout', 10);
  assert.equal(ui.elements.get('stationtimeout').value, 10);
  ui.update('stationtimeout', 25);
  assert.equal(ui.rows.length, 1);
  assert.equal(ui.elements.get('stationtimeout').value, 25);
});

test('setting messages on the player page do not create detached controls', () => {
  const ui = setup(false);
  ui.update('stationtimeout', 10);
  assert.equal(ui.rows.length, 0);
});

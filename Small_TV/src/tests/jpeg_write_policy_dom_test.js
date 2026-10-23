// DOM/HTTP contract only; actual NVS and physical flash are tested in C/QEMU.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const script = fs.readFileSync(path.join(__dirname, '../../local_site/photo_write_policy.js'), 'utf8');
const settle = () => new Promise(resolve => setImmediate(resolve));
let checks = 0;

async function fixture(saved, readOK = true, saveOK = true) {
    // Keep text and HTML distinct; injecting a server message as markup fails.
    const elements = Object.fromEntries(['form', 'limit', 'save', 'status'].map(key => [key, {value: '200', textContent: ''}]));
    Object.defineProperty(elements.status, 'innerHTML', {set() { throw new Error('Unsafe HTML insertion'); }});
    let submit;
    elements.form.addEventListener = (event, handler) => { assert.equal(event, 'submit'); submit = handler; };
    const calls = [];
    const document = {
        addEventListener(event, handler) { assert.equal(event, 'DOMContentLoaded'); handler(); },
        getElementById(id) { return elements[id.slice('jpeg-write-'.length)]; }
    };
    const fetch = async (url, options) => {
        calls.push({url, options});
        return options ? {ok: saveOK, text: async () => '<img src=x onerror=bad()>'} :
            {ok: readOK, json: async () => ({limit_kib: saved})};
    };
    vm.runInNewContext(script, {document, fetch, Number, JSON, Error});
    await settle();
    return {elements, calls, submit: async value => {
        elements.limit.value = value; let prevented = false;
        await submit({preventDefault() { prevented = true; }}); assert.ok(prevented);
    }};
}

(async () => {
    for (const saved of [0, 200, 4294967295]) {
        const f = await fixture(saved);
        assert.equal(f.elements.limit.value, String(saved)); assert.equal(f.elements.save.disabled, false);
        await f.submit('0');
        assert.equal(f.calls[1].url, '/set_jpeg_write_limit');
        assert.equal(f.calls[1].options.body, '{"limit_kib":0}');
        assert.match(f.elements.status.textContent, /disabled/); checks++;
    }
    for (const value of ['', '-1', '0.1', '4294967296', '1e2', 'abc']) {
        const f = await fixture(200); await f.submit(value);
        assert.equal(f.calls.length, 1); assert.match(f.elements.status.textContent, /whole number/); checks++;
    }
    for (const saved of [-1, 0.5, 4294967296, '0', null]) {
        const f = await fixture(saved);
        assert.equal(f.elements.save.disabled, true); assert.match(f.elements.status.textContent, /Invalid saved/); checks++;
    }
    const failedRead = await fixture(0, false);
    assert.equal(failedRead.elements.save.disabled, true); checks++;
    const failedSave = await fixture(200, true, false); await failedSave.submit('0');
    assert.match(failedSave.elements.status.textContent, /Could not save: <img/);
    assert.equal(failedSave.elements.save.disabled, false); checks++;
    console.log(JSON.stringify({passed: true, cases: checks, real_browser_tested: false}));
})().catch(error => { console.error(error); process.exitCode = 1; });

/* Execute real page scan callbacks against synthetic HTTP records and a small DOM. */
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {readFileSync} from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';

const directory = process.argv[2];
if (!directory) throw new Error('Pass the generated pages directory');
const checks = [];
const pages = {};

async function scan(page, records) {
    /* Run the shipped scan handlers; mocks supply only DOM and HTTP boundaries. */
    const html = readFileSync(path.join(directory, page + '.html'), 'utf8');
    pages[page] = crypto.createHash('sha256').update(html).digest('hex');
    const code = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(match => match[1]).join('\n');
    const ready = [], nodes = new Map(), requests = [], errors = [];
    function element() {
        return {children: [], value: '', style: {}, addEventListener() {},
            appendChild(child) {this.children.push(child);},
            set innerHTML(value) {this.children = [];},
            get textContent() {return this.label ?? '';},
            set textContent(value) {this.label = String(value);}};
    }
    const document = {
        addEventListener(event, callback) {if (event === 'DOMContentLoaded') ready.push(callback);},
        getElementById(id) {if (!nodes.has(id)) nodes.set(id, element()); return nodes.get(id);},
        createElement: element, querySelector() {return null;}, querySelectorAll() {return [];}
    };
    const context = vm.createContext({document, window: {addEventListener() {}},
        console: {log() {}, error(error) {errors.push(String(error));}},
        fetch: async url => {requests.push(url);
            // Hold unrelated settings initialization reads at the HTTP boundary.
            if (url !== '/scan') return new Promise(() => {});
            return {ok: true, json: async () => records};},
        setInterval() {}, setTimeout() {}});
    new vm.Script(code, {filename: page + '.html'}).runInContext(context);
    if (page === 'setup') ready.forEach(callback => callback());
    else context.refreshList(); // Legacy optional settings control, with its DOM present.
    for (let attempt = 0; attempt < 20; attempt++) await new Promise(setImmediate);
    assert.deepEqual(errors, []);
    assert.deepEqual(requests.filter(url => url === '/scan'), ['/scan']);
    return nodes.get(page === 'setup' ? 'ssid' : 'wifi_list').children;
}

for (const page of ['setup', 'settings']) {
    for (const [name, records, labels] of [
        ['signed-dbms', [{ssid: 'Near', rssi: -22}, {ssid: 'Far', rssi: -91}, {ssid: 'Limit', rssi: -127}],
         ['Near (-22dBm)', 'Far (-91dBm)', 'Limit (-127dBm)']],
        ['zero-and-missing', [{ssid: 'Zero', rssi: 0}, {ssid: 'Unknown'}, {ssid: 'Bad', rssi: 'invalid'}],
         ['Zero (0dBm)', 'Unknown', 'Bad']],
        ['literal-ssid', [{ssid: '<img src=x onerror=alert(1)> & "quoted"', rssi: -40}],
         ['<img src=x onerror=alert(1)> & "quoted" (-40dBm)']],
        ['non-finite', [{ssid: 'NaN', rssi: NaN}, {ssid: 'Inf', rssi: Infinity}], ['NaN', 'Inf']]
    ]) {
        try {
            const options = await scan(page, records);
            assert.deepEqual(options.map(option => option.label), labels);
            assert.deepEqual(options.map(option => option.value), records.map(row => row.ssid));
            if (page === 'setup') assert.equal(options[0].selected, true);
            checks.push({page, case: name, passed: true});
        } catch (error) {checks.push({page, case: name, passed: false, error: error.message});}
    }
}
const report = {passed: checks.every(row => row.passed), checks, pages,
    scope: 'Actual generated scan handlers; mocked DOM/HTTP. Settings legacy scan is tested with its optional control present. Browser/RF acceptance remains separate.'};
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;

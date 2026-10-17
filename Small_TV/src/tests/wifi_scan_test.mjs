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

async function scan(page, records, {scanFails = false} = {}) {
    /* Run the shipped scan handlers; mocks supply only DOM and HTTP boundaries. */
    const html = readFileSync(path.join(directory, page + '.html'), 'utf8');
    pages[page] = crypto.createHash('sha256').update(html).digest('hex');
    const code = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(match => match[1]).join('\n');
    const ready = [], nodes = new Map(), requests = [], errors = [], prompts = [];
    let promptReply = null;
    function element() {
        return {children: [], value: '', style: {}, dataset: {}, listeners: {},
            addEventListener(event, callback) {this.listeners[event] = callback;},
            appendChild(child) {this.children.push(child);},
            get selectedOptions() {return this.children.filter(child => child.selected);},
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
        prompt(message) {prompts.push(message); return promptReply;},
        fetch: async (url, options) => {requests.push({url, options});
            // Hold unrelated settings initialization reads at the HTTP boundary.
            if (url !== '/scan') return new Promise(() => {});
            if (scanFails) throw new Error('Synthetic scan failure');
            return {ok: true, json: async () => records};},
        setInterval() {}, setTimeout() {}});
    new vm.Script(code, {filename: page + '.html'}).runInContext(context);
    if (page === 'setup') ready.forEach(callback => callback());
    else context.refreshList(); // Legacy optional settings control, with its DOM present.
    for (let attempt = 0; attempt < 20; attempt++) await new Promise(setImmediate);
    if (!scanFails) assert.deepEqual(errors, []);
    assert.deepEqual(requests.filter(row => row.url === '/scan').map(row => row.url), ['/scan']);
    const select = nodes.get(page === 'setup' ? 'ssid' : 'wifi_list');
    return {options: select.children, prompts, requests,
        submit(index, reply) {
            /* Exercise the actual form listener and selected option identity. */
            promptReply = reply;
            select.children.forEach((option, position) => {option.selected = position === index;});
            select.value = select.children[index].value;
            document.getElementById('password').value = 'synthetic-test-pass';
            nodes.get('wifiForm').listeners.submit({preventDefault() {}});
        }};
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
            const {options} = await scan(page, records);
            assert.deepEqual(options.map(option => option.label), labels);
            assert.deepEqual(options.map(option => option.value), records.map(row => row.ssid));
            if (page === 'setup') assert.equal(options[0].selected, true);
            checks.push({page, case: name, passed: true});
        } catch (error) {checks.push({page, case: name, passed: false, error: error.message});}
    }
}
for (const scenario of [
    {name: 'real-ssid-manual', records: [{ssid: 'manual', rssi: -32}], index: 0,
     promptReply: 'wrong-network', promptCount: 0, sent: 'manual'},
    {name: 'real-ssid-ordinary', records: [{ssid: 'Kitchen & <TV>', rssi: -50}], index: 0,
     promptCount: 0, sent: 'Kitchen & <TV>'},
    {name: 'manual-entry', records: [], index: 1, promptReply: 'Hidden TV', promptCount: 1, sent: 'Hidden TV'},
    {name: 'manual-entry-literal-manual', records: [], index: 1, promptReply: 'manual', promptCount: 1, sent: 'manual'},
    {name: 'manual-cancel', records: [], index: 1, promptReply: null, promptCount: 1, sent: null},
    {name: 'manual-empty', records: [], index: 1, promptReply: '', promptCount: 1, sent: null},
    {name: 'manual-after-scan-error', records: [], index: 1, scanFails: true,
     promptReply: 'Recovery TV', promptCount: 1, sent: 'Recovery TV'}
]) {
    try {
        const loaded = await scan('setup', scenario.records, scenario);
        loaded.submit(scenario.index, scenario.promptReply);
        assert.equal(loaded.prompts.length, scenario.promptCount);
        const sent = loaded.requests.filter(row => row.url === '/configure');
        assert.equal(sent.length, scenario.sent === null ? 0 : 1);
        if (sent.length) {
            assert.equal(sent[0].options.method, 'POST');
            assert.deepEqual(JSON.parse(sent[0].options.body),
                {ssid: scenario.sent, password: 'synthetic-test-pass'});
        }
        checks.push({page: 'setup', case: scenario.name, passed: true});
    } catch (error) {checks.push({page: 'setup', case: scenario.name, passed: false, error: error.message});}
}
const report = {passed: checks.every(row => row.passed), checks, pages,
    scope: 'Actual generated scan and setup-submit handlers; mocked DOM/HTTP/prompt. Settings legacy scan is tested with its optional control present. Browser/RF acceptance remains separate.'};
console.log(JSON.stringify(report, null, 2));
if (!report.passed) process.exitCode = 1;

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const test = require('node:test');
function loader(failures) {
  const source = fs.readFileSync(path.join(__dirname,'../yoRadio/src/core/netserver.h'),'utf8');
  const code = source.slice(source.indexOf('const loadUiElement ='),
    source.indexOf('    (async () => {'));
  const state = {attempts:0, removed:0, delays:[]};
  const context = {
    document: {createElement:()=>({remove:()=>++state.removed}),
      head:{appendChild:el=>{ ++state.attempts; queueMicrotask(()=>state.attempts<=failures?el.onerror():el.onload());}}},
    setTimeout:(fn,ms)=>{state.delays.push(ms);fn();},
    console:{log:()=>{}}
  };
  vm.runInNewContext(code+'\nthis.load = loadUiElement;',context);
  return {state, load:context.load};
}
test('native bootstrap retries failed script downloads sequentially and succeeds',async()=>{
  const {state,load}=loader(2);
  await load('script',el=>el.src='/script.js');
  assert.equal(state.attempts,3);
  assert.equal(state.removed,2);
  assert.deepEqual(state.delays,[250,500]);
});
test('native bootstrap stops after three failures instead of retrying forever',async()=>{
  const {state,load}=loader(99);
  await assert.rejects(load('link',el=>el.href='/style.css'),/Unable to load/);
  assert.equal(state.attempts,3);
  assert.equal(state.removed,3);
});

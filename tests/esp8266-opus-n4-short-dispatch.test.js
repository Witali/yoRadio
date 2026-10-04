const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root}=require('../tools/esp8266_opus_asm/export.cjs');
const {analyze,archive}=require('../tools/esp8266_opus_asm/analyze_n4_short_dispatch.cjs');
test('prospective short-N4 dispatch frequencies reproduce from authenticated traces',()=>{
 const actual=analyze(),saved=JSON.parse(fs.readFileSync(path.join(root,archive)));
 assert.deepEqual(actual,saved);
 assert.match(actual.scope,/no exact instruction\/cycle saving claim/);
 assert.deepEqual(actual.cases.map(c=>[c.name,c.helper_calls,c.cuts.find(x=>x.cut===10).bypassed_helper_calls]),[
  ['stereo-128',536,233],['stereo-192',1055,201],['stereo-320-20ms',1204,157],['stereo-510',5287,755]
 ]);
 for(const c of actual.cases)for(const cut of c.cuts){
  assert.equal(cut.bypassed_helper_calls+cut.remaining_helper_calls,c.helper_calls);
  assert.ok(cut.original_linear_steps_in_bypassed_calls>=cut.bypassed_helper_calls);
 }
});

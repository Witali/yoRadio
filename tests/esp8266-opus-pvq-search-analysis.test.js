const test=require('node:test'),assert=require('node:assert/strict');
const {search,selfTest,summarize}=require('../tools/esp8266_opus_asm/analyze_pvq_search.cjs');
test('all modeled search brackets return the identical coordinate',()=>{assert.ok(selfTest().cases>100000);});
test('linear model includes its final successful load; binary reuses initial q',()=>{
 assert.deepEqual(search(3,9,5,'linear'),{index:5,loads:5});
 assert.deepEqual(search(3,3,3,'binary'),{index:3,loads:0});
 assert.equal(search(3,9,9,'prefix2').loads,1);
});
test('empty SILK corpus is not described as a search speedup',()=>{
 assert.equal(summarize([]).relative_probe_reduction_percent.binary,null);
});
test('invalid bounds fail rather than narrowing the decoded domain',()=>{
 for(const args of[[2,9,5],[3,2,2],[3,9,10],[3,9,2]])assert.throws(()=>search(...args,'binary'));
 assert.throws(()=>search(3,9,5,'unknown'));
});

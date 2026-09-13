const test=require('node:test'),assert=require('node:assert/strict');
const {linkedGraph,reachableDisassembly}=require('../tools/esp8266_opus_asm/report_layout.cjs');
test('linked graph compares direct CALL0 and relocated indirect CALLX0 without hiding cost',()=>{
 const direct='100: 000005 call0 500 <target>\n103: f00d ret.n\n';
 const indirect='200: 000001 l32r a0, 800 <literal>\n203: 0000c0 callx0 a0\n206: f00d ret.n\n';
 const resolve=x=>x===0x500?'target':'0x'+x.toString(16),word=x=>{assert.equal(x,0x800);return 0x500;};
 const a=linkedGraph(direct,word,resolve),b=linkedGraph(indirect,word,resolve);
 assert.deepEqual(a.graph,b.graph);assert.equal(a.physical_instruction_count,2);assert.equal(b.physical_instruction_count,3);
 assert.equal(b.relaxed_indirect_calls,1);assert.equal(a.relaxed_indirect_calls,0);
 assert.notDeepEqual(a.graph,linkedGraph(direct.replace('500','504'),word,resolve).graph);
});
test('linked graph retains branch destinations, register operations and numeric literals',()=>{
 const a='100: 000001 l32r a2, 800 <literal>\n103: 000026 beqz a2, 108 <f+8>\n106: 223b addi.n a2, a2, 1\n108: f00d ret.n\n';
 const graph=linkedGraph(a,()=>123,String).graph;
 assert.match(graph[0],/literal:123/);assert.match(graph[1],/instruction:3/);
 for(const changed of [a.replace('a2, a2, 1','a2, a2, 2'),a.replace('108 <','106 <')])assert.notDeepEqual(linkedGraph(changed,()=>123,String).graph,graph);
 assert.notDeepEqual(linkedGraph(a,()=>124,String).graph,graph);
 assert.throws(()=>linkedGraph(a.replace('108 <','107 <'),()=>123,String));
});
test('CFG follows real targets, never decodes padding after J, rejects reachable garbage',()=>{
 const s={address:0x100,bytes:10,name:'f'},blocks=new Map([
  [0x100,'100: 000006 j 108 <f+8>\n103: ff .byte 0xff\n108: f00d ret.n'],
  [0x108,'108: f00d ret.n']
 ]);
 const text=reachableDisassembly('',s,start=>{assert.ok(blocks.has(start));return blocks.get(start);});
 assert.equal(text.split('\n').length,2);assert.doesNotMatch(text,/\.byte/);
 assert.throws(()=>reachableDisassembly('',s,start=>blocks.get(start).replace('j 108','beqz a2, 108')));
 assert.throws(()=>reachableDisassembly('',s,()=> '100: 000006 j 10f <outside>'));
});

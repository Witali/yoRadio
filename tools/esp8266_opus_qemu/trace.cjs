/* Dynamic TCG instruction accounting, NOT CPU-cycle or flash-latency modelling.
 * Run with exec,in_asm,nochain. Without nochain repeated TBs may be invisible.
 * Only a normally completed, PCM-verified run is eligible for this report.
 */
const assert=require('node:assert/strict');
const regions={
 pvq:[[0x402531c0,0x402531c0+985],[0x40251024,0x40251024+94]],
};
function traceFilter(proof,variant) {
 // This scope is valid only for these two frozen layouts. A new experiment
 // must explicitly audit its function/helper boundaries before tracing.
 assert.ok(['esp8266-opus-ebands-final-candidate-v2','esp8266-opus-pvq-n3-unroll4-candidate-v1'].includes(variant));
 const fn=proof.actual_functions.decode_pulses;
 assert.equal(fn.address,regions.pvq[0][0]);assert.equal(fn.bytes,985);
 return regions.pvq.map(([a,b])=>'0x'+a.toString(16)+'+'+(b-a)).join(',');
}
function summarize(text) {
 const blocks=new Map(),pcCounts=new Map();let pending=[],executions=0;
 for(const line of text.split(/\r?\n/)) {
  const ins=line.match(/^0x([0-9a-f]+):\s+(\S+)\s*(.*)$/);
  if(ins){pending.push({address:parseInt(ins[1],16),op:ins[2],args:ins[3]});continue;}
  if(line==='----------------'){assert.equal(pending.length,0,'Unexecuted pending translation');continue;}
  const trace=line.match(/^Trace \d+: [0-9a-f]+ \[[0-9a-f]+\/([0-9a-f]+)\/[0-9a-f]+\/[0-9a-f]+\]/);
  if(!trace)continue;
  const pc=parseInt(trace[1],16);
  if(pending.length){assert.equal(pending[0].address,pc);if(blocks.has(pc))assert.deepEqual(blocks.get(pc),pending);blocks.set(pc,pending);pending=[];}
  const block=blocks.get(pc);assert.ok(block,'Execution has no known disassembly: '+pc.toString(16));++executions;
  for(const insn of block){const old=pcCounts.get(insn.address);if(old){assert.equal(old.op,insn.op);assert.equal(old.args,insn.args);++old.executions;}else pcCounts.set(insn.address,{...insn,executions:1});}
 }
 assert.equal(pending.length,0);assert.ok(executions);
 const totals={};
 for(const [name,ranges] of Object.entries(regions)) {
  const rows=[...pcCounts.values()].filter(i=>ranges.some(([a,b])=>i.address>=a&&i.address<b));
  const sum=predicate=>rows.filter(predicate).reduce((n,i)=>n+i.executions,0);
  totals[name]={instructions:sum(()=>true),load_instructions:sum(i=>/^l(?:8|16|32)/.test(i.op)),store_instructions:sum(i=>/^s(?:8|16|32)i/.test(i.op)),calls:sum(i=>/^call/.test(i.op)),unique_instructions:rows.length};
 }
 return {scope:'Executed instructions in decode_pulses and N3 helper only; callees excluded. Counts are not cycles or predicted CPU percent.',tb_executions:executions,totals,pc_counts:[...pcCounts.values()].sort((a,b)=>a.address-b.address)};
}
module.exports={summarize,regions,traceFilter};

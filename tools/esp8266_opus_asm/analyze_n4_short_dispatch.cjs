// Frequency evidence for a future K-threshold dispatch, NOT a CPU estimate.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
function analyze(){
 const dir=path.join(root,'docs/benchmarks/esp8266-opus-pvq-search-2026-09-19');
 const summary=JSON.parse(fs.readFileSync(path.join(dir,'summary.json')));
 const qemuFile=path.join(root,'tests/results/esp8266-opus-qemu-n4-uniform256-20261004/summary.json');
 const qemuBytes=fs.readFileSync(qemuFile),qemu=JSON.parse(qemuBytes),cases=[];
 for(const name of ['stereo-128','stereo-192','stereo-320-20ms','stereo-510']){
  const c=summary.cases.find(c=>c.name===name);assert.ok(c);const data=fs.readFileSync(path.join(dir,name+'.jsonl'));assert.equal(hash(data),c.trace_sha256);
  const rows=data.toString().trim().split(/\r?\n/).filter(Boolean).map(JSON.parse).filter(([n,k,t])=>n===4&&k>t);
  const dynamic=qemu.profiles[name].uniform256.calls-qemu.profiles[name].accepted.calls;
  assert.equal(rows.length,dynamic,'Trace does not match current QEMU helper dispatch');
  cases.push({name,trace_sha256:c.trace_sha256,helper_calls:dynamic,cuts:[8,10,12,16].map(cut=>{
   const small=rows.filter(([,k])=>k<cut);return {cut,bypassed_helper_calls:small.length,remaining_helper_calls:rows.length-small.length,original_linear_steps_in_bypassed_calls:small.reduce((s,[,k,t])=>s+k-t,0)};
  })});
 }
 const r={scope:'Prospective K<threshold dispatch counts from authenticated N/K/tail host traces, cross-checked against QEMU helper calls. Residual index absent: no exact instruction/cycle saving claim.',
  recipe_sha256_lf:sourceHash(__filename),qemu_summary_sha256:hash(qemuBytes),cases};
 return r;
}
const archive='docs/benchmarks/esp8266-opus-n4-uniform256-2026-10-04/short-dispatch.json';
module.exports={analyze,archive};
if(require.main===module){
 const args=process.argv.slice(2);assert.ok(args.length===0||(args.length===1&&args[0]==='--archive'),'Usage: node analyze_n4_short_dispatch.cjs [--archive]');
 const data=JSON.stringify(analyze(),null,2)+'\n',out=path.join(root,args.length?archive:'.build/opus-n4-short-dispatch.json');
 if(args.length&&fs.existsSync(out))assert.equal(fs.readFileSync(out,'utf8').replace(/\r\n/g,'\n'),data,'Do not replace earlier evidence');
 else {fs.mkdirSync(path.dirname(out),{recursive:true});fs.writeFileSync(out,data);}
 console.log(data);
}

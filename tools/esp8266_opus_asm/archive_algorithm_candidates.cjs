const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
function archive() {
 const source=path.join(root,'.build/opus-algorithm-candidates'),dest=path.join(root,'docs/benchmarks/esp8266-opus-algorithm-candidates-2026-09-19');
 const report=JSON.parse(fs.readFileSync(path.join(source,'results.json')));
 assert.equal(report.passed,true);assert.equal(report.variants.length,6);
 assert.equal(report.model_sha256,sourceHash(path.join(__dirname,'algorithm_candidates.cjs')));
 for(const v of report.variants) {assert.equal(v.passed,true);assert.equal(v.cases.length,v.kind==='observe'?10:24);assert.ok(v.cases.every(c=>c.pcm.exact));}
 const files=['results.json','lx106.json','n4-prefix/analysis.json','direct/results.json'];
 for(const kind of report.variants.map(v=>v.kind).filter(k=>k!=='observe')) {
  const dir=path.join(source,kind,'lx106');
  for(const name of fs.readdirSync(dir).filter(n=>n.endsWith('.disassembly.txt')||n.endsWith('.stack.txt')))files.push(kind+'/lx106/'+name);
 }
 const inventory=[];
 for(const name of files) {
  const bytes=fs.readFileSync(path.join(source,name)),target=path.join(dest,name);fs.mkdirSync(path.dirname(target),{recursive:true});
  if(fs.existsSync(target))assert.deepEqual(fs.readFileSync(target),bytes,'Do not overwrite archived evidence: '+name);
  else fs.writeFileSync(target,bytes);
  inventory.push({name,bytes:bytes.length,sha256:hash(bytes)});
 }
 fs.writeFileSync(path.join(dest,'inventory.json'),JSON.stringify({scope:report.scope,files:inventory},null,2)+'\n');console.log('Archived',files.length,'files');
}
module.exports={archive};if(require.main===module)archive();

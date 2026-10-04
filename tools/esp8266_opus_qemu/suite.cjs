/* Reproducible, computer-only A/B. Hardware speed acceptance stays pending. */
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {root,hash}=require('../esp8266_opus_asm/export.cjs');
const {summarize}=require('./trace.cjs');
const variants={accepted:'esp8266-opus-ebands-final-candidate-v2',n3_unroll4:'esp8266-opus-pvq-n3-unroll4-candidate-v1'};
function run(args=process.argv.slice(2)) {
 const i=args.indexOf('--output');assert.equal(args.length,i<0?0:2);
 const out=path.resolve(i<0?path.join(root,'.build/opus-qemu-suite'):args[i+1]);
 const relative=path.relative(root,out);assert.ok(relative&&!relative.startsWith('..')&&!path.isAbsolute(relative));
 assert.ok(!fs.existsSync(out),'Choose a new evidence directory');fs.mkdirSync(out,{recursive:true});
 const inventory=[];
 function save(name,data) {if(typeof data!=='string'&&!Buffer.isBuffer(data))data=JSON.stringify(data,null,2)+'\n';if(typeof data==='string')data=Buffer.from(data);fs.writeFileSync(path.join(out,name),data);inventory.push({name,bytes:data.length,sha256:hash(data)});}
 const results={scope:'Offline QEMU LX106; not ESP8266 CPU cycles or live I2S qualification',correctness:{},profiles:{},negative_guard:false,deterministic_replay:false};
 function attempt(label,variant,options=[],failure=false) {
  console.log(label);
  const r=spawnSync(process.execPath,[path.join(__dirname,'run.cjs'),'--variant',variant,...options],{encoding:'utf8',maxBuffer:4*1024*1024,timeout:60000});
  save(label+'.runner.log',(r.stdout||'')+(r.stderr||''));if(r.error)throw r.error;
  const build=path.join(root,'.build/opus-qemu',variant);
  for(const file of ['stdout.log','stderr.log'])if(fs.existsSync(path.join(build,file)))save(label+'.'+file+'.gz',zlib.gzipSync(fs.readFileSync(path.join(build,file))));
  const report=JSON.parse(fs.readFileSync(path.join(build,'report.json')));
  if(failure){assert.notEqual(r.status,0);assert.match(r.stderr,/QEMU 20:/);assert.equal(report.passed,false);return null;}
  assert.equal(r.status,0,r.stderr);assert.equal(report.passed,true);save(label+'.json',report);
  if(options.includes('--trace-pvq')) {
   const trace=fs.readFileSync(path.join(build,'trace.log'));assert.equal(hash(trace),report.instruction_trace.sha256);
   const parsed=summarize(trace.toString());save(label+'.trace.log.gz',zlib.gzipSync(trace));save(label+'.trace-summary.json',parsed);
   assert.deepEqual(parsed.totals,report.instruction_trace.totals);
  }
  return report;
 }
 for(const [label,variant] of Object.entries(variants))results.correctness[label]=attempt(label+'-extended',variant,['--extended']);
 assert.deepEqual(results.correctness.accepted.cases,results.correctness.n3_unroll4.cases);
 for(const fixture of ['stereo-128','stereo-192','stereo-320-20ms','stereo-510']) {
  const pair={};for(const [label,variant] of Object.entries(variants)) {
   const flags=['--fixture',fixture,'--no-self-tests','--trace-pvq'];if(/320|510/.test(fixture))flags.push('--extended');
   pair[label]=attempt(label+'-'+fixture,variant,flags);
  }
  assert.deepEqual(pair.accepted.cases,pair.n3_unroll4.cases);
  const a=pair.accepted.instruction_trace.totals.pvq,b=pair.n3_unroll4.instruction_trace.totals.pvq;
  results.profiles[fixture]={accepted:a,n3_unroll4:b,instruction_delta:b.instructions-a.instructions,load_delta:b.load_instructions-a.load_instructions,instruction_change_percent:100*(b.instructions/a.instructions-1)};
 }
 const replay=attempt('n3-replay-stereo-192',variants.n3_unroll4,['--fixture','stereo-192','--no-self-tests','--trace-pvq']);
 assert.deepEqual(replay.instruction_trace.totals.pvq,results.profiles['stereo-192'].n3_unroll4);results.deterministic_replay=true;
 attempt('negative-canary',variants.accepted,['--fixture','stereo-192','--fault-guard'],true);results.negative_guard=true;
 save('summary.json',results);save('inventory.json',inventory);console.log(JSON.stringify({passed:true,out,profiles:results.profiles},null,2));return results;
}
module.exports={run};if(require.main===module)run();

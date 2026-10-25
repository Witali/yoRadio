/* Reproducible, computer-only qualification of the accepted decoder.
 * Experimental A/B candidates remain on their research branch. */
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {root,hash}=require('../esp8266_opus_asm/export.cjs');
const {summarize}=require('./trace.cjs');
const variants={accepted:'esp8266-opus-ebands-final-candidate-v2'};
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
  // A clean checkout first compiles the sanitizer oracle through WSL.
  // The actual QEMU process retains the runner's separate 60-second limit.
  const r=spawnSync(process.execPath,[path.join(__dirname,'run.cjs'),'--variant',variant,...options],{encoding:'utf8',maxBuffer:4*1024*1024,timeout:options.includes('--extended')?600000:60000});
  save(label+'.runner.log',(r.stdout||'')+(r.stderr||''));if(r.error)throw r.error;
  const build=path.join(root,'.build/opus-qemu',variant);
  for(const file of ['stdout.log','stderr.log'])if(fs.existsSync(path.join(build,file)))save(label+'.'+file+'.gz',zlib.gzipSync(fs.readFileSync(path.join(build,file))));
  const report=JSON.parse(fs.readFileSync(path.join(build,'report.json')));
  if(failure){assert.notEqual(r.status,0);assert.match(r.stderr,/QEMU 20:/);assert.equal(report.passed,false);return null;}
  assert.equal(r.status,0,r.stderr);assert.equal(report.passed,true);save(label+'.json',report);
  for(const fixture of report.fixtures) {
   const data=fs.readFileSync(path.join(build,fixture.name+'.input.opuspkt'));
   assert.equal(hash(data),fixture.packet_sha256);
   const name=fixture.name+'.opuspkt.gz',previous=inventory.find(item=>item.name===name);
   if(previous)assert.equal(hash(zlib.gunzipSync(fs.readFileSync(path.join(out,name)))),fixture.packet_sha256);
   else save(name,zlib.gzipSync(data));
  }
  if(options.includes('--trace-pvq')) {
   const trace=fs.readFileSync(path.join(build,'trace.log'));assert.equal(hash(trace),report.instruction_trace.sha256);
   const parsed=summarize(trace.toString(),{allowEmpty:report.instruction_trace.silk_only});save(label+'.trace.log.gz',zlib.gzipSync(trace));save(label+'.trace-summary.json',parsed);
   assert.deepEqual(parsed.totals,report.instruction_trace.totals);
  }
  return report;
 }
 for(const [label,variant] of Object.entries(variants))results.correctness[label]=attempt(label+'-extended',variant,['--extended']);
 for(const fixture of ['mono-12','mono-24','stereo-64','stereo-128','stereo-192','stereo-320-20ms','stereo-510']) {
  const pair={};for(const [label,variant] of Object.entries(variants)) {
   const flags=['--fixture',fixture,'--no-self-tests','--trace-pvq'];if(/320|510/.test(fixture))flags.push('--extended');
   pair[label]=attempt(label+'-'+fixture,variant,flags);
  }
  results.profiles[fixture]={accepted:pair.accepted.instruction_trace.totals.pvq};
 }
 const replay=attempt('accepted-replay-stereo-192',variants.accepted,['--fixture','stereo-192','--no-self-tests','--trace-pvq']);
 assert.deepEqual(replay.instruction_trace.totals.pvq,results.profiles['stereo-192'].accepted);results.deterministic_replay=true;
 attempt('negative-canary',variants.accepted,['--fixture','stereo-192','--fault-guard'],true);results.negative_guard=true;
 save('summary.json',results);save('inventory.json',inventory);console.log(JSON.stringify({passed:true,out,profiles:results.profiles},null,2));return results;
}
module.exports={run};if(require.main===module)run();

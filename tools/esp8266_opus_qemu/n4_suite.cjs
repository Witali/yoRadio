// Offline A/B evidence for the independent N4 ASM lookup experiment.
const fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process'),{root,hash}=require('../esp8266_opus_asm/export.cjs');
const {summarize}=require('./trace.cjs');
const variants={accepted:'esp8266-opus-ebands-final-candidate-v2',n4:'esp8266-opus-pvq-n4-prefix-candidate-v1'};
function run(args=process.argv.slice(2)){
 assert.ok(!args.length||(args.length===2&&args[0]==='--output'));
 const out=path.resolve(args[1]||path.join(root,'.build/opus-qemu-n4-suite'));
 const relative=path.relative(root,out);assert.ok(relative&&!relative.startsWith('..')&&!path.isAbsolute(relative));
 assert.ok(!fs.existsSync(out),'Evidence directory already exists');fs.mkdirSync(out,{recursive:true});
 const inventory=[],result={scope:'QEMU LX106 correctness/instructions only; no ESP8266 timing or board access',correctness:{},profiles:{},deterministic_replay:false};
 function save(name,data){if(typeof data!=='string'&&!Buffer.isBuffer(data))data=JSON.stringify(data,null,2)+'\n';if(typeof data==='string')data=Buffer.from(data);fs.writeFileSync(path.join(out,name),data);inventory.push({name,bytes:data.length,sha256:hash(data)});}
 function attempt(label,kind,options){
  console.log(label);const variant=variants[kind];
  const r=spawnSync(process.execPath,[path.join(__dirname,'run.cjs'),'--variant',variant,...options],{encoding:'utf8',maxBuffer:4*1024*1024,timeout:60000});
  save(label+'.runner.log',(r.stdout||'')+(r.stderr||''));if(r.error)throw r.error;
  const build=path.join(root,'.build/opus-qemu',variant);
  for(const n of ['stdout.log','stderr.log'])if(fs.existsSync(path.join(build,n)))save(label+'.'+n+'.gz',zlib.gzipSync(fs.readFileSync(path.join(build,n))));
  assert.equal(r.status,0,r.stderr);const report=JSON.parse(fs.readFileSync(path.join(build,'report.json')));assert.equal(report.passed,true);save(label+'.json',report);
  if(options.includes('--trace-pvq')){
   const trace=fs.readFileSync(path.join(build,'trace.log'));assert.equal(hash(trace),report.instruction_trace.sha256);
   const parsed=summarize(trace.toString(),{helperName:kind==='n4'?'N4':'N3',allowEmpty:report.instruction_trace.silk_only});assert.deepEqual(parsed.totals,report.instruction_trace.totals);
   save(label+'.trace.log.gz',zlib.gzipSync(trace));save(label+'.trace-summary.json',parsed);
  }
  if(kind==='accepted'&&label.endsWith('extended'))for(const f of report.fixtures){
   const data=fs.readFileSync(path.join(build,f.name+'.input.opuspkt'));assert.equal(hash(data),f.packet_sha256);save(f.name+'.opuspkt.gz',zlib.gzipSync(data));
  }
  return report;
 }
 for(const kind of Object.keys(variants))result.correctness[kind]=attempt(kind+'-extended',kind,['--extended']);
 assert.equal(result.correctness.accepted.cases.length,24);assert.deepEqual(result.correctness.accepted.cases,result.correctness.n4.cases);
 for(const fixture of ['mono-12','mono-24','stereo-64','stereo-128','stereo-192','stereo-320-20ms','stereo-510']){
  const pair={};for(const kind of Object.keys(variants)){
   const options=['--fixture',fixture,'--no-self-tests','--trace-pvq'];if(/320|510/.test(fixture))options.push('--extended');
   pair[kind]=attempt(kind+'-'+fixture,kind,options);
  }
  assert.deepEqual(pair.accepted.cases,pair.n4.cases);
  const a=pair.accepted.instruction_trace.totals.pvq,b=pair.n4.instruction_trace.totals.pvq;
  result.profiles[fixture]={accepted:a,n4:b,instruction_delta:b.instructions-a.instructions,instruction_change_percent:a.instructions?100*(b.instructions/a.instructions-1):0,load_delta:b.load_instructions-a.load_instructions};
 }
 const again=attempt('n4-replay-192','n4',['--fixture','stereo-192','--no-self-tests','--trace-pvq']);
 assert.deepEqual(again.instruction_trace.totals.pvq,result.profiles['stereo-192'].n4);result.deterministic_replay=true;
 save('summary.json',result);save('inventory.json',inventory);console.log(JSON.stringify({passed:true,out,profiles:result.profiles},null,2));return result;
}
module.exports={run};if(require.main===module)run();

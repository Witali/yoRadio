#!/usr/bin/env node
// Explicit OTA + raw codec ABBA experiment. Never retries a mutation or uses UART.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawn}=require('node:child_process');
const {hash,root}=require('./export.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function plan(cycles=5){
  assert.ok(Number.isInteger(cycles)&&cycles>=5&&cycles<=25);
  return Array.from({length:cycles},()=>['A','B','B','A']).flat();
}
function checkArtifacts(aDir,bDir,fixtures,experiment='backend'){
  const manifests=[aDir,bDir].map(dir=>{
    const m=read(path.join(dir,'manifest.json')),app=fs.readFileSync(path.join(dir,'app.bin'));
    assert.equal(hash(app),m.app_sha256.toLowerCase());assert.equal(app.length,m.bytes);
    assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);
    assert.equal(m.opus_benchmark_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(fixtures,'manifest.json'))));
    return m;
  });
  const [a,b]=manifests;assert.equal(a.opus_backend,'gcc-asm');
  assert.ok(['backend','pvq-iram'].includes(experiment));
  const allowed=['built_utc','app_sha256','bytes'];
  if(experiment==='backend'){
    assert.ok(['optimized-asm','hoisted-asm'].includes(b.opus_backend));
    assert.equal(a.opus_asm_optimization_sha256,null);assert.match(b.opus_asm_optimization_sha256,/^[0-9a-f]{64}$/i);
    allowed.push('opus_backend','opus_asm_optimization_sha256');
  }else{
    assert.equal(b.opus_backend,'gcc-asm');assert.equal(a.opus_pvq_iram,false);assert.equal(b.opus_pvq_iram,true);
    allowed.push('opus_pvq_iram');
  }
  for(const key of new Set([...Object.keys(a),...Object.keys(b)]))
    if(!allowed.includes(key))
      assert.deepEqual(a[key],b[key],'Unmatched build setting: '+key);
  return {A:a,B:b};
}
async function run({reference,candidate,fixtures,directory,base='http://192.168.100.6',cycles=5,experiment='backend',interval=1500}){
  assert.ok(Number.isInteger(interval)&&interval>=250&&interval<=60000);
  const artifacts=checkArtifacts(reference,candidate,fixtures,experiment),order=plan(cycles);
  // New directory only: never overwrite evidence or infer completion from a lock.
  fs.mkdirSync(directory,{recursive:false});
  const report={date:new Date().toISOString(),base,experiment,interval_ms:interval,artifacts,order,events:[],complete:false};
  const save=()=>fs.writeFileSync(path.join(directory,'series.json'),JSON.stringify(report,null,2)+'\n');
  save();
  function child(script,args,log){return new Promise((resolve,reject)=>{
    const out=fs.createWriteStream(path.join(directory,log));
    const p=spawn(process.execPath,[path.join(root,script),...args],{cwd:root,windowsHide:true});
    p.stdout.pipe(out,{end:false});p.stderr.pipe(out,{end:false});
    p.on('error',e=>{out.end();reject(e)});
    p.on('close',code=>out.end(()=>code===0?resolve():reject(Error(`${script} exited ${code}; inspect ${log}, do not restart an ambiguous device operation`))));
  });}
  try{
    const before=await fetch(new URL('/api/native/opus-benchmark',base),{signal:AbortSignal.timeout(8000)});
    assert.equal(before.status,200);report.before=await before.json();save();
    assert.ok([0,3,4].includes(report.before.state),'A benchmark is already active; observe that run');
    let loaded=null;
    const reports={A:[],B:[]};
    for(const [index,backend] of order.entries()){
      const label=String(index+1).padStart(2,'0')+'-'+backend;
      if(loaded!==backend){
        const file='ota-'+label+'.json',event={kind:'ota',backend,file,started:new Date().toISOString()};
        report.events.push(event);save();console.log(`STEP ${index+1}/${order.length}: OTA ${backend}`);
        await child('tools/esp8266_audio_profile/check_prefill_board.cjs',['ota','--base',base,'--firmware',path.join(backend==='A'?reference:candidate,'app.bin'),'--output',path.join(directory,file)],'ota-'+label+'.log');
        const ota=read(path.join(directory,file));assert.equal(ota.pass,true);
        assert.equal(ota.sha256,artifacts[backend].app_sha256.toLowerCase());
        event.finished=new Date().toISOString();event.sha256=hash(fs.readFileSync(path.join(directory,file)));save();
        loaded=backend;
      }
      const file='run-'+label+'.json',event={kind:'run',backend,file,started:new Date().toISOString()};
      report.events.push(event);save();console.log(`STEP ${index+1}/${order.length}: raw benchmark ${backend}`);
      await child('tools/esp8266_opus_profile/run_board.cjs',['--base',base,'--fixtures',fixtures,'--interval-ms',String(interval),'--output',path.join(directory,file)],'run-'+label+'.log');
      const data=read(path.join(directory,file));assert.equal(data.final.state,3);assert.equal(data.final.error,0);
      reports[backend].push(data);event.finished=new Date().toISOString();event.sha256=hash(fs.readFileSync(path.join(directory,file)));save();
      console.log(`DONE ${index+1}/${order.length}: CPU ${data.comparison.map(c=>c.task_budget_percent.toFixed(2)).join('/')}%`);
      await new Promise(resolve=>setTimeout(resolve,3000));
    }
    const result=compare(reports.A,reports.B);
    result.scope=result.scope.replace('Sequential A/B, not interleaved.',`Interleaved ABBA, ${cycles} cycles, no discarded attempts.`);
    result.artifacts=artifacts;result.order=order;result.experiment=experiment;result.interval_ms=interval;
    result.inputs=report.events.filter(e=>e.kind==='run').map(({backend,file,sha256})=>({backend,file,sha256}));
    fs.writeFileSync(path.join(directory,'comparison.json'),JSON.stringify(result,null,2)+'\n');
    report.complete=true;report.finished=new Date().toISOString();save();
    console.table(result.cases.map(c=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
  }catch(error){report.error=error.stack;save();throw error;}
}
module.exports={plan,checkArtifacts};
if(require.main===module){
  const args=process.argv.slice(2),value=k=>{const i=args.indexOf(k);assert.ok(i>=0,'Missing '+k);return path.resolve(args[i+1]);};
  const optional=(k,f)=>args.includes(k)?args[args.indexOf(k)+1]:f;
  run({reference:value('--reference'),candidate:value('--candidate'),fixtures:value('--fixtures'),directory:value('--directory'),experiment:optional('--experiment','backend'),interval:Number(optional('--interval-ms','1500'))}).catch(e=>{console.error(e);process.exitCode=1});
}

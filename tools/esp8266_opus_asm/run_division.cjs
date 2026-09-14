// Explicit LAN test, no UART/reset/OTA. Retry observations of the SAME run,
// never silently start another run after an uncertain POST or observation.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs');
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
function request(base,method='GET'){
 return new Promise((resolve,reject)=>{
  const req=http.request(new URL('/api/native/opus-benchmark',base),{method,agent:false,headers:{Connection:'close','Content-Length':0}},res=>{
   let text='';res.on('data',s=>{text+=s;if(text.length>16384)req.destroy(Error('response bound'));});
   res.on('error',reject);res.on('end',()=>{try{assert.ok(res.statusCode>=200&&res.statusCode<300,'HTTP '+res.statusCode);resolve(JSON.parse(text));}catch(e){reject(e);}});
  });const timer=setTimeout(()=>req.destroy(Error('observation timeout')),8000);
  req.on('close',()=>clearTimeout(timer));req.on('error',reject);req.end();
 });
}
function validate(result,census){
 assert.equal(result.division_microbenchmark,true);assert.equal(result.clock_hz,1000000);
 assert.equal(result.state,3);assert.equal(result.error,0);assert.equal(result.divisions.length,census.cases.length);
 assert.equal(result.results.length,0,'Not a raw decoder CPU measurement');
 assert.equal(result.warm,!(result.run&1));assert.equal(result.rounds,10);
 for(const [i,r]of result.divisions.entries()){
  assert.equal(r.id,i);assert.equal(r.error,0);
  assert.equal(r.calls,census.cases[i].calls*result.rounds);
  assert.equal(r.batches,Math.ceil(census.cases[i].calls/192)*result.rounds);
  assert.equal(r.reference_hash,r.candidate_hash);
  assert.ok(r.min_dram>0&&r.stack_free_lifetime>0);
  if(r.calls)assert.ok(r.reference_ticks>0&&r.candidate_ticks>0);
 }
}
async function main(){
 const base=process.argv[2]||'http://192.168.100.6',dir=path.resolve(process.argv[3]||path.join(root,'.build/opus-division-board'));
 const censusPath=path.join(root,'.build/opus-bands-division-census/census.json'),census=JSON.parse(fs.readFileSync(censusPath));
 fs.mkdirSync(dir,{recursive:true});
 const initial=await request(base);assert.equal(initial.division_microbenchmark,true);
 assert.ok(![1,2].includes(initial.state),'Existing run is still live; observe it, do not restart');
 for(let i=1;i<=20;i++){
  const file=path.join(dir,'run-'+String(i).padStart(2,'0')+'.json');assert.ok(!fs.existsSync(file),'Never overwrite an attempt');
  const record={date:new Date().toISOString(),base,census_sha256:hash(fs.readFileSync(censusPath)),scope:'Paired helper wall microseconds; not decoder CPU',observations:[],errors:[]};
  const save=()=>fs.writeFileSync(file,JSON.stringify(record,null,2)+'\n');
  record.before=await request(base);assert.ok(![1,2].includes(record.before.state));save();
  try{record.start=await request(base,'POST');save();}catch(e){record.errors.push('Uncertain POST: '+e.message);save();throw e;}
  const expected=record.before.run+1,deadline=Date.now()+120000;
  while(Date.now()<deadline){
   try{
    const s=await request(base);record.observations.push(s);save();
    assert.equal(s.run,expected,'Different run observed');
    if(s.state===3||s.state===4){record.final=s;save();break;}
   }catch(e){record.errors.push(e.message);save();}
   await delay(1000);
  }
  assert.ok(record.final,'Observation deadline; do not restart the run');
  validate(record.final,census);record.passed=true;save();
  const r=record.final.divisions[4];
  console.log(JSON.stringify({attempt:i,run:expected,warm:record.final.warm,
   ref_ticks:r.reference_ticks,new_ticks:r.candidate_ticks,reduction:100*(1-r.candidate_ticks/r.reference_ticks),
   min_dram:r.min_dram,stack:r.stack_free_lifetime,errors:record.errors}));
  await delay(2000);
 }
}
module.exports={validate,request};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});

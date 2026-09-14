const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash}=require('./export.cjs'),{validate}=require('./run_division.cjs');
const med=a=>{const s=[...a].sort((x,y)=>x-y),i=s.length>>1;return s.length%2?s[i]:(s[i-1]+s[i])/2;};
const stats=a=>({min:Math.min(...a),median:med(a),max:Math.max(...a)});
function report(){
 const dest=path.join(root,'firmware/development/esp8266-opus-division-micro-v2');
 const dir=path.join(root,'.build/opus-division-board-v2'),cd=path.join(root,'.build/opus-bands-division-census');
 const census=JSON.parse(fs.readFileSync(path.join(cd,'census.json'))),runs=[];
 const copy=(src,to)=>{fs.mkdirSync(path.dirname(to),{recursive:true});if(fs.existsSync(to))assert.equal(hash(fs.readFileSync(to)),hash(fs.readFileSync(src)),'Refuse changed archived evidence');else fs.copyFileSync(src,to);};
 for(let i=1;i<=20;i++){
  const name='run-'+String(i).padStart(2,'0')+'.json',file=path.join(dir,name),r=JSON.parse(fs.readFileSync(file));
  validate(r.final,census);assert.equal(r.passed,true);assert.equal(r.census_sha256,hash(fs.readFileSync(path.join(cd,'census.json'))));
  copy(file,path.join(dest,'runs',name));runs.push(r);
 }
 const groups=[false,true].map(warm=>{
  const selected=runs.filter(r=>r.final.warm===warm);assert.equal(selected.length,10);
  return {warm,runs:selected.length,cases:census.cases.map((f,i)=>{
   const rows=selected.map(r=>r.final.divisions[i]);
   return {name:f.name,actual_divisions_per_audio:f.calls,audio_ms:f.audio_ms,
    reference_us:stats(rows.map(r=>r.reference_ticks)),candidate_us:stats(rows.map(r=>r.candidate_ticks)),
    median_reduction_percent:f.calls?100*(1-med(rows.map(r=>r.candidate_ticks))/med(rows.map(r=>r.reference_ticks))):null,
    max_reference_batch_us:Math.max(...rows.map(r=>r.reference_max)),max_candidate_batch_us:Math.max(...rows.map(r=>r.candidate_max)),
    min_dram:Math.min(...rows.map(r=>r.min_dram)),min_stack:Math.min(...rows.map(r=>r.stack_free_lifetime))};
  })};
 });
 for(const name of ['census.json','operands.bin','opus_division_fixtures.h',...census.cases.map(f=>f.name+'.trace.txt')])copy(path.join(cd,name),path.join(dest,'census',name));
 for(const [from,to]of [['build-v2.log','build.log'],['tests.log','tests.log']])copy(path.join(cd,from),path.join(dest,to));
 const failed=JSON.parse(fs.readFileSync(path.join(root,'.build/opus-division-board/run-01.json')));
 assert.equal(failed.final.error,-9104);
 const v1=path.join(root,'firmware/development/esp8266-opus-division-micro-v1');
 copy(path.join(root,'.build/opus-division-board/run-01.json'),path.join(v1,'failed-run.json'));
 copy(path.join(cd,'build.log'),path.join(v1,'build.log'));
 const result={scope:'20 paired same-image helper microbenchmarks; complete operands from RAM; NOT raw decoder CPU or cache-miss counters',
  units:'microseconds, SDK wall timer; includes timer/loop/hash/interrupts/preemption, no subtraction',
  groups,observations_with_errors:runs.filter(r=>r.errors.length).length,
  failed_v1:'../esp8266-opus-division-micro-v1/failed-run.json (CCOUNT reset, invalid timing, retained)',
  min_dram:Math.min(...runs.flatMap(r=>r.final.divisions.map(d=>d.min_dram))),
  min_stack:Math.min(...runs.flatMap(r=>r.final.divisions.map(d=>d.stack_free_lifetime))),
  heap_after:stats(runs.map(r=>r.final.dram_after)),goal_decoder_cpu_improved:false};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result,null,2));
}
if(require.main===module)report();

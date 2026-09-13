const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {phaseBuild}=require('./run_phase_regressions.cjs');
const {prepareReference}=require('./prepare_generic32_reference.cjs');
const {execute,hostPath,root,component}=require('./build_host.cjs');
const {fixtureDirectory,sha256}=require('./fixtures.cjs');
const {comparePcm}=require('./run_regressions.cjs');
async function run({output}={}) {
  prepareReference();
  const reference=await phaseBuild(false),candidate=await phaseBuild(true,
    {silkScratch:true,autocorrCompact:true,silkPlcIram:true,sanitize:true});
  const directory=fs.mkdtempSync(path.join(root,'.build/plc-iram-fallback-'));
  const input=path.join(fixtureDirectory,'mono-12.opuspkt');
  const cases=[];
  for(const rate of [48000,24000])for(const burst of [1,6])for(const capacity of [16384,11232]) {
    const name=`rate${rate}-burst${burst}-words${capacity}`;
    function probe(build,tag) {
      const file=path.join(directory,name+'-'+tag+'.pcm');
      const meta=JSON.parse(execute('env',[`OPUS_PHASE_RATE=${rate}`,`OPUS_PHASE_PLC_BURST=${burst}`,
        'OPUS_PHASE_CAPACITY=6144',`OPUS_PHASE_WORD_CAPACITY=${capacity}`,
        hostPath(build.binary),hostPath(file),'--plc',hostPath(input)]));
      return {meta,pcm:fs.readFileSync(file)};
    }
    const before=probe(reference,'reference'),after=probe(candidate,'bounded');
    const pcm=comparePcm(before.pcm,after.pcm);assert.equal(pcm.exact,true,name);
    assert.ok(after.meta.pcm_guards_ok&&after.meta.reset_exact&&after.meta.plc_frames>0);
    assert.ok(after.meta.scratch_word_peak_bytes<=capacity);
    if(capacity===11232)assert.ok(after.meta.word_dram_fallbacks>0&&after.meta.word_arena_allocations===0);
    else assert.ok(after.meta.word_arena_allocations>0&&after.meta.word_dram_fallbacks===0);
    cases.push({name,bounded:after.meta,pcm});
    console.log(name+': exact; DRAM '+after.meta.scratch_byte_peak_bytes+', word fallback '+after.meta.word_dram_fallbacks);
  }
  const report={passed:true,scope:'Host generic32 mono SILK with PLC. Restrict IRAM to11232 persistent bytes to force DRAM fallback. No physical width/speed proof.',
    sanitizers:['address','undefined'],input_sha256:sha256(fs.readFileSync(input)),
    source_sha256_lf:Object.fromEntries(['upstream/silk/PLC.c','opus_memory.c','opus_memory.h'].map(name=>
      [name,sha256(Buffer.from(fs.readFileSync(path.join(component,name),'utf8').replace(/\r\n/g,'\n')))])),cases};
  if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={run};
if(require.main===module){const i=process.argv.indexOf('--output');run({output:i<0?undefined:process.argv[i+1]})
  .then(r=>console.log('PASS '+r.cases.length+' fallback cases')).catch(e=>{console.error(e.stack);process.exitCode=1;});}

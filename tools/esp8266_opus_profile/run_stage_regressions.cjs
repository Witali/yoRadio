// Recompile every instrumented TU + probe for each selection, reuse unchanged
// bounded objects. Host clocks test instrumentation correctness, NOT speed.
const fs=require('node:fs'), path=require('node:path'), assert=require('node:assert/strict');
const {buildHost,runProbe,execute,hostPath,root,component}=require('./build_host.cjs');
const {fixtureDirectory}=require('./fixtures.cjs');
const {comparePcm}=require('./run_regressions.cjs');
const changed=['silk/decode_frame.c','silk/dec_API.c','celt/celt_decoder.c'];
async function run(output=path.join(root,'.build/opus-stage-regressions/results.json')) {
  const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true});
  const source=JSON.parse(fs.readFileSync(path.join(base.out,'build.json'))).sources;
  const dir=path.dirname(output); fs.mkdirSync(dir,{recursive:true});
  const fixtures=JSON.parse(fs.readFileSync(path.join(fixtureDirectory,'manifest.json'))).fixtures;
  const report={timing:'No host speed claims; all stage selections compared with macro-off PCM',cases:[]};
  for(const f of fixtures)runProbe({bounded:true,fastInt64:0,firFlashWord:true,fixture:path.join(fixtureDirectory,f.name+'.opuspkt'),output:path.join(dir,f.name+'.off.pcm')});
  const route=['mono-12','mono-24','stereo-64','stereo-128','mono-12'].map(n=>path.join(fixtureDirectory,n+'.opuspkt'));
  const sequencePcm=path.join(dir,'sequence.off.pcm');
  execute(hostPath(base.binary),['--sequence',hostPath(sequencePcm),...route.map(hostPath)]);
  for(let stage=1;stage<=11;stage++) {
    const out=path.join(dir,'stage-'+stage);fs.mkdirSync(out,{recursive:true});
    const flags=[...base.flags,'-DYORADIO_OPUS_PROFILE_STAGE='+stage];
    const objects=base.objects.map((object,i)=>{
      if(!changed.some(file=>source[i]===path.join(component,'upstream',file)) && source[i]!==path.join(__dirname,'probe.c'))return object;
      const candidate=path.join(out,path.basename(source[i])+'.o');
      execute('gcc',[...flags,'-c',hostPath(source[i]),'-o',hostPath(candidate)]);return candidate;
    });
    const counter=path.join(out,'counter.o');
    execute('gcc',[...flags,'-c',hostPath(path.join(component,'opus_stage_profile.c')),'-o',hostPath(counter)]);
    const binary=path.join(out,'probe');
    execute('gcc',[...objects.map(hostPath),hostPath(counter),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
    let totalCalls=0;
    for(const f of fixtures) {
      const pcm=path.join(out,f.name+'.pcm');
      const result=JSON.parse(execute(hostPath(binary),[hostPath(path.join(fixtureDirectory,f.name+'.opuspkt')),hostPath(pcm),'--self-test']));
      const comparison=comparePcm(fs.readFileSync(path.join(dir,f.name+'.off.pcm')),fs.readFileSync(pcm));
      assert.equal(comparison.exact,true);assert.equal(result.profile_stage,stage);
      assert.ok(result.scratch_byte_peak_bytes<=6144 && result.scratch_word_peak_bytes<=16384);
      if(stage<=5 && f.name.startsWith('stereo')) assert.equal(result.stage_calls,0);
      if(stage>=6 && f.name==='mono-12') assert.equal(result.stage_calls,0);
      totalCalls+=result.stage_calls;
      report.cases.push({stage,fixture:f.name,calls:result.stage_calls,pcm:comparison});
    }
    assert.ok(totalCalls>0,'selected stage must actually execute');
    const sequenceOut=path.join(out,'sequence.pcm');
    const sequence=JSON.parse(execute(hostPath(binary),['--sequence',hostPath(sequenceOut),...route.map(hostPath)]));
    const pcm=comparePcm(fs.readFileSync(sequencePcm),fs.readFileSync(sequenceOut));
    assert.equal(pcm.exact,true);assert.equal(sequence.reset_exact,true);assert.ok(sequence.plc_frames>0);
    assert.ok(sequence.scratch_byte_peak_bytes<=6144 && sequence.scratch_word_peak_bytes<=16384);
    report.cases.push({stage,fixture:'mixed-modes-plc-reset',calls:sequence.stage_calls,pcm});
    console.log('Stage',stage,'exact PCM, calls',totalCalls);
  }
  report.passed=true; fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');return report;
}
if(require.main===module) run(process.argv.includes('--output')?path.resolve(process.argv[process.argv.indexOf('--output')+1]):undefined)
  .catch(error=>{console.error(error);process.exitCode=1;});
module.exports={run};

const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {buildHost,runProbe,execute,hostPath,root,component}=require('./build_host.cjs');
const {runRegressions,comparePcm}=require('./run_regressions.cjs');
const {fixtureDirectory,sha256}=require('./fixtures.cjs');
const {run:runBlocks}=require('./run_block_regressions.cjs');

async function run(output=path.join(__dirname,'celt-decode-results.json')) {
  const dir=path.join(root,'.build/opus-celt-decode-regression');fs.mkdirSync(dir,{recursive:true});
  const options={bounded:true,fastInt64:0,firFlashWord:true};
  const off=await buildHost(options),on=await buildHost({...options,celtDecodeOnly:true});
  const full=await runRegressions({fastInt64:0,firFlashWord:true,celtDecodeOnly:true,output:path.join(dir,'full.json')});
  const phase=[];
  for(const file of fs.readdirSync(path.join(fixtureDirectory,'phase')).filter(f=>f.endsWith('.opuspkt')).sort()) {
    const fixture=path.join(fixtureDirectory,'phase',file),a=path.join(dir,file+'.off.pcm'),b=path.join(dir,file+'.on.pcm');
    const before=runProbe({...options,fixture,output:a});
    const after=runProbe({...options,celtDecodeOnly:true,fixture,output:b});
    const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true,file);
    for(const field of ['persistent_bytes','scratch_byte_peak_bytes','scratch_word_peak_bytes']) assert.equal(after[field],before[field],field);
    phase.push({file,input_sha256:sha256(fs.readFileSync(fixture)),before,after,pcm});
    console.log('Exact phase',file);
  }
  const blocks=await runBlocks({celtDecodeOnly:true,output:path.join(dir,'blocks.json')});
  // Instrument the changed TU and the guard; other codec objects are NOT
  // sanitized. Exercise the early rejection even with invalid scratch inputs.
  const flags=[...on.flags,'-fsanitize=address,undefined','-fno-sanitize-recover=all'];
  const bandObject=path.join(dir,'bands.sanitized.o'),guardObject=path.join(dir,'guard.o'),guard=path.join(dir,'guard');
  execute('gcc',[...flags,'-c',hostPath(path.join(component,'upstream/celt/bands.c')),'-o',hostPath(bandObject)]);
  execute('gcc',[...flags,'-Wall','-Wextra','-Werror','-c',hostPath(path.join(__dirname,'celt_decode_guard.c')),'-o',hostPath(guardObject)]);
  const objects=on.objects.filter(o=>!o.endsWith('probe.c.o')&&!o.endsWith(path.join('celt','bands.c.o')));
  execute('gcc',[...flags,...objects.map(hostPath),hostPath(bandObject),hostPath(guardObject),'-Wl,--gc-sections','-lm','-o',hostPath(guard)]);
  execute(hostPath(guard),[]);
  const sanitized=path.join(dir,'probe-sanitized-bands'),sanitizedPcm=[];
  execute('gcc',[...flags,...objects.map(hostPath),hostPath(bandObject),hostPath(on.objects.find(o=>o.endsWith('probe.c.o'))),'-Wl,--gc-sections','-lm','-o',hostPath(sanitized)]);
  for(const f of full.fixtures) {
    const input=path.join(fixtureDirectory,f.name+'.opuspkt'),reference=path.join(dir,f.name+'.san-reference.pcm'),actual=path.join(dir,f.name+'.sanitized.pcm');
    runProbe({...options,fixture:input,output:reference});
    const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(sanitized),hostPath(input),hostPath(actual),'--self-test']));
    const pcm=comparePcm(fs.readFileSync(reference),fs.readFileSync(actual));assert.equal(pcm.exact,true);
    assert.equal(result.arena_guards_ok,true);assert.equal(result.oom_reinitialized_exact,true);
    sanitizedPcm.push({name:f.name,pcm});
  }
  const report={passed:true,scope:'Exact generic32 PCM, bounded scratch, cancellation/reset/OOM. No host timing claim. ASan/UBSan instruments bands.c for encoder rejection and five full PCM fixtures, not the entire decoder.',
    source_sha256_lf:sha256(Buffer.from(fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8').replace(/\r\n/g,'\n'))),
    full,phase,blocks,encoder_guard_asan_ubsan:true,sanitized_pcm:sanitizedPcm};
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={run};
if(require.main===module)run(process.argv.includes('--output')?path.resolve(process.argv[process.argv.indexOf('--output')+1]):undefined)
  .then(r=>console.log('PASS CELT decoder-only:',r.full.fixtures.length+1+r.phase.length+r.blocks.cases.length,'PCM scenarios'))
  .catch(e=>{console.error(e.stack);process.exitCode=1;});

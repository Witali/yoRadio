const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {buildHost,runProbe,execute,hostPath,root,component}=require('./build_host.cjs');
const {runRegressions,comparePcm}=require('./run_regressions.cjs');
const {fixtureDirectory,sha256}=require('./fixtures.cjs');
const {run:runBlocks}=require('./run_block_regressions.cjs');
async function run(output=path.join(__dirname,'div-once-results.json')) {
  const dir=path.join(root,'.build/opus-div-once-regression');fs.mkdirSync(dir,{recursive:true});
  const options={bounded:true,fastInt64:0,firFlashWord:true};
  const off=await buildHost(options),on=await buildHost({...options,divOnce:true});
  const full=await runRegressions({fastInt64:0,firFlashWord:true,divOnce:true,output:path.join(dir,'full.json')});
  const files=fs.readdirSync(path.join(fixtureDirectory,'phase')).filter(f=>f.endsWith('.opuspkt')).sort().map(f=>'phase/'+f);
  files.push('through192/stereo-192.opuspkt');
  const extra=[];
  for(const file of files){
    const fixture=path.join(fixtureDirectory,file),name=file.replaceAll('/','-');
    const a=path.join(dir,name+'.off.pcm'),b=path.join(dir,name+'.on.pcm');
    const before=runProbe({...options,fixture,output:a}),after=runProbe({...options,divOnce:true,fixture,output:b});
    const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true,file);
    for(const key of ['persistent_bytes','scratch_byte_peak_bytes','scratch_word_peak_bytes'])assert.equal(after[key],before[key],key);
    assert.equal(after.reset_exact,true);assert.equal(after.oom_reinitialized_exact,true);assert.equal(after.arena_guards_ok,true);
    extra.push({file,input_sha256:sha256(fs.readFileSync(fixture)),before,after,pcm});
    console.log('Exact',file);
  }
  const blocks=await runBlocks({divOnce:true,output:path.join(dir,'blocks.json')});
  // Sanitize vq.c (the real hot division caller), not claim whole-codec coverage.
  const flags=[...on.flags,'-fsanitize=address,undefined','-fno-sanitize-recover=all'];
  const object=path.join(dir,'vq.sanitized.o'),binary=path.join(dir,'probe-sanitized-vq');
  execute('gcc',[...flags,'-c',hostPath(path.join(component,'upstream/celt/vq.c')),'-o',hostPath(object)]);
  execute('gcc',[...flags,...on.objects.filter(o=>!o.endsWith(path.join('celt','vq.c.o'))).map(hostPath),hostPath(object),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
  const sanitized=[];
  for(const name of ['mono-12','mono-24','stereo-64','stereo-128','through192/stereo-192']) {
    const input=path.join(fixtureDirectory,name+'.opuspkt'),stem=name.replaceAll('/','-');
    const before=path.join(dir,stem+'.san-before.pcm'),after=path.join(dir,stem+'.san-after.pcm');
    runProbe({...options,fixture:input,output:before});
    const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(binary),hostPath(input),hostPath(after),'--self-test']));
    const pcm=comparePcm(fs.readFileSync(before),fs.readFileSync(after));assert.equal(pcm.exact,true,name);
    assert.equal(result.arena_guards_ok,true);assert.equal(result.oom_reinitialized_exact,true);
    sanitized.push({name,pcm});
  }
  const sources=['upstream/celt/mathops.h','upstream/celt/fixed_generic.h','upstream/celt/vq.c','CMakeLists.txt'];
  const report={passed:true,scope:'Full mono48k PCM/reset/PLC/OOM/block callback regressions. vq.c caller sanitized; not entire codec. No board timing claim.',
    source_sha256_lf:Object.fromEntries(sources.map(file=>[file,sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n')))])),
    full,extra,blocks,sanitized};
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={run};if(require.main===module)run().then(r=>console.log('PASS',r.full.fixtures.length+1+r.extra.length+r.blocks.cases.length,'PCM scenarios')).catch(e=>{console.error(e.stack);process.exitCode=1;});

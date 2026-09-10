const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'), path=require('node:path'), {spawnSync}=require('node:child_process');
const {execute,hostPath,root,component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {defaultCompiler}=require('../tools/esp8266_opus_profile/check_xtensa_word_access.cjs');
const {defaultObjdump}=require('../tools/esp8266_opus_profile/check_xtensa_iram.cjs');
const header=path.join(component,'opus_fir_word.h');
const {sha256}=require('../tools/esp8266_opus_profile/fixtures.cjs');

test('saved full FIR decoder regression matches current sources and exact PCM',()=>{
  const report=JSON.parse(fs.readFileSync(path.join(root,'tools/esp8266_opus_profile/fir-word-results.json'),'utf8'));
  assert.equal(report.passed,true);assert.equal(report.fir_flash_word,true);
  for(const [file,hash] of Object.entries(report.fir_source_sha256_lf))
    assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  assert.equal(report.fixtures.length,5);
  for(const item of [...report.fixtures,report.mixed_sequence]) {
    assert.equal(item.pcm.exact,true);assert.equal(item.pcm.max_absolute_error,0);
    assert.ok(item.bounded.scratch_byte_peak_bytes<=6144);
    assert.ok(item.bounded.scratch_word_peak_bytes<=16384);
  }
});
test('FIR flash pairs default off; invalid macro values rejected',()=>{
  const args=['-E','-dM','-x','c','-include',hostPath(header),'/dev/null'];
  assert.match(execute('gcc',args),/^#define YORADIO_OPUS_FIR_FLASH_WORD 0$/m);
  assert.throws(()=>execute('gcc',['-DYORADIO_OPUS_FIR_FLASH_WORD=2',...args]),/must be 0 or 1/);
});
test('actual FIR pair path is bit exact over all fractional phases, clipping and guard cases',()=>{
  const out=path.join(root,'.build/opus-fir-unit'); fs.mkdirSync(out,{recursive:true});
  const include=['', 'upstream/include','upstream/celt','upstream/silk'].map(n=>'-I'+hostPath(path.join(component,n)));
  const flags=['-O3','-g','-std=c99','-fwrapv','-ffunction-sections','-fdata-sections',
    '-fno-pie','-fsanitize=address,undefined','-DOPUS_FAST_INT64=0',...include];
  const probe=hostPath(path.join(root,'tools/esp8266_opus_profile/fir_pair_probe.c'));
  const objects=[];
  for(const on of [0,1]) {
    const name=on?'candidate':'reference', obj=hostPath(path.join(out,name+'.o')); objects.push(obj);
    execute('gcc',[...flags,'-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_FIR_FLASH_WORD='+on,
      '-DYORADIO_OPUS_FIR_TEST_HOOKS=1','-DFIR_PROBE_ENTRY=fir_'+name,
      '-Dsilk_resampler_private_IIR_FIR=unused_'+name,'-c',probe,'-o',obj]);
  }
  const binary=hostPath(path.join(out,'fir-probe'));
  execute('gcc',[...flags,'-no-pie','-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_FIR_FLASH_WORD=1',
    probe,hostPath(path.join(component,'upstream/silk/resampler_rom.c')),...objects,'-Wl,--gc-sections','-o',binary]);
  const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',binary]));
  assert.equal(result.passed,true);assert.equal(result.cases,35);assert.equal(result.samples,357590);
  assert.equal(result.rows,4095);assert.equal(result.pair_reads,4*result.samples);
});
test('Xtensa actual FIR uses four word table reads and no added persistent RAM or stack',{
  skip:!fs.existsSync(defaultCompiler)&&'Pinned Xtensa compiler unavailable',
},()=>{
  const out=path.join(root,'.build/opus-fir-xtensa');fs.mkdirSync(out,{recursive:true});
  const cmd=(p,a)=>{const r=spawnSync(p,a,{encoding:'utf8',maxBuffer:4e6});assert.equal(r.status,0,r.stdout+r.stderr);return r.stdout;};
  const result=[];
  const romObject=path.join(out,'fir-rom.o');
  cmd(defaultCompiler,['-O3','-ffunction-sections','-fdata-sections',
    '-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_FIR_FLASH_WORD=1',
    ...['','upstream/include','upstream/celt','upstream/silk'].map(n=>'-I'+path.join(component,n)),
    '-c',path.join(component,'upstream/silk/resampler_rom.c'),'-o',romObject]);
  const romSections=cmd(defaultObjdump,['-h',romObject]);
  const table=romSections.match(/\.rodata\.silk_resampler_frac_FIR_12\s+([\da-f]+)\s+[\da-f]+\s+[\da-f]+\s+[\da-f]+\s+2\*\*(\d+)/);
  assert.ok(table,romSections);assert.equal(parseInt(table[1],16),96);
  assert.ok(Number(table[2])>=2,'FIR table must be word aligned in target object');
  for(const on of [0,1]) {
    const object=path.join(out,'fir-'+on+'.o');
    cmd(defaultCompiler,['-O3','-g','-std=c99','-fwrapv','-fstack-usage','-ffunction-sections','-fdata-sections',
      '-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_WORD_ASM=1','-DYORADIO_OPUS_FIR_FLASH_WORD='+on,
      ...['','upstream/include','upstream/celt','upstream/silk'].map(n=>'-I'+path.join(component,n)),
      '-c',path.join(component,'upstream/silk/resampler_private_IIR_FIR.c'),'-o',object]);
    const asm=cmd(defaultObjdump,['-dlr','-j','.text.silk_resampler_private_IIR_FIR',object]);
    let file='';const word=[];
    for(const line of asm.split(/\r?\n/)){
      const loc=line.match(/[\\/]([^\\/:]+\.[ch]):\d+/);if(loc)file=loc[1];
      if(file==='opus_memory.h'&&/^\s*[\da-f]+:\s+[\da-f]+\s/.test(line))word.push(line);
    }
    const wordLoads=word.filter(l=>/\sl32i(?:\.n)?\s/.test(l));
    assert.equal(wordLoads.length,on?4:0);
    assert.deepEqual(word.filter(l=>/\s(?:l16ui|l16si|l8ui|s16i|s8i|memw)\s/.test(l)),[]);
    const sections=cmd(defaultObjdump,['-h',object]);
    const mutable=[...sections.matchAll(/^\s*\d+\s+\.(?:bss|data)(?:\.\S+)?\s+([\da-f]+)/gm)]
      .reduce((n,m)=>n+parseInt(m[1],16),0);assert.equal(mutable,0);
    const stack=Number(fs.readFileSync(object.replace(/\.o$/,'.su'),'utf8').match(/:silk_resampler_private_IIR_FIR\t(\d+)/)[1]);
    result.push({on,stack,mutable,word_loads:wordLoads});
  }
  assert.ok(result[1].stack<=result[0].stack,JSON.stringify(result));
  fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2)+'\n');
});

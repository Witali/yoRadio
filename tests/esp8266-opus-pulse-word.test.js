const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),{spawnSync}=require('node:child_process');
const {execute,hostPath,root,component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {defaultCompiler}=require('../tools/esp8266_opus_profile/check_xtensa_word_access.cjs');
const {defaultObjdump}=require('../tools/esp8266_opus_profile/check_xtensa_iram.cjs');
const header=path.join(component,'opus_pulse_word.h');
const {sha256}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const include=['','upstream/include','upstream/celt','upstream/silk','upstream/silk/fixed','upstream/src'];

test('saved full pulse PCM evidence matches current sources and pristine phase corpus',()=>{
  const report=JSON.parse(fs.readFileSync(path.join(root,'tools/esp8266_opus_profile/pulse-word-results.json'),'utf8'));
  assert.equal(report.passed,true);assert.equal(report.pulse_flash_word,true);assert.equal(report.fir_flash_word,true);
  for(const [file,hash] of Object.entries(report.pulse_source_sha256_lf))
    assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  for(const item of [...report.fixtures,report.mixed_sequence]) {
    assert.equal(item.pcm.exact,true);assert.equal(item.pcm.max_absolute_error,0);
    assert.ok(item.bounded.scratch_byte_peak_bytes<=6144);assert.ok(item.bounded.scratch_word_peak_bytes<=16384);
  }
  const phase=JSON.parse(fs.readFileSync(path.join(root,'tools/esp8266_opus_profile/pulse-phase-results.json'),'utf8'));
  assert.equal(phase.passed,true);assert.equal(phase.pulse_flash_word,true);assert.equal(phase.fir_flash_word,true);
  assert.equal(phase.cases.length,22);
  for(const item of phase.cases) {
    assert.equal(item.pcm.exact,true);assert.equal(item.pcm.max_absolute_error,0);
    assert.equal(item.bounded.pcm_guards_ok,true);assert.equal(item.bounded.reset_exact,true);
  }
});

test('pulse word access is default-off and disabled for custom modes or non-fixed arithmetic',()=>{
  const flags=['-E','-dM','-x','c','-include',hostPath(header),'/dev/null'];
  assert.match(execute('gcc',flags),/^#define YORADIO_OPUS_PULSE_WORD_ENABLED 0$/m);
  assert.throws(()=>execute('gcc',['-DYORADIO_OPUS_PULSE_FLASH_WORD=2',...flags]),/must be 0 or 1/);
  const on=['-DYORADIO_OPUS_PULSE_FLASH_WORD=1','-DYORADIO_OPUS_BOUNDED=1'];
  assert.match(execute('gcc',[...on,...flags]),/^#define YORADIO_OPUS_PULSE_WORD_ENABLED 0$/m);
  assert.match(execute('gcc',[...on,'-DFIXED_POINT=1','-DCUSTOM_MODES=1',...flags]),/^#define YORADIO_OPUS_PULSE_WORD_ENABLED 0$/m);
  assert.match(execute('gcc',[...on,'-DFIXED_POINT=1',...flags]),/^#define YORADIO_OPUS_PULSE_WORD_ENABLED 1$/m);
});

test('actual pulse search and all static table entries remain exact under ASan/UBSan',()=>{
  const out=path.join(root,'.build/opus-pulse-unit');fs.mkdirSync(out,{recursive:true});
  const flags=['-O3','-g','-std=c99','-fwrapv','-ffunction-sections','-fdata-sections',
    '-fno-pie','-fsanitize=address,undefined','-DOPUS_FAST_INT64=0',
    ...include.map(n=>'-I'+hostPath(path.join(component,n)))];
  const probe=hostPath(path.join(root,'tools/esp8266_opus_profile/pulse_probe.c')),objects=[];
  for(const on of [0,1]) {
    const name=on?'candidate':'reference',object=hostPath(path.join(out,name+'.o'));objects.push(object);
    execute('gcc',[...flags,'-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_PULSE_FLASH_WORD='+on,
      '-DYORADIO_OPUS_PULSE_TEST_HOOKS=1','-DPULSE_PROBE_ENTRY=pulse_'+name,
      '-Dopus_custom_mode_create=unused_create_'+name,'-Dopus_custom_mode_destroy=unused_destroy_'+name,
      '-c',probe,'-o',object]);
  }
  const binary=hostPath(path.join(out,'probe'));
  execute('gcc',[...flags,'-no-pie',probe,...objects,'-Wl,--gc-sections','-lm','-o',binary]);
  const result=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',binary]));
  assert.equal(result.passed,true);assert.equal(result.rows,97);assert.equal(result.tables,7);
  assert.ok(result.cases>190000 && result.word_reads>1000000);
  fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(result,null,2)+'\n');
});

test('Xtensa pulse tables have complete aligned words and real consumers add no static RAM',{
  skip:!fs.existsSync(defaultCompiler)&&'Pinned target compiler unavailable',
},()=>{
  const out=path.join(root,'.build/opus-pulse-xtensa');fs.mkdirSync(out,{recursive:true});
  const cmd=(program,args)=>{const r=spawnSync(program,args,{encoding:'utf8',maxBuffer:8e6});assert.equal(r.status,0,r.stdout+r.stderr);return r.stdout;};
  const results=[];
  for(const on of [0,1]) for(const file of ['modes','bands','celt']) {
    const object=path.join(out,file+'-'+on+'.o');
    cmd(defaultCompiler,['-O3','-g','-std=c99','-fwrapv','-fstack-usage','-ffunction-sections','-fdata-sections',
      '-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_WORD_ASM=1','-DYORADIO_OPUS_PULSE_FLASH_WORD='+on,
      ...include.map(n=>'-I'+path.join(component,n)),'-c',path.join(component,'upstream/celt',file+'.c'),'-o',object]);
    const sections=cmd(defaultObjdump,['-h',object]);
    const mutable=[...sections.matchAll(/^\s*\d+\s+\.(?:data|bss)(?:\.\S+)?\s+([\da-f]+)/gm)]
      .reduce((n,m)=>n+parseInt(m[1],16),0);assert.equal(mutable,0);
    const stack=fs.readFileSync(object.replace(/\.o$/,'.su'),'utf8').trim().split(/\r?\n/)
      .map(l=>l.split('\t')).map(a=>({name:a[0].split(':').at(-1),bytes:Number(a[1])}));
    if(on&&file==='modes') for(const [name,size] of [['cache_index50',212],['cache_bits50',392],['cache_caps50',168]]) {
      const row=sections.split(/\r?\n/).find(l=>l.includes('.rodata.'+name+' '));assert.ok(row,name);
      const fields=row.trim().split(/\s+/);assert.equal(parseInt(fields[2],16),size);
      assert.ok(Number(fields.at(-1).split('**')[1])>=2,row);
    }
    const asm=cmd(defaultObjdump,['-dlr',object]);let source='';const loads=[];
    for(const line of asm.split(/\r?\n/)) {
      const loc=line.match(/[\\/]([^\\/:]+\.[ch]):\d+/);if(loc)source=loc[1];
      if(source==='opus_pulse_word.h'||source==='opus_memory.h') {
        if(/^\s*[\da-f]+:\s+[\da-f]+\s+(?:l32i(?:\.n)?|l8ui|l16ui|l16si|memw)\s/.test(line))loads.push(line);
      }
    }
    // Existing word helpers legitimately occur elsewhere in bands.c too.
    if(on&&file==='celt') {
      assert.ok(loads.some(l=>/\sl32i(?:\.n)?\s/.test(l)));
      assert.deepEqual(loads.filter(l=>/\s(?:l8ui|l16ui|l16si|memw)\s/.test(l)),[]);
    }
    results.push({on,file,mutable,stack});
  }
  for(const candidate of results.filter(r=>r.on)) {
    const reference=results.find(r=>!r.on&&r.file===candidate.file);
    assert.deepEqual(candidate.stack,reference.stack,'Target stack changed: '+candidate.file);
  }
  fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(results,null,2)+'\n');
});

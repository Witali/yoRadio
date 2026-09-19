const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'),win=process.platform==='win32';
const host=p=>win?'/mnt/'+p[0].toLowerCase()+p.slice(2).replaceAll('\\','/'):p;
const exec=(program,args)=>spawnSync(win?'wsl.exe':program,win?['--exec',program,...args]:args,{encoding:'utf8',timeout:60000});
test('Helix timed owner cleans up OOM, cancellation and decoder errors, supports repeats',t=>{
  if(exec('g++',['--version']).status!==0)return t.skip('g++ unavailable');
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'helix-timing-'));t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const binary=path.join(dir,'test'),main=path.join(root,'esp8266/rtos-sdk-native/main');
  const args=['-std=c++17','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-pie','-no-pie','-DYORADIO_ESP8266_OPUS_BENCHMARK=1',
    ...['tests/native/helix_timing','tests/native/opus_board_benchmark','esp8266/rtos-sdk-native/main','esp8266/rtos-sdk-native/components/helix_codecs'].map(p=>'-I'+host(path.join(root,p))),
    host(path.join(main,'helix_timing_benchmark.cpp')),host(path.join(root,'tests/native/helix_timing/test.cpp')),'-o',host(binary)];
  const build=exec('g++',args);assert.equal(build.status,0,build.stdout+build.stderr);
  const run=exec(host(binary),[]);assert.equal(run.status,0,run.stdout+run.stderr);assert.match(run.stdout,/boundaries PASS/);
});
test('timing fixture parser validates complete 48k MPEG1/AAC-LC frames',()=>{
  const {frames}=require('../tools/esp8266_audio_profile/generate_helix_timing.cjs');
  const mp3=Buffer.alloc(192);mp3.set([255,251,84,0]);assert.equal(frames(mp3,'MP3')[0].samples,1152);
  assert.throws(()=>frames(mp3.subarray(0,191),'MP3'));
  const aac=Buffer.alloc(20);aac.set([255,241,76,128,2,128,0]);assert.equal(frames(aac,'AAC')[0].samples,1024);
  aac[6]=1;assert.throws(()=>frames(aac,'AAC'));
});
test('common result table uses task time rather than network/wall latency',()=>{
  const {median,table}=require('../tools/esp8266_audio_profile/summarize_codec_timing.cjs');
  assert.equal(median([4,1,3,2]),2.5);
  assert.match(table({rows:[{codec:'MP3',kbps:128,frame_audio_ms:24,mean_decode_ms:6,cpu_budget_percent:25,max_wall_ms:50}]}),/6.000 \| 25.00% \| 50.000/);
});

const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..'), dir=fs.mkdtempSync(path.join(root,'.build/small-gzip-'));
const wsl=process.platform==='win32', p=f=>wsl?'/mnt/'+f[0].toLowerCase()+f.slice(2).replace(/\\/g,'/'):f;
const bin=path.join(dir,'encoder'), options={encoding:'utf8'};
const args=['-std=c11','-O2','-Wall','-Wextra','-Werror','-fsanitize=undefined',
  '-I'+p(path.join(root,'esp8266/rtos-sdk-native/main')),p(path.join(root,'tests/native/esp8266_small_gzip_test.c')),
  p(path.join(root,'esp8266/rtos-sdk-native/main/small_gzip.c')),'-o',p(bin)];
const build=spawnSync(wsl?'wsl.exe':'cc',wsl?['--exec','gcc',...args]:args,options);
assert.equal(build.status,0,build.stdout+build.stderr);
test('bounded streaming gzip round-trips binary and playlist data with standard zlib',()=>{
  let seed=123456789;
  const random=Buffer.from(Array.from({length:70003},()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed&255;}));
  const station=Buffer.from('Радио тест\thttp://radio.example:8000/stream.mp3\t0\r\n'.repeat(1500));
  const fixtures=[Buffer.alloc(0),Buffer.from([255]),Buffer.from([0,255]),Buffer.alloc(32769,65),
    Buffer.from(Array.from({length:65537},(_,i)=>i&255)),random,station];
  for(let i=0;i<fixtures.length;i++) {
    const input=path.join(dir,'input'),output=path.join(dir,'output.gz');fs.writeFileSync(input,fixtures[i]);
    let reference;
    for(const chunk of [1,2,3,257,258,512,672,4096]) {
      const argv=[p(input),p(output),String(chunk)];
      const run=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin),...argv]:argv,options);
      assert.equal(run.status,0,run.stdout+run.stderr);
      const compressed=fs.readFileSync(output);
      assert.deepEqual(zlib.gunzipSync(compressed),fixtures[i]);
      if(reference)assert.deepEqual(compressed,reference,'Input chunk boundaries must not change output');
      reference=compressed;
    }
  }
});
test('gzip writer failure is propagated and cannot be finished as success',()=>{
  const input=path.join(dir,'failure-input'),output=path.join(dir,'failure.gz');
  fs.writeFileSync(input,Buffer.from(Array.from({length:30000},(_,i)=>(i*73+(i>>4))&255)));
  const argv=[p(input),p(output),'672','512'];
  const run=spawnSync(wsl?'wsl.exe':bin,wsl?['--exec',p(bin),...argv]:argv,options);
  assert.equal(run.status,2,run.stdout+run.stderr);
  assert.throws(()=>zlib.gunzipSync(fs.readFileSync(output)));
});

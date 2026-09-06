// Flash isolated Simple/predictive tests, then restore the EXACT saved app0.
// No application UART TX, OTA selection, NVS, bootloader or SPIFFS writes.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {execute}=require('./run_rcpdm_radio');
const root=path.resolve(__dirname,'../..');
const sha=data=>crypto.createHash('sha256').update(data).digest('hex');
function otaCrc(bytes) {
  // Matches SDK otatool.py: binascii.crc32(seq_bytes, 0xffffffff).
  let crc=0;
  for(const b of bytes) { crc^=b; for(let i=0;i<8;++i) crc=(crc>>>1)^((crc&1)?0xedb88320:0); }
  return (~crc)>>>0;
}
function inspectBackup(data) {
  assert.equal(data.length,0x400000,'Need a complete 4 MiB private backup');
  const expected=[['nvs',0x9000,0x6000],['phy_init',0xf000,0x1000],['app0',0x10000,0xf0000],
                  ['otadata',0x100000,0x2000],['app1',0x110000,0xf0000],['spiffs',0x3c0000,0x40000]];
  expected.forEach(([label,offset,size],i)=>{
    const p=0x8000+32*i; assert.equal(data.readUInt16LE(p),0x50aa);
    assert.equal(data.toString('ascii',p+12,p+28).replace(/\0.*$/s,''),label);
    assert.equal(data.readUInt32LE(p+4),offset); assert.equal(data.readUInt32LE(p+8),size);
  });
  const entries=[0x100000,0x101000].map(p=>({seq:data.readUInt32LE(p),
    valid:data.readUInt32LE(p)!==0xffffffff && data.readUInt32LE(p+28)===otaCrc(data.subarray(p,p+4))}));
  const valid=entries.filter(e=>e.valid);
  assert.ok(valid.length || entries.every(e=>e.seq===0xffffffff),'Invalid OTA metadata: inspect manually');
  const active=valid.length?(Math.max(...valid.map(e=>e.seq))-1)%2:0;
  assert.equal(active,0,'This runner only writes app0; active app1 must be handled explicitly');
  assert.equal(data[0x10000],0xe9,'Missing ESP8266 app0 header');
  return {entries,active,flash_sha256:sha(data),app0_sha256:sha(data.subarray(0x10000,0x100000))};
}
function main() {
  const backup=path.resolve(process.argv[2]||'.build/rcpdm-simple-board/private/flash-before.bin');
  const directory=path.resolve(process.argv[3]||'.build/rcpdm-simple-board/runs');
  const port=process.argv[4]||'COM8'; assert.match(port,/^COM\d+$/i);
  const data=fs.readFileSync(backup),info=inspectBackup(data);
  if(process.argv.includes('--preflight')) { console.log(JSON.stringify(info,null,2)); return; }
  fs.mkdirSync(directory,{recursive:true});
  const restore=path.join(path.dirname(backup),'app0-restore.bin');
  if(fs.existsSync(restore)) assert.equal(sha(fs.readFileSync(restore)),info.app0_sha256);
  else fs.writeFileSync(restore,data.subarray(0x10000,0x100000),{flag:'wx'});
  const python=path.join(root,'.build/esp8266-python/Scripts/python.exe');
  const esptool=path.join(root,'.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py');
  const env={...process.env,PYTHONIOENCODING:'utf-8'};
  const images={};
  for(const mode of ['production','simple']) {
    const folder=path.join(root,`firmware/development/esp8266-rcpdm-speed/${mode}-simple-board`);
    const manifest=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'),'utf8').replace(/^\uFEFF/,''));
    const binary=path.join(folder,'app.bin'),bytes=fs.readFileSync(binary);
    assert.equal(sha(bytes),manifest.sha256.toLowerCase()); assert.equal(bytes.length,manifest.bytes);
    assert.ok(bytes.length<=0xf0000); assert.equal(manifest.batch,true);
    images[mode]={binary,sha256:sha(bytes),bytes:bytes.length};
  }
  const record={started_utc:new Date().toISOString(),port,backup:info,images,rounds:[],restored:false};
  const save=()=>fs.writeFileSync(path.join(directory,'run-manifest.json'),JSON.stringify(record,null,2)+'\n');
  const run=(args,log)=>{const r=execute(python,args,{cwd:root,env}); fs.writeFileSync(log,r.stdout+r.stderr); return r.stdout+r.stderr;};
  const install=(file,log)=>run([esptool,'--chip','esp8266','--port',port,'--baud','460800',
    '--before','default_reset','--after','no_reset','write_flash','--flash_mode','keep',
    '--flash_size','4MB','--flash_freq','keep','0x10000',file],log);
  save();
  try {
    // Symmetric ABBA ordering reduces bias from a monotonic environmental drift.
    for(const [round,mode] of [[1,'production'],[1,'simple'],[2,'simple'],[2,'production']]) {
      const prefix=path.join(directory,`round-${round}-${mode}`);
      assert.ok(!fs.existsSync(prefix+'-uart.log'),'Do not overwrite a recorded run');
      console.log(`Flashing ${mode}, round ${round} (app0 only)`);
      install(images[mode].binary,prefix+'-flash.log');
      console.log(`Capturing ${mode} output benchmark (45 seconds)`);
      const log=run(['tools/monitor_esp8266.py','--port',port,'--reset','--seconds','45'],prefix+'-uart.log');
      assert.match(log,/audio_output_bench: complete/);
      assert.match(log,/stalled producer.*PASS/);
      assert.doesNotMatch(log,/invalid=[1-9]|PCM write failed|bit-exact FAIL|stalled producer.*FAIL/);
      const label=mode==='simple'?'RCPDM-Simple':'RCPDM';
      assert.ok(log.includes(`${label} bit-exact PASS: 493216 words and states`));
      assert.ok(log.includes(`${label} batch bit-exact PASS: 2144 words`));
      const samples=[...log.matchAll(/pack_only round=(\d+) samples=48000 elapsed=(\d+) us checksum=([0-9a-f]+)/g)];
      assert.equal(samples.length,3); assert.equal(new Set(samples.map(m=>m[3])).size,1);
      record.rounds.push({round,mode,pack_us:samples.map(m=>Number(m[2])),checksum:samples[0][3]}); save();
      console.log(log.split(/\r?\n/).filter(s=>/bit-exact|audio_output_bench: (pack_only|producer_nonwait|dma |heap |complete)/.test(s)).join('\n'));
    }
  } finally {
    console.log('Restoring exact app0 from private backup');
    install(restore,path.join(directory,'restore-flash.log'));
    record.restored=true; save();
    const log=run(['tools/monitor_esp8266.py','--port',port,'--reset','--seconds','45'],path.join(directory,'restore-uart.log'));
    assert.match(log,/yoRadio ESP8266 RTOS SDK native starting/);
    assert.match(log,/profile: HTTP only, Helix MP3\/AAC, I2S-PDM DMA GPIO 3/);
    record.restore_boot_verified=true; record.finished_utc=new Date().toISOString(); save();
    console.log('Original native I2S-PDM radio restored and boot verified.');
  }
}
module.exports={inspectBackup,otaCrc};
if(require.main===module) main();

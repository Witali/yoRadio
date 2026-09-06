const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {build}=require('../tools/esp8266_audio_profile/build_rcpdm8_quality');
const {execute}=require('../tools/esp8266_audio_profile/run_rcpdm_radio');

// Independent BigInt oracle additionally checks file endianness, >32-bit PCM
// frames and that state is not reset at a PCM or 32-bit word boundary.
function reference(samples,bits,shift,method) {
  let state=method?0x80000000n:0n;
  const result=Buffer.alloc(samples.length*bits/8); let pos=0;
  for(const sample of samples) {
    const target=BigInt(sample+32768)*(method?65536n:1n);
    let word=0;
    for(let bit=0;bit<bits;bit++) {
      let high;
      if(!method) { state+=target; high=state>=65536n; if(high) state-=65536n; }
      else {
        const down=state-(state>>BigInt(shift));
        const up=state+((0xffffffffn-state)>>BigInt(shift));
        high=target>(method===2?state:down+((up-down)>>1n));
        state=high?up:down;
      }
      word=((word<<1)|Number(high))>>>0;
      if((bit+1)%Math.min(bits,32)===0) {
        const bytes=Math.min(bits,32)/8;
        result.writeUIntLE(word,pos,bytes);pos+=bytes;word=0;
      }
    }
  }
  return result;
}

test('same-rate PDM matrix preserves decisions and packs all 8..128 new bits', t=>{
  const dir=fs.mkdtempSync(path.join(os.tmpdir(),'pdm-matrix-'));
  t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));
  const exe=build(dir,'pdm_matrix_quality');
  const checks=JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(checks.pass,true);assert.equal(checks.variants,23);
  assert.ok(checks.word_state_checks>3000000);assert.equal(checks.grouping_checks,3840);
  const samples=[0,0,0,-32768,32767,-32767,32766,-1,1,16384,-17000,0,0];
  const pcm=Buffer.alloc(samples.length*2);
  samples.forEach((x,i)=>pcm.writeInt16LE(x,i*2));
  const input=path.join(dir,'input.pcm'),prefix=path.join(dir,'out');
  fs.writeFileSync(input,pcm);execute(exe,[input,prefix]);
  let variants=0;
  [8,16,32,64,128].forEach((bits,index)=>{
    const pdm=fs.readFileSync(`${prefix}.pdm${bits}.bin`);
    assert.deepEqual(pdm,reference(samples,bits,0,0));++variants;
    for(const shift of new Set([4,index+2])) for(const [name,method] of [['rc',1],['simple',2]]) {
      const file=fs.readFileSync(`${prefix}.${name}${bits}-a${2**shift}.bin`);
      assert.deepEqual(file,reference(samples,bits,shift,method));++variants;
    }
  });
  assert.equal(variants,23);
});

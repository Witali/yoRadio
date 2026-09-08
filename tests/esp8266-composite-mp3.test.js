const test=require('node:test'), assert=require('node:assert/strict'), fs=require('node:fs');
const crypto=require('node:crypto');
const {makeWave}=require('../tools/esp8266_audio_profile/generate_composite_mp3.cjs');
test('composite source is deterministic stereo tone/noise with headroom',()=>{
  const a=makeWave(),b=makeWave(),c=makeWave(12345);
  assert.deepEqual(a,b); assert.notDeepEqual(a,c);
  assert.equal(a.length,44+44100*4);
  let peak=0,energy=0,difference=0;
  for(let i=44;i<a.length;i+=4) {
    const l=a.readInt16LE(i),r=a.readInt16LE(i+2);
    peak=Math.max(peak,Math.abs(l),Math.abs(r));energy+=l*l+r*r;
    difference+=Math.abs(l-r);
  }
  assert.equal(peak,23170); assert.ok(energy>1e11); assert.ok(difference>1e7);
});
test('stored MP3s use real sequential frames and match fixture hashes',()=>{
  const dir='tests/fixtures/mp3_composite/';
  const manifest=JSON.parse(fs.readFileSync(dir+'manifest.json'));
  for(const [name,expected] of Object.entries(manifest.files)) {
    const b=fs.readFileSync(dir+name);
    assert.equal(b.length,expected.bytes);
    assert.equal(crypto.createHash('sha256').update(b).digest('hex'),expected.sha256);
    if(!name.endsWith('.mp3'))continue;
    let offset=0,count=0,reservoirFrames=0;
    const rates=[0,32,40,48,56,64,80,96,112,128,160,192,224,256,320];
    while(offset<b.length) {
      const f=b.subarray(offset);
      assert.equal(f[0],255); assert.equal(f[1]&0xfe,0xfa);
      assert.equal((f[2]>>2)&3,0); // MPEG1 44.1 kHz at every bitrate.
      const size=Math.floor(144000*rates[f[2]>>4]/44100)+((f[2]>>1)&1);
      assert.ok(size>0&&offset+size<=b.length);
      const side=4+((f[1]&1)?0:2),reservoir=(f[side]<<1)|(f[side+1]>>7);
      if(count===0)assert.equal(reservoir,0);
      if(reservoir)reservoirFrames++;
      assert.notEqual(f.subarray(side+32,side+36).toString(),'Info');
      assert.notEqual(f.subarray(side+32,side+36).toString(),'Xing');
      offset+=size;count++;
    }
    assert.ok(count>=38);
    // Low-rate files must exercise the reservoir rather than disabling it.
    if(!name.includes('320'))assert.ok(reservoirFrames>0);
  }
});

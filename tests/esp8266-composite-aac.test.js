const test=require('node:test'), assert=require('node:assert/strict'), fs=require('node:fs');
const crypto=require('node:crypto');
test('AAC matrix contains complete sequential AAC-LC frames from the same MP3 source',()=>{
  const dir='tests/fixtures/aac_composite/';
  const manifest=JSON.parse(fs.readFileSync(dir+'manifest.json'));
  const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
  assert.equal(sha(fs.readFileSync(dir+manifest.source_wav)),manifest.source_sha256);
  for(const [name,expected] of Object.entries(manifest.files)) {
    const b=fs.readFileSync(dir+name);
    assert.equal(b.length,expected.bytes); assert.equal(sha(b),expected.sha256);
    let offset=0,count=0;
    while(offset<b.length) {
      const f=b.subarray(offset);
      assert.equal(f[0],255); assert.equal(f[1]&0xf6,0xf0);
      assert.equal(f[2]>>6,1);
      assert.equal((f[2]>>2)&15,4);
      assert.equal(((f[2]&1)<<2)|(f[3]>>6),2);
      assert.equal(f[6]&3,0);
      const size=((f[3]&3)<<11)|(f[4]<<3)|(f[5]>>5);
      assert.ok(size>7 && size<=1536 && offset+size<=b.length);
      offset+=size; count++;
    }
    assert.ok(count>=44 && count<=46);
  }
});

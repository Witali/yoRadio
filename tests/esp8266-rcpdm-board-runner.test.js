const test=require('node:test'),assert=require('node:assert/strict');
const {otaCrc,inspectBackup}=require('../tools/esp8266_audio_profile/run_rcpdm_simple_board');
const {parseRun}=require('../tools/esp8266_audio_profile/summarize_rcpdm_simple_board');
function backup() {
  const data=Buffer.alloc(0x400000,255);
  [['nvs',0x9000,0x6000],['phy_init',0xf000,0x1000],['app0',0x10000,0xf0000],
   ['otadata',0x100000,0x2000],['app1',0x110000,0xf0000],['spiffs',0x3c0000,0x40000]].forEach(([label,offset,size],i)=>{
    const p=0x8000+i*32; data.fill(0,p,p+32); data.writeUInt16LE(0x50aa,p);
    data.writeUInt32LE(offset,p+4); data.writeUInt32LE(size,p+8); data.write(label,p+12,'ascii');
  });
  data[0x10000]=0xe9; return data;
}
function seq(data,p,value) { data.writeUInt32LE(value,p); data.writeUInt32LE(otaCrc(data.subarray(p,p+4)),p+28); }
test('board runner validates SDK OTA CRC and refuses to overwrite an inactive app0',()=>{
  for(const [value,expected] of [[1,0x4743989a],[2,0x55f63774],[3,0xed4a5011]]) {
    const b=Buffer.alloc(4); b.writeUInt32LE(value); assert.equal(otaCrc(b),expected);
  }
  const data=backup(); assert.equal(inspectBackup(data).active,0);
  seq(data,0x100000,2); seq(data,0x101000,3); assert.equal(inspectBackup(data).active,0);
  seq(data,0x101000,4); assert.throws(()=>inspectBackup(data),/active app1/);
  data[0x10001]=1; data.writeUInt32LE(0,0x10001c); data.writeUInt32LE(0,0x10101c);
  assert.throws(()=>inspectBackup(data),/Invalid OTA metadata/);
  assert.throws(()=>inspectBackup(Buffer.alloc(20)),/complete 4 MiB/);
  const wrong=backup(); wrong.writeUInt32LE(0x100000,0x8000+5*32+4); assert.throws(()=>inspectBackup(wrong));
});
test('board result parser rejects missing proof, incomplete tests and DMA underruns',()=>{
  const log=['RCPDM-Simple bit-exact PASS: 493216 words and states','RCPDM-Simple batch bit-exact PASS: 2144 words',
    ...[0,1,2].map(i=>`audio_output_bench: pack_only round=${i} samples=48000 elapsed=100000 us checksum=12345678 DMA=off`),
    'audio_output_bench: result calls=3764 wall=10000000 audio=10037333 write=9900000 invalid=0',
    'audio_output_bench: spi_wait=8700000 invalid=0',
    'audio_output_bench: producer_nonwait=1200000',
    'audio_output_bench: dma eof=941 partial_start=0 blocked_partial=0 fifo_empty=0',
    'audio_output_bench: spi_gap empty=0','audio_output_bench: heap free=108532 min_free=105752',
    'stalled producer (65 ms): PASS','audio_output_bench: complete'].join('\n');
  assert.equal(parseRun(log,'simple').underruns,0);
  assert.throws(()=>parseRun(log,'production'));
  for(const bad of [log.replace('empty=0','empty=1'),log.replace('invalid=0','invalid=1'),
    log.replace('audio_output_bench: complete',''),log.replace('493216','493215')]) assert.throws(()=>parseRun(bad,'simple'));
});

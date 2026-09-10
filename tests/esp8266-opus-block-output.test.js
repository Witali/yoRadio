const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {pack,grouped,run}=require('../tools/esp8266_opus_profile/run_block_regressions.cjs');
const {framed}=require('../tools/esp8266_opus_profile/generate_phase_fixtures.cjs');
const {inspect}=require('../tools/esp8266_opus_profile/inspect_ogg_packets.cjs');
const {inspectPackets,sha256,fixtureDirectory}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const {component}=require('../tools/esp8266_opus_profile/build_host.cjs');
test('packet fixture builder covers CBR/VBR and padding and preserves mode changes and tails',()=>{
  const a=Buffer.from([0xf8,0xff,0xfe]),b=Buffer.from([0xf8,0xff,0xfe,0]),c=Buffer.from([0x78,0]);
  assert.equal(pack([a,a])[0]&3,1);assert.equal(pack([a,b],true)[0]&3,2);
  const padded=pack([a,b,a],true,17);assert.equal(padded[0]&3,3);assert.equal(padded[1],0xc3);
  const data=framed([a,a,c,c,c,c,c]);
  assert.equal(inspectPackets(grouped(data,3)).samples,inspectPackets(data).samples);
  assert.throws(()=>pack([a,c]));assert.throws(()=>pack([a,b]));
});
test('capture inspector verifies complete-page CRC and explicitly retains truncated-tail information',()=>{
  const data=fs.readFileSync(path.join(fixtureDirectory,'mono-24.opus'));
  const full=inspect(data);assert.ok(full.report.packets>0);assert.equal(full.report.trailing_bytes,0);
  const tail=inspect(Buffer.concat([data,Buffer.alloc(12)]));
  assert.equal(tail.report.trailing_bytes,12);assert.deepEqual(tail.raw,full.raw);
  const bad=Buffer.from(data);bad[22]^=1;assert.throws(()=>inspect(bad),/CRC/);
});
test('saved bounded block PCM matches pristine including 120ms packets with no extra PCM or heap allocation',()=>{
  const report=JSON.parse(fs.readFileSync(path.join(__dirname,'../tools/esp8266_opus_profile/block-results.json')));
  assert.equal(report.passed,true);assert.ok(report.cases.length>=11);
  for(const [file,hash] of Object.entries(report.source_sha256_lf))
    assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  for(const c of report.cases){assert.equal(c.pcm.exact,true);assert.equal(c.pcm.max_absolute_error,0);
    assert.equal(c.result.pcm_bytes,1920);assert.equal(c.result.allocations,0);assert.equal(c.result.guards,true);
    assert.equal(c.result.sink_mutation,true);assert.equal(c.result.reentry_rejected,true);
    assert.ok(c.result.scratch_bytes<=6144&&c.result.scratch_words<=16384&&c.result.largest_block<=960);}
  assert.ok(report.cases.some(c=>c.packet_durations_ms['120']>0));
  assert.ok(report.cases.some(c=>c.name==='mixed-long-silk-hybrid-celt'));
});
test('full block-output corpus can be reproduced',{skip:process.env.OPUS_BLOCK_TEST!=='1'&&'Set OPUS_BLOCK_TEST=1 for full host comparison',timeout:240000},async()=>{
  assert.equal((await run()).passed,true);
});

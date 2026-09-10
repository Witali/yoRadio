const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,buildHost,runProbe}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {fixtureDirectory,sha256,inspectPackets}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const {buildBoardFixtures}=require('../tools/esp8266_opus_profile/build_board_fixtures.cjs');
const {comparePcm}=require('../tools/esp8266_opus_profile/run_regressions.cjs');
const corpus=path.join(fixtureDirectory,'through192');
test('through192 is a separate test corpus, original high-rate fixtures remain intact',()=>{
  const manifest=JSON.parse(fs.readFileSync(path.join(corpus,'manifest.json')));
  assert.deepEqual(manifest.fixtures.map(f=>f.bitrate_kbps),[12,24,64,128,192]);
  for(const f of manifest.fixtures){
    const data=fs.readFileSync(path.resolve(corpus,f.packet_file||f.name+'.opuspkt'));
    assert.equal(sha256(data),f.opuspkt_sha256);assert.equal(inspectPackets(data).packets,61);
  }
  const f=manifest.fixtures.at(-1);assert.equal(f.max_packet_bytes,480);
  const legacy=JSON.parse(fs.readFileSync(path.join(fixtureDirectory,'manifest.json')));
  assert.equal(legacy.fixtures.at(-1).bitrate_kbps,510);
  assert.equal(sha256(fs.readFileSync(path.join(fixtureDirectory,'stereo-510.opuspkt'))),legacy.fixtures.at(-1).opuspkt_sha256);
});
test('192kbps test packet selection has honest labels and exact decoder-only PCM',{timeout:180000},async()=>{
  const out=path.join(root,'.build/opus-test-through192');fs.mkdirSync(out,{recursive:true});
  const report=buildBoardFixtures({corpus,output:path.join(out,'board')});
  assert.equal(report.fixture_count,5);assert.equal(report.fixtures.at(-1).name,'stereo-192');
  assert.equal(report.fixtures.at(-1).bitrate_kbps,192);
  const common={bounded:true,fastInt64:0,firFlashWord:true},fixture=path.join(corpus,'stereo-192.opuspkt');
  for(const celtDecodeOnly of [false,true]){
    await buildHost({...common,celtDecodeOnly});
    const result=runProbe({...common,celtDecodeOnly,fixture,output:path.join(out,celtDecodeOnly?'on.pcm':'off.pcm')});
    assert.equal(result.arena_guards_ok,true);assert.equal(result.oom_reinitialized_exact,true);
    assert.ok(result.scratch_byte_peak_bytes<=6144&&result.scratch_word_peak_bytes<=16384);
  }
  const pcm=comparePcm(fs.readFileSync(path.join(out,'off.pcm')),fs.readFileSync(path.join(out,'on.pcm')));
  assert.equal(pcm.exact,true);assert.equal(pcm.max_absolute_error,0);
  fs.writeFileSync(path.join(out,'pcm.json'),JSON.stringify(pcm,null,2)+'\n');
});

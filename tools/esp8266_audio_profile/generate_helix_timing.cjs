// Own tone/noise corpus. Frame copies and validation are outside decode timing.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {makeWave}=require('./generate_composite_mp3.cjs');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
function frames(data,codec) {
  const result=[]; let offset=0;
  while(offset<data.length) {
    const b=data.subarray(offset); let bytes,samples;
    assert.equal(b[0],255,'Frame sync');
    if(codec==='MP3') {
      assert.equal(b[1]&0xfe,0xfa,'MPEG1 Layer III');
      assert.equal((b[2]>>2)&3,1,'48 kHz');
      const kbps=[0,32,40,48,56,64,80,96,112,128,160,192,224,256,320][b[2]>>4];
      assert.ok(kbps);bytes=Math.floor(144000*kbps/48000)+((b[2]>>1)&1);samples=1152;
    } else {
      assert.equal(b[1]&0xf6,0xf0,'ADTS sync');
      assert.equal((b[2]>>2)&15,3,'48 kHz');
      assert.equal(b[2]>>6,1,'AAC-LC');
      assert.equal(b[6]&3,0,'One AAC raw block');
      bytes=((b[3]&3)<<11)|(b[4]<<3)|(b[5]>>5);samples=1024;
    }
    assert.ok(bytes>=7&&bytes<=1536&&offset+bytes<=data.length,'Complete bounded frame');
    result.push({data:data.subarray(offset,offset+bytes),samples});offset+=bytes;
  }
  return result;
}
function generate(out,ffmpeg='ffmpeg') {
  fs.mkdirSync(out,{recursive:true});const wav=makeWave();
  const fixtures=[],entries=[],chunks=[];let offset=0;
  for(const [codec,bitrate] of [['MP3',64],['MP3',128],['MP3',320],['AAC',48],['AAC',128],['AAC',320]]) {
    const name=codec.toLowerCase()+'-'+bitrate, file=path.join(out,name+(codec==='MP3'?'.mp3':'.aac'));
    const args=['-hide_banner','-loglevel','error','-y','-i','pipe:0','-map_metadata','-1','-ar','48000','-ac','2'];
    args.push(...(codec==='MP3'?['-c:a','libmp3lame','-b:a',bitrate+'k','-joint_stereo','1','-reservoir','1','-write_xing','0','-id3v2_version','0']:['-c:a','aac','-profile:a','aac_low','-b:a',bitrate+'k','-f','adts']),file);
    const r=spawnSync(ffmpeg,args,{input:wav});assert.equal(r.status,0,r.stderr?.toString());
    const encoded=fs.readFileSync(file), selected=frames(encoded,codec).slice(0,20);
    assert.equal(selected.length,20);const first=entries.length;
    for(const frame of selected) {
      const padded=Buffer.alloc((frame.data.length+3)&~3);frame.data.copy(padded);
      entries.push({offset,length:frame.data.length});chunks.push(padded);offset+=padded.length;
    }
    const samples=selected.reduce((n,f)=>n+f.samples,0),bytes=selected.reduce((n,f)=>n+f.data.length,0);
    fixtures.push({name,codec,kind:codec==='MP3'?1:2,bitrate_kbps:bitrate,actual_kbps:bytes*8*48000/samples/1000,
      first_packet:first,packet_count:selected.length,samples,rate:48000,source_channels:2,
      encoded_sha256:hash(encoded),selected_sha256:hash(Buffer.concat(selected.map(f=>f.data)))});
  }
  const payload=Buffer.concat(chunks),words=[];
  for(let n=0;n<payload.length;n+=4)words.push('0x'+payload.readUInt32LE(n).toString(16)+'U');
  const rows=[];for(let n=0;n<words.length;n+=8)rows.push('  '+words.slice(n,n+8).join(',')+',');
  const header=`#pragma once\n#include <stdint.h>\nstruct helix_timing_fixture_t {uint32_t kind, first, count, samples;};\nstruct helix_timing_packet_t {uint32_t offset, bytes;};\n#define HELIX_TIMING_CASES ${fixtures.length}U\n#define HELIX_TIMING_PACKETS ${entries.length}U\n#define HELIX_TIMING_PAYLOAD_BYTES ${payload.length}U\nstatic const helix_timing_fixture_t helix_timing_fixtures[] = {\n${fixtures.map(f=>`  {${f.kind},${f.first_packet},${f.packet_count},${f.samples}},`).join('\n')}\n};\nstatic const helix_timing_packet_t helix_timing_packets[] = {\n${entries.map(e=>`  {${e.offset},${e.length}},`).join('\n')}\n};\nstatic const uint32_t helix_timing_payload[] = {\n${rows.join('\n')}\n};\n`;
  const report={schema:1,source:'Deterministic tones, sweep and seeded noise; see generate_composite_mp3.cjs',
    source_sha256:hash(wav),sample_rate:48000,output_channels:1,
    encoder:spawnSync(ffmpeg,['-version'],{encoding:'utf8'}).stdout.split(/\r?\n/)[0],
    header_sha256:hash(header),payload_bytes:payload.length,fixtures};
  fs.writeFileSync(path.join(out,'helix_timing_fixtures.h'),header);
  fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={frames,generate};
if(require.main===module)console.log(JSON.stringify(generate(path.resolve(process.argv[2]||'.build/helix-timing-fixtures')),null,2));

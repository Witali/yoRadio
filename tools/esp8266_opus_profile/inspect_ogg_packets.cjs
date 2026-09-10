// Inspect a bounded local capture without publishing its audio. Only complete
// CRC-verified pages contribute; a truncated tail is explicitly reported.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {sha256,inspectPackets}=require('./fixtures.cjs');
const {framed}=require('./generate_phase_fixtures.cjs');
function inspect(data) {
  assert.ok(data.length<=4*1024*1024,'Capture bound exceeded');
  let pos=0,parts=[],pages=0;const packets=[],layouts={};
  while(pos+27<=data.length) {
    assert.equal(data.toString('ascii',pos,pos+4),'OggS');assert.equal(data[pos+4],0);
    const count=data[pos+26],lace=data.subarray(pos+27,pos+27+count);
    if(lace.length!==count)break;
    const end=pos+27+count+lace.reduce((a,b)=>a+b,0);if(end>data.length)break;
    let crc=0;for(let i=pos;i<end;i++){crc^=(i>=pos+22&&i<pos+26?0:data[i])<<24;
      for(let bit=0;bit<8;bit++)crc=((crc<<1)^((crc&0x80000000)?0x04c11db7:0))>>>0;}
    assert.equal(crc,data.readUInt32LE(pos+22),'Ogg CRC mismatch');
    pos+=27+count;pages++;
    for(const size of lace) {
      parts.push(data.subarray(pos,pos+size));pos+=size;
      if(size<255) {
        const packet=Buffer.concat(parts);parts=[];
        if(['OpusHead','OpusTags'].includes(packet.toString('ascii',0,8)))continue;
        const toc=packet[0],c=toc>>>3,code=toc&3;
        const frames=code===0?1:code===3?packet[1]&63:2;
        const frameMs=c<12?[10,20,40,60][c&3]:c<16?[10,20][c&1]:[2.5,5,10,20][c&3];
        const key=JSON.stringify({mode:c<12?'SILK':c<16?'Hybrid':'CELT',toc,frame_ms:frameMs,frames,packet_ms:frames*frameMs});
        layouts[key]=(layouts[key]||0)+1;packets.push(packet);
      }
    }
  }
  const raw=framed(packets);
  return {raw,report:{sha256:sha256(data),capture_bytes:data.length,complete_bytes:pos,pages,
    trailing_bytes:data.length-pos,partial_packet_bytes:parts.reduce((n,p)=>n+p.length,0),
    layouts:Object.entries(layouts).map(([layout,count])=>({...JSON.parse(layout),count})),...inspectPackets(raw)}};
}
module.exports={inspect};
if(require.main===module) {
  const [input,output,raw]=process.argv.slice(2);assert.ok(input&&output,'capture.opus report.json [packets.opuspkt]');
  const result=inspect(fs.readFileSync(input));fs.mkdirSync(path.dirname(output),{recursive:true});
  fs.writeFileSync(output,JSON.stringify(result.report,null,2)+'\n');if(raw)fs.writeFileSync(raw,result.raw);
  console.log(JSON.stringify(result.report,null,2));
}

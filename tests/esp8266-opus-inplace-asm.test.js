const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const r=require('../tools/esp8266_opus_asm/pvq_inplace_b1.cjs'),p=require('../tools/esp8266_opus_asm/pvq_inplace_b1_proof.cjs');
const published=path.join(r.art('candidate'),'preflight.json');
const proofFile=fs.existsSync(published)?published:path.join(r.build('candidate'),'local-proof.json');
const present=fs.existsSync(proofFile),local=present?r.read(proofFile):null;
function data(){
 const before=fs.existsSync(published)?require('node:zlib').gunzipSync(fs.readFileSync(path.join(r.art('candidate'),'parent.elf.gz'))):fs.readFileSync(path.join(r.build('control'),'yoradio_esp8266_helix_native.elf'));
 const after=require('../tools/esp8266_opus_asm/frozen_reloads.cjs').patchElf(before,local.patches);
 return{...local,info:{functions:local.functions},before,after};
}
test('linked clone keeps instructions, literals, stack and fallback',{skip:!present},()=>{
 assert.deepEqual(p.structural(data()),local.semantic.structural);
});
test('guard rejects other B and unsafe K without corrupting arguments',{skip:!present},()=>{
 assert.deepEqual(p.guards(data()),{cases:80,exact:true,no_extra_stack:true});
 const d=data();d.dis={...d.dis,guard:d.dis.guard.replace('bnei','beqi')};assert.throws(()=>p.guards(d));
});
test('proof rejects a changed output-store width',{skip:!present},()=>{
 const d=data();d.dis={...d.dis,inplace_decode16:d.dis.inplace_decode16.replace('s16i','s32i')};assert.throws(()=>p.structural(d));
});
test('proof rejects changing the original fallback',{skip:!present},()=>{
 const d=data(),{offsetAt}=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');d.after=Buffer.from(d.after);d.after[offsetAt(d.after,r.site+3,1)]^=1;assert.throws(()=>p.structural(d));
});
test('pulse decode changes five stores, one stride and the final X offset',{skip:!present},()=>{
 const edits=r.edits(local.functions.decode_pulses);assert.equal(edits.size,7);
 assert.equal([...edits.values()].flat().filter(s=>s.startsWith('s16i')).length,5);
 assert.deepEqual(edits.get(0x40253514),['addi a3, a4, 52','srli a3, a3, 1']);
});
test('patched function entry is an LX106 J to the proven guard',{skip:!present},()=>{
 const {readAt}=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs');
 const bytes=readAt(data().after,r.site,3),word=bytes[0]|(bytes[1]<<8)|(bytes[2]<<16);
 assert.equal(word&63,6);const signedDisplacement=(word<<8)>>14;
 assert.equal(r.site+4+signedDisplacement,r.guard);
});
test('ISA interpreter arithmetic shift and signed halfword boundaries',()=>{
 const code=p.program('1000: 000000 l16si a2, a3, 0\n1003: 000000 ssr a4\n1006: 000000 sra a2, a2\n1009: 000000 s16i a2, a3, 0');
 for(const raw of[0,1,32767,32768,65535])for(const shift of[0,1,15,31]){
  const registers=Array(16).fill(0);registers[3]=0x2000;registers[4]=shift;let written;
  p.interpret(code,{registers,start:0x1000,stop:0x100c,read:(a,n)=>{assert.equal(a,0x2000);assert.equal(n,2);return raw;},write:(a,n,v)=>{assert.equal(a,0x2000);assert.equal(n,2);written=v&65535;}});
  assert.equal(written,(((raw<<16)>>16)>>shift)&65535);
 }
});

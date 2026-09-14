const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const f=require('../tools/esp8266_opus_asm/frozen_reloads.cjs');
const {hash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const proof=read(path.join(f.art('candidate'),'preflight.json'));
const elf=zlib.gunzipSync(fs.readFileSync(path.join(f.art('candidate'),'parent.elf.gz')));
test('all eight ASM copies preserve symbolic state for arbitrary register and stack values',()=>{
 for(const s of f.specs)assert.deepEqual(f.symbolic(s.ops),f.symbolic([...s.ops.slice(0,-1),'mov '+s.copy]));
 assert.equal(f.specs.length,8);
 for(const s of f.specs)assert.notDeepEqual(f.symbolic(s.ops),f.symbolic([...s.ops.slice(0,-1),'mov '+s.copy.split(', ')[0]+', a0']));
});
test('proof refuses writes, MMIO loads, calls, unknown instructions and changed stack source',()=>{
 for(const op of ['s32i a2, a1, 32','l32i a2, a4, 0','call0 helper','mov a1, a2','ssr a3','unknown a2, a3','l32i a2, a1, 3'])assert.throws(()=>f.symbolic([op]));
 const s=f.specs[0],bad=[...s.ops];bad[1]='mov a7, a5';assert.notDeepEqual(f.symbolic(bad),f.symbolic([...bad.slice(0,-1),'mov '+s.copy]));
});
test('linked matching rejects interior branch entries, missing sequences and duplicate sequences',()=>{
 const spec=f.specs[1],fn=proof.functions[spec.fn],p=f.findPatch(fn,spec);assert.equal(p.address,proof.patches[1].address);
 assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly.replace('a10, a1, 56','a10, a1, 52')},spec));
 const extra='\n'+(fn.address+fn.bytes+8).toString(16)+': 000000 j '+p.address.toString(16)+' <target>';
 assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly+extra},spec),/bypasses/);
 assert.throws(()=>f.findPatch({...fn,disassembly:fn.disassembly+'\n'+fn.disassembly},spec),/unique/);
});
test('eight exact patches leave all other ELF bytes and all RAM/address metadata unchanged',()=>{
 const out=f.patchElf(elf,proof.patches);assert.equal(hash(out),proof.candidate_elf_sha256);assert.equal(out.length,elf.length);
 const allowed=new Set(proof.patches.flatMap(p=>Array.from({length:p.bytes},(_,i)=>f.offsetAt(elf,p.address,p.bytes)+i)));
 for(let i=0;i<elf.length;i++)if(!allowed.has(i))assert.equal(out[i],elf[i]);
 assert.equal(proof.static_ram_delta,0);assert.equal(proof.stack_delta,0);
 const bad=structuredClone(proof.patches);bad[0].before_hex='00'.repeat(bad[0].bytes);assert.throws(()=>f.patchElf(elf,bad));
 assert.throws(()=>f.patchElf(elf,[...proof.patches,proof.patches[0]]));
 assert.throws(()=>f.offsetAt(elf,0xfffffff0,4));
});
test('packaged app keeps addresses and payload except eight instruction slots and checksum/digest',()=>{
 const a=fs.readFileSync(path.join(f.art('control'),'app.bin')),b=fs.readFileSync(path.join(f.art('candidate'),'app.bin'));
 assert.deepEqual(f.compareApps(a,b,proof.patches),proof.imageProof);
 const bad=Buffer.from(b),x=require('../tools/esp8266_opus_asm/frozen_div.cjs').inspectImage(b);bad[x.segments[0].offset]^=1;bad[x.checksumOffset]^=1;Buffer.from(hash(bad.subarray(0,x.checksumOffset+1)),'hex').copy(bad,x.checksumOffset+1);assert.throws(()=>f.compareApps(a,bad,proof.patches),/Unrelated/);
});
test('archived proof matches recipe, decoder profile and assembled opcode object',()=>{
 const {manifests}=require('../tools/esp8266_opus_asm/report_frozen_reloads.cjs').verifyPair();
 for(const change of [m=>m.cpu_mhz=80,m=>m.flash='QIO80',m=>m.opus_benchmark_output=true,m=>m.opus_input_bytes+=4,m=>m.opus_function_profile=true]){const b=structuredClone(manifests.candidate);change(b);assert.throws(()=>f.manifestPair(manifests.control,b));}
});

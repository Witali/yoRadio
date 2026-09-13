// Evidence for this A/B pair: same relocatable static_handler semantics, but
// different post-link call encoding. Not a cycle/cache model or global proof.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,run,hash}=require('./export.cjs'),{canonical}=require('./disassembly.cjs');
function wordAt(file,address){
 const b=fs.readFileSync(file);assert.equal(b.subarray(0,4).toString('hex'),'7f454c46');
 assert.equal(b[4],1);assert.equal(b[5],1); // ELF32, little endian.
 const start=b.readUInt32LE(32),stride=b.readUInt16LE(46),count=b.readUInt16LE(48);
 for(let i=0;i<count;i++){
  const p=start+i*stride,base=b.readUInt32LE(p+12),bytes=b.readUInt32LE(p+20);
  if(b.readUInt32LE(p+4)!==1||address<base||address+4>base+bytes)continue;
  return b.readUInt32LE(b.readUInt32LE(p+16)+address-base);
 }
 throw Error('Address not backed by a PROGBITS section');
}
function audit(compiler){
 const bin=path.dirname(compiler),dump=path.join(bin,'xtensa-lx106-elf-objdump.exe');
 const variants=['esp8266-opus-functions-control-v2','esp8266-opus-bands-update-fast-v1'];
 const data=variants.map(variant=>{
  const dir=path.join(root,'.build',variant),elf=path.join(dir,'yoradio_esp8266_helix_native.elf');
  const object=path.join(dir,'esp-idf/main/CMakeFiles/__idf_main.dir/web_service.c.obj');
  return {variant,elf,elf_sha256:hash(fs.readFileSync(elf)),object_sha256:hash(fs.readFileSync(object)),
   instructions:canonical(run(dump,['-dr','-j','.text.static_handler',object])),
   // Known instruction boundary of the matching close(fd) basic block.
   snippet:run(dump,['-d','--start-address=0x40222300','--stop-address=0x4022230b',elf])};
 });
 assert.deepEqual(data[0].instructions,data[1].instructions);
 assert.match(data[0].snippet,/40222302:\s+\w+\s+call0\s+40295a40 <close>/);
 assert.match(data[1].snippet,/40222302:\s+\w+\s+l32r\s+a0, 40210490/);
 assert.match(data[1].snippet,/40222305:\s+\w+\s+callx0\s+a0/);
 assert.equal(wordAt(data[1].elf,0x40210490),0x40295ab4);
 const nm=run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',data[1].elf]);
 assert.match(nm,/^40295ab4\s+\w+\s+\S\s+close$/m);
 const report={scope:'Pinned pair only. Same object instruction semantics and branch graph; linker retains an indirect close call in candidate. Not evidence of an HTTP correctness bug, cache-miss count or measured timing attribution.',
  object_instructions_equal:true,object_instruction_count:data[0].instructions.length,
  normalized_object_sha256:hash(data[0].instructions.join('\n')),
  variants:data.map(({instructions,elf,...rest})=>rest),
  candidate_literal:{address:'0x40210490',value:'0x40295ab4',target:'close'}};
 const file=path.join(root,'firmware/development',variants[1],'link-relaxation.json');
 fs.writeFileSync(file,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={wordAt,audit};if(require.main===module)audit(process.argv[2]);

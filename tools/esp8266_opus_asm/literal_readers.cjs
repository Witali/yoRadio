// Audit every possible L32R encoding, then require a real reachable instruction.
// Linear objdump can start in alignment padding and invent a literal reader.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {run}=require('./export.cjs');
const {sections}=require('./frozen_div.cjs');
const {reachableDisassembly}=require('./report_layout.cjs');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
function literalReader(file,address){
 const elf=fs.readFileSync(file),possible=[];
 for(const s of sections(elf).filter(s=>/^(\.flash\.text|\.iram0\.text)$/.test(s.name)))
  for(let i=0;i+3<=s.bytes;i++){
   const o=s.offset+i,pc=s.address+i;
   if((elf[o]&15)!==1)continue;
   const target=((pc+3)&~3)+(elf.readUInt16LE(o+1)<<2)-0x40000;
   if(target===address)possible.push(pc);
  }
 const symbols=[...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',file]).matchAll(/^([0-9a-f]+)\s+([0-9a-f]+)\s+[Tt]\s+(.+)$/gm)]
  .map(m=>({address:parseInt(m[1],16),bytes:parseInt(m[2],16),name:m[3]}));
 const cache=new Map(),readers=[];
 for(const pc of possible){
  const owners=symbols.filter(s=>pc>=s.address&&pc<s.address+s.bytes);
  assert.equal(owners.length,1,'Unowned/ambiguous possible literal reader '+pc.toString(16));
  const s=owners[0];
  if(!cache.has(s.address))cache.set(s.address,reachableDisassembly(file,s,undefined,{followInternalCalls:true}));
  const line=cache.get(s.address).split('\n').find(l=>new RegExp('^\\s*'+pc.toString(16)+':').test(l));
  if(line){assert.match(line,new RegExp('l32r\\s+[^,]+,\\s*'+address.toString(16)+'\\b'));readers.push(line);}
 }
 return readers;
}
module.exports={literalReader};

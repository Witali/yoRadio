#!/usr/bin/env node
// Link-only experiment proof. Never flashes or infers dynamic heap from ELF.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {execFileSync}=require('node:child_process');
const {hash}=require('./export.cjs');
const wanted=['alg_unquant','decode_pulses'];
function symbols(text){
 const result=[];
 for(const line of text.split(/\r?\n/)){
  const m=line.match(/^([0-9a-f]+)\s+([0-9a-f]+)\s+([Tt])\s+(\S+)$/);
  if(m)result.push({address:parseInt(m[1],16),size:parseInt(m[2],16),name:m[4]});
 }
 assert.ok(result.length>100,'Missing ELF text symbols');return result;
}
function sections(text){
 const out={};
 for(const line of text.split(/\r?\n/)){
  const m=line.match(/^([.\w]+)\s+(\d+)\s+(\d+)\s*$/);
  if(m)out[m[1]]=Number(m[2]);
 }
 for(const n of ['.iram0.text','.iram0.bss','.dram0.data','.dram0.bss'])assert.ok(n in out,'Missing '+n);
 return out;
}
function check(reference,candidate,bin){
 const tool=(name,args)=>execFileSync(path.join(bin,'xtensa-lx106-elf-'+name+'.exe'),args,{encoding:'utf8',maxBuffer:64*1024*1024});
 const a=symbols(tool('nm',['-S',reference])),b=symbols(tool('nm',['-S',candidate]));
 const flash=x=>x>=0x40200000&&x<0x41000000,iram=x=>x>=0x40100000&&x<0x4010c000;
 const moves=[];
 for(const old of a){
  const next=b.filter(x=>x.name===old.name);
  if(flash(old.address)&&next.some(x=>iram(x.address)))moves.push(old.name);
 }
 assert.deepEqual(moves.sort(),wanted,'Unexpected functions moved to IRAM');
 const functions=wanted.map(name=>{
  const old=a.filter(x=>x.name===name),next=b.filter(x=>x.name===name);
  assert.equal(old.length,1);assert.equal(next.length,1);
  // IRAM-to-flash calls may no longer relax to short CALL0. Linked sizes can
  // change even with identical object instructions/relocations (checked below).
  return {name,reference:old[0],candidate:next[0]};
 });
 const sa=sections(tool('size',['-A',reference])),sb=sections(tool('size',['-A',candidate]));
 for(const n of ['.iram0.vectors','.iram0.bss','.dram0.data','.dram0.bss'])assert.equal(sa[n],sb[n],n+' changed');
 const raw=tool('nm',[candidate]).match(/^([0-9a-f]+)\s+\w\s+_iram_end$/m);
 assert.ok(raw,'Missing _iram_end');const end=parseInt(raw[1],16);
 const arena=16384,guard=2048,headroom=0x4010c000-end-arena;
 assert.ok(headroom>=guard,'IRAM arena + conservative headroom no longer fit');
 const archive=elf=>path.join(path.dirname(elf),'esp-idf','opus_decoder','libopus_decoder.a');
 // Same instructions and relocations in all objects, except the archive path banner.
 const disasm=elf=>tool('objdump',['-d','-r',archive(elf)]).replace(/In archive [^\r\n]+/,'In archive OPUS');
 const da=disasm(reference),db=disasm(candidate);assert.equal(hash(da),hash(db),'Opus object instructions/relocations changed');
 return {functions,reference_sections:sa,candidate_sections:sb,iram_text_growth:sb['.iram0.text']-sa['.iram0.text'],
  iram_end:end,arena_bytes:arena,conservative_headroom:headroom,required_headroom:guard,
  opus_disassembly_sha256:hash(da),reference_elf_sha256:hash(fs.readFileSync(reference)),
  candidate_elf_sha256:hash(fs.readFileSync(candidate)),
  reference_app_sha256:hash(fs.readFileSync(reference.replace(/\.elf$/,'.bin'))),
  candidate_app_sha256:hash(fs.readFileSync(candidate.replace(/\.elf$/,'.bin'))),
  note:'Static link proof only; physical arena allocation and DRAM safety still require testing.'};
}
module.exports={symbols,sections,check};
if(require.main===module){
 const [reference,candidate,bin,output]=process.argv.slice(2);
 assert.ok(reference&&candidate&&bin&&output,'Usage: check_iram.cjs A.elf B.elf tool-bin output.json');
 assert.ok(!fs.existsSync(output),'Never overwrite evidence');
 const result=check(reference,candidate,bin);fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
}

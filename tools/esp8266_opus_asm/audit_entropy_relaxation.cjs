// Verify all size-changing functions, resolving only actual equal printable
// NUL-terminated flash strings when the linker omitted their symbol names.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,sourceHash}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs'),{sections}=require('./frozen_div.cjs');
function stringAt(elf,address){
 const s=sections(elf).find(s=>s.type===1&&s.flags&2&&address>=s.address&&address<s.address+s.bytes);
 if(!s||address<0x40200000||address>=0x40300000)return null;
 const offset=s.offset+address-s.address,limit=Math.min(s.offset+s.bytes,offset+512);
 let end=offset;
 for(;end<limit&&elf[end];end++)if(elf[end]!==9&&elf[end]!==10&&elf[end]!==13&&(elf[end]<32||elf[end]>126))return null;
 if(end===limit)return null; // An empty C string is the single NUL byte.
 return elf.subarray(offset,end+1).toString('hex');
}
function blockAt(elf,map,address){
 // Anonymous .LC0 in silk/dec_API has no sized nm symbol. Resolve the entire
 // input rodata section by the real map, not an arbitrary prefix/window.
 const rows=[...map.matchAll(/^ \.rodata\s+0x([0-9a-f]+)\s+0x([0-9a-f]+)\s+([^\r\n]+)$/gm)];
 const row=rows.find(r=>parseInt(r[1],16)===address);if(!row)return null;
 const size=parseInt(row[2],16),s=sections(elf).find(s=>s.type===1&&s.flags&2&&address>=s.address&&address+size<=s.address+s.bytes);
 if(!s||address<0x40200000||address>=0x40300000||!size)return null;
 return {object:row[3].replaceAll('\\','/'),size,bytes_hex:elf.subarray(s.offset+address-s.address,s.offset+address-s.address+size).toString('hex')};
}
function withoutIdentityMoves(graph){
 const drop=s=>/^mov (a\d+), \1$/.test(s),map=new Map();let index=0;
 graph.forEach((s,i)=>{map.set(i,index);if(!drop(s))index++;});
 return graph.filter(s=>!drop(s)).map(s=>s.replace(/instruction:(\d+)/g,(_,i)=>{
  const n=map.get(Number(i));assert.ok(n!==undefined&&n<index,'Invalid identity-move branch target');return 'instruction:'+n;
 }));
}
function audit(){
 const dir=path.join(root,'firmware/development/esp8266-opus-entropy-iram-v1');
 const proof=JSON.parse(fs.readFileSync(path.join(dir,'preflight.json')));
 const names=Object.keys(proof.control.function_sizes).filter(n=>JSON.stringify(proof.control.function_sizes[n])!==JSON.stringify(proof.candidate.function_sizes[n]));
 const variants=['esp8266-opus-entropy-control-v1','esp8266-opus-entropy-iram-v1'];
 const elf=variants.map(v=>fs.readFileSync(path.join(root,'.build',v,'yoradio_esp8266_helix_native.elf')));
 const maps=variants.map(v=>fs.readFileSync(path.join(root,'.build',v,'yoradio_esp8266_helix_native.map'),'utf8'));
 for(const [i,p]of [proof.control,proof.candidate].entries())assert.equal(hash(elf[i]),p.elf_sha256);
 const [a,b]=variants.map(v=>inspect(v,names)),strings=[];
 for(const n of names){
  const x=withoutIdentityMoves(a.functions[n].graph),y=withoutIdentityMoves(b.functions[n].graph);assert.equal(x.length,y.length,n+' length');
  for(let i=0;i<x.length;i++){
   if(x[i]===y[i])continue;
   const m=x[i].match(/^(l32r a\d+, literal:)0x([0-9a-f]+)$/),k=y[i].match(/^(l32r a\d+, literal:)0x([0-9a-f]+)$/);
   assert.ok(m&&k&&m[1]===k[1],n+' instruction '+i+': '+x[i]+' / '+y[i]);
   const from=parseInt(m[2],16),to=parseInt(k[2],16),value=stringAt(elf[0],from);
   if(value){
    assert.equal(stringAt(elf[1],to),value,n+' changed string');
    strings.push({function:n,instruction:i,from,to,kind:'string',bytes_hex_including_nul:value});
   }else{
    const block=blockAt(elf[0],maps[0],from);assert.ok(block,n+' unresolved literal');
    assert.deepEqual(blockAt(elf[1],maps[1],to),block,n+' changed readonly block');
    strings.push({function:n,instruction:i,from,to,kind:'rodata',...block});
   }
  }
 }
 const result={passed:true,recipe_sha256_lf:sourceHash(__filename),names,strings,control:a,candidate:b,
  scope:'All linked-size-changing function graphs identical except proven byte-identical relocated flash strings/complete input rodata sections, identity MOV padding and normalized direct/indirect CALL0 relaxation. Full physical instructions retained.'};
 fs.writeFileSync(path.join(dir,'relaxation-check.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({passed:true,functions:names.length,relocated_string_references:strings.length}));return result;
}
module.exports={audit,stringAt,blockAt,withoutIdentityMoves};if(require.main===module)audit();

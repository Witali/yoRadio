// Diagnostic-only ROM/ASM A/B with identical linked addresses and instructions.
// Change one aligned L32R target word, not the hot loop, ABI, RAM or linker map.
// Never patch an uploaded image in place: build/check two new app-only artifacts.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {root,hash,sourceHash,run}=require('./export.cjs');
const {reachableDisassembly}=require('./report_layout.cjs');
const parent='esp8266-opus-small-div-tail-v1',variant=t=>'esp8266-opus-frozen-div-'+t+'-v1';
const art=t=>path.join(root,'firmware/development',variant(t));
const build=t=>path.join(root,'.build',variant(t));
const elfName='yoradio_esp8266_helix_native.elf';
const compilerBin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const python='C:/Work/yoRadio/.build/esp8266-python/Scripts/python.exe';
const esptool='C:/Work/yoRadio/.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esptool_py/esptool/esptool.py';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function save(p,bytes){
 if(typeof bytes==='string')bytes=Buffer.from(bytes);
 fs.mkdirSync(path.dirname(p),{recursive:true});
 if(fs.existsSync(p))assert.deepEqual(fs.readFileSync(p),bytes,'Do not replace different artifact: '+p);
 else fs.writeFileSync(p,bytes);
}
function sections(b){
 assert.equal(b.subarray(0,6).toString('hex'),'7f454c460101');
 assert.equal(b.readUInt16LE(18),94,'Xtensa ELF required');
 const off=b.readUInt32LE(32),stride=b.readUInt16LE(46),count=b.readUInt16LE(48);
 assert.ok(stride>=40&&count>0&&off+count*stride<=b.length);
 const rows=Array.from({length:count},(_,i)=>{const p=off+i*stride;return {
  nameOffset:b.readUInt32LE(p),type:b.readUInt32LE(p+4),flags:b.readUInt32LE(p+8),
  address:b.readUInt32LE(p+12),offset:b.readUInt32LE(p+16),bytes:b.readUInt32LE(p+20)};});
 const strings=rows[b.readUInt16LE(50)];assert.ok(strings&&strings.offset+strings.bytes<=b.length);
 for(const s of rows){
  assert.ok(s.nameOffset<strings.bytes);const start=strings.offset+s.nameOffset,end=b.indexOf(0,start);
  assert.ok(end>=start&&end<strings.offset+strings.bytes);s.name=b.toString('utf8',start,end);
  if(s.type!==8)assert.ok(s.offset+s.bytes<=b.length);
 }
 return rows;
}
function wordOffset(b,address){
 assert.equal(address%4,0);
 const matches=sections(b).filter(s=>s.type===1&&(s.flags&2)&&address>=s.address&&address+4<=s.address+s.bytes);
 assert.equal(matches.length,1,'One allocated PROGBITS word');
 return matches[0].offset+address-matches[0].address;
}
function patchLiteral(input,address,from,to){
 const offset=wordOffset(input,address);assert.equal(input.readUInt32LE(offset),from);
 assert.notEqual(from,to);const output=Buffer.from(input);output.writeUInt32LE(to,offset);
 assert.deepEqual(output.subarray(0,offset),input.subarray(0,offset));
 assert.deepEqual(output.subarray(offset+4),input.subarray(offset+4));
 return {output,offset};
}
// SDK ESP8266 v3 save() uses an 8-byte V1 header and appends a SHA256 digest.
// Inspect both XOR checksum and digest; esptool image_info only checks XOR here.
function inspectImage(b){
 assert.equal(b[0],0xe9);const count=b[1];assert.ok(count>0&&count<=16);
 let offset=8,checksum=0xef;const segments=[];
 for(let i=0;i<count;i++){
  assert.ok(offset+8<=b.length);const address=b.readUInt32LE(offset),bytes=b.readUInt32LE(offset+4);
  offset+=8;assert.equal(bytes%4,0);assert.ok(offset+bytes<=b.length);
  const data=b.subarray(offset,offset+bytes);for(const v of data)checksum^=v;
  segments.push({address,bytes,offset,sha256:hash(data)});offset+=bytes;
 }
 const checksumOffset=offset|15;assert.equal(b.length,checksumOffset+1+32);
 assert.ok(b.subarray(offset,checksumOffset).every(v=>v===0));assert.equal(b[checksumOffset],checksum);
 assert.equal(b.subarray(checksumOffset+1).toString('hex'),hash(b.subarray(0,checksumOffset+1)));
 return {header:b.subarray(0,8).toString('hex'),segments,checksumOffset,checksum,sha256:hash(b)};
}
function compareImages(a,b,literal,from,to){
 const aa=inspectImage(a),bb=inspectImage(b);assert.equal(a.length,b.length);assert.equal(aa.header,bb.header);
 assert.equal(aa.checksumOffset,bb.checksumOffset);
 assert.deepEqual(aa.segments.map(({sha256,...s})=>s),bb.segments.map(({sha256,...s})=>s));
 const matches=aa.segments.filter(s=>literal>=s.address&&literal+4<=s.address+s.bytes);
 assert.equal(matches.length,1);const offset=matches[0].offset+literal-matches[0].address;
 assert.equal(a.readUInt32LE(offset),from);assert.equal(b.readUInt32LE(offset),to);
 const changed=[];for(let i=0;i<a.length;i++)if(a[i]!==b[i]){
  assert.ok((i>=offset&&i<offset+4)||i===aa.checksumOffset||i>aa.checksumOffset,'Other app bytes changed: '+i);changed.push(i);
 }
 assert.ok(changed.length);return {literal_offset:offset,changed_offsets:changed,reference:aa,candidate:bb};
}
function generate(){
 require('./verify.cjs').verify('bands-small-div-tail-asm');
 const parentDir=path.join(root,'firmware/development',parent),manifest=read(path.join(parentDir,'manifest.json'));
 const proof=read(path.join(parentDir,'preflight.json')),source=path.join(root,'.build',parent,elfName);
 const input=fs.readFileSync(source);assert.equal(hash(input),proof.candidate.elf_sha256);
 const app=fs.readFileSync(path.join(parentDir,'app.bin'));assert.equal(hash(app),manifest.app_sha256.toLowerCase());
 assert.equal(app.length,manifest.bytes);assert.equal(manifest.diagnostic,true);assert.equal(manifest.opus_benchmark,true);
 assert.equal(manifest.opus_benchmark_output,false);assert.equal(manifest.opus_function_profile,false);
 assert.equal(manifest.opus_profile_stage,0);assert.equal(manifest.opus_division_benchmark,false);
 const nm=run(path.join(compilerBin,'xtensa-lx106-elf-nm.exe'),['-n',source]);
 const symbols=Object.fromEntries([...nm.matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 const helper=symbols.yoradio_opus_small_udiv,rom=symbols.__udivsi3;
 assert.equal(helper,proof.helper.address);assert.equal(rom,0x4000e21c);
 const calls=[];
 for(const name of ['ec_decode','ec_dec_uint']){
  const f=proof.candidate.functions[name],text=reachableDisassembly(source,f);
  assert.equal(text,f.disassembly,name+' actual linked instructions');const lines=text.split('\n');
  for(let i=0;i<lines.length-1;i++){
   const m=lines[i].match(/^\s*([0-9a-f]+):.*\bl32r\s+a0, ([0-9a-f]+) /);
   if(m&&/\bcallx0\s+a0$/.test(lines[i+1])){
    const literal=parseInt(m[2],16);if(input.readUInt32LE(wordOffset(input,literal))===helper)
     calls.push({function:name,instruction:parseInt(m[1],16),literal,asm:[lines[i],lines[i+1]]});
   }
  }
 }
 assert.equal(calls.length,3);const literals=[...new Set(calls.map(c=>c.literal))];assert.equal(literals.length,1);
 const literal=literals[0],{output:control,offset}=patchLiteral(input,literal,helper,rom);
 // All headers, symbols, segments, addresses, instructions and RAM sections
 // are byte-identical, not merely equivalent normalized instruction graphs.
 const shaSections=bytes=>sections(bytes).filter(s=>s.flags&2).map(s=>({...s,sha256:s.type===8?null:hash(bytes.subarray(s.offset,s.offset+s.bytes))}));
 const baselineSections=shaSections(input),controlSections=shaSections(control);
 assert.deepEqual(baselineSections.map(({sha256,...s})=>s),controlSections.map(({sha256,...s})=>s));
 assert.deepEqual(baselineSections.filter((s,i)=>s.sha256!==controlSections[i].sha256).map(s=>s.name),['.flash.text']);
 const images={},packagingLogs={};
 for(const [target,elf]of [['asm',input],['rom',control]]){
  fs.mkdirSync(build(target),{recursive:true});save(path.join(build(target),elfName),elf);
  const dest=path.join(build(target),'app.bin');
  packagingLogs[target]=run(python,[esptool,'--chip','esp8266','elf2image','--flash_mode','dio','--flash_freq','40m','--flash_size','4MB','--version=3','-o',dest,path.join(build(target),elfName)]);
  images[target]=fs.readFileSync(dest);inspectImage(images[target]);assert.ok(images[target].length<=0xf0000);
 }
 assert.deepEqual(images.asm,app,'Repacked unmodified ELF must reproduce saved app exactly');
 const imageProof=compareImages(images.asm,images.rom,literal,helper,rom);
 const result={schema:1,parent,parent_manifest_sha256:hash(fs.readFileSync(path.join(parentDir,'manifest.json'))),
  recipe_sha256_lf:sourceHash(__filename),esptool_sha256:hash(fs.readFileSync(esptool)),
  scope:'Frozen-layout diagnostic only. All ELF bytes identical except one aligned literal target word; no RAM or instruction changes.',
  parent_elf_sha256:hash(input),rom_elf_sha256:hash(control),elf_bytes:input.length,literal,elf_offset:offset,helper,rom,calls,
  sections:{asm:baselineSections,rom:controlSections},imageProof,static_ram_delta:0,
  packaging:{chip:'esp8266',version:3,header_mode:'dio',frequency:'40m',size:'4MB',sdk_config:'QIO40; SDK uses DIO image header then enables quad mode in bootloader',logs:packagingLogs}};
 for(const target of ['asm','rom']){
  save(path.join(art(target),'app.bin'),images[target]);
  save(path.join(art(target),'sdkconfig'),fs.readFileSync(path.join(parentDir,'sdkconfig')));
  const m={...manifest,purpose:'Frozen-layout '+target+' entropy division diagnostic; not production; no flashing by generator',
   app_sha256:hash(images[target]),bytes:images[target].length,
   post_link_division_target:target,post_link_recipe_sha256_lf:result.recipe_sha256_lf,
   post_link_parent_app_sha256:hash(app),post_link_parent_elf_sha256:hash(input),post_link_literal:literal};
  save(path.join(art(target),'manifest.json'),JSON.stringify(m,null,2)+'\n');
  save(path.join(art(target),'image-info.log'),run(python,[esptool,'--chip','esp8266','image_info',path.join(art(target),'app.bin')]));
 }
 save(path.join(art('asm'),'linked.elf.gz'),zlib.gzipSync(input,{level:9}));
 save(path.join(art('asm'),'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({passed:true,literal:'0x'+literal.toString(16),calls:3,elf_bytes_changed:input.reduce((n,v,i)=>n+(v!==control[i]),0),app_bytes:app.length,static_ram_delta:0,asm_sha256:hash(images.asm),rom_sha256:hash(images.rom)}));
 return result;
}
module.exports={parent,variant,art,build,elfName,sections,wordOffset,patchLiteral,inspectImage,compareImages,generate};
if(require.main===module)generate();

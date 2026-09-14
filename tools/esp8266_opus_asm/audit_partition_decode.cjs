// Independent linked-CFG proof; no timing inference from instruction counts.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs'),{normal}=require('./report_small_div_inline.cjs');
const {analyze}=require('./partition_decode.cjs');
const control='esp8266-opus-folding-control-v1',candidate='esp8266-opus-partition-decode-v1';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function program(graph){
 const labels={};const ops=graph.map((text,i)=>{labels['instruction:'+i]=i;const [op,...tail]=text.split(/\s+/);return {op,args:tail.join(' ').split(/,\s*/),row:i,text};});
 return {ops,labels};
}
function project(graph){
 const p=program(graph),proof=analyze(p),branches=new Map(proof.branches.map(b=>[b.index,b]));
 const dead=new Set(proof.dead.map(d=>d.index));
 const kept=[];
 for(const [i,text]of graph.entries()){
  if(dead.has(i))continue;
  const b=branches.get(i);if(b&&!b.taken)continue;
  kept.push({i,text:b?'j instruction:'+b.target:text});
 }
 // Remove J-to-next only, resolving any already empty branch row. This is a
 // semantic canonicalization, not a claim that emitted jump cycles are free.
 const next=i=>{const v=kept.find(k=>k.i>=i);assert.ok(v);return v.i;};
 const drop=new Set();for(let j=0;j<kept.length-1;j++){
  const m=kept[j].text.match(/^j instruction:(\d+)$/);if(m&&next(+m[1])===kept[j+1].i)drop.add(kept[j].i);
 }
 const live=kept.filter(k=>!drop.has(k.i)),lookup=new Map(live.map((k,i)=>[k.i,i]));
 const resolve=i=>{const v=live.find(k=>k.i>=i);assert.ok(v);return lookup.get(v.i);};
 return {graph:live.map(k=>k.text.replace(/instruction:(\d+)/g,(_,i)=>'instruction:'+resolve(+i))),branches:proof.branches,dead:proof.dead.length};
}
function audit(){
 require('./verify.cjs').verify('bands-partition-decode-asm');
 const dir=path.join(root,'firmware/development',candidate),names=['quant_partition','quant_band','quant_all_bands','ec_tell_frac','ec_dec_uint','celt_decode_with_ec_dred'];
 const [a,b]=[control,candidate].map(v=>inspect(v,names));
 for(const [s,n]of Object.entries(a.sections))if(!s.startsWith('.flash.'))assert.equal(b.sections[s],n,s);
 const x=project(normal(a.functions.quant_partition.graph)),y=project(normal(b.functions.quant_partition.graph));
 assert.equal(x.branches.length,3);assert.equal(y.branches.length,0);assert.deepEqual(y.graph,x.graph,'Actual decoder CFG/operands/calls');
 for(const n of names.filter(n=>n!=='quant_partition'))assert.deepEqual(normal(b.functions[n].graph),normal(a.functions[n].graph),n);
 const decoder=normal(b.functions.celt_decode_with_ec_dred.graph),calls=decoder.flatMap((s,i)=>s==='call0 quant_all_bands'?[i]:[]);
 assert.equal(calls.length,1);
 const index=calls[0];let previous=index-1,needed='a2';
 for(;previous>=0;previous--){
  const s=decoder[previous];assert.doesNotMatch(s,/^(?:b|j |ret |call0 )/,'Argument trace crosses control flow');
  if(new RegExp('^mov '+needed+', a[0-9]+$').test(s)){needed=s.split(', ')[1];continue;}
  if(new RegExp('^(?!s(?:8|16|32)i )\\S+ '+needed+',').test(s)){assert.equal(s,'movi '+needed+', 0','encode=0 actual argument');break;}
 }
 assert.ok(previous>=0);
 // No branch can enter after the dominating write and skip the zero argument.
 for(const s of decoder)for(const m of s.matchAll(/instruction:(\d+)/g))assert.ok(+m[1]<=previous||+m[1]>index,'Branch bypasses encode initializer');
 const map=fs.readFileSync(path.join(root,'.build',candidate,'yoradio_esp8266_helix_native.map'),'utf8');
 const cross=map.match(/^quant_all_bands\s+[^\r\n]+\r?\n(?:[ \t]+[^\r\n]+\r?\n)*/m)?.[0];assert.ok(cross);
 assert.deepEqual(cross.trim().split(/\r?\n/).map(l=>l.trim().split(/\s+/).at(-1)),['esp-idf/opus_decoder/libopus_decoder.a(bands.c.obj)','esp-idf/opus_decoder/libopus_decoder.a(celt_decoder.c.obj)']);
 const bands=fs.readFileSync(path.join(component,'upstream/celt/bands.c'),'utf8');
 assert.deepEqual([...bands.matchAll(/ctx(?:\.|->)encode\s*=(?!=)[^;]*;/g)].map(m=>m[0]),['ctx.encode = encode;']);
 assert.deepEqual([...bands.matchAll(/ctx\s*=\s*ctx_save\d*;/g)].map(m=>m[0]),['ctx = ctx_save;','ctx = ctx_save2;']);
 const recipe=read(path.join(component,'asm/lx106/bands-partition-decode.json'));
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),app=fs.readFileSync(path.join(d,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());return m;});
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_partition_decode_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set(manifests.flatMap(m=>Object.keys(m))))if(!identity.includes(k))assert.deepEqual(manifests[0][k]??null,manifests[1][k]??null,k);
 assert.equal(manifests[1].opus_bands_partition_decode_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(component,'asm/lx106/bands-partition-decode.json'))));
 const host=read(path.join(root,'.build/opus-bands-partition-decode/correctness.json'));assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,recipe.recipe_sha256_lf);assert.ok(host.cases.some(c=>c.name==='stereo-510'));
 const result={passed:true,checker_sha256_lf:sourceHash(__filename),recipe,manifests,static_ram_delta:0,reference:a,candidate:b,projected:{control:x,candidate:y},call_chain:{cross_reference:cross,decoder_argument_instructions:decoder.slice(previous,index+1),encode_assignment:'ctx.encode = encode;',copies:['ctx_save','ctx_save2'],scope:'Pinned source: ctx only passed to private bands helpers; copies preserve encode, recursive partition calls reuse ctx; valid decoder calls, not an encoder API'},host};
 fs.writeFileSync(path.join(dir,'preflight.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:true,removed_source_instructions:recipe.proof.removed_instructions,removed_linked_instructions:x.dead,bytes:manifests[1].bytes,delta:manifests[1].bytes-manifests[0].bytes,ram_delta:0,partition_bytes:[a.functions.quant_partition.bytes,b.functions.quant_partition.bytes]}));return result;
}
module.exports={program,project,audit,control,candidate};if(require.main===module)audit();

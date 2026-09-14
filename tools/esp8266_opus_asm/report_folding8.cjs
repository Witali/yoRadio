const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash,run}=require('./export.cjs');
const {inspect,linkedGraph}=require('./report_layout.cjs'),{wordAt}=require('./audit_update_link.cjs');
const {collapse,normal}=require('./report_small_div_inline.cjs'),{archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const {validateRun}=require('./report_small_div_tail.cjs');
const control='esp8266-opus-folding-control-v1',candidate='esp8266-opus-folding8-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-folding8-board');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function compileModel(graph,table){
 const ops=graph.map(s=>{const i=s.indexOf(' ');return [s.slice(0,i),...s.slice(i+1).split(/,\s*/)];});
 for(const [op,...args]of ops){assert.ok(['movi','bltu','extui','bnez','srli','l32r','addx4','l32i','j','call0','ret','mov'].includes(op));for(const a of args)if(a.startsWith('instruction:'))assert.ok(+a.slice(12)>=0&&+a.slice(12)<ops.length);}
 return (N,initial)=>{
  const r=Uint32Array.from(initial);r[14]=N;r[2]=(N<<22)>>>0;
  let pc=0,count=0;const reg=s=>+s.slice(1),value=s=>s.startsWith('a')?r[reg(s)]:Number(s),target=s=>+s.slice(12);
  while(count++<24){assert.ok(ops[pc]);const [op,a,b,c,e]=ops[pc++],dst=reg(a);switch(op){
   case 'movi':r[dst]=Number(b);break;case 'mov':r[dst]=value(b);break;
   case 'bltu':if(value(a)<value(b))pc=target(c);break;
   case 'bnez':if(value(a)!==0)pc=target(b);break;
   case 'extui':assert.equal(c,'0');assert.equal(e,'3');r[dst]=value(b)&7;break;
   case 'srli':assert.equal(c,'3');r[dst]=value(b)>>>3;break;
   case 'l32r':assert.equal(b,'literal:yoradio_opus_folding8_table');r[dst]=0x40200000;break;
   case 'addx4':r[dst]=value(b)*4+value(c);break;
   case 'l32i':{const address=value(b)+Number(c);assert.equal(address%4,0);const i=(address-0x40200000)/4;assert.ok(i>=0&&i<table.length);r[dst]=table[i];break;}
   case 'j':pc=target(a);break;
   case 'call0':assert.equal(a,'celt_sqrt');return {fallback:true,registers:r,count};
   case 'ret':return {fallback:false,registers:r,result:r[2],count};
  }}throw Error('Non-terminating folding graph');
 };
}
function modelCheck(graph,table){
 const exec=compileModel(graph,table);let seed=0x18813527,cases=0,fast=0;
 const rand=()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return seed>>>0;};
 const check=N=>{const initial=Array.from({length:16},rand);initial[14]=N>>>0;const out=exec(N,initial),expected=(N>>>0)<=176&&!(N&7);
  assert.equal(out.fallback,!expected);if(expected){assert.equal(out.result,table[N>>>3]);fast++;}else assert.equal(out.registers[2],(N<<22)>>>0);
  for(const k of [0,1,5,6,7,8,9,10,11,12,13,14,15])assert.equal(out.registers[k],initial[k]);cases++;
 };
 for(let N=-4096;N<=4096;N++)check(N);for(let i=0;i<100000;i++)check(rand());
 return {passed:true,cases,fast,scope:'Actual linked instruction semantics, bounds and ABI; fallback preserves original shifted input; not hardware timing'};
}
function preflight(){
 require('./verify.cjs').verify('bands-folding8-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),b=fs.readFileSync(path.join(d,'app.bin'));assert.equal(b.length,m.bytes);assert.equal(hash(b),m.app_sha256.toLowerCase());assert.ok(b.length<=0xf0000);return m;});
 const [ma,mb]=manifests;assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-folding8-asm');
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_folding8_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,k);
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_division_benchmark,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);}
 const recipeFile=path.join(component,'asm/lx106/bands-folding8.json'),recipe=read(recipeFile);assert.equal(mb.opus_bands_folding8_manifest_sha256.toLowerCase(),hash(fs.readFileSync(recipeFile)));
 const names=['quant_band','quant_partition','quant_all_bands','celt_sqrt','celt_cos_norm','ec_decode','ec_dec_uint','ec_dec_update','decode_pulses','clt_mdct_backward_c'];
 const a=inspect(control,names),b=inspect(candidate,names),old=inspect('esp8266-opus-inline-control-v1',names);
 for(const [s,n]of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],n,s);
 const elf=path.join(root,'.build',candidate,'yoradio_esp8266_helix_native.elf');
 const symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',elf]).matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 const sized=[...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',elf]).matchAll(/^([0-9a-f]+)\s+([0-9a-f]+)\s+\S\s+(.+)$/gm)].map(m=>({address:parseInt(m[1],16),bytes:parseInt(m[2],16),name:m[3]}));
 const resolve=address=>{const exact=sized.filter(s=>s.address===address).sort((x,y)=>x.name.localeCompare(y.name));if(exact.length)return exact[0].name;
  const inside=sized.filter(s=>address>s.address&&address<s.address+s.bytes).sort((x,y)=>x.bytes-y.bytes||x.name.localeCompare(y.name));return inside.length?inside[0].name+'+0x'+(address-inside[0].address).toString(16):'0x'+address.toString(16);
 };
 const graph=text=>linkedGraph(text,n=>wordAt(elf,n),resolve).graph,region={start:symbols.y_fold8_begin,end:symbols.y_fold8_end};assert.ok(region.end>region.start);
 const rows=b.functions.quant_band.disassembly.split('\n'),inside=rows.filter(line=>{const m=line.match(/^\s*([0-9a-f]+):/);return m&&parseInt(m[1],16)>=region.start&&parseInt(m[1],16)<region.end;});
 const dis=inside.join('\n')+'\n'+region.end.toString(16)+': f00d ret.n',g=normal(graph(dis));
 const table=sized.find(s=>s.name==='yoradio_opus_folding8_table');assert.equal(table.bytes,92);assert.equal(table.address%4,0);assert.ok(table.address>=0x40200000);
 const values=require('./folding8.cjs').coefficients();for(const [i,v]of values.entries())assert.equal(wordAt(elf,table.address+4*i),v);
 const model=modelCheck(g,values);
 const collapsed=collapse(b.functions.quant_band.disassembly,[region]).replace(region.start.toString(16)+': 000005 call0 4000e21c <__udivsi3>',region.start.toString(16)+': 000005 call0 '+symbols.celt_sqrt.toString(16)+' <celt_sqrt>');
 for(const n of names){assert.deepEqual(normal(a.functions[n].graph),normal(old.functions[n].graph),n+' control');assert.deepEqual(normal(n==='quant_band'?graph(collapsed):b.functions[n].graph),normal(a.functions[n].graph),n+' candidate');}
 const host=read(path.join(root,'.build/opus-bands-folding8/correctness.json'));assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,recipe.recipe_sha256_lf);assert.ok(host.cases.some(c=>c.name==='stereo-510'));
 const result={passed:true,checker_sha256_lf:sourceHash(__filename),manifests,recipe,static_ram_delta:0,control:a,candidate:b,expansion:{...region,bytes:region.end-region.start,graph:g,disassembly:dis},table,model,host,scope:'Exact linked folding8 body and original caller CFG, fixed-point coefficients and no RAM/stack growth; physical speed separately measured'};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({passed:true,bytes:mb.bytes,delta:mb.bytes-ma.bytes,table_bytes:table.bytes,model}));return result;
}
function report(){
 const proof=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const [name,list]of [['before',a],['candidate',b],['after',a2]]){const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);assert.equal(ota.sha256,proof.manifests[name==='candidate'?1:0].app_sha256.toLowerCase());for(const r of list)validateRun(r.report,fixtures,ota.after.app_address);fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));}
 const initial=compare(a.map(r=>r.report),b.map(r=>r.report)),repeated=compare(a2.map(r=>r.report),b.map(r=>r.report));
 const result={proof,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:{before:a.map(({report,...r})=>r),candidate:b.map(({report,...r})=>r),after:a2.map(({report,...r})=>r)},scope:'All30 physical raw A/B/A attempts retained; not live qualification'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));console.log(JSON.stringify(result.selection));return result;
}
module.exports={compileModel,modelCheck,preflight,report,control,candidate,experiment};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}

// Three exact inline divisions, compared with the unchanged tell-inline base.
// Prove linked expansions, collapse only those regions back to original calls,
// and retain every physical A/B/A observation. No claim about cache misses.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash,run}=require('./export.cjs');
const {inspect,linkedGraph}=require('./report_layout.cjs'),{wordAt}=require('./audit_update_link.cjs');
const {normalizeBranches}=require('./pvq_addx.cjs'),{withoutIdentityMoves}=require('./audit_entropy_relaxation.cjs');
const {archive}=require('./report_bands.cjs'),{validateRun}=require('./report_small_div_tail.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const control='esp8266-opus-inline-control-v1',candidate='esp8266-opus-small-div-inline-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-small-div-inline-board');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
const normal=g=>normalizeBranches(withoutIdentityMoves(g)).graph;
function rows(text){return text.split(/\r?\n/).filter(Boolean).map(line=>{
 const m=line.match(/^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*$/);assert.ok(m,line);
 return {line,address:parseInt(m[1],16),op:m[3],args:m[4]};
});}
function collapse(text,regions){
 const input=rows(text),out=[];
 for(const r of input){
  const inside=regions.find(s=>r.address>=s.start&&r.address<s.end);
  if(inside){if(r.address===inside.start)out.push(r.address.toString(16)+': 000005 call0 4000e21c <__udivsi3>');continue;}
  if(/^b|^j$/.test(r.op)){
   const t=r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);assert.ok(t);
   const address=parseInt(t[1],16);
   assert.ok(!regions.some(s=>address>s.start&&address<s.end),'External branch into inline body');
  }out.push(r.line);
 }
 for(const s of regions)assert.ok(input.some(r=>r.address===s.start)&&input.some(r=>r.address===s.end),'Inline boundary missing');
 return out.join('\n');
}
function preflight(){
 require('./verify.cjs').verify('bands-small-div-inline-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),b=fs.readFileSync(path.join(d,'app.bin'));assert.equal(b.length,m.bytes);assert.equal(hash(b),m.app_sha256.toLowerCase());assert.ok(b.length<=0xf0000);return m;});
 const [ma,mb]=manifests;
 assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-small-div-inline-asm');
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_small_div_inline_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,k);
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_division_benchmark,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);}
 const recipeFile=path.join(component,'asm/lx106/bands-small-div-inline.json'),recipe=read(recipeFile);
 assert.equal(mb.opus_bands_small_div_inline_manifest_sha256.toLowerCase(),hash(fs.readFileSync(recipeFile)));
 const names=['ec_decode','ec_dec_uint','ec_decode_bin','ec_dec_update','ec_dec_bit_logp','quant_partition','quant_all_bands','decode_pulses','celt_cos_norm','clt_mdct_backward_c'];
 const a=inspect(control,names),b=inspect(candidate,names),old=inspect('esp8266-opus-entropy-control-v1',names);
 for(const [s,n]of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],n,s);
 const elf=path.join(root,'.build',candidate,'yoradio_esp8266_helix_native.elf');
 const symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',elf]).matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 assert.equal(symbols.__udivsi3,0x4000e21c);
 const sized=[...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',elf]).matchAll(/^([0-9a-f]+)\s+([0-9a-f]+)\s+\S\s+(.+)$/gm)].map(m=>({address:parseInt(m[1],16),bytes:parseInt(m[2],16),name:m[3]}));
 const resolve=address=>{const exact=sized.filter(s=>s.address===address).sort((x,y)=>x.name.localeCompare(y.name));if(exact.length)return exact[0].name;
  const inside=sized.filter(s=>address>s.address&&address<s.address+s.bytes).sort((x,y)=>x.bytes-y.bytes||x.name.localeCompare(y.name));
  return inside.length?inside[0].name+'+0x'+(address-inside[0].address).toString(16):'0x'+address.toString(16);
 };
 const graph=text=>linkedGraph(text,n=>wordAt(elf,n),resolve).graph;
 const regions=[0,1,2].map(i=>({id:i,function:i?'ec_dec_uint':'ec_decode',start:symbols['y_div_inline_'+i+'_begin'],end:symbols['y_div_inline_'+i+'_end']}));
 const expansions=[];
 for(const r of regions){
  assert.ok(r.end>r.start);const full=rows(b.functions[r.function].disassembly),body=full.filter(x=>x.address>=r.start&&x.address<r.end);
  assert.equal(body[0].address,r.start);assert.ok(full.some(x=>x.address===r.end));
  // End marker is the original next caller instruction, not an actual RET.
  // A synthetic RET represents the inline block's fall-through exit only.
  const dis=body.map(x=>x.line).join('\n')+'\n'+r.end.toString(16)+': f00d ret.n';
  const g=normal(graph(dis));assert.equal(g.filter(x=>x==='call0 0x4000e21c').length,1);
  assert.equal(g.filter(x=>x.startsWith('mul16u ')).length,4);
  assert.ok(!g.some(x=>/^s(?:8|16|32)i|^callx|^jx/.test(x)));
  if(expansions.length)assert.deepEqual(g,expansions[0].graph,'All three actual expansions');
  expansions.push({...r,bytes:r.end-r.start,graph:g,disassembly:dis});
 }
 const model=require('./inline_div_model.cjs').validate(expansions[0].graph);
 for(const n of names){
  assert.deepEqual(normal(a.functions[n].graph),normal(old.functions[n].graph),n+' control');
  const own=regions.filter(s=>s.function===n);
  const restored=own.length?graph(collapse(b.functions[n].disassembly,own)):b.functions[n].graph;
  assert.deepEqual(normal(restored),normal(a.functions[n].graph),n+' collapsed caller');
 }
 const table=sized.find(s=>s.name==='yoradio_opus_small_div_table');assert.equal(table.bytes,516);assert.equal(table.address%4,0);assert.ok(table.address>=0x40200000);
 for(const [i,v]of require('./small_div.cjs').table.entries())assert.equal(wordAt(elf,table.address+4*i),v);
 const host=read(path.join(root,'.build/opus-bands-small-div/correctness.json'));assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,recipe.small_recipe_sha256_lf);
 assert.ok(host.cases.some(c=>c.name==='stereo-510'));assert.ok(host.cases.some(c=>c.name==='stereo-320-20ms'));
 const result={passed:true,manifests,recipe,checker_sha256_lf:sourceHash(__filename),model_sha256_lf:sourceHash(path.join(__dirname,'inline_div_model.cjs')),
  static_ram_delta:0,changed_calls:3,control:a,candidate:b,expansions,model,table,host,
  scope:'Actual linked inline arithmetic and restored caller CFG/stack exact; unchanged semantic host mirror through 510 kbps. Physical speed still required.'};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({passed:true,bytes:mb.bytes,static_ram_delta:0,model,expansions:expansions.map(({graph,disassembly,...r})=>r)}));return result;
}
function report(){
 const proof=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),
 b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const [name,list]of [['before',a],['candidate',b],['after',a2]]){
  const ota=read(path.join(experiment,'ota-'+name+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,proof.manifests[name==='candidate'?1:0].app_sha256.toLowerCase());
  for(const r of list)validateRun(r.report,fixtures,ota.after.app_address);
  fs.copyFileSync(path.join(experiment,'ota-'+name+'.json'),path.join(dest,'ota-'+name+'.json'));
 }
 const initial=compare(a.map(r=>r.report),b.map(r=>r.report)),repeated=compare(a2.map(r=>r.report),b.map(r=>r.report));
 const result={proof,initial,repeated,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},
  inputs:{before:a.map(({report,...r})=>r),candidate:b.map(({report,...r})=>r),after:a2.map(({report,...r})=>r)},
  scope:'30 physical raw A/B/A attempts, all retained; not live qualification'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,report,collapse,normal,control,candidate,experiment};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}

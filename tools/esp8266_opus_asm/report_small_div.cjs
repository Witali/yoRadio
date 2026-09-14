// Matched best-parent A/B/A; all runs remain part of the report.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash,run}=require('./export.cjs');
const {inspect,linkedGraph}=require('./report_layout.cjs'),{archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs'),{selectHighBitrate}=require('./selection.cjs');
const recipe=require('./small_div.cjs');
const control='esp8266-opus-bands-tell-inline-v1',candidate='esp8266-opus-bands-small-div-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-small-div-board');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function preflight(){
 require('./verify.cjs').verify('bands-small-div-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),app=fs.readFileSync(path.join(d,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());return m;});
 const [ma,mb]=manifests;assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-small-div-asm');
 for(const m of manifests){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_bands_text_literals??false,false);}
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_small_div_manifest_sha256','built_utc','source_revision','app_sha256','bytes','opus_bands_text_literals'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile changed: '+k);
 const rm=read(path.join(component,'asm/lx106/bands-small-div.json'));
 assert.equal(mb.opus_bands_small_div_manifest_sha256.toLowerCase(),hash(fs.readFileSync(path.join(component,'asm/lx106/bands-small-div.json'))));
 assert.equal(rm.parent_sha256_lf,ma.opus_bands_tell_inline_manifest_sha256.toLowerCase());
 const names=['ec_decode','ec_dec_uint','ec_decode_bin','ec_dec_update','quant_partition','quant_all_bands','clt_mdct_backward_c'];
 const a=inspect(control,names),b=inspect(candidate,names);
 for(const [section,bytes]of Object.entries(a.sections).filter(([section])=>!section.startsWith('.flash.')))assert.equal(b.sections[section],bytes,'Static RAM changed: '+section);
 const originalDivide=a.functions.ec_decode.graph.filter(v=>v.startsWith('call0 '));assert.equal(originalDivide.length,2);assert.equal(originalDivide[0],originalDivide[1]);
 let calls=0;
 for(const n of names){
  const restored=b.functions[n].graph.map(v=>{if(v==='call0 yoradio_opus_small_udiv'){calls++;return originalDivide[0];}return v;});
  assert.deepEqual(restored,a.functions[n].graph,'Unexpected linked code change: '+n);
 }
 assert.equal(calls,3);
 const elf=path.join(root,'.build',candidate,'yoradio_esp8266_helix_native.elf');
 const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
 const symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',elf]).matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 const helperStart=symbols.yoradio_opus_small_udiv,helperBytes=rm.files[2].sections_after['.text.yoradio_opus_small_udiv'];
 assert.equal(helperBytes,114);
 const dis=require('./small_div_link.cjs').helperDisassembly(helperStart,helperStart+helperBytes,(start,end)=>run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+start.toString(16),'--stop-address=0x'+end.toString(16),elf]));
 const {wordAt}=require('./audit_update_link.cjs');
 const resolve=n=>n===symbols.yoradio_opus_small_div_table?'yoradio_opus_small_div_table':n===symbols.__udivsi3?'__udivsi3':'0x'+n.toString(16);
 const graph=linkedGraph(dis,n=>wordAt(elf,n),resolve).graph;
 const labels=new Map(),expected=[];let active=false;
 for(const line of recipe.helper.split('\n')){
  const t=line.split('#')[0].trim();if(t==='yoradio_opus_small_udiv:')active=true;
  if(active&&t.startsWith('.size '))break;if(!active||!t)continue;
  if(t.endsWith(':'))labels.set(t.slice(0,-1),expected.length);
  else if(!t.startsWith('.'))expected.push(t);
 }
 const normalized=expected.map(t=>{
  let [op,...rest]=t.split(/\s+/);op=op.replace(/\.n$/,'');const args=rest.join('').split(',');
  if(op==='srli'&&args[2]==='16'){op='extui';args[2]='16';args[3]='16';}
  if(op==='l32r')args[1]='literal:'+(args[1]==='.Ly_small_table'?'yoradio_opus_small_div_table':'__udivsi3');
  if(op==='movi'&&args[1]==='256')args[1]='0x100';
  if(op.startsWith('b'))args[args.length-1]='instruction:'+labels.get(args.at(-1));
  return op+' '+args.join(', ');
 });
 assert.deepEqual(graph,normalized,'Helper machine code differs from instruction model');
 assert.equal(symbols.yoradio_opus_small_div_table%4,0);
 assert.ok(symbols.yoradio_opus_small_div_table>=0x40200000&&symbols.yoradio_opus_small_div_table<0x40300000,'Table must be in flash');
 for(const [i,v]of recipe.table.entries())assert.equal(wordAt(elf,symbols.yoradio_opus_small_div_table+4*i),v);
 const host=read(path.join(root,'.build/opus-bands-small-div/correctness.json'));
 assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,rm.recipe_sha256_lf);
 const result={schema:1,manifests,recipe:rm,reference:a,candidate:b,changed_calls:calls,static_ram_delta:0,host,
  helper:{address:helperStart,bytes:helperBytes,graph,disassembly:dis,table_address:symbols.yoradio_opus_small_div_table,table_bytes:516,original_divide_address:symbols.__udivsi3}};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({bytes:mb.bytes,static_ram_delta:0,changed_calls:calls,helper_bytes:helperBytes,table_bytes:516,exact_linked_graph:true,sections:{A:a.sections,B:b.sections}}));return result;
}
function report(){
 const build=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 for(const [stage,rows]of [['before',a],['candidate',b],['after',a2]]){
  const ota=read(path.join(experiment,'ota-'+stage+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,build.manifests[stage==='candidate'?1:0].app_sha256.toLowerCase());
  for(const r of rows){assert.equal(r.report.before.data.app_address,ota.after.app_address);assert.equal(r.report.after.data.app_address,ota.after.app_address);}
 }
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const r of [...a,...b,...a2]){assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);for(const [i,v]of r.report.final.results.entries()){assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);}}
 const initial=compare(a.map(x=>x.report),b.map(x=>x.report)),repeated=compare(a2.map(x=>x.report),b.map(x=>x.report));
 const host=read(path.join(root,'.build/opus-bands-small-div/correctness.json'));assert.equal(host.passed,true);assert.ok(host.cases.some(c=>c.name==='stereo-510'));assert.ok(host.cases.some(c=>c.name==='stereo-320-20ms'));
 const fixtureHash=sourceHash(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));for(const m of build.manifests)assert.equal(m.opus_benchmark_manifest_sha256.toLowerCase(),fixtureHash);
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,build,initial,repeated,host_pcm:host,host_scope:'Exact small-div C semantic mirror plus tell-inline; actual helper checked by instruction interpreter and linked graph/table proof.',selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:{before:compact(a),candidate:compact(b),after:compact(a2)},scope:'30 physical A/B/A attempts; raw RAM packets through192, no output/profiler. No discarded runs; not live qualification.'};
 for(const f of ['initial-snapshot.json','ota-before.json','ota-candidate.json','ota-after.json'])fs.copyFileSync(path.join(experiment,f),path.join(dest,f));
 for(const f of ['build.log','build-second.log','build-final.log','host.log','regression.log','regression-initial-table.log'])fs.copyFileSync(path.join(root,'.build/opus-bands-small-div',f),path.join(dest,f));
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={preflight,report};if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}

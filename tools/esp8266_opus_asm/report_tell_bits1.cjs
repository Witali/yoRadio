// Strict best-control / bits1 / repeated-control report. No discarded runs.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash,run}=require('./export.cjs');
const {archive}=require('./report_bands.cjs'),{compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const av='esp8266-opus-bands-tell-inline-v1',bv='esp8266-opus-bands-tell-bits1-v1';
const aa=path.join(root,'firmware/development',av),art=path.join(root,'firmware/development',bv);
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function preflight(){
 const ma=read(path.join(aa,'manifest.json')),mb=read(path.join(art,'manifest.json'));
 for(const [dir,m] of [[aa,ma],[art,mb]]){
  const app=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);
 }
 assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-tell-bits1-asm');
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_tell_bits1_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile changed: '+k);
 const recipe=path.join(component,'asm/lx106/bands-tell-bits1.json'),rm=read(recipe);
 assert.equal(mb.opus_bands_tell_bits1_manifest_sha256.toLowerCase(),hash(fs.readFileSync(recipe)));
 assert.equal(rm.parent_sha256_lf,ma.opus_bands_tell_inline_manifest_sha256.toLowerCase());
 require('./verify.cjs').verify('bands-tell-bits1-asm');
 const inspect=variant=>{
  const elf=path.join(root,'.build',variant,'yoradio_esp8266_helix_native.elf');
  const sections=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-size.exe'),['-A',elf]).matchAll(/^(\.(?:iram0|dram0|flash)\.\S+)\s+(\d+)\s+/gm)].map(m=>[m[1],Number(m[2])]));
  const symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',elf]).matchAll(/^([0-9a-f]+)\s+([0-9a-f]+)\s+\S\s+(ec_tell_frac|ec_dec_bits|quant_partition|quant_all_bands|quant_band|correction\$2307|y_opus_tell_correction)$/gm)]
   .map(m=>[m[3],{address:'0x'+m[1],bytes:parseInt(m[2],16)}]));
  assert.deepEqual(symbols.y_opus_tell_correction,symbols['correction$2307']);assert.equal(symbols.y_opus_tell_correction.bytes,32);
  const code={};for(const name of ['quant_partition','quant_band','quant_all_bands']){
   const s=symbols[name],stop=parseInt(s.address,16)+s.bytes;
   code[name]=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address='+s.address,'--stop-address=0x'+stop.toString(16),elf]);
  }
  const fastPaths=[];
  if(variant===bv)for(const [name,body] of Object.entries(code)){
   const lines=body.split(/\r?\n/);
   for(let i=0;i<lines.length;i++)if(/l32i\.n\s+a4,\s*a2,\s*16$/.test(lines[i])){
    const jump=lines[i+1]?.match(/beqz\.n\s+a4,\s*([0-9a-f]+)/);if(!jump)continue;
    assert.match(lines.slice(i,i+12).join('\n'),/extui\s+a2,\s*a5,\s*0,\s*1/);
    // Decode from the actual branch target: linear objdump can lose sync
    // on unreachable alignment padding immediately before a cold CALL0.
    const cold=run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+jump[1],'--stop-address=0x'+(parseInt(jump[1],16)+3).toString(16),elf]);
    assert.match(cold,new RegExp('call0\\s+'+symbols.ec_dec_bits.address.slice(2)+'\\s+<ec_dec_bits>'));
    fastPaths.push({function:name,code:lines.slice(i,i+12).join('\n'),cold_address:'0x'+jump[1],cold_disassembly:cold});
   }
  }
  if(variant===bv)assert.equal(fastPaths.length,3);
  return {elf_sha256:hash(fs.readFileSync(elf)),sections,symbols,hot_disassembly:code,fast_paths:fastPaths};
 };
 const a=inspect(av),b=inspect(bv);assert.ok(Object.keys(a.sections).length>=5);
 for(const [s,n] of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],n,'Static RAM changed: '+s);
 for(const name of ['ec_tell_frac','ec_dec_bits'])assert.equal(a.symbols[name].bytes,b.symbols[name].bytes,'Shared function size changed');
 const result={reference_manifest:ma,candidate_manifest:mb,recipe:rm,reference:a,candidate:b,static_ram_delta:0};
 fs.writeFileSync(path.join(art,'preflight.json'),JSON.stringify(result,null,2)+'\n');return result;
}
function report(){
 const build=preflight(),controls=path.join(art,'controls');
 const a=archive(path.join(root,'.build/opus-tell-bits1-control-20260913'),path.join(controls,'before'));
 const b=archive(path.join(root,'.build/opus-bands-tell-bits1-20260913'),path.join(art,'runs'));
 const a2=archive(path.join(root,'.build/opus-tell-bits1-control-repeat-20260913'),path.join(controls,'after'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const r of [...a,...b,...a2]){
  assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);
  for(const [i,v] of r.report.final.results.entries()){
   assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);
   assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);
  }
 }
 const initial=compare(a.map(v=>v.report),b.map(v=>v.report)),repeated=compare(a2.map(v=>v.report),b.map(v=>v.report));
 const host=read(path.join(root,'.build/opus-bands-tell-bits1/correctness.json'));
 assert.equal(host.passed,true);assert.equal(host.recipe_sha256_lf,build.recipe.recipe_sha256_lf);
 const selection={initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)};
 const absolute=cases=>cases.map(c=>({name:c.name,delta_us_per_20ms_audio:200*(c.candidate.task_budget_percent.median-c.reference.task_budget_percent.median)}));
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,initial,repeated,absolute:{initial:absolute(initial.cases),repeated:absolute(repeated.cases)},build,host,selection,
  inputs:{reference:compact(a),candidate:compact(b),repeated:compact(a2)},scope:'Ten A, ten B, ten repeated A. Best tell-inline control. Raw only, no live qualification.'};
 fs.writeFileSync(path.join(art,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(selection,null,2));return result;
}
module.exports={preflight,report};if(require.main===module){if(process.argv.includes('--preflight')){const r=preflight();console.log(JSON.stringify({static_ram_delta:r.static_ram_delta,symbols:{a:r.reference.symbols,b:r.candidate.symbols},sections:{a:r.reference.sections,b:r.candidate.sections}},null,2));}else report();}

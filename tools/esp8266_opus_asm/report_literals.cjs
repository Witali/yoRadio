// Placement-only experiment: pinned bands ASM assembled with text literals.
// No instruction timing model: validate final ELF, then retain all board runs.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,hash,run}=require('./export.cjs');
const {inspect}=require('./report_layout.cjs');
const {archive}=require('./report_bands.cjs');
const {compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs');
const control='esp8266-opus-bands-tell-inline-v1',candidate='esp8266-opus-bands-literals-v1';
const dest=path.join(root,'firmware/development',candidate),experiment=path.join(root,'.build/opus-literals-20260913');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function profiles(a,b){
 assert.equal(a.opus_backend,'bands-tell-inline-asm');assert.equal(b.opus_backend,a.opus_backend);
 assert.equal(a.opus_bands_text_literals??false,false);assert.equal(b.opus_bands_text_literals,true);
 for(const m of [a,b]){assert.equal(m.diagnostic,true);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);}
 const allowed=['opus_bands_text_literals','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(a),...Object.keys(b)]))if(!allowed.includes(k))assert.deepEqual(b[k]??null,a[k]??null,'Build profile changed: '+k);
}
function checkCommands(commands){
 const matches=commands.filter(v=>v.command.includes('--text-section-literals'));
 assert.equal(matches.length,1,'Flag must affect exactly one translation unit');
 assert.match(matches[0].file.replaceAll('\\','/'),/\/bands-tell-inline\/upstream\/celt\/bands\.c\.s$/);
 return matches[0];
}
function literalSites(fn){
 return [...fn.disassembly.matchAll(/^\s*([0-9a-f]+):\s+[0-9a-f]+\s+l32r\s+(a\d+),\s*([0-9a-f]+)/gm)].map(m=>({pc:parseInt(m[1],16),register:m[2],pool:parseInt(m[3],16),distance:parseInt(m[1],16)-parseInt(m[3],16)}));
}
function preflight(){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const manifests=[control,candidate].map(v=>{const d=path.join(root,'firmware/development',v),m=read(path.join(d,'manifest.json')),app=fs.readFileSync(path.join(d,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());return m;});
 profiles(...manifests);
 const command=checkCommands(read(path.join(root,'.build',candidate,'compile_commands.json')));
 const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
 const obj=path.join(root,'.build',candidate,'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/asm/lx106/bands-tell-inline/upstream/celt/bands.c.obj');
 // All surviving bands functions, not just the three headline hot functions.
 const all=run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',path.join(root,'.build',control,'yoradio_esp8266_helix_native.elf')]);
 const names=[...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',obj]).matchAll(/^[0-9a-f]+\s+[0-9a-f]+\s+[Tt]\s+(\S+)$/gm)].map(m=>m[1]).filter(n=>new RegExp('\\s'+n.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+'$','m').test(all));
 assert.ok(names.includes('quant_all_bands'));names.push('ec_tell_frac','ec_dec_bits');
 const a=inspect(control,names),b=inspect(candidate,names);
 for(const [s,bytes] of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],bytes,'Static RAM changed: '+s);
 for(const name of names){assert.deepEqual(b.functions[name].graph,a.functions[name].graph,'Linked graph changed: '+name);for(const f of [a.functions[name],b.functions[name]])f.literal_sites=literalSites(f);}
 const changed=names.filter(n=>JSON.stringify(a.functions[n].literal_sites)!==JSON.stringify(b.functions[n].literal_sites));assert.ok(changed.length,'No actual placement change');
 const r={schema:1,manifests,command,reference:a,candidate:b,changed_literal_functions:changed,linked_graphs_exact:true,static_ram_delta:0};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(r,null,2)+'\n');
 console.log(JSON.stringify({functions:names.length,changed_literal_functions:changed,static_ram_delta:0,sections:{A:a.sections,B:b.sections},bytes:manifests.map(m=>m.bytes)}));return r;
}
function report(){
 const build=preflight(),a=archive(path.join(experiment,'before'),path.join(dest,'controls/before')),b=archive(path.join(experiment,'candidate'),path.join(dest,'runs')),a2=archive(path.join(experiment,'after'),path.join(dest,'controls/after'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const r of [...a,...b,...a2]){assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);for(const [i,v] of r.report.final.results.entries()){assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);}}
 const initial=compare(a.map(x=>x.report),b.map(x=>x.report)),repeated=compare(a2.map(x=>x.report),b.map(x=>x.report));
 const host=read(path.join(root,'.build/opus-bands-tell-inline/correctness.json'));assert.equal(host.passed,true);
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,build,initial,repeated,host,selection:{initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)},inputs:{before:compact(a),candidate:compact(b),after:compact(a2)},scope:'30 physical A/B/A attempts; raw RAM packets, no output/profiler, no discarded runs. Not live qualification.'};
 for(const f of ['host-parent.log','regression.log','ota-before.json','ota-before.log','ota-candidate.json','ota-candidate.log','ota-after.json','ota-after.log']){const bytes=fs.readFileSync(path.join(experiment,f)),to=path.join(dest,f);if(fs.existsSync(to))assert.equal(hash(fs.readFileSync(to)),hash(bytes));else fs.writeFileSync(to,bytes);}
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(result.selection));return result;
}
module.exports={profiles,checkCommands,literalSites,preflight,report};
if(require.main===module){if(process.argv.includes('--preflight'))preflight();else report();}

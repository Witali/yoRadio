const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const recipe=require('../tools/esp8266_opus_asm/pvq_n4_prefix.cjs'),sem=require('../tools/esp8266_opus_asm/pvq_n4_prefix_proof.cjs');
const base=require('../tools/esp8266_opus_asm/frozen_reloads.cjs'),{hash}=require('../tools/esp8266_opus_asm/export.cjs');
const {readAt}=require('../tools/esp8266_opus_asm/pvq_exp2_table32_proof.cjs');
const {sections}=require('../tools/esp8266_opus_asm/frozen_div.cjs');
const pre=()=>JSON.parse(fs.readFileSync(path.join(recipe.art('candidate'),'preflight.json')));
const parent=()=>zlib.gunzipSync(fs.readFileSync(path.join(recipe.art('candidate'),'parent.elf.gz')));
test('N4 linked instructions preserve exact rank/p and live registers over full stored domains',()=>{
 const p=pre();assert.deepEqual(sem.prove(p.functions.decode_pulses,p.actual_functions.decode_pulses,p.helperDisassembly,p.table),p.semantic);
 assert.ok(p.semantic.interval_cases>300000);assert.equal(p.semantic.dense_indices,65472);
 assert.equal(p.semantic.mathematical.initial_K_pairs,9658561);assert.equal(p.semantic.stack_bytes,48);
 assert.equal(p.semantic.stores,0);assert.equal(p.semantic.sar_writes,0);assert.equal(p.app_bytes,903216);
});
test('three fixed-address patches leave all other ELF bytes and original U table intact',()=>{
 const p=pre(),a=parent(),b=base.patchElf(a,p.patches);assert.equal(hash(a),p.parent_elf_sha256);assert.equal(hash(b),p.candidate_elf_sha256);
 assert.deepEqual(p.dependencies,recipe.dependencies());assert.equal(fs.readFileSync(path.join(recipe.art('candidate'),'patches.s'),'utf8'),recipe.sourceFor());
 assert.deepEqual(p.patches.map(x=>[x.address,x.bytes]),[[sem.site,43],[sem.helper,94],[sem.dataAddress,1048]]);
 assert.deepEqual(require('../tools/esp8266_opus_asm/pvq_n3_diff_proof.cjs').table(b),p.table);
 const object=fs.readFileSync(path.join(recipe.art('candidate'),'patches.elf')),ss=sections(object);
 for(const [i,patch] of p.patches.entries()){const s=ss.find(x=>x.name==='.text.patch'+i);assert.equal(s.address,patch.address);assert.equal(s.bytes,patch.bytes);assert.equal(object.subarray(s.offset,s.offset+s.bytes).toString('hex'),patch.after_hex);}
 const entries=require('../tools/esp8266_opus_asm/algorithm_candidates.cjs').n4Table().entries;
 assert.equal(readAt(b,sem.dataAddress,4).readUInt32LE(),sem.tableAddress);
 entries.forEach((x,i)=>assert.equal(readAt(b,sem.tableAddress+i*4,4).readUInt32LE(),x));
});
test('table/helper storage is decoder-unreachable and static/stack RAM do not grow',()=>{
 const p=pre(),a=parent(),audit=require('../tools/esp8266_opus_asm/pvq_prefix_word_proof.cjs').storage({functions:p.functions},path.join(recipe.build('control'),'../',recipe.parent,'yoradio_esp8266_helix_native.elf'),a);
 assert.deepEqual(p.storage.contract,audit.contract);assert.deepEqual(p.storage.encoder,audit.encoder_storage);assert.deepEqual(p.storage.helper,audit.storage);
 assert.equal(p.storage.replaced_encoder_bytes,1048);assert.equal(p.static_ram_delta,0);assert.equal(p.stack_delta,0);
});
test('saved disassembly is regenerated from the actual patched ELF and app images match',()=>{
 const p=pre(),layout=require('../tools/esp8266_opus_asm/report_layout.cjs');
 const elf=path.join(recipe.build('candidate'),'yoradio_esp8266_helix_native.elf');assert.equal(hash(fs.readFileSync(elf)),p.candidate_elf_sha256);
 assert.equal(layout.reachableDisassembly(elf,p.actual_functions.decode_pulses),p.actual_functions.decode_pulses.disassembly);
 assert.equal(layout.reachableDisassembly(elf,{name:'n4_leaf',address:sem.helper,bytes:sem.helperBytes}),p.helperDisassembly);
 const images={};for(const t of ['control','candidate']){
  const m=JSON.parse(fs.readFileSync(path.join(recipe.art(t),'manifest.json')));images[t]=fs.readFileSync(path.join(recipe.art(t),'app.bin'));
  assert.equal(hash(images[t]),m.app_sha256);assert.equal(images[t].length,p.app_bytes);assert.deepEqual(m.post_link_bundle_dependencies,p.dependencies);
  assert.equal(m.post_link_pvq_n4_prefix_variant,t);assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);
 }
 assert.deepEqual(base.compareApps(images.control,images.candidate,p.patches),p.imageProof);
});
test('wrong guards, packed fields, arithmetic and fallback branches are rejected',()=>{
 const p=pre();sem.checkHelper(p.helperDisassembly);
 for(const [from,to] of [['a2, 16, 16','a2, 15, 16'],['a2, 64','a2, 32'],['a8, 22, 10','a8, 21, 10'],['a8, 6, 16','a8, 6, 15'],['mull','mul16s'],['a3, a3, 2','a3, a3, 3'],['a12, a12, 1','a12, a12, -1'],['bltu','bgeu'],['ret.n','retw.n']]){
  assert.ok(p.helperDisassembly.includes(from),from);assert.throws(()=>sem.checkHelper(p.helperDisassembly.replace(from,to)));
 }
 assert.throws(()=>sem.auditSite({...p.actual_functions.decode_pulses,disassembly:p.actual_functions.decode_pulses.disassembly.replace('beqi\ta13, 4','beqi\ta13, 3')},true));
});

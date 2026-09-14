const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),zlib=require('node:zlib');
const {hash,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const frozen=require('../tools/esp8266_opus_asm/frozen_div.cjs');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const proof=read(path.join(frozen.art('asm'),'preflight.json'));
const elf=zlib.gunzipSync(fs.readFileSync(path.join(frozen.art('asm'),'linked.elf.gz')));
const asm=fs.readFileSync(path.join(frozen.art('asm'),'app.bin'));
const rom=fs.readFileSync(path.join(frozen.art('rom'),'app.bin'));
test('frozen ELF changes one aligned call target without moving any code or RAM',()=>{
 assert.equal(hash(elf),proof.parent_elf_sha256);assert.equal(elf.length,proof.elf_bytes);
 assert.equal(proof.recipe_sha256_lf,sourceHash(path.join(__dirname,'../tools/esp8266_opus_asm/frozen_div.cjs')));
 const {output,offset}=frozen.patchLiteral(elf,proof.literal,proof.helper,proof.rom);
 assert.equal(offset,proof.elf_offset);assert.equal(hash(output),proof.rom_elf_sha256);
 assert.deepEqual(frozen.sections(output),frozen.sections(elf));
 assert.deepEqual(output.subarray(0,offset),elf.subarray(0,offset));
 assert.deepEqual(output.subarray(offset+4),elf.subarray(offset+4));
 assert.equal(proof.calls.length,3);assert.ok(proof.calls.every(c=>c.literal===proof.literal));
 assert.equal(proof.static_ram_delta,0);
});
test('both SDK images have valid checksums/digests and only the literal/checksum/digest differ',()=>{
 assert.deepEqual(frozen.compareImages(asm,rom,proof.literal,proof.helper,proof.rom),proof.imageProof);
 for(const [target,bytes]of [['asm',asm],['rom',rom]]){
  const m=read(path.join(frozen.art(target),'manifest.json'));
  assert.equal(m.app_sha256,hash(bytes));assert.equal(m.bytes,bytes.length);
  assert.equal(m.post_link_division_target,target);assert.equal(m.post_link_recipe_sha256_lf,proof.recipe_sha256_lf);
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);
  assert.equal(m.opus_profile_stage,0);assert.equal(m.opus_function_profile,false);
 }
});
test('post-link patch refuses wrong, unaligned, absent and NOBITS targets',()=>{
 assert.throws(()=>frozen.patchLiteral(elf,proof.literal,proof.rom,proof.helper));
 assert.throws(()=>frozen.patchLiteral(elf,proof.literal+1,proof.helper,proof.rom));
 assert.throws(()=>frozen.patchLiteral(elf,0xfffffffc,proof.helper,proof.rom));
 const bss=frozen.sections(elf).find(s=>s.type===8&&s.bytes>=4);assert.ok(bss);
 assert.throws(()=>frozen.patchLiteral(elf,bss.address,proof.helper,proof.rom));
 assert.throws(()=>frozen.sections(elf.subarray(0,128)));
 const otherCpu=Buffer.from(elf);otherCpu.writeUInt16LE(3,18);assert.throws(()=>frozen.sections(otherCpu));
});
test('valid app checksum does not permit unrelated payload changes',()=>{
 const info=frozen.inspectImage(rom),bad=Buffer.from(rom),offset=info.segments[0].offset;
 assert.notEqual(offset,proof.imageProof.literal_offset);bad[offset]^=1;bad[info.checksumOffset]^=1;
 Buffer.from(hash(bad.subarray(0,info.checksumOffset+1)),'hex').copy(bad,info.checksumOffset+1);
 frozen.inspectImage(bad);
 assert.throws(()=>frozen.compareImages(asm,bad,proof.literal,proof.helper,proof.rom),/Other app bytes/);
 const checksum=Buffer.from(rom);checksum[info.checksumOffset]^=1;assert.throws(()=>frozen.inspectImage(checksum));
 const digest=Buffer.from(rom);digest[digest.length-1]^=1;assert.throws(()=>frozen.inspectImage(digest));
 assert.throws(()=>frozen.inspectImage(Buffer.concat([rom,Buffer.alloc(1)])));
});

test('frozen pair refuses mismatched benchmark, memory and platform settings',()=>{
 const {pairedManifests,verifyPair}=require('../tools/esp8266_opus_asm/report_frozen_div.cjs');
 const {manifests}=verifyPair();
 for(const change of [
  m=>{m.cpu_mhz=80;},m=>{m.flash='QIO80';},m=>{m.opus_input_bytes+=4;},
  m=>{m.opus_benchmark_output=true;},m=>{m.opus_function_profile=true;},
  m=>{m.opus_profile_stage=1;},m=>{m.post_link_division_target='rom';}
 ]){const b=structuredClone(manifests.asm);change(b);assert.throws(()=>pairedManifests(manifests.rom,b));}
});

test('frozen A/B/A archive retains thirty exact physical runs and the negative result',()=>{
 const {root}=require('../tools/esp8266_opus_asm/export.cjs');
 const {compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
 const {selectHighBitrate}=require('../tools/esp8266_opus_asm/selection.cjs');
 const {validateRun}=require('../tools/esp8266_opus_asm/report_small_div_tail.cjs');
 const {verifyPair}=require('../tools/esp8266_opus_asm/report_frozen_div.cjs');
 const dir=frozen.art('asm'),result=read(path.join(dir,'comparison.json'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 assert.deepEqual(result.pair,verifyPair());
 const groups={};
 for(const [name,subdir]of [['before','controls/before'],['candidate','runs'],['after','controls/after']]){
  assert.equal(fs.readdirSync(path.join(dir,subdir)).filter(n=>/^run\d+\.json$/.test(n)).length,10);
  const inputs=result.inputs[name];assert.equal(inputs.length,10);
  const ota=read(path.join(dir,'ota-'+name+'.json'));assert.equal(ota.pass,true);
  assert.equal(ota.sha256,result.pair.manifests[name==='candidate'?'asm':'rom'].app_sha256);
  groups[name]=inputs.map((r,i)=>{
   const file=path.join(root,r.file);assert.equal(file,path.join(dir,subdir,'run'+(i+1)+'.json'));
   const bytes=fs.readFileSync(file);assert.equal(hash(bytes),r.sha256);
   const report=JSON.parse(bytes);validateRun(report,fixtures,ota.after.app_address);return report;
  });
 }
 assert.deepEqual(compare(groups.before,groups.candidate),result.initial);
 assert.deepEqual(compare(groups.after,groups.candidate),result.repeated);
 for(const k of ['initial','repeated']){
  assert.deepEqual(selectHighBitrate(result[k].cases),result.relative_pair_selection[k]);
  assert.equal(result.relative_pair_selection[k].accepted_for_experimental_asm,false);
  assert.equal(result.relative_pair_selection[k].target_192_cpu_at_most_70,false);
 }
 const previous=fs.readFileSync(path.join(root,result.historical_best.file));
 assert.equal(hash(previous),result.historical_best.sha256);
 assert.equal(result.candidate_beats_both_historical_192,false);
 const censusBytes=fs.readFileSync(path.join(root,result.attribution.source)),census=JSON.parse(censusBytes);
 assert.equal(hash(censusBytes),result.attribution.sha256);
 result.attribution.cases.forEach((a,i)=>{
  const c=result.initial.cases[i],h=census.cases[i];assert.equal(a.name,h.name);
  assert.equal(a.calls_per_run,h.calls*groups.candidate[0].final.rounds);
  const extra=(c.candidate.task_budget_percent.median-c.reference.task_budget_percent.median)*c.candidate.samples_per_run/4.8;
  assert.equal(a.extra_total_us,extra);
  assert.equal(a.extra_us_per_host_call,a.calls_per_run?extra/a.calls_per_run:null);
  assert.equal(a.powers,h.powers);assert.equal(a.fallback,h.fallback);
 });
});

// Matched firmware and live-file A/B. All attempted windows remain in the
// report; wall-time/idle DMA counters are never called decoder CPU usage.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {summarizeSeries}=require('./compare_live_input.cjs');
const {sha256}=require('./fixtures.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
const {parseSymbols}=require('./audit_target.cjs');
const {root}=require('./build_host.cjs');
function checkManifests(a,b) {
  assert.equal(a.opus_pcm_publish,false);assert.equal(b.opus_pcm_publish,true);
  for(const m of [a,b]) {
    assert.equal(m.diagnostic,true);assert.equal(m.opus_stream_test,true);
    assert.equal(m.opus_benchmark,false);assert.equal(m.opus_input_bytes,1024);
  }
  const allowed=['opus_pcm_publish','app_sha256','bytes','built_utc'];
  for(const k of new Set([...Object.keys(a),...Object.keys(b)]))
    if(!allowed.includes(k))assert.deepEqual(b[k],a[k],`Unrelated build difference: ${k}`);
}
function readSeries(directory) {
  const read=f=>fs.readFileSync(path.join(directory,f));
  const manifest=JSON.parse(read('manifest.json').toString().replace(/^\uFEFF/,''));
  const app=read('app.bin');assert.equal(app.length,manifest.bytes);
  assert.equal(sha256(app),manifest.app_sha256.toLowerCase());
  const reports=[],inputs=[],unconfirmedStarts=[];
  for(let i=1;i<=10;i++) {
    const text=read(`run${i}.json`).toString();reports.push(JSON.parse(text));
    const start=read(`start${i}.log`).toString().replace(/^\uFEFF/,'');
    let confirmed=false;try { confirmed=JSON.parse(start).queued===true; }catch {}
    if(!confirmed)unconfirmedStarts.push(i);
    inputs.push({run:i,sha256_lf:sha256(Buffer.from(text.replace(/\r\n/g,'\n'))),
      start_confirmed:confirmed,start_sha256_lf:sha256(Buffer.from(start.replace(/\r\n/g,'\n')))});
  }
  return {manifest,inputs,unconfirmed_starts:unconfirmedStarts,...summarizeSeries(reports)};
}
function targetEvidence(build) {
  const dump=args=>{
    const r=spawnSync(defaultObjdump,args,{encoding:'utf8',maxBuffer:8e6});
    if(r.error)throw r.error;assert.equal(r.status,0,r.stderr);return r.stdout;
  };
  const object=path.join(build,'esp-idf/main/CMakeFiles/__idf_main.dir/esp8266_nodac_i2s.c.obj');
  const elf=path.join(build,'yoradio_esp8266_helix_native.elf');
  const symbol=parseSymbols(dump(['-t',object])).get('nodac_slc_isr');
  assert.ok(symbol);assert.equal(symbol.bytes,387);
  const section=dump(['-s','-j',symbol.section,object]).split('Contents of section')[1];
  const sections={};
  for(const line of dump(['-h',elf]).split(/\r?\n/)) {
    const m=line.match(/^\s*\d+\s+(\.(?:dram0\.(?:data|bss)|iram0\.(?:text|bss|vectors)|flash\.(?:text|rodata)))\s+([0-9a-f]+)/);
    if(m)sections[m[1]]=parseInt(m[2],16);
  }
  assert.equal(Object.keys(sections).length,7);
  return {sections,isr_bytes:symbol.bytes,isr_section_sha256:sha256(Buffer.from(section)),
    app_elf_sha256:sha256(fs.readFileSync(elf))};
}
function compare(a,b,output) {
  const reference=readSeries(a),candidate=readSeries(b);
  checkManifests(reference.manifest,candidate.manifest);
  const before=targetEvidence(path.join(root,'.build',path.basename(a)));
  const after=targetEvidence(path.join(root,'.build',path.basename(b)));
  assert.equal(before.isr_section_sha256,after.isr_section_sha256,'ISR changed');
  for(const k of Object.keys(before.sections).filter(k=>!k.startsWith('.flash')))
    assert.equal(before.sections[k],after.sections[k],`Static RAM changed: ${k}`);
  const fixture=fs.readFileSync(path.join(__dirname,'live-fixtures/silk12.opus'));
  const result={scope:'Own SILK12 HTTP, ten requested starts per variant (unconfirmed starts listed), 3s startup allowance then 25s requested sparse health window. Failures retained. Not raw CPU timing.',
    fixture:{name:'silk12.opus',bytes:fixture.length,sha256:sha256(fixture)},
    reference,candidate,target:{before,after},
    candidate_all_windows_continuous:candidate.all_qualified,
    all_starts_confirmed:!reference.unconfirmed_starts.length&&!candidate.unconfirmed_starts.length};
  fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify({qualified:[reference.qualified,candidate.qualified],
    before:reference.observed_only,after:candidate.observed_only},null,2));
  return result;
}
module.exports={checkManifests,targetEvidence,compare};
if(require.main===module) {
  const [a,b,out]=process.argv.slice(2);assert.ok(a&&b&&out,'reference candidate output required');compare(a,b,out);
}

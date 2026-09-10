const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {sha256}=require('../tools/esp8266_opus_profile/fixtures.cjs');
const {compareArtifacts,compare}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
test('single reciprocal is opt-in and binds complete PCM/arena evidence',()=>{
  assert.match(fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8'),/option\(YORADIO_OPUS_DIV_ONCE [^\n]+ OFF\)/);
  const r=require('../tools/esp8266_opus_profile/div-once-results.json');assert.equal(r.passed,true);
  for(const [file,hash] of Object.entries(r.source_sha256_lf))assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  assert.equal(r.full.div_once,true);assert.equal(r.extra.length,11);assert.equal(r.blocks.cases.length,11);
  for(const c of [...r.full.fixtures,r.full.mixed_sequence,...r.extra,...r.blocks.cases,...r.sanitized])assert.equal(c.pcm.exact,true);
});
test('reciprocal board A/B forbids unrelated changes',()=>{
  const a={opus_div_once:false,opus_rotation_lx106:false,opus_celt_decode_only:false};
  compareArtifacts(a,{...a,opus_div_once:true},'opus_div_once');
  assert.throws(()=>compareArtifacts(a,{...a,opus_div_once:true,opus_rotation_lx106:true},'opus_div_once'),/rotation/);
});
test('target reciprocal path follows outlined GCC function and does not add static RAM',()=>{
  const r=require('../tools/esp8266_opus_profile/div-once-target-results.json');
  assert.equal(r.passed,true);assert.equal(r.off_instructions_exact,true);
  assert.equal(r.reciprocal_call_sites.off.alg_unquant,3);
  assert.equal(r.reciprocal_call_sites.on.alg_unquant,0);
  assert.equal(r.reciprocal_call_sites.outlined_rotation.celt_rcp,1);
  for(const k of ['.dram0.data','.dram0.bss','.iram0.bss','.iram0.text'])assert.equal(r.sections.delta[k],0);
});

test('archived reciprocal A/B retains all ten attempts and its negative speed result',()=>{
  const directory=path.resolve(__dirname,'../firmware/development');
  const r=require('../firmware/development/esp8266-opus-div192-on/comparison.json');
  const reports=[];
  for(const side of ['reference','candidate']) {
    const name=side==='reference'?'off':'on';
    const folder=path.join(directory,'esp8266-opus-div192-'+name);
    const manifest=JSON.parse(fs.readFileSync(path.join(folder,'manifest.json'),'utf8'));
    assert.deepEqual(manifest,r.artifacts[side]);
    assert.equal(sha256(fs.readFileSync(path.join(folder,'app.bin'))),manifest.app_sha256.toLowerCase());
    assert.equal(r.attempts[side].recorded,10);assert.deepEqual(r.attempts[side].failed,[]);
    assert.equal(r.inputs[side].length,10);
    reports.push(r.inputs[side].map((input,i)=>{
      const data=fs.readFileSync(path.join(folder,input.file));
      assert.equal(sha256(data),input.sha256);
      assert.deepEqual(data,fs.readFileSync(path.join(folder,`attempt${i+1}.json`)));
      return JSON.parse(data);
    }));
  }
  compareArtifacts(r.artifacts.reference,r.artifacts.candidate,'opus_div_once');
  const actual=compare(...reports);
  for(const key of ['cases','reference','candidate'])assert.deepEqual(actual[key],r[key]);
  for(const c of r.cases.slice(2))assert.ok(c.median_task_reduction_percent < -10);
});

test('compiler-only inlining probe is source-bound and does not claim board timing',()=>{
  const r=require('../tools/esp8266_opus_profile/div-codegen-results.json');
  assert.match(r.scope,/not accepted optimization or board speed evidence/);
  for(const [file,hash] of Object.entries(r.source_sha256_lf))
    assert.equal(sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n'))),hash,file);
  assert.equal(r.reports.length,4);
  const find=name=>r.reports.find(v=>v.name===name).functions.find(f=>f.name==='alg_unquant');
  assert.equal(find('configured').calls.celt_rcp,undefined);
  assert.equal(find('inline-1000').calls.celt_rcp,1);
  assert.ok(find('inline-1000').bytes > find('configured').bytes);
});

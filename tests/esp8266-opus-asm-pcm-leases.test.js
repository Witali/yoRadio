const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const helper=path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder/asm/pcm_leases.cmake').replaceAll('\\','/');
function run(sources){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'opus-lease-select-'));
 const script=path.join(dir,'select.cmake');
 fs.writeFileSync(script,`include("${helper}")\nyoradio_opus_pcm_lease_dispatcher(selected "/component" ${sources.map(s=>'"'+s+'"').join(' ')})\nfile(WRITE "${dir.replaceAll('\\','/')}/selected.txt" "\${selected}")\n`);
 const r=spawnSync(process.env.OPUS_TEST_CMAKE || 'cmake',['-P',script],{encoding:'utf8'});
 assert.ifError(r.error);
 if(!r.status)r.selected=fs.readFileSync(path.join(dir,'selected.txt'),'utf8').split(';');
 return r;
}
test('lease adapter replaces only the packet dispatcher, retaining every hot ASM unit',()=>{
 const sources=['/frozen/upstream/celt/bands.c.s','/frozen/upstream/src/opus_decoder.c.s','/frozen/upstream/silk/decode_core.c.s','/frozen/upstream/celt/celt_decoder.c.s'];
 const r=run(sources);assert.equal(r.status,0,r.stderr);
 assert.deepEqual(r.selected,[sources[0],'/component/upstream/src/opus_decoder.c',sources[2],sources[3]]);
});
test('missing/duplicate frozen dispatcher is rejected',()=>{
 for(const sources of [[],['/a/upstream/celt/celt_decoder.c.s'],['/a/upstream/src/opus_decoder.c.s','/b/upstream/src/opus_decoder.c.s']]){
  const r=run(sources);assert.notEqual(r.status,0);assert.match(r.stderr,/exactly one frozen packet dispatcher/);
 }
});
test('authenticated corpus and incompatible state ABI guards remain before selection',()=>{
 const s=fs.readFileSync(path.join(path.dirname(helper),'select.cmake'),'utf8');
 assert.ok(s.indexOf('verify.cjs')<s.indexOf('yoradio_opus_pcm_lease_dispatcher('));
 assert.match(s,/foreach\(flag YORADIO_OPUS_LOW_RAM YORADIO_OPUS_CELT_DECODE_ONLY/);
 assert.match(s,/if\(YORADIO_OPUS_PCM_LEASES\)/);
});

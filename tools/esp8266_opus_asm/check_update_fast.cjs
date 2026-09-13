// Independent real-C normalization test and host-only dynamic path census.
// No timing claims; no firmware/source changes outside private build products.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash}=require('./export.cjs'),{once}=require('./bands.cjs');
const {helper,cModels}=require('./update_fast.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function main(){
 const dir=path.join(root,'.build/opus-bands-update-fast');fs.mkdirSync(dir,{recursive:true});
 const model=path.join(dir,'update.model.c'),reference=path.join(dir,'entdec.reference.c'),unit=path.join(dir,'unit');
 fs.writeFileSync(model,'#include "entdec.h"\nvoid ec_dec_update_reference(ec_dec*,unsigned,unsigned,unsigned);\n'+
  helper().replace('static void y_update_fast','void ec_dec_update').replace('else ec_dec_update(','else ec_dec_update_reference('));
 fs.writeFileSync(reference,fs.readFileSync(path.join(component,'upstream/celt/entdec.c'),'utf8').replace('void ec_dec_update(', 'void ec_dec_update_reference('));
 const inc=['','upstream/include','upstream/celt','upstream/silk'].map(p=>'-I'+hostPath(path.join(component,p)));
 execute('gcc',['-O2','-fwrapv','-ffunction-sections','-fdata-sections','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all',
  '-DYORADIO_OPUS_BOUNDED=1','-DOPUS_FAST_INT64=0',...inc,hostPath(model),hostPath(reference),
  hostPath(path.join(root,'tests/native/esp8266_opus_asm_entropy_test.c')),'-Wl,--gc-sections','-lm','-o',hostPath(unit)]);
 const unitResult=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(unit)]));assert.equal(unitResult.passed,true);console.log(unitResult);
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 let text=fs.readFileSync(cModels()[0].file,'utf8');
 const counters=[
 '#include <stdio.h>','static unsigned long long y_calls,y_fast;',
 '__attribute__((destructor)) static void y_report(void) {',
 ' fprintf(stderr,"Y_UPDATE {\\"calls\\":%llu,\\"fast\\":%llu}\\n",y_calls,y_fast);','}',''].join('\n');
 text=once(text,'static void y_update_fast(',counters+'static void y_update_fast(');
 text=once(text,' if(rng>8388608u) {',' y_calls++;\n if(rng>8388608u) {\n  y_fast++;');
 const counted=path.join(dir,'bands.counted.c'),object=path.join(dir,'bands.counted.o'),binary=path.join(dir,'counted');
 fs.writeFileSync(counted,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(counted),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/bands.c.o')?(replaced++,object):p);assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const report={scope:'Host semantic mirror vs original C and host path counts at two bands sites; not LX106 timing.',recipe_sha256_lf:sourceHash(__filename),unit:unitResult,cases:[]};
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 for(const f of JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures){
  const a=path.join(dir,f.name+'.count-base.pcm'),b=path.join(dir,f.name+'.counted.pcm'),input=path.join(fixtures,f.name+'.opuspkt');
  const run=(bin,out)=>{
   const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(input),hostPath(out)];
   const r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});
   assert.equal(r.status,0,r.stderr);return r;
  };
  const aResult=run(base.binary,a),bResult=run(binary,b),counts=JSON.parse(bResult.stderr.match(/^Y_UPDATE (.+)$/m)[1]);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  assert.ok(counts.fast<=counts.calls);report.cases.push({name:f.name,packets:f.packet_count,samples:JSON.parse(aResult.stdout).samples,counts,pcm});
  console.log(f.name,counts);
 }
 report.passed=true;fs.writeFileSync(path.join(dir,'paths.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});

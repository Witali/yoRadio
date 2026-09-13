const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {buildHost,execute,hostPath,root,component}=require('./build_host.cjs');
const {comparePcm}=require('./run_regressions.cjs');
const {names}=require('./function_profile_result.cjs');
async function run(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true});
 const out=path.join(root,'.build/opus-function-regressions');fs.mkdirSync(out,{recursive:true});
 const extras=['opus_function_profile.c','opus_function_wrappers.c'].map(f=>path.join(component,f));
 extras.push(path.join(__dirname,'function_host_clock.c'));
 const objects=extras.map((src,i)=>{
  const obj=path.join(out,'extra'+i+'.o');
  execute('gcc',[...base.flags,'-DYORADIO_OPUS_FUNCTION_PROFILE=1','-c',hostPath(src),'-o',hostPath(obj)]);return obj;
 });
 const binary=path.join(out,'probe');
 execute('gcc',[...base.objects.map(hostPath),...objects.map(hostPath),...names.map(n=>'-Wl,--wrap='+n),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const report={scope:'Host exact PCM and ABI only, synthetic clock, not speed',cases:[]};
 for(const f of JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures){
  const input=path.join(fixtures,f.name+'.opuspkt'),a=path.join(out,f.name+'.base.pcm'),b=path.join(out,f.name+'.profile.pcm');
  const reference=JSON.parse(execute(hostPath(base.binary),[hostPath(input),hostPath(a),'--self-test']));
  const candidate=JSON.parse(execute(hostPath(binary),[hostPath(input),hostPath(b),'--self-test']));
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  report.cases.push({name:f.name,pcm,reference,candidate});console.log(f.name,'exact PCM');
 }
 const route=['mono-12','mono-24','stereo-64','stereo-192','mono-12'].map(n=>hostPath(path.join(fixtures,n+'.opuspkt')));
 const a=path.join(out,'mixed.base.pcm'),b=path.join(out,'mixed.profile.pcm');
 const reference=JSON.parse(execute(hostPath(base.binary),['--sequence',hostPath(a),...route]));
 const candidate=JSON.parse(execute(hostPath(binary),['--sequence',hostPath(b),...route]));
 const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
 report.cases.push({name:'mixed PLC and reset',pcm,reference,candidate});
 report.passed=true;fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)run().catch(e=>{console.error(e);process.exitCode=1});

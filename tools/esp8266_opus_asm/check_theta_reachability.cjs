// Exhaustive standard-mode reachability audit, independent of audio fixtures.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const dir=path.join(root,'.build/opus-theta-reachability');fs.mkdirSync(dir,{recursive:true});
 const source=path.join(__dirname,'theta_reachability.c'),object=path.join(dir,'audit.o'),binary=path.join(dir,'audit');
 execute('gcc',[...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 const excluded=base.objects.filter(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/bands.c.o')||p.endsWith('probe.c.o'));
 assert.equal(excluded.length,2);
 const objects=base.objects.filter(p=>!excluded.includes(p));
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),hostPath(object),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const log=execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(binary)]);
 fs.writeFileSync(path.join(dir,'audit.log'),log);
 const rows=log.trim().split(/\r?\n/).map(s=>JSON.parse(s)),summary=rows.pop();
 assert.equal(summary.passed,true);assert.equal(rows.length,64);
 const inputs=['upstream/celt/bands.c','upstream/celt/modes.c','upstream/celt/static_modes_fixed.h',
  'upstream/celt/entcode.h','upstream/celt/rate.h','upstream/include/config.h'];
 const report={schema:1,scope:'Current standard-mode decoder only; not CUSTOM_MODES, future modes, encoder entry points or arbitrary direct helper calls.',
  compiler:base.compiler,sanitizers:['address','undefined'],firmware_changed:false,
  hashes:Object.fromEntries(inputs.map(p=>[p,sourceHash(path.join(component,p))])),
  harness_sha256_lf:sourceHash(source),summary,rows};
 fs.writeFileSync(path.join(dir,'result.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(summary,null,2));
}
module.exports={main};
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});

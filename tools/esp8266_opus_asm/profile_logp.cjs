// Count actual ec_dec_bit_logp normalize/no-normalize calls on the host.
// Counters are never included in firmware; no host timing claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash,hash}=require('./export.cjs'),{once}=require('./bands.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const dir=path.join(root,'.build/opus-bands-logp'),source='upstream/celt/entdec.c';fs.mkdirSync(dir,{recursive:true});
 let text=fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n');
 const signature='int ec_dec_bit_logp(ec_dec *_this,unsigned _logp){';
 const helpers=['#include <stdio.h>','static unsigned y_counts[32][2],y_invalid;',
  '__attribute__((destructor)) static void y_count_report(void) {',
  ' fprintf(stderr,"LOGP_INVALID %u\\n",y_invalid);',
  ' for(int n=0;n<32;n++) if(y_counts[n][0]+y_counts[n][1]) fprintf(stderr,"LOGP_COUNTS %d %u %u\\n",n,y_counts[n][0],y_counts[n][1]);',
  '}',''].join('\n');
 text=once(text,signature,helpers+signature);
 const body=text.match(/int ec_dec_bit_logp\(ec_dec \*_this,unsigned _logp\)\{[\s\S]*?^\}/m)[0];
 text=text.replace(body,once(body,'  ec_dec_normalize(_this);',
  '  if(_logp<32) y_counts[_logp][_this->rng<=EC_CODE_BOT]++; else y_invalid++;\n  ec_dec_normalize(_this);'));
 const file=path.join(dir,'entdec.counted.c'),object=path.join(dir,'entdec.counted.o'),binary=path.join(dir,'counted');fs.writeFileSync(file,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(file),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/entdec.c.o')?(replaced++,object):p);assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const selected=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({...f,file:path.join(fixtures,f.name+'.opuspkt')}));
 selected.push(...require('./high_fixtures.cjs').generate());
 const report={scope:'One host fixed-point pass per file; no counters in firmware, not target timing.',recipe_sha256_lf:sourceHash(__filename),source_sha256_lf:sourceHash(path.join(component,source)),cases:[]};
 for(const f of selected){
  const a=path.join(dir,f.name+'.census-base.pcm'),b=path.join(dir,f.name+'.counted.pcm');
  const run=(bin,out)=>{const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(f.file),hostPath(out)],r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);return r;};
  run(base.binary,a);const r=run(binary,b);assert.match(r.stderr,/^LOGP_INVALID 0$/m);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  const counts=[...r.stderr.matchAll(/^LOGP_COUNTS (\d+) (\d+) (\d+)$/gm)].map(m=>({logp:Number(m[1]),fast:Number(m[2]),normalize:Number(m[3])}));
  const fast=counts.reduce((s,x)=>s+x.fast,0),normalize=counts.reduce((s,x)=>s+x.normalize,0);
  const decoded=JSON.parse(r.stdout);assert.equal(decoded.sample_rate,48000);assert.equal(decoded.output_channels,1);assert.equal(decoded.samples,pcm.compared_samples);
  const row={name:f.name,packet_sha256:hash(fs.readFileSync(f.file)),packets:decoded.packets,samples:decoded.samples,audio_duration_ms:decoded.samples/48,fast,normalize,counts,pcm};report.cases.push(row);
  console.log(JSON.stringify({name:f.name,audio_ms:row.audio_duration_ms,fast,normalize,fast_percent:100*fast/(fast+normalize)}));
 }
 report.passed=true;fs.writeFileSync(path.join(dir,'census.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});

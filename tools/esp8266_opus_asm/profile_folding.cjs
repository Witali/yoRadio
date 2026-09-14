// Count actual folding sqrt sites without adding any counters to the firmware.
// Coefficients come from the compiled upstream fixed-point celt_sqrt, not sqrt().
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,sourceHash,hash}=require('./export.cjs'),{once}=require('./bands.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
function instrument(text){
 assert.doesNotMatch(text,/y_fold_counts|y_fold_invalid/,'Already instrumented folding source');
 const helpers=['#include <stdio.h>','static unsigned y_fold_counts[4097],y_fold_invalid;',
  '__attribute__((destructor)) static void y_fold_report(void) {',
  ' fprintf(stderr,"FOLD_INVALID %u\\n",y_fold_invalid);',
  ' for(int n=0;n<=4096;n++) if(y_fold_counts[n]) fprintf(stderr,"FOLD_COUNTS %d %u\\n",n,y_fold_counts[n]);',
  '}',''].join('\n');
 text=once(text,'/* This function is responsible for encoding and decoding a band for the mono case. */',helpers+'/* This function is responsible for encoding and decoding a band for the mono case. */');
 return once(text,'         n = celt_sqrt(SHL32(EXTEND32(N0),22));',
  '         if(N0>=0 && N0<=4096) y_fold_counts[N0]++; else y_fold_invalid++;\n         n = celt_sqrt(SHL32(EXTEND32(N0),22));');
}
function standardSizes(text){
 const body=text.match(/static const opus_int16 eband5ms\[\] = \{([\s\S]*?)\};/)[1].replace(/\/\*[\s\S]*?\*\//g,'');
 const bands=body.split(',').map(s=>Number(s.trim()));assert.equal(bands.length,22);assert.equal(bands[0],0);assert.equal(bands[21],100);
 const rows=[];for(let lm=0;lm<4;lm++)for(let i=0;i<21;i++)rows.push({band:i,lm,N:(bands[i+1]-bands[i])<<lm});
 return {bands,rows,sizes:[...new Set(rows.map(r=>r.N))].sort((a,b)=>a-b)};
}
async function main(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'tell-inline'});
 const dir=path.join(root,'.build/opus-folding-census'),source='upstream/celt/bands.c';fs.mkdirSync(dir,{recursive:true});
 // Count the same fixed-point semantic parent as the current ASM control.
 const parent=require('./tell_inline.cjs').cModels().find(x=>x.source===source);assert.ok(parent);
 const file=path.join(dir,'bands.counted.c'),object=path.join(dir,'bands.counted.o'),binary=path.join(dir,'counted');
 fs.writeFileSync(file,instrument(fs.readFileSync(parent.file,'utf8').replace(/\r\n/g,'\n')));
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(file),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/objects/bands.model.c.o')?(replaced++,object):p);assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const math=base.objects.find(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/mathops.c.o'));assert.ok(math);
 const probe=path.join(dir,'sqrt-probe.c'),probeBin=path.join(dir,'sqrt-probe');
 fs.writeFileSync(probe,'#include <stdio.h>\n#include "config.h"\n#ifndef FIXED_POINT\n#error Fixed-point configuration is required\n#endif\n#include "mathops.h"\nint main(void){for(int n=0;n<512;n++) printf("%d %d\\n",n,(int)celt_sqrt((opus_int32)((opus_uint32)n<<22)));return 0;}\n');
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,hostPath(probe),hostPath(math),...base.linkFlags,'-Wl,--gc-sections','-lm','-o',hostPath(probeBin)]);
 const raw=execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(probeBin)]),values=raw.trim().split(/\r?\n/).map((s,i)=>{const [n,value]=s.split(' ').map(Number);assert.equal(n,i);return value;});assert.equal(values.length,512);
 const modeFile=path.join(component,'upstream/celt/modes.c'),standard=standardSizes(fs.readFileSync(modeFile,'utf8'));
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const selected=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({...f,file:path.join(fixtures,f.name+'.opuspkt')}));
 selected.push(...require('./high_fixtures.cjs').generate());
 const report={schema:1,scope:'One host fixed-point pass per fixture; no board timing, no firmware changes. Table values compiled from original integer sqrt.',recipe_sha256_lf:sourceHash(__filename),source_sha256_lf:sourceHash(path.join(component,source)),math_source_sha256_lf:sourceHash(path.join(component,'upstream/celt/mathops.c')),mode_source_sha256_lf:sourceHash(modeFile),parent_manifest_sha256_lf:sourceHash(path.join(component,'asm/lx106/bands-tell-inline.json')),standard,table:standard.sizes.map(N=>({N,value:values[N]})),all_values:values,cases:[]};
 for(const f of selected){
  const a=path.join(dir,f.name+'.base.pcm'),b=path.join(dir,f.name+'.counted.pcm');
  const run=(bin,out)=>{const args=['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),hostPath(f.file),hostPath(out)],r=process.platform==='win32'?spawnSync('wsl.exe',['--exec','env',...args],{encoding:'utf8'}):spawnSync('env',args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);return r;};
  run(base.binary,a);const r=run(binary,b);assert.match(r.stderr,/^FOLD_INVALID 0$/m);
  fs.writeFileSync(path.join(dir,f.name+'.trace.txt'),r.stderr);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  const counts=[...r.stderr.matchAll(/^FOLD_COUNTS (\d+) (\d+)$/gm)].map(m=>({N:Number(m[1]),calls:Number(m[2])}));
  const calls=counts.reduce((s,c)=>s+c.calls,0),constantN2=counts.find(c=>c.N===2)?.calls||0,decoded=JSON.parse(r.stdout);
  assert.equal(decoded.sample_rate,48000);assert.equal(decoded.output_channels,1);assert.equal(decoded.samples,pcm.compared_samples);
  const row={name:f.name,packet_sha256:hash(fs.readFileSync(f.file)),packets:decoded.packets,samples:decoded.samples,audio_duration_ms:decoded.samples/48,calls,constant_N2_calls:constantN2,counts,pcm,trace_sha256:hash(Buffer.from(r.stderr))};report.cases.push(row);
  console.log(JSON.stringify({name:f.name,audio_ms:row.audio_duration_ms,calls,constantN2}));
 }
 assert.equal(values[0],0);assert.equal(values[256],32767);assert.equal(values[511],32767);
 report.fixed_point=true;report.config_sha256_lf=sourceHash(path.join(component,'upstream/include/config.h'));
 report.compiler=base.compiler;report.flags=base.flags;report.link_flags=base.linkFlags;
 report.passed=true;fs.writeFileSync(path.join(dir,'census.json'),JSON.stringify(report,null,2)+'\n');
 return report;
}
module.exports={instrument,standardSizes,main};if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});

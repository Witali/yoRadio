// Host-only census of the actual rng/ft divisions replaced by small_div.cjs.
// One fresh decode per fixture, not the probe's additional reset/PLC passes.
// Preserve every operand, its order and repetitions for a same-image LX106
// microbenchmark. Host runtime is deliberately NOT treated as target speed.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');

function parse(text){
 if(!text.trim())return [];
 const lines=text.trim().split(/\r?\n/);
 return lines.map(line=>{
  assert.match(line,/^\d+,\d+$/);
  const pair=line.split(',').map(Number);
  assert.ok(pair.every(Number.isSafeInteger));
  assert.ok(pair[0]>=0&&pair[0]<=0xffffffff&&pair[1]>0&&pair[1]<=0xffffffff);
  return pair;
 });
}
function summarize(pairs){
 const counts=new Map();let small=0,powers=0,nmin=0xffffffff,nmax=0;
 for(const [n,d]of pairs){
  counts.set(d,(counts.get(d)||0)+1);small+=d<=256;powers+=(d&(d-1))===0;
  nmin=Math.min(nmin,n);nmax=Math.max(nmax,n);
 }
 return {calls:pairs.length,small,fallback:pairs.length-small,powers,nmin:pairs.length?nmin:null,nmax:pairs.length?nmax:null,
  histogram:[...counts].map(([d,calls])=>({d,calls})).sort((a,b)=>b.calls-a.calls||a.d-b.d)};
}
function instrument(text){
 const needle='_this->ext=celt_udiv(_this->rng,_ft);';
 assert.equal(text.split(needle).length,2);
 const helper=[
  '#include <stdio.h>','#include <stdlib.h>',
  'static FILE *y_trace;',
  'static void y_trace_close(void){if(y_trace&&fclose(y_trace))abort();}',
  'static opus_uint32 y_trace_div(opus_uint32 n,opus_uint32 d){',
  ' if(!y_trace){const char *p=getenv("YORADIO_OPUS_DIVISION_TRACE");',
  '  if(!p||!(y_trace=fopen(p,"wb"))||atexit(y_trace_close))abort();}',
  ' if(fprintf(y_trace,"%lu,%lu\\n",(unsigned long)n,(unsigned long)d)<0)abort();',
  ' return n/d;','}',''
 ].join('\n');
 assert.equal(text.split('unsigned ec_decode(').length,2);
 return text.replace('unsigned ec_decode(',helper+'unsigned ec_decode(')
  .replace(needle,'_this->ext=y_trace_div(_this->rng,_ft);');
}
async function census(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'tell-inline'});
 const dir=path.join(root,'.build/opus-bands-division-census');fs.mkdirSync(dir,{recursive:true});
 const source=path.join(component,'upstream/celt/entdec.c'),file=path.join(dir,'entdec.counted.c');
 const object=path.join(dir,'entdec.counted.o'),binary=path.join(dir,'counted');
 fs.writeFileSync(file,instrument(fs.readFileSync(source,'utf8').replace(/\r\n/g,'\n')));
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(file),'-o',hostPath(object)]);
 let replaced=0;const objects=base.objects.map(p=>p.replaceAll('\\','/').endsWith('/upstream/celt/entdec.c.o')?(replaced++,object):p);
 assert.equal(replaced,1);
 execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const manifest=path.join(fixtures,'manifest.json'),operands=[];
 const report={schema:1,scope:'Host one-pass operand census; no target timing or cache claim',
  recipe_sha256_lf:sourceHash(__filename),source_sha256_lf:sourceHash(source),manifest_sha256:hash(fs.readFileSync(manifest)),cases:[]};
 for(const f of JSON.parse(fs.readFileSync(manifest)).fixtures){
  const input=path.join(fixtures,f.name+'.opuspkt'),trace=path.join(dir,f.name+'.trace.txt');
  const a=path.join(dir,f.name+'.base.pcm'),b=path.join(dir,f.name+'.counted.pcm');
  const run=(bin,out,traced)=>JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',
   ...(traced?['YORADIO_OPUS_DIVISION_TRACE='+hostPath(trace)]:[]),hostPath(bin),hostPath(input),hostPath(out)]));
  // SILK-only fixtures can execute no ec_decode() divisions.
  // Clear the trace so zero calls cannot reuse an earlier run.
  fs.writeFileSync(trace,'');
  const reference=run(base.binary,a,false),decoded=run(binary,b,true);
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  assert.equal(hash(fs.readFileSync(b)),f.pcm_sha256);
  for(const k of ['samples','packets','sample_rate','output_channels','scratch_byte_peak_bytes','scratch_word_peak_bytes'])assert.equal(decoded[k],reference[k],k);
  assert.equal(decoded.samples,f.samples);assert.equal(decoded.packets,f.packet_count);
  const pairs=parse(fs.readFileSync(trace,'utf8')),stats=summarize(pairs);
  const row={name:f.name,packet_sha256:hash(fs.readFileSync(input)),samples:decoded.samples,packets:decoded.packets,
   audio_ms:decoded.samples/48,first_pair:operands.length,...stats,trace_sha256:hash(fs.readFileSync(trace)),pcm};
  operands.push(...pairs);report.cases.push(row);
  console.log(JSON.stringify({...row,histogram:stats.histogram.slice(0,12),pcm:pcm.exact}));
 }
 const payload=Buffer.alloc(operands.length*8);
 operands.forEach(([n,d],i)=>{payload.writeUInt32LE(n,i*8);payload.writeUInt32LE(d,i*8+4);});
 fs.writeFileSync(path.join(dir,'operands.bin'),payload);
 report.payload_bytes=payload.length;report.payload_sha256=hash(payload);report.passed=true;
 fs.writeFileSync(path.join(dir,'census.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({payload_bytes:payload.length,pairs:operands.length}));
 return report;
}
module.exports={parse,summarize,instrument,census};
if(require.main===module)census().catch(e=>{console.error(e);process.exitCode=1;});

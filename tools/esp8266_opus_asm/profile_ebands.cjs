// Frequency evidence only: source-level reads, not target load counts/timing.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
const units=['bands','celt_decoder','rate'];
function instrument(text,unit,observer){
 assert.ok(units.includes(unit));assert.doesNotMatch(text,/y_eband_read/);
 // Preserve offsets while masking comments and literals, never instrument prose.
 const masked=text.replace(/\/\*[\s\S]*?\*\/|\/\/[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g,m=>m.replace(/[^\n]/g,' '));
 const re=/\b(?:(?:[a-zA-Z_]\w*)->)?eBands\s*\[/g,sites=[];let m;
 while((m=re.exec(masked))){
  const start=m.index,open=re.lastIndex-1;let end=open+1,depth=1;
  while(end<masked.length && depth){if(masked[end]==='[')depth++;if(masked[end]===']')depth--;end++;}
  assert.equal(depth,0);const pointer=masked.slice(start,open).trim(),index=text.slice(open+1,end-1);
  assert.ok(['eBands','m->eBands'].includes(pointer),'Unreviewed eBands pointer '+pointer);
  assert.match(index,/^[\w+\- >]+$/,'Unreviewed index '+index);
  sites.push({id:sites.length,line:text.slice(0,start).split('\n').length,pointer,index,expression:text.slice(start,end),start,end});re.lastIndex=end;
 }
 assert.ok(sites.length>0);
 let output=text;
 for(const s of [...sites].reverse())output=output.slice(0,s.start)+`y_eband_read(${s.pointer},(${s.index}),${s.id},__func__)`+output.slice(s.end);
 output=`#define Y_EBAND_UNIT "${unit}"\n#define Y_EBAND_SITES ${sites.length}\n${observer}\n${output}`;
 return{output,sites};
}
function validateCounts(counts,sites){
 assert.equal(counts.length,sites.length);let total=0;
 for(const [i,c]of counts.entries()){
  assert.equal(c.id,i);assert.equal(c.indices.length,22);assert.equal(typeof c.function,'string');
  for(const n of[c.total,...c.indices])assert.ok(Number.isSafeInteger(n)&&n>=0);
  assert.equal(c.total,c.indices.reduce((a,b)=>a+b,0));assert.equal(c.total===0,c.function==='');total+=c.total;
 }return total;
}
async function profile(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'pvq-exp2-table32'});
 const out=path.join(root,'.build/opus-ebands-profile');fs.mkdirSync(out,{recursive:true});
 const models=require('./pvq_exp2_table32.cjs').cModels(),observer=path.join(__dirname,'ebands_probe.inc.c');
 const build=JSON.parse(fs.readFileSync(path.join(base.out,'build.json'))),objects=[...base.objects],metadata={};
 for(const unit of units){
  const rel='upstream/celt/'+unit+'.c',model=models.find(m=>m.source===rel),file=model?model.file:path.join(component,rel);
  const index=build.sources.indexOf(file);assert.ok(index>=0,unit+' object source missing');
  const {output,sites}=instrument(fs.readFileSync(file,'utf8').replace(/\r\n/g,'\n'),unit,fs.readFileSync(observer,'utf8'));
  const source=path.join(out,unit+'.counted.c'),object=path.join(out,unit+'.counted.o');fs.writeFileSync(source,output);
  execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);objects[index]=object;
  metadata[unit]={source_sha256_lf:sourceHash(file),generated_sha256_lf:sourceHash(source),sites};
 }
 const binary=path.join(out,'observer');execute('gcc',[...base.linkFlags,...objects.map(hostPath),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={schema:1,scope:'Host source-expression census only. Does not measure LX106 loads, cache misses or CPU. Same accepted exp2-table32 semantic model; firmware unchanged.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(observer),parent_recipe_sha256_lf:sourceHash(path.join(__dirname,'pvq_exp2_table32.cjs')),units:metadata,compiler:base.compiler,flags:base.flags,cases:[]};
 for(const f of spec){
  const a=path.join(out,f.name+'.base.pcm'),b=path.join(out,f.name+'.counted.pcm'),prefix=path.join(out,f.name);
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(a)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_EBAND_COUNTS='+hostPath(prefix),hostPath(binary),hostPath(f.file),hostPath(b)]));
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,k));assert.deepEqual(reference[k],probe[k]);}
  const counts={},totals={},functions={};
  for(const unit of units){counts[unit]=JSON.parse(fs.readFileSync(prefix+'.'+unit+'.json'));totals[unit]=validateCounts(counts[unit],metadata[unit].sites);
   for(const c of counts[unit])if(c.total)functions[unit+':'+c.function]=(functions[unit+':'+c.function]||0)+c.total;}
  const seconds=probe.samples/48000;
  result.cases.push({name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,seconds,counts,totals,functions});
  console.log(f.name,JSON.stringify({seconds,totals,functions}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={units,instrument,validateCounts,profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});

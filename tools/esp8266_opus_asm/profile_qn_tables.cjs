// Audit remaining compute_theta/compute_qn table reads on the accepted host model.
// Counts are semantic workload, not LX106 timing or an inlining/PC attribution.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs'),{once}=require('./bands.cjs');
const anchors={
 begin:'static int compute_qn(',
 logn:'   pulse_cap = m->logN[i]+LM*(1<<BITRES);',
 exp2:'      qn = exp2_table8[qb&0x7]>>(14-(qb>>BITRES));',
 partition:'   cache = m->cache.bits + y_pvq_index_half(m,(LM+1)*m->nbEBands+i);',
 search:'      q = y_endpoint_cost(m, i, LM, b, y_row_length, &curr_bits);'
};
function instrument(text,observer){
 text=once(text,anchors.begin,observer+'\n'+anchors.begin);
 text=once(text,anchors.logn,'   pulse_cap = y_qn_logn(m,i,stereo)+LM*(1<<BITRES);');
 text=once(text,anchors.exp2,'      qn = y_qn_exp2(exp2_table8,qb&0x7,stereo)>>(14-(qb>>BITRES));');
 text=once(text,anchors.partition,'   y_qn_counts.partition++; if(N==2)y_qn_counts.partition_n2++;\n'+anchors.partition);
 return once(text,anchors.search,'      y_qn_counts.search++; if(N==2)y_qn_counts.search_n2++;\n'+anchors.search);
}
function validateCounts(c){
 for(const [key,n]of [['logn',2],['exp2',2],['logn_index',21],['exp2_index',8]]){
  assert.equal(c[key].length,n);for(const v of c[key])assert.ok(Number.isSafeInteger(v)&&v>=0);
 }
 for(const k of ['partition','partition_n2','search','search_n2'])assert.ok(Number.isSafeInteger(c[k])&&c[k]>=0);
 const sum=v=>v.reduce((a,b)=>a+b,0);
 assert.equal(sum(c.logn),sum(c.logn_index));assert.equal(sum(c.exp2),sum(c.exp2_index));
 for(let i=0;i<2;i++)assert.ok(c.exp2[i]<=c.logn[i]);
 assert.equal(c.partition-c.search,c.logn[0],'Every non-stereo theta is one actual partition split');
 assert.equal(c.partition_n2,c.search_n2,'N=2 never splits');assert.ok(c.search_n2<=c.search);assert.ok(c.search<=c.partition);
 return sum(c.logn)+sum(c.exp2);
}
function linkedInventory(){
 const dir=path.join(root,'firmware/development/esp8266-opus-pvq-index-half-candidate-v1');
 const p=JSON.parse(fs.readFileSync(path.join(dir,'preflight.json'))),base=require('./frozen_reloads.cjs');
 const parent=require('node:zlib').gunzipSync(fs.readFileSync(path.join(dir,'parent.elf.gz')));
 assert.equal(hash(parent),p.parent_elf_sha256);const elf=base.patchElf(parent,p.patches);assert.equal(hash(elf),p.candidate_elf_sha256);
 const sections=require('./frozen_div.cjs').sections(elf);
 const read=(address,bytes)=>{const s=sections.find(s=>s.type===1&&(s.flags&2)&&address>=s.address&&address+bytes<=s.address+s.bytes);assert.ok(s);return elf.subarray(s.offset+address-s.address,s.offset+address-s.address+bytes);};
 const logAddress=read(0x402d3968+48,4).readUInt32LE(),expAddress=read(0x40211a9c,4).readUInt32LE();
 const tables=[['logN',logAddress,42],['exp2_table8',expAddress,16]].map(([name,address,bytes])=>{
  assert.equal(address%4,0);const raw=read(address,bytes),values=[];
  for(let i=0;i<bytes;i+=2)values.push(raw.readInt16LE(i));
  return{name,address,bytes,values,sha256:hash(raw),last_aligned_word_hex:read((address+bytes-2)&~3,4).toString('hex')};
 });
 assert.deepEqual(tables[1].values,[16384,17866,19483,21247,23170,25267,27554,30048]);
 const rows=require('./bits_fifth_proof.cjs').parsed(p.actual_functions.quant_partition);
 const loads=[[0x4024db91,'l16si a4, a10, 0'],[0x4024dc76,'l16si a3, a3, 0']].map(([address,text])=>{assert.equal(rows.find(r=>r.address===address)?.text,text);return{address,text};});
 return{elf_sha256:p.candidate_elf_sha256,tables,loads,scope:'Pinned quant_partition instruction/table inventory; host call counts are semantic, not a per-PC trace. No new helper, full ABI proof or timing.'};
}
async function profile(){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:'pvq-index-half'});
 const out=path.join(root,'.build/opus-qn-tables-profile');fs.mkdirSync(out,{recursive:true});
 const model=require('./pvq_index_half.cjs').cModels().find(m=>m.source==='upstream/celt/bands.c');assert.ok(model);
 const observer=path.join(__dirname,'qn_tables_probe.inc.c');
 const text=instrument(fs.readFileSync(model.file,'utf8').replace(/\r\n/g,'\n'),fs.readFileSync(observer,'utf8'));
 const source=path.join(out,'bands.model.c'),object=path.join(out,'bands.model.o'),binary=path.join(out,'observer');fs.writeFileSync(source,text);
 execute('gcc',['-I'+hostPath(path.join(component,'upstream/celt')),...base.flags,'-c',hostPath(source),'-o',hostPath(object)]);
 const expected=path.join(base.out,'objects',path.basename(model.file)+'.o');assert.equal(base.objects.filter(p=>p===expected).length,1);
 execute('gcc',[...base.linkFlags,...base.objects.map(p=>hostPath(p===expected?object:p)),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
 const fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const spec=JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures.map(f=>({name:f.name,file:path.join(fixtures,f.name+'.opuspkt')}));
 spec.push(...require('./high_fixtures.cjs').generate().map(f=>({name:f.name,file:f.file})));
 const result={schema:1,scope:'Host original-value table reads and partition N=2 census. No target change, no timing, no claim that host inlining matches GCC LX106.',recipe_sha256_lf:sourceHash(__filename),observer_sha256_lf:sourceHash(observer),parent_recipe_sha256_lf:sourceHash(path.join(__dirname,'pvq_index_half.cjs')),generated_model_sha256_lf:sourceHash(source),linked_inventory:linkedInventory(),compiler:base.compiler,flags:base.flags,cases:[]};
 for(const f of spec){
  const original=path.join(out,f.name+'.base.pcm'),observed=path.join(out,f.name+'.observed.pcm'),stats=path.join(out,f.name+'.counts.json');
  const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(base.binary),hostPath(f.file),hostPath(original)]));
  const probe=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0','YORADIO_QN_COUNTS='+hostPath(stats),hostPath(binary),hostPath(f.file),hostPath(observed)]));
  const pcm=comparePcm(fs.readFileSync(original),fs.readFileSync(observed));assert.equal(pcm.exact,true);
  for(const k of['samples','packets','scratch_byte_peak_bytes','scratch_word_peak_bytes','mono_state_bytes','stereo_state_bytes','arena_guards_ok']){assert.ok(Object.hasOwn(reference,k));assert.deepEqual(reference[k],probe[k]);}
  const counts=JSON.parse(fs.readFileSync(stats)),loads=validateCounts(counts),seconds=probe.samples/48000;
  result.cases.push({name:f.name,fixture_sha256:hash(fs.readFileSync(f.file)),reference,probe,pcm,counts,seconds,table_reads_per_audio_second:loads/seconds});
  console.log(f.name,JSON.stringify({logn:counts.logn,exp2:counts.exp2,search_n2:counts.search_n2,seconds,table_reads_per_audio_second:loads/seconds}));
 }
 result.passed=true;fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(result,null,2)+'\n');return result;
}
module.exports={anchors,instrument,validateCounts,linkedInventory,profile};if(require.main===module)profile().catch(e=>{console.error(e);process.exitCode=1;});

const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,sourceHash}=require('./export.cjs');
const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
const {comparePcm}=require('../esp8266_opus_profile/run_regressions.cjs');
const {verifyStates}=require('./host_state.cjs');
async function check(kind){
 const base=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
 const candidate=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true,asmBandsModel:kind});
 const out=path.join(root,'.build/opus-bands-'+kind),fixtures=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 fs.mkdirSync(out,{recursive:true});
 const report={scope:'Host semantic mirror, exact PCM/guards; not LX106 execution or timing',kind,recipe_sha256_lf:sourceHash(path.join(__dirname,kind==='intensity'?'bands.cjs':kind.replaceAll('-','_')+'.cjs')),cases:[]};
 const probe=(bin,args)=>JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(bin),...args]));
 const compare=(name,args)=>{
  const a=path.join(out,name+'.base.pcm'),b=path.join(out,name+'.candidate.pcm');
  const reference=probe(base.binary,args(a)),result=probe(candidate.binary,args(b));
  const pcm=comparePcm(fs.readFileSync(a),fs.readFileSync(b));assert.equal(pcm.exact,true,name);
  verifyStates(reference,result,name==='mixed');
  report.cases.push({name,pcm,reference,candidate:result});console.log(name,'exact PCM');
 };
 for(const f of JSON.parse(fs.readFileSync(path.join(fixtures,'manifest.json'))).fixtures)
  compare(f.name,pcm=>[hostPath(path.join(fixtures,f.name+'.opuspkt')),hostPath(pcm),'--self-test']);
 if(kind==='cache-reuse'||kind==='inner4'||kind==='logp'||kind==='tell-inline'||kind==='small-div'||kind==='folding8'||kind==='partition-decode'||kind==='ec-bits'||kind==='micro-bundle'||kind==='pvq-dim-pointer'||kind==='partition-points'||kind==='bits-fifth'||kind==='bits-fourth'||kind==='endpoint-cost'||kind==='pvq-byte-word'||kind==='pvq-a4-word'||kind==='pvq-row-word'||kind==='pvq-endpoint-word'||kind==='pvq-index-word'||kind==='pvq-index-half'||kind==='pvq-logn-word'||kind==='pvq-exp2-word'||kind==='pvq-exp2-table32'||kind==='pvq-qn-table'||kind==='ebands-pair'||kind==='ebands-more'||kind==='allocation-byte'){
  const high=require('./high_fixtures.cjs').generate();
  report.high_fixtures=high.map(f=>({name:f.name,command:f.command,sha256:require('node:crypto').createHash('sha256').update(fs.readFileSync(f.file)).digest('hex')}));
  for(const f of high)compare(f.name,pcm=>[hostPath(f.file),hostPath(pcm),'--self-test']);
 }
 compare('mixed',pcm=>['--sequence',hostPath(pcm),...['mono-12','mono-24','stereo-64','stereo-192','mono-12'].map(n=>hostPath(path.join(fixtures,n+'.opuspkt')))]);
 if(kind==='partition-decode'||kind==='ec-bits'||kind==='micro-bundle'||kind==='pvq-dim-pointer'||kind==='partition-points'||kind==='bits-fifth'||kind==='bits-fourth'||kind==='endpoint-cost'||kind==='pvq-byte-word'||kind==='pvq-a4-word'||kind==='pvq-row-word'||kind==='pvq-endpoint-word'||kind==='pvq-index-word'||kind==='pvq-index-half'||kind==='pvq-logn-word'||kind==='pvq-exp2-word'||kind==='pvq-exp2-table32'||kind==='pvq-qn-table'||kind==='ebands-pair'||kind==='ebands-more'||kind==='allocation-byte'){
  const phase=path.join(root,'tests/fixtures/opus_native/phase');
  for(const name of fs.readdirSync(phase).filter(n=>n.endsWith('.opuspkt')).sort())compare('phase-'+name,pcm=>[hostPath(path.join(phase,name)),hostPath(pcm),'--self-test']);
  const {grouped}=require('../esp8266_opus_profile/run_block_regressions.cjs');
  const specs=[['192-120ms',path.join(fixtures,'stereo-192.opuspkt'),6],['320-120ms',path.join(root,'.build/opus-high-compatibility/stereo-320-20ms.opuspkt'),6],['320-48frames',path.join(root,'.build/opus-high-compatibility/stereo-320-2.5ms.opuspkt'),48]];
  report.compound=[];
  for(const [name,input,count]of specs){const file=path.join(out,name+'.opuspkt'),bytes=grouped(fs.readFileSync(input),count);fs.writeFileSync(file,bytes);
   report.compound.push({name,count,sha256:require('node:crypto').createHash('sha256').update(bytes).digest('hex')});
   compare(name,pcm=>[hostPath(file),hostPath(pcm),'--self-test']);
  }
 }
 report.passed=true;fs.writeFileSync(path.join(out,'correctness.json'),JSON.stringify(report,null,2)+'\n');
}
if(require.main===module)check(process.argv[2]).catch(e=>{console.error(e);process.exitCode=1;});

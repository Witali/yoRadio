const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const {buildHost,execute,hostPath,component} = require('./build_host.cjs');
const {sha256} = require('./fixtures.cjs');
async function run({output,sanitize=true}={}) {
  const results=[];
  for(const autocorrCompact of [false,true]) {
    const build=await buildHost({bounded:true,fastInt64:0,autocorrCompact,sanitize});
    const source=path.join(__dirname,'autocorr_probe.c'), object=path.join(build.out,'autocorr_probe.o'),binary=path.join(build.out,'autocorr_probe');
    execute('gcc',[...build.flags,'-Wall','-Wextra','-Werror','-c',hostPath(source),'-o',hostPath(object)]);
    execute('gcc',[...build.linkFlags,...build.objects.filter(f=>!f.endsWith('probe.c.o')).map(hostPath),hostPath(object),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
    results.push({compiler:build.compiler,flags:build.flags,...JSON.parse(execute(hostPath(binary),[]))});
  }
  const [before,after]=results;assert.equal(before.cases.length,after.cases.length);
  let avoided=0,fallbacks=0,maxReduction=0;
  const cases=after.cases.map((actual,i)=>{
    const {scratch_peak:oldPeak,zero_scratch_oom:oldOom,...expected}=before.cases[i];
    const {scratch_peak:newPeak,zero_scratch_oom:newOom,...value}=actual;
    assert.deepEqual(value,expected);assert.ok(newPeak<=oldPeak);
    assert.equal(oldOom,oldPeak>0);assert.equal(newOom,newPeak>0);
    const compact=actual.lag<=24 && actual.overlap<=actual.n/2;
    assert.equal(newPeak===0,compact);
    if(compact)avoided++;else fallbacks++;
    maxReduction=Math.max(maxReduction,oldPeak-newPeak);
    return {...actual,reference_scratch_peak:oldPeak};
  });
  assert.ok(avoided&&fallbacks);
  const source='upstream/celt/celt_lpc.c';
  const report={passed:true,scope:'Host generic32 isolated autocorrelation. Bit-exact correlation and shift, unchanged input, required allocation/OOM preserved. Not physical CPU or whole-decoder RAM.',
    sanitizers:sanitize?['address','undefined']:[],compiler:after.compiler,flags:after.flags,
    allocation_avoided_cases:avoided,original_fallback_cases:fallbacks,max_peak_reduction_bytes:maxReduction,
    source_sha256_lf:{[source]:sha256(Buffer.from(fs.readFileSync(path.join(component,source),'utf8').replace(/\r\n/g,'\n')))},cases};
  if(output)fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={run};
if(require.main===module){const i=process.argv.indexOf('--output');run({output:i<0?undefined:process.argv[i+1],sanitize:!process.argv.includes('--no-sanitize')})
  .then(r=>console.log(JSON.stringify({passed:r.passed,cases:r.cases.length,avoided:r.allocation_avoided_cases,fallbacks:r.original_fallback_cases,maxReduction:r.max_peak_reduction_bytes})))
  .catch(e=>{console.error(e.stack);process.exitCode=1;});}

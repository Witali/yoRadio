// Verify a representation-only rewrite against all previously saved bitstreams.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {build}=require('./build_rcpdm8_quality');
const {execute}=require('./run_rcpdm_radio');
const root=path.resolve(__dirname,'../..');
const output=path.resolve(process.argv[2]||'.build/rcpdm-simple-one-branch-proof');
const source=path.join(root,'docs/benchmarks/esp8266-rcpdm-simple-2026-09-06/results.json');
const before=JSON.parse(fs.readFileSync(source,'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const exe=build(path.join(output,'build'),'rcpdm_simple_quality');
const selfTest=JSON.parse(execute(exe,['--self-test']).stdout);
const cases=[];
for(const c of before.cases) {
  const pcm=path.resolve(root,c.pcm); assert.equal(sha(pcm),c.pcm_sha256);
  const prefix=path.join(output,c.id); execute(exe,[pcm,prefix]);
  for(const [mode,expected] of Object.entries(c.bitstream_sha256)) assert.equal(sha(`${prefix}.${mode}.bin`),expected,`${c.id}: ${mode}`);
  cases.push({id:c.id,pcm_sha256:c.pcm_sha256,bitstream_sha256:c.bitstream_sha256});
}
const result={pass:true,self_test:selfTest,source_sha256:sha(path.join(root,'tests/native/rcpdm_simple.h')),
  reference_report_sha256:sha(source),cases,bitstreams_checked:cases.reduce((n,c)=>n+Object.keys(c.bitstream_sha256).length,0)};
fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
console.log(`All ${result.bitstreams_checked} bitstreams unchanged; ${selfTest.word_state_comparisons} word/state and ${selfTest.batch_word_checks} batch checks passed.`);

const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {execute}=require('./run_rcpdm_radio');
const root=path.resolve(__dirname,'../..');
const source=path.join(root,'radio_output/rcpdm8-quality');
const target=path.join(root,'docs/benchmarks/esp8266-rcpdm8-quality-2026-09-06');
const result=JSON.parse(fs.readFileSync(path.join(source,'results.json'),'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
if(result.cases.length!==9 || result.self_test.comparisons!==2959296 || !result.self_test.pass) throw Error('Incomplete result');
for(const [file,expected] of Object.entries(result.source_sha256)) if(sha(path.join(root,file))!==expected) throw Error(`Modified source: ${file}`);
for(const c of result.cases) {
  if(sha(c.pcm)!==c.pcm_sha256) throw Error(`PCM hash mismatch: ${c.id}`);
  for(const [name,expected] of Object.entries(c.bitstream_sha256)) if(sha(path.join(source,`${c.id}.${name}.bin`))!==expected) throw Error('Bitstream hash mismatch');
  for(const [name,data] of Object.entries(c.listening)) if(data.clipped || sha(path.join(source,`${c.id}.${name}.wav`))!==data.sha256) throw Error('WAV validation failed');
  c.pcm=path.relative(root,c.pcm).replaceAll('\\','/');
}
fs.mkdirSync(target,{recursive:true});
fs.writeFileSync(path.join(target,'results.json'),JSON.stringify(result,null,2)+'\n');
const tests=execute(process.execPath,['--test','tests/esp8266-rcpdm8-quality.test.js','tests/esp8266-rcpdm.test.js'],{cwd:root});
fs.writeFileSync(path.join(target,'native-tests.log'),tests.stdout+tests.stderr);
const python=process.argv[2] || 'python';
const model=execute(python,['tests/rcpdm8_quality_model_test.py'],{cwd:root});
fs.writeFileSync(path.join(target,'model-tests.log'),model.stdout+model.stderr);
console.log('Archived 9 cases, 54 verified bitstreams, 54 unclipped WAVs; native/model regressions passed.');

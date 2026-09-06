// Archive evidence only. Copyrighted broadcast/PCM/PDM files stay local.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {execute} = require('./run_rcpdm_radio');
const root = path.resolve(__dirname,'../..');
const capture = path.resolve(process.argv[2] || path.join(root,'radio_output/rcpdm-real-radio-20260906'));
const destination = path.resolve(process.argv[3] || path.join(root,'docs/benchmarks/esp8266-rcpdm-real-radio-2026-09-06'));
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const manifest = JSON.parse(fs.readFileSync(path.join(capture,'manifest.json'),'utf8'));
const result = JSON.parse(fs.readFileSync(path.join(capture,'benchmark-repeat/results.json'),'utf8'));
if (result.cases.length !== 15 || result.cases.some(c => c.variants.length !== 14 || c.bitMismatches || c.stateMismatches || c.wordMismatches)) throw Error('Incomplete/failed benchmark');
for (const clip of manifest.clips.filter(c=>c.ok)) {
  if (hash(path.join(capture,clip.file)) !== clip.sha256 || hash(path.join(capture,clip.pcm)) !== clip.pcmSha256) throw Error(`Capture checksum mismatch: ${clip.id}`);
}
for (const c of result.cases.filter(c=>c.volume===254)) {
  for (const [file, expected] of Object.entries(c.savedOutputs))
    if (hash(path.join(capture,'benchmark-repeat',file)) !== expected) throw Error(`Output checksum mismatch: ${file}`);
  if (c.savedOutputs[`${c.id}-v254.original.rcpdm32le`] !== c.savedOutputs[`${c.id}-v254.state4.rcpdm32le`]) throw Error('Saved bitstreams differ');
}
fs.mkdirSync(destination,{recursive:true});
const clips = manifest.clips.map(c=>({id:c.id,name:c.name,url:c.url,capturedUtc:c.capturedUtc,
  file:c.file,bytes:c.bytes,sha256:c.sha256,pcm:c.pcm,pcmBytes:c.pcmBytes,pcmSha256:c.pcmSha256,
  seconds:c.pcmSeconds,codec:c.probe?.streams[0]?.codec_name,profile:c.probe?.streams[0]?.profile,
  bitrate:Number(c.probe?.streams[0]?.bit_rate),sampleRate:c.sampleRate,channels:c.channels,
  captureWarnings:c.captureWarnings,decodeWarnings:c.decodeWarnings,ok:c.ok}));
fs.writeFileSync(path.join(destination,'captures.json'),JSON.stringify({capturedUtc:manifest.capturedUtc,
  decoder:manifest.decoder,provenance:manifest.provenance,localDirectory:path.relative(root,capture).replaceAll('\\','/'),clips},null,2)+'\n');
for (const [from,to] of [['benchmark-final/results.json','exploratory-results.json'],['benchmark-repeat/results.json','results.json'],['benchmark-repeat/build.log','build.log']])
  fs.copyFileSync(path.join(capture,from),path.join(destination,to));
const tests = execute(process.execPath,['--test','tests/esp8266-rcpdm-radio.test.js','tests/esp8266-rcpdm-run-analysis.test.js','tests/esp8266-rcpdm.test.js','tests/esp8266-direct-pdm.test.js'],{cwd:root});
fs.writeFileSync(path.join(destination,'tests.log'),tests.stdout+tests.stderr);
const select = (c,n) => c.variants.find(v=>v.name===n);
const summary = {samples:result.cases.reduce((sum,c)=>sum+c.samples,0),variants:14,
  wordStateComparisons:result.cases.reduce((sum,c)=>sum+c.samples*14,0),
  fullVolume:result.cases.filter(c=>c.volume===254).map(c=>({id:c.id,
    productionMsPerAudioSecond:select(c,'production').medianUs*48/c.samples,
    variants:Object.fromEntries(c.variants.map(v=>[v.name,{coveredBitsPercent:v.coveredBitsPercent,groups:v.groups,
      highGroups:v.highGroups,wordsWithGroupPercent:100*v.wordsWithGroup/c.samples,
      timeRatio:v.medianUs/select(c,'production').medianUs}]))})),
  timeRatioRanges:Object.fromEntries(result.cases[0].variants.map(v=>{const values=result.cases.map(c=>select(c,v.name).medianUs/select(c,'production').medianUs);return[v.name,{min:Math.min(...values),max:Math.max(...values)}]}))};
fs.writeFileSync(path.join(destination,'summary.json'),JSON.stringify(summary,null,2)+'\n');
console.log(`Archived 15 cases / ${summary.wordStateComparisons} word+state comparisons; all audio hashes and 6 host regressions passed.`);

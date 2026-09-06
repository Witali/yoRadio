const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname,'../..');
function execute(command,args,options={}) {
  const r = spawnSync(command,args,{encoding:'utf8',windowsHide:true,timeout:240000,maxBuffer:8*1024*1024,...options});
  if (r.error || r.status !== 0) throw Error(`${command}: ${r.error || r.status}\n${r.stdout}\n${r.stderr}`);
  return r;
}
function findVcVars() {
  const base = 'C:/Program Files/Microsoft Visual Studio';
  if (!fs.existsSync(base)) throw Error('Visual Studio C++ build tools not installed');
  for (const version of fs.readdirSync(base).sort().reverse()) {
    const directory = path.join(base,version);
    if (!fs.statSync(directory).isDirectory()) continue;
    for (const edition of fs.readdirSync(directory).sort().reverse()) {
      const candidate = path.join(directory,edition,'VC/Auxiliary/Build/vcvars64.bat');
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  throw Error('vcvars64.bat not found');
}
function build(directory) {
  fs.mkdirSync(directory,{recursive:true});
  const exe = path.join(directory,process.platform === 'win32' ? 'rcpdm-radio.exe' : 'rcpdm-radio');
  const source = path.join(__dirname,'rcpdm_radio_benchmark.cpp');
  const includes = [path.join(root,'esp8266/rtos-sdk-native/main'),path.join(root,'tests/native')];
  let log;
  if (process.platform === 'win32') {
    const cmd = path.join(directory,'build.cmd');
    fs.writeFileSync(cmd,`@call "${findVcVars()}" >nul\r\n@if errorlevel 1 exit /b %errorlevel%\r\n@cl /nologo /std:c++17 /O2 /EHsc /W4 ${includes.map(p => `/I"${p}"`).join(' ')} "${source}" /Fe:"${exe}"\r\n`);
    const result = execute('cmd.exe',['/d','/c',cmd],{cwd:directory});
    log = result.stdout+result.stderr;
  } else {
    const result = execute('c++',['-std=c++17','-O3','-Wall','-Wextra',...includes.map(p=>`-I${p}`),source,'-o',exe],{cwd:directory});
    log = result.stdout+result.stderr;
  }
  fs.writeFileSync(path.join(directory,'build.log'),log);
  return exe;
}
function sha256(file) { return crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex'); }
function main() {
  const capture = path.resolve(process.argv[2] || path.join(root,'radio_output/rcpdm-real-radio-20260906'));
  const output = path.resolve(process.argv[3] || path.join(capture,'benchmark'));
  const manifest = JSON.parse(fs.readFileSync(path.join(capture,'manifest.json'),'utf8'));
  const exe = build(output);
  const selfTest = JSON.parse(execute(exe,['--self-test']).stdout);
  console.log(`Self-test: ${selfTest.wordStateComparisons} word/state comparisons passed`);
  const sources = ['esp8266/rtos-sdk-native/main/rc_pdm.h','tests/native/rcpdm_variants.h','tests/native/rcpdm_runs.h','tools/esp8266_audio_profile/rcpdm_radio_benchmark.cpp'];
  const result = {measuredUtc:new Date().toISOString(),platform:process.platform,arch:process.arch,
    cpu:os.cpus()[0].model,compiler:process.platform === 'win32' ? 'MSVC /O2 /std:c++17' : 'c++ -O3 -std=c++17',
    selfTest,sourceHashes:Object.fromEntries(sources.map(file=>[file,sha256(path.join(root,file))])),
    pipeline:'FFmpeg decode to native-rate signed 16-bit PCM; native Q15 gain, neutral balance, normalization off, C stereo /2, native hold resampler to 48 kHz, 32-bit RCPDM MSB first.',
    timing:'7 rotating rounds; only modulation and word stores, no counters, decoding, I/O, gain or resampling. One warmup per variant. Desktop wall time, NOT LX106 cycles.', cases:[]};
  for (const clip of manifest.clips.filter(c=>c.ok)) {
    if (sha256(path.join(capture,clip.pcm)) !== clip.pcmSha256 || sha256(path.join(capture,clip.file)) !== clip.sha256) throw Error(`Modified capture ${clip.id}`);
    for (const volume of [254,128,64]) {
      const prefix = path.join(output,`${clip.id}-v${volume}`);
      const args = [path.join(capture,clip.pcm),String(clip.sampleRate),String(clip.channels),String(volume),'7',prefix];
      if (volume === 254) args.push('--save');
      const run = JSON.parse(execute(exe,args).stdout);
      run.id = clip.id; run.name = clip.name;
      if (volume === 254) {
        run.savedOutputs = Object.fromEntries(['mono48.s16le','original.rcpdm32le','state4.rcpdm32le'].map(suffix => [`${clip.id}-v254.${suffix}`,sha256(`${prefix}.${suffix}`)]));
      }
      result.cases.push(run);
      fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(result,null,2)+'\n');
      const baseline = run.variants[0].medianUs;
      console.log(`${clip.id} volume=${volume}: ${run.samples} samples; `+run.variants.filter(v=>v.groupSize).map(v=>`${v.name} ${(baseline/v.medianUs).toFixed(2)}x/${v.coveredBitsPercent.toFixed(3)}% bits`).join(', '));
    }
  }
  console.log(`Saved ${result.cases.length} cases in ${output}`);
}
module.exports = {build,execute};
if (require.main === module) main();

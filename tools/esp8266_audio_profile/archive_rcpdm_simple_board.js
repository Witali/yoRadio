const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {execute}=require('./run_rcpdm_radio');
const {summarize}=require('./summarize_rcpdm_simple_board');
const root=path.resolve(__dirname,'../..');
const source=path.resolve(process.argv[2]||path.join(root,'.build/rcpdm-simple-board/runs'));
const target=path.resolve(process.argv[3]||path.join(root,'docs/benchmarks/esp8266-rcpdm-simple-board-2026-09-06'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const record=JSON.parse(fs.readFileSync(path.join(source,'run-manifest.json'),'utf8'));
assert.equal(record.restored,true); assert.equal(record.restore_boot_verified,true);
assert.deepEqual(record.rounds.map(r=>r.mode),['production','simple','simple','production']);
const results=summarize(source);
fs.mkdirSync(target,{recursive:true});
results.measured_utc=record.finished_utc;
results.port=record.port;
results.restore_app0_sha256=record.backup.app0_sha256;
results.images={}; results.static_memory={}; results.source_sha256={};
for(const file of ['esp8266/rtos-sdk-native/main/native_audio_output.c',
  'esp8266/rtos-sdk-native/main/audio_output_benchmark.c','esp8266/rtos-sdk-native/main/esp8266_nodac_i2s.c',
  'esp8266/rtos-sdk-native/main/rc_pdm.h','esp8266/rtos-sdk-native/main/CMakeLists.txt',
  'tests/native/rcpdm_simple.h','tests/native/rcpdm_simple_reference.h']) results.source_sha256[file]=sha(path.join(root,file));
for(const mode of ['production','simple']) {
  const image=record.images[mode]; assert.equal(sha(image.binary),image.sha256);
  results.images[mode]={file:path.relative(root,image.binary).replaceAll('\\','/'),bytes:image.bytes,sha256:image.sha256};
  const build=path.join(root,'.build/rcpdm-speed-results',path.basename(path.dirname(image.binary)));
  const sections=fs.readFileSync(path.join(build,'sections.txt'),'utf8');
  results.static_memory[mode]=Object.fromEntries([...sections.matchAll(/^(\.(?:iram0|dram0|flash)\.\w+)\s+(\d+)\s+\d+/gm)].map(m=>[m[1],Number(m[2])]));
  fs.copyFileSync(path.join(build,'build.log'),path.join(target,`${mode}-build.log`));
  fs.writeFileSync(path.join(target,`${mode}-sections.txt`),JSON.stringify(results.static_memory[mode],null,2)+'\n');
  const asm=fs.readFileSync(path.join(build,'disassembly.txt'),'utf8');
  const relevant=[];
  for(const symbol of ['i2s_pdm_pack32','i2s_rcpdm_fill']) {
    const fragment=asm.match(new RegExp(`^[0-9a-f]+ <${symbol}>:[\\s\\S]*?(?=^[0-9a-f]+ <|$(?![\\s\\S]))`,'m'));
    assert.ok(fragment,`Missing ${symbol}`); relevant.push(fragment[0]);
  }
  fs.writeFileSync(path.join(target,`${mode}-packers.asm`),relevant.join('\n').trimEnd()+'\n');
  fs.copyFileSync(path.join(path.dirname(image.binary),'manifest.json'),path.join(target,`${mode}-image.json`));
}
fs.copyFileSync(path.join(root,'.build/rcpdm-speed/sdkconfig'),path.join(target,'sdkconfig'));
for(const run of results.runs) fs.copyFileSync(path.join(source,run.file),path.join(target,run.file));
const restored=fs.readFileSync(path.join(source,'restore-uart.log'),'utf8').replace(/\x1b\[[0-9;]*m/g,'');
fs.writeFileSync(path.join(target,'restore-summary.log'),restored.split(/\r?\n/).filter(s=>/native starting|profile:|Settings restored|SPIFFS mounted|Loaded index|WebUI:|DHCP|got ip|IP address/.test(s)).join('\n')+'\n');
const flashed=fs.readFileSync(path.join(source,'restore-flash.log'),'utf8');
assert.match(flashed,/Hash of data verified/);
fs.writeFileSync(path.join(target,'restore-verified.log'),flashed.split(/\r?\n/).filter(s=>/Wrote |Hash of data verified/.test(s)).join('\n')+'\n');
const tests=execute(process.execPath,['--test','tests/esp8266-rcpdm-board-runner.test.js',
  'tests/esp8266-rcpdm-simple-asm.test.js',
  'tests/esp8266-rcpdm-simple.test.js','tests/esp8266-direct-pdm.test.js','tests/esp8266-rcpdm.test.js',
  'tests/esp8266-audio-output-benchmark.test.js','tests/esp8266-i2s-pdm-output.test.js'],{cwd:root});
fs.writeFileSync(path.join(target,'host-tests.log'),tests.stdout+tests.stderr);
fs.writeFileSync(path.join(target,'results.json'),JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify(results.summary,null,2));
console.log('Archived physical ABBA results, verified firmware hashes and host tests. Private flash backup excluded.');

// Archive only public benchmark evidence, never the private flash backup or Wi-Fi boot log.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const {MODES,summarize}=require('./summarize_rcpdm_feedback_board');
const root=path.resolve(__dirname,'../..');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const json=file=>JSON.parse(fs.readFileSync(file,'utf8').replace(/^\uFEFF/,''));
function readToolText(file) {
  const data=fs.readFileSync(file);
  return data[0]===0xff&&data[1]===0xfe?data.subarray(2).toString('utf16le'):data.toString('utf8');
}
function main() {
  assert.equal(process.argv.length,4,'Usage: archive_rcpdm_feedback_board.js runs new-report-directory');
  const source=path.resolve(process.argv[2]),dest=path.resolve(process.argv[3]);
  assert.ok(!fs.existsSync(dest),'Use a fresh report directory');
  const record=json(path.join(source,'run-manifest.json'));
  assert.ok(record.restored&&record.full_flash_verified&&record.restore_boot_verified,'Restore and full-flash verification required');
  assert.deepEqual(record.modes,MODES);assert.equal(record.rounds.length,8);
  const result=summarize(source);
  result.started_utc=record.started_utc;result.finished_utc=record.finished_utc;
  result.order=record.rounds.map(r=>`${r.round}:${r.mode}`);
  result.restore={app0_sha256:record.backup.app0_sha256,flash_sha256:record.backup.flash_sha256,
    full_flash_verified:true,boot_verified:true};
  result.builds={};
  fs.mkdirSync(dest,{recursive:true});
  for(const mode of MODES) {
    const folder=path.join(root,'firmware/development/esp8266-rcpdm-feedback-benchmark',mode);
    const manifest=json(path.join(folder,'manifest.json'));
    assert.equal(sha(path.join(folder,'app.bin')),record.images[mode].sha256);
    assert.equal(sha(path.join(folder,'sdkconfig')),manifest.config_sha256.toLowerCase());
    const build=path.join(root,'.build/rcpdm-feedback-benchmark',mode);
    const sections=Object.fromEntries([...readToolText(path.join(build,'sections.txt')).matchAll(/^(\.[\w.]+)\s+(\d+)\s+\d+/gm)].map(m=>[m[1],Number(m[2])]));
    const symbols=[...readToolText(path.join(build,'symbols.txt')).matchAll(/^([\da-f]+) ([\da-f]+) (\w) (.+)$/gm)]
      .filter(m=>['i2s_pdm_pack32','i2s_rcpdm_fill','s_rcpdm','s_pdm_integrator'].includes(m[4]))
      .map(m=>({name:m[4],address:m[1],bytes:parseInt(m[2],16),type:m[3]}));
    result.builds[mode]={manifest,static_dram:sections['.dram0.data']+sections['.dram0.bss'],
      static_iram:sections['.iram0.vectors']+sections['.iram0.text']+sections['.iram0.bss'],sections,symbols};
    fs.copyFileSync(path.join(folder,'sdkconfig'),path.join(dest,`${mode}-sdkconfig`));
    const disassembly=readToolText(path.join(build,'disassembly.txt'));
    const functions=[...disassembly.matchAll(/^([\da-f]+) <([^>]+)>:[\s\S]*?(?=^[\da-f]+ <|$(?![\s\S]))/gm)]
      .filter(m=>['i2s_pdm_pack32','i2s_rcpdm_fill'].includes(m[2])).map(m=>m[0]);
    assert.ok(functions.length>0,'Missing actual firmware packer disassembly');
    fs.writeFileSync(path.join(dest,`${mode}-packers.asm.txt`),functions.join('\n').trimEnd()+'\n');
  }
  for(const run of result.runs) {
    const raw=fs.readFileSync(path.join(source,run.file),'utf8');
    const clean=raw.replace(/\x1b\[[0-9;]*m/g,'').split(/[\r\n]+/)
      .filter(s=>/audio_output_bench:|I2S[- ]|RCPDM|RC-PDM|isolated generated-PCM/.test(s)).join('\n')+'\n';
    fs.writeFileSync(path.join(dest,run.file),clean);
  }
  const verified=summarize(dest);
  assert.deepEqual(verified.summary,result.summary,'Sanitized log lost timing/proof data');
  fs.writeFileSync(path.join(dest,'results.json'),JSON.stringify(result,null,2)+'\n');
  console.log(JSON.stringify(result.summary,null,2));
}
if(require.main===module)main();

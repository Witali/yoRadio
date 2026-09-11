const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {compare,compareArtifacts}=require('../tools/esp8266_opus_profile/compare_raw.cjs');
const base=path.resolve(__dirname,'../firmware/development');
const read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
for (const variant of ['rotation192','stride1'])
test('archived '+variant+' rotation keeps all twenty exact-PCM attempts and the CELT slowdown',()=>{
  const dirs=['off','on'].map(x=>path.join(base,'esp8266-opus-'+variant+'-'+x));
  const saved=read(path.join(dirs[1],'comparison.json'));
  const runs=dirs.map((dir,k)=>Array.from({length:10},(_,i)=>{
    const file='run'+(i+1)+'.json',bytes=fs.readFileSync(path.join(dir,file));
    assert.ok(fs.statSync(path.join(dir,'run'+(i+1)+'.log')).size>0);
    // Git on Windows can convert text to CRLF; archived input hashes used LF.
    assert.equal(crypto.createHash('sha256').update(bytes.toString('utf8').replace(/\r\n/g,'\n')).digest('hex'),saved.inputs[k?'candidate':'reference'][i].sha256);
    return JSON.parse(bytes);
  }));
  const actual=JSON.parse(JSON.stringify(compare(...runs)));
  for(const key of ['reference','candidate','cases'])assert.deepEqual(actual[key],saved[key],key);
  compareArtifacts(...dirs.map(dir=>read(path.join(dir,'manifest.json'))),'opus_rotation_lx106');
  assert.equal(saved.comparison_valid,true);
  assert.deepEqual(saved.reference.observation_errors,[]);
  assert.deepEqual(saved.candidate.observation_errors,[]);
  for(let i=2;i<5;i++)assert.ok(actual.candidate.cases[i].task_budget_percent.median>actual.reference.cases[i].task_budget_percent.median);
});

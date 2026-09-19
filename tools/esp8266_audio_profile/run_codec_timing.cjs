// Repeated on-board measurements only: no implicit OTA, reset or serial use.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const args=process.argv.slice(2),get=(k,d)=>args.includes(k)?args[args.indexOf(k)+1]:d;
const mode=get('--mode','opus'),runs=Number(get('--runs',10)),fixtures=get('--fixtures');
assert.ok(['opus','helix'].includes(mode));assert.ok(Number.isInteger(runs)&&runs>=1&&runs<=100);
assert.ok(fixtures,'--fixtures is required');
const out=path.resolve(get('--output','.build/codec-timing/'+mode));fs.mkdirSync(out,{recursive:true});
for(let i=1;i<=runs;++i) {
  const file=path.join(out,'run'+i+'.json'),log=path.join(out,'run'+i+'.log');
  assert.ok(!fs.existsSync(file),'Refuse to overwrite evidence: '+file);
  console.log(`${mode}: run ${i}/${runs}`);
  const r=spawnSync(process.execPath,[path.join(__dirname,'../esp8266_opus_profile/run_board.cjs'),
    '--base',get('--base','http://192.168.100.6'),'--fixtures',path.resolve(fixtures),
    '--output',file,'--interval-ms',get('--interval-ms','10000'),...(mode==='helix'?['--helix']:[])],
    {encoding:'utf8',timeout:330000,maxBuffer:4e6});
  fs.writeFileSync(log,(r.stdout||'')+(r.stderr||''));
  if(r.error||r.status!==0)throw Error('Measurement failed; retained '+file+' '+(r.error||r.stderr));
  const v=JSON.parse(fs.readFileSync(file));
  console.log(v.comparison.map(x=>`${x.name}: ${x.task_budget_percent.toFixed(2)}%`).join('; '));
}

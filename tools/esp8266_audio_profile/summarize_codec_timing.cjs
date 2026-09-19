const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
function median(a){a=[...a].sort((x,y)=>x-y);return(a[(a.length-1)>>1]+a[a.length>>1])/2;}
function summarize(directories) {
  const groups=new Map();
  for(const dir of directories)for(const name of fs.readdirSync(dir).filter(n=>/^run\d+\.json$/.test(n))) {
    const file=path.join(dir,name),r=JSON.parse(fs.readFileSync(file));
    assert.equal(r.final?.state,3,file+' incomplete');assert.equal(r.final.error,0);
    assert.equal(r.final.physical_output,false);assert.ok(!r.final.profile_stage&&!r.final.functions);
    assert.ok(r.fixtures&&r.final.results.length===r.fixtures.fixtures.length);
    r.final.results.forEach((v,i)=>{
      const f=r.fixtures.fixtures[i],codec=f.codec||'Opus',key=codec+'/'+f.name;
      assert.equal(Boolean(r.final.helix_timing),codec!=='Opus','Wrong firmware benchmark marker');
      assert.equal(v.error,0);assert.equal(v.samples,f.samples*r.final.rounds);assert.equal(v.packets,f.packet_count*r.final.rounds);
      assert.ok(v.task_us>0&&v.samples>0);if(codec==='Opus')assert.equal(v.pcm_hash,f.expected_hash);
      const groupsForCase=groups.get(key)||[];
      if(groupsForCase.length)assert.deepEqual(f,groupsForCase[0].f,'Do not mix changed fixtures');
      groupsForCase.push({file,f,v,empty:r.final.empty_task_us,codec});groups.set(key,groupsForCase);
    });
  }
  const rows=[];
  for(const [key,g] of groups) {
    assert.ok(g.every(x=>x.v.pcm_hash===g[0].v.pcm_hash),key+' changing PCM warm-up hash');
    const values=g.map(x=>({avg:x.v.task_us/x.v.packets,
      budget:x.v.task_us*4.8/x.v.samples,
      corrected:Math.max(0,x.v.task_us-x.empty*x.v.packets)*4.8/x.v.samples,
      wall:x.v.wall_us/x.v.packets}));
    rows.push({codec:g[0].codec,name:g[0].f.name,kbps:g[0].f.bitrate_kbps,
      actual_kbps:g[0].f.actual_kbps??g[0].f.bitrate_kbps,
      runs:g.length,frames:g.reduce((n,x)=>n+x.v.packets,0),frame_audio_ms:g[0].f.samples/g[0].f.packet_count/48,
      mean_decode_ms:median(values.map(v=>v.avg))/1000,cpu_budget_percent:median(values.map(v=>v.budget)),
      corrected_budget_estimate_percent:median(values.map(v=>v.corrected)),
      cpu_budget_min_percent:Math.min(...values.map(v=>v.budget)),cpu_budget_max_percent:Math.max(...values.map(v=>v.budget)),
      mean_wall_ms:median(values.map(v=>v.wall))/1000,max_wall_ms:Math.max(...g.map(x=>x.v.max_wall_us))/1000,
      min_dram_bytes:Math.min(...g.map(x=>x.v.min_dram)),stack_free_bytes:Math.min(...g.map(x=>x.v.stack_free_lifetime)),
      pcm_hash:g[0].v.pcm_hash,files:g.map(x=>x.file.replaceAll('\\','/'))});
  }
  return {method:'Median of per-run mean task runtime; interrupts/instrumentation charged to task remain. Not whole-radio CPU.',rows};
}
function table(report) {
  return '| Кодек | кбит/с | Аудио в кадре, мс | Декодирование, мс/кадр | CPU-бюджет | Максимум wall, мс |\n'+
    '|---|---:|---:|---:|---:|---:|\n'+report.rows.map(r=>`| ${r.codec} | ${r.kbps} | ${r.frame_audio_ms.toFixed(2)} | ${r.mean_decode_ms.toFixed(3)} | ${r.cpu_budget_percent.toFixed(2)}% | ${r.max_wall_ms.toFixed(3)} |`).join('\n')+'\n';
}
module.exports={median,summarize,table};
if(require.main===module) {
  const args=process.argv.slice(2),out=args.shift();assert.ok(out&&args.length,'output-base input-directory...');
  const report=summarize(args);fs.mkdirSync(path.dirname(out),{recursive:true});
  fs.writeFileSync(out+'.json',JSON.stringify(report,null,2)+'\n');fs.writeFileSync(out+'.md',table(report));console.log(table(report));
}

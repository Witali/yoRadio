// Whole-snapshot static inventory. Counts are NOT execution frequencies/cycles.
const fs=require('node:fs'),path=require('node:path');
const {root,component,run,sourceHash}=require('./export.cjs');
function audit(nm,elf){
 const base=path.join(component,'asm/lx106'),manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json')));
 const linked=new Map([...run(nm,['-S',elf]).matchAll(/^[0-9a-f]+ ([0-9a-f]+) [tT] (\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 const functions=[];
 for(const f of manifest.files){
  const text=fs.readFileSync(path.join(base,f.asm),'utf8');
  for(const name of f.functions){
   const escape=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
   const body=text.match(new RegExp('^'+escape(name)+':[\\s\\S]*?(?=^\\s*\\.size\\s+'+escape(name)+',)','m'))?.[0];
   if(!body)throw Error('Missing body '+name);
   const ops=body.split(/\r?\n/).map(l=>l.split('#')[0].trim()).filter(l=>l&&!l.startsWith('.')&&!l.endsWith(':'));
   const calls=ops.filter(l=>/^call/.test(l)).map(l=>l.split(/\s+/)[1]);
   functions.push({source:f.source,name,linked:linked.has(name),linked_bytes:linked.get(name)??null,instructions:ops.length,
    sar_setups:ops.filter(l=>/^(ssr|ssl|ssa8l|ssa8b)\s/.test(l)).length,
    narrow_loads:ops.filter(l=>/^(l8ui|l16ui|l16si)\s/.test(l)).length,
    stack_accesses:ops.filter(l=>/^[ls](?:8|16|32)\S*\s+\w+,\s*sp,/.test(l)).length,
    arithmetic_helpers:calls.filter(l=>/^__(?:[um]*div|[um]*mod|muldi|ash|lsh)/.test(l)),calls});
  }
 }
 const report={date:new Date().toISOString(),scope:'Every exported function; linked marks name presence in the control ELF. Static counts, not hotness, latency or flash-vs-RAM attribution.',baseline_manifest_sha256:sourceHash(path.join(base,'manifest.json')),functions};
 const output=path.join(root,'firmware/development/esp8266-opus-hoisted-asm-library/algorithm-inventory.json');
 fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log('Functions',functions.length,'linked',functions.filter(f=>f.linked).length);
 console.table(functions.filter(f=>f.linked&&f.sar_setups).sort((a,b)=>b.sar_setups-a.sar_setups).slice(0,15).map(({name,linked_bytes,sar_setups,stack_accesses,narrow_loads})=>({name,linked_bytes,sar_setups,stack_accesses,narrow_loads})));
 return report;
}
module.exports={audit};if(require.main===module)audit(process.argv[2],process.argv[3]);

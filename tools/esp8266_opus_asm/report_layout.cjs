// Independent placement-only A/B/C/A experiment. Preserve all numbered runs.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,hash,run}=require('./export.cjs');
const {archive}=require('./report_bands.cjs'),{compare}=require('../esp8266_opus_profile/compare_raw.cjs');
const {selectHighBitrate}=require('./selection.cjs'),{wordAt}=require('./audit_update_link.cjs');
const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
const control='esp8266-opus-bands-tell-inline-v1',variant=n=>'esp8266-opus-bands-layout'+n+'-v1';
const art=v=>path.join(root,'firmware/development',v),read=p=>JSON.parse(fs.readFileSync(p,'utf8').replace(/^\uFEFF/,''));
function reachableDisassembly(elf,s,readBlock=(start,end)=>run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+start.toString(16),'--stop-address=0x'+end.toString(16),elf])){
 const pending=[s.address],rows=new Map(),end=s.address+s.bytes;
 while(pending.length){
  const start=pending.pop();if(rows.has(start))continue;
  assert.ok(start>=s.address&&start<end,'Branch leaves '+s.name);
  const text=readBlock(start,end);
  let next=start,stopped=false;
  for(const line of text.split(/\r?\n/)){
   const m=line.match(/^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*$/);if(!m)continue;
   const address=parseInt(m[1],16);assert.equal(address,next,'Disassembly boundary');
   if(rows.has(address)){stopped=true;break;}
   assert.ok([4,6].includes(m[2].length));assert.doesNotMatch(m[3],/^\.|unknown|ill|excw|^jx$/,'Invalid reachable instruction '+line);
   rows.set(address,line);next+=m[2].length/2;
   if(/^b|^j$/.test(m[3])){
    const t=m[4].match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);assert.ok(t,'Unresolved branch');pending.push(parseInt(t[1],16));
   }
   if(/^(j|ret(?:\.n)?)$/.test(m[3])){stopped=true;break;}
  }
  assert.ok(stopped,'Unexpected fall-through at function end');
 }
 return [...rows].sort((a,b)=>a[0]-b[0]).map(([,line])=>line).join('\n');
}
function linkedGraph(text,resolveWord,resolveAddress){
 const rows=[];
 for(const line of text.split(/\r?\n/)){
  const m=line.match(/^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*$/);if(!m)continue;
  if(m[3]==='.byte'){assert.match(m[4],/^00$/);assert.ok(rows.length&&/^(j|ret(?:\.n)?)$/.test(rows.at(-1).op));continue;}
  assert.doesNotMatch(m[3],/unknown|ill/);rows.push({address:parseInt(m[1],16),op:m[3],args:m[4]});
 }
 assert.ok(rows.length);
 const target=r=>r.args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);
 const branched=new Set(rows.filter(r=>r.op!=='l32r').flatMap(r=>target(r)?[parseInt(target(r)[1],16)]:[]));
 const normalized=[];let relaxed=0;
 for(let i=0;i<rows.length;i++){
  const r={...rows[i]},t=target(r);
  // CALL0 clobbers a0 with the return address. A linker-generated
  // L32R a0/function; CALLX0 a0 has the same call0 ABI, but different cost.
  if(r.op==='l32r'&&r.args.startsWith('a0,')&&rows[i+1]?.op==='callx0'&&rows[i+1].args==='a0'&&!branched.has(rows[i+1].address)){
   assert.ok(t);r.op='call0';r.args=resolveAddress(resolveWord(parseInt(t[1],16)));r.resolved=true;relaxed++;i++;
  }
  normalized.push(r);
 }
 const index=new Map(normalized.map((r,i)=>[r.address,i]));
 const graph=normalized.map(r=>{
  let op=r.op.replace(/\.n$/,''),args=r.args;const t=target(r);
  if(t){
   const address=parseInt(t[1],16);let value;
   if(op==='l32r')value='literal:'+resolveAddress(resolveWord(address));
   else if(op==='call0')value=resolveAddress(address);
   else {assert.ok(index.has(address),'Nonlocal branch '+r.args);value='instruction:'+index.get(address);}
   args=args.slice(0,args.length-t[0].length)+(t[0].startsWith(',')?', ':'')+value;
  }
  const regs=args.split(/,\s*/);if(op==='or'&&regs.length===3&&regs[1]===regs[2]){op='mov';args=regs.slice(0,2).join(', ');}
  return op+' '+args;
 });
 return {graph,physical_instruction_count:rows.length,relaxed_indirect_calls:relaxed};
}
function inspect(v){
 const elf=path.join(root,'.build',v,'yoradio_esp8266_helix_native.elf');
 const sections=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-size.exe'),['-A',elf]).matchAll(/^(\.(?:iram0|dram0|flash)\.\S+)\s+(\d+)\s+/gm)].map(m=>[m[1],Number(m[2])]));
 const all=[...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-S',elf]).matchAll(/^([0-9a-f]+)\s+([0-9a-f]+)\s+(\S)\s+(.+)$/gm)].map(m=>({address:parseInt(m[1],16),bytes:parseInt(m[2],16),type:m[3],name:m[4]}));
 const resolve=a=>{
  const exact=all.filter(s=>s.address===a).sort((x,y)=>x.name.localeCompare(y.name));if(exact.length)return exact[0].name;
  const inside=all.filter(s=>a>s.address&&a<s.address+s.bytes).sort((x,y)=>x.bytes-y.bytes||x.name.localeCompare(y.name));
  return inside.length?inside[0].name+'+0x'+(a-inside[0].address).toString(16):'0x'+a.toString(16);
 };
 const functions={};
 for(const name of ['quant_partition','quant_band','quant_all_bands','ec_tell_frac','ec_dec_bits']){
  const s=all.find(s=>s.name===name);assert.ok(s);
  // Follow real entry/branch boundaries. Linear objdump misdecodes unreachable
  // alignment zeros after J as the beginning of the next valid instruction.
  const disassembly=reachableDisassembly(elf,s);
  functions[name]={...s,disassembly,...linkedGraph(disassembly,a=>wordAt(elf,a),resolve)};
 }
 return {elf_sha256:hash(fs.readFileSync(elf)),sections,functions};
}
function preflight(n){
 assert.ok([32,128].includes(n));const av=art(control),bv=art(variant(n)),ma=read(path.join(av,'manifest.json')),mb=read(path.join(bv,'manifest.json'));
 for(const [dir,m] of [[av,ma],[bv,mb]]){
  const app=fs.readFileSync(path.join(dir,'app.bin'));assert.equal(app.length,m.bytes);assert.equal(hash(app),m.app_sha256.toLowerCase());
  assert.equal(m.opus_benchmark,true);assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);
 }
 assert.equal(ma.opus_backend,'bands-tell-inline-asm');assert.equal(mb.opus_backend,'bands-layout'+n+'-asm');
 const identity=['opus_backend','opus_bands_tell_inline_manifest_sha256','opus_bands_layout_manifest_sha256','built_utc','source_revision','app_sha256','bytes'];
 for(const k of new Set([...Object.keys(ma),...Object.keys(mb)]))if(!identity.includes(k))assert.deepEqual(mb[k]??null,ma[k]??null,'Build profile changed: '+k);
 const recipe=path.join(component,'asm/lx106/bands-layout'+n+'.json'),rm=read(recipe);
 assert.equal(mb.opus_bands_layout_manifest_sha256.toLowerCase(),hash(fs.readFileSync(recipe)));
 assert.equal(rm.parent_sha256_lf,ma.opus_bands_tell_inline_manifest_sha256.toLowerCase());require('./verify.cjs').verify(mb.opus_backend);
 const a=inspect(control),b=inspect(variant(n));assert.ok(Object.keys(a.sections).length>=5);
 for(const [s,size] of Object.entries(a.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(b.sections[s],size,'Static RAM changed: '+s);
 for(const name of Object.keys(a.functions))assert.deepEqual(b.functions[name].graph,a.functions[name].graph,'Linked graph changed: '+name);
 const result={reference_manifest:ma,candidate_manifest:mb,recipe:rm,reference:a,candidate:b,static_ram_delta:0,linked_hot_graphs_exact:true};
 fs.writeFileSync(path.join(bv,'preflight.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify({pad:n,bytes:mb.bytes,static_ram_delta:0,linked_hot_graphs_exact:true,functions:Object.fromEntries(Object.entries(b.functions).map(([k,v])=>[k,{address:v.address,bytes:v.bytes,instructions:v.physical_instruction_count,indirect_calls:v.relaxed_indirect_calls}]))}));return result;
}
function report(n){
 const build=preflight(n),dest=art(variant(n));
 const a=archive(path.join(root,'.build/opus-layout-control-20260913'),path.join(dest,'controls/before'));
 const b=archive(path.join(root,'.build/opus-bands-layout'+n+'-20260913'),path.join(dest,'runs'));
 const a2=archive(path.join(root,'.build/opus-layout-control-repeat-20260913'),path.join(dest,'controls/after'));
 const fixtures=read(path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures/manifest.json'));
 for(const r of [...a,...b,...a2]){
  assert.equal(r.report.interval_ms,15000);assert.equal(r.report.final.profile_stage??0,0);assert.ok(!r.report.final.functions);
  for(const [i,v] of r.report.final.results.entries()){
   assert.equal(v.pcm_hash,fixtures.fixtures[i].expected_hash);assert.equal(v.samples,fixtures.fixtures[i].samples*r.report.final.rounds);assert.equal(v.packets,fixtures.fixtures[i].packet_count*r.report.final.rounds);
  }
 }
 const initial=compare(a.map(v=>v.report),b.map(v=>v.report)),repeated=compare(a2.map(v=>v.report),b.map(v=>v.report));
 const host=read(path.join(root,'.build/opus-bands-tell-inline/correctness.json'));assert.equal(host.passed,true);
 const parent=read(path.join(component,'asm/lx106/bands-tell-inline.json'));assert.equal(host.recipe_sha256_lf,parent.recipe_sha256_lf);
 const selection={initial:selectHighBitrate(initial.cases),repeated:selectHighBitrate(repeated.cases)};
 const compact=rows=>rows.map(({report,...r})=>r);
 const result={schema:1,initial,repeated,selection,build,host,inputs:{reference:compact(a),candidate:compact(b),repeated:compact(a2)},scope:'Placement-only, ten A/ten B/ten C/ten A; the two candidates share the same controls. Raw-only, no live qualification.'};
 fs.writeFileSync(path.join(dest,'comparison.json'),JSON.stringify(result,null,2)+'\n');
 console.table(initial.cases.map((c,i)=>({name:c.name,A:c.reference.task_budget_percent.median,B:c.candidate.task_budget_percent.median,A2:repeated.cases[i].reference.task_budget_percent.median,reduction:c.median_task_reduction_percent})));
 console.log(JSON.stringify(selection));return result;
}
module.exports={linkedGraph,reachableDisassembly,inspect,preflight,report};if(require.main===module){const n=Number(process.argv[2]);if(process.argv.includes('--preflight'))preflight(n);else report(n);}

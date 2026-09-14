// Exact address-only ADDX4 overlay over the best tell-inline parent.
// No arithmetic/entropy/table changes, new live registers, or additional RAM.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,sourceHash,run}=require('./export.cjs');
const {canonical}=require('./disassembly.cjs');
const kind='pvq-addx',source='upstream/celt/cwrs.c';
const baseline=()=>fs.readFileSync(path.join(component,'asm/lx106/gcc/'+source+'.s'),'utf8').replace(/\r\n/g,'\n');
const body=text=>text.match(/^decode_pulses:[\s\S]*?(?=^\s*\.size\s+decode_pulses,)/m)?.[0];
function pair(a,b){
 const s=a.match(/^slli\s+(a\d+),\s*(a\d+),\s*2$/);
 const t=b.match(/^add(?:\.n)?\s+(a\d+),\s*(a\d+),\s*(a\d+)$/);
 if(!s||!t||s[1]!==t[1])return null;
 const other=t[2]===s[1]&&t[3]!==s[1]?t[3]:t[3]===s[1]&&t[2]!==s[1]?t[2]:null;
 return other?{dst:s[1],index:s[2],base:other,op:`addx4 ${s[1]}, ${s[2]}, ${other}`}:null;
}
function replacements(text){
 const b=body(text);assert.ok(b,'decode_pulses missing');const lines=b.split('\n'),rows=[];
 for(let i=0;i<lines.length;i++){
  let j=i+1;while(j<lines.length&&(!lines[j].trim()||lines[j].trim().startsWith('#')))j++;
  const a=lines[i].split('#')[0].trim(),c=(lines[j]||'').split('#')[0].trim(),p=pair(a,c);
  // Labels/directives are not skipped: no entry can land between fused ops.
  if(p)rows.push({...p,i,j,before:[a,c]});
 }
 assert.equal(rows.length,20,'Pinned GCC address pairs changed');return {b,lines,rows};
}
function transform(text){
 text=text.replace(/\r\n/g,'\n');assert.doesNotMatch(text,/PVQ ADDX4/);
 const {b,lines,rows}=replacements(text);
 for(const p of rows){
  lines[p.i]='# PVQ ADDX4: '+p.before.join(' ; ')+' => one exact address operation.';
  lines[p.j]='\t'+p.op+'\t# dst = (index << 2) + base, modulo 2^32; shifted temporary dies here.';
 }
 lines.splice(1,0,'# PVQ ADDX4 overlay: call0 ABI, arguments/return and stack are unchanged.',
  '# Only dead address temporaries are fused; a0/a1/a12..a15 and SAR retain their original semantics.',
  '# No load/store widths, table contents, branch conditions or valid packet modes are changed.');
 return text.replace(b,lines.join('\n'));
}
// Normalize the original object/linked graph to the candidate, keeping all
// branch destinations. A target into the second instruction forbids fusion.
function fuseGraph(graph){
 const targets=new Set(graph.flatMap(s=>[...s.matchAll(/instruction:(\d+)/g)].map(m=>+m[1])));
 const map=new Map(),out=[];let count=0;
 for(let i=0;i<graph.length;i++){
  map.set(i,out.length);const p=pair(graph[i],graph[i+1]||'');
  if(p&&!targets.has(i+1)){out.push(p.op);map.set(i+1,out.length-1);i++;count++;}
  else out.push(graph[i]);
 }
 return {count,graph:out.map(s=>s.replace(/instruction:(\d+)/g,(_,n)=>{
  assert.ok(map.has(+n));return 'instruction:'+map.get(+n);
 }))};
}
// GAS relaxes an out-of-range conditional to its inverse over an unconditional
// jump. Shrinking the body can make that jump unnecessary. Normalize only the
// exact two-edge equivalence, never arbitrary branches or reachable padding.
function normalizeBranches(graph){
 const inverse={bltu:'bgeu',bgeu:'bltu',blt:'bge',bge:'blt',beq:'bne',bne:'beq',beqz:'bnez',bnez:'beqz',blti:'bgei',bgei:'blti',beqi:'bnei',bnei:'beqi'};
 const targets=new Set(graph.flatMap(s=>[...s.matchAll(/instruction:(\d+)/g)].map(m=>+m[1])));
 const out=[],map=new Map();let collapsed=0;
 for(let i=0;i<graph.length;i++){
  map.set(i,out.length);const b=graph[i].match(/^(\w+) (.*?)(?:, )?instruction:(\d+)$/),j=(graph[i+1]||'').match(/^j instruction:(\d+)$/);
  if(b&&j&&inverse[b[1]]&&+b[3]===i+2&&!targets.has(i+1)){
   const args=b[2].replace(/, $/,'');out.push(inverse[b[1]]+' '+args+(args?', ':'')+'instruction:'+j[1]);
   map.set(i+1,out.length-1);i++;collapsed++;
  }else out.push(graph[i]);
 }
 return {collapsed,graph:out.map(s=>s.replace(/instruction:(\d+)/g,(_,n)=>{assert.ok(map.has(+n));return 'instruction:'+map.get(+n);} ))};
}
function generate(compiler){
 require('./verify.cjs').verify('bands-tell-inline-asm');
 const base=path.join(component,'asm/lx106'),pf=path.join(base,'bands-tell-inline.json'),parent=JSON.parse(fs.readFileSync(pf));
 const manifest=JSON.parse(fs.readFileSync(path.join(base,'manifest.json'))),entry=manifest.files.find(f=>f.source===source);
 const original=path.join(base,entry.asm);assert.equal(sourceHash(original),entry.asm_sha256_lf);
 const dir=path.join(root,'.build/opus-bands-'+kind);fs.mkdirSync(dir,{recursive:true});
 const overlay='bands-'+kind+'/'+source+'.s',dest=path.join(base,overlay);fs.mkdirSync(path.dirname(dest),{recursive:true});
 fs.writeFileSync(dest,transform(baseline()));
 const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
 const a=path.join(dir,'control.o'),b=path.join(dir,'candidate.o');
 for(const [s,o]of [[original,a],[dest,b]])run(compiler,['-mlongcalls','-x','assembler','-c',s,'-o',o]);
 const sizes=p=>Object.fromEntries([...run(dump,['-h',p]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
 const sa=sizes(a),sb=sizes(b);assert.deepEqual(Object.keys(sa),Object.keys(sb));let proof;
 for(const s of Object.keys(sa).filter(s=>sa[s]&&!s.startsWith('.xt.'))){
  if(s.startsWith('.text.')){
   const ga=canonical(run(dump,['-dr','-j',s,a])),gb=canonical(run(dump,['-dr','-j',s,b]));
   if(s==='.text.decode_pulses'){proof=fuseGraph(ga);assert.equal(proof.count,20);assert.deepEqual(normalizeBranches(gb).graph,normalizeBranches(proof.graph).graph);}
   else assert.deepEqual(gb,ga,s);
  }else{assert.equal(sb[s],sa[s],s);assert.equal(run(dump,['-s','-j',s,b]).split('\n').slice(3).join('\n'),run(dump,['-s','-j',s,a]).split('\n').slice(3).join('\n'),s);}
 }
 for(const [name,o]of [['control',a],['candidate',b]])fs.writeFileSync(path.join(dir,name+'.disassembly.txt'),run(dump,['-dr',o]));
 const files=[...parent.files.map(e=>({source:e.source,overlay:e.overlay,overlay_sha256_lf:e.overlay_sha256_lf})),
  {source,overlay,overlay_sha256_lf:sourceHash(dest),sections_before:sa,sections_after:sb}];
 const report={schema:1,candidate:'bands-pvq-addx-v1',base_manifest_sha256:sourceHash(path.join(base,'manifest.json')),
  recipe_sha256_lf:sourceHash(__filename),parent_sha256_lf:sourceHash(pf),files,
  changed_function:'decode_pulses',fused_pairs:proof.count,object_instruction_graph_exact:true,
  additional_static_ram_bytes:0,stack_change_bytes:0,physical_speed_measured:false};
 fs.writeFileSync(path.join(base,'bands-pvq-addx.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={kind,source,baseline,body,pair,replacements,transform,fuseGraph,normalizeBranches,generate};if(require.main===module)generate(process.argv[2]);

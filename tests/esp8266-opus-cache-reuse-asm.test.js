const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component}=require('../tools/esp8266_opus_asm/export.cjs');
const recipe=require('../tools/esp8266_opus_asm/cache_reuse.cjs');
const before=fs.readFileSync(path.join(component,'asm/lx106/bands-tell-inline/upstream/celt/bands.c.s'),'utf8').replace(/\r\n/g,'\n');
const after=recipe.transform(before);
// Execute the actual source instructions from .L22 to the cost consumer or
// the q=0 exit, including the original cold .L59 branch. No handwritten fast
// algorithm is substituted for the overlay under test.
function compile(text){
 const body=text.match(/^quant_partition:[\s\S]*?(?=^\s*\.size\s+quant_partition,)/m)[0];
 const ops=[],labels={};
 for(const raw of body.split('\n')){
  const line=raw.split('#')[0].trim();if(!line)continue;
  if(line.endsWith(':')){labels[line.slice(0,-1)]=ops.length;continue;}
  const [op,...tail]=line.split(/\s+/);ops.push({op,args:tail.join('').split(',')});
 }
 return (cache,budget)=>{
  const r=Array.from({length:16},(_,i)=>(0x12345600+i)|0);r[2]=4096;r[6]=cache[0];r[14]=budget;
  const value=x=>/^a\d+$/.test(x)?r[+x.slice(1)]:Number(x),set=(x,v)=>r[+x.slice(1)]=v|0;
  let pc=labels['.L22'],loads=0,steps=0;
  while(++steps<150){
   if(pc===labels['.L61'])return {q:0,cost:0,r,loads};
   const {op,args:a}=ops[pc++];
   if(op==='l32i.n'&&a.join(',')==='a6,a12,32')return {q:r[4],cost:r[8]+1,r,loads};
   const [d,x,y]=a;
   if(op==='mov.n')set(d,value(x));
   else if(op==='movi.n')set(d,value(x));
   else if(op==='add.n'||op==='addi.n')set(d,value(x)+value(y));
   else if(op==='sub')set(d,value(x)-value(y));
   else if(op==='srai')set(d,value(x)>>value(y));
   else if(op==='l8ui') {const at=value(x)+value(y)-4096;assert.ok(at>=0&&at<cache.length);set(d,cache[at]);loads++;}
   else if(op==='bge'||op==='blt'){if(op==='bge'?value(d)>=value(x):value(d)<value(x))pc=labels[y];}
   else if(op==='beqz.n'){if(!value(d))pc=labels[x];}
   else if(op==='j')pc=labels[d];
   else throw Error('Unexpected executed instruction '+op+' '+a.join(','));
  }
  throw Error('Instruction loop did not terminate');
 };
}
function reference(cache,b){
 let lo=0,hi=cache[0];b--;
 for(let i=0;i<6;i++){const mid=(lo+hi+1)>>1;if(cache[mid]>=b)hi=mid;else lo=mid;}
 const q=b-(lo===0?-1:cache[lo])<=cache[hi]-b?lo:hi;
 return {q,cost:q===0?0:cache[q]+1};
}
test('real ASM preserves all 16 registers and exact cost across every standard cache/budget',()=>{
 const header=fs.readFileSync(path.join(component,'upstream/celt/static_modes_fixed.h'),'utf8');
 const array=name=>header.match(new RegExp(name+'\\[.*?\\] = \\{([\\s\\S]*?)\\};'))[1].match(/-?\d+/g).map(Number);
 const indices=[...new Set(array('cache_index50').filter(n=>n>=0))],bytes=array('cache_bits50');
 const a=compile(before),b=compile(after);let saved=0,total=0;
 for(const start of indices){const cache=bytes.slice(start,start+bytes[start]+1);
  for(let budget=0;budget<=16383;budget++){
   const x=a(cache,budget),y=b(cache,budget),ref=reference(cache,budget);
   assert.equal(x.q,ref.q);assert.equal(x.cost,ref.cost);
   assert.equal(y.q,x.q);assert.equal(y.cost,x.cost);assert.deepEqual(y.r,x.r);
   assert.ok(y.loads===x.loads||y.loads===x.loads-1);saved+=x.loads-y.loads;total++;
  }
 }
 assert.equal(indices.length,23);assert.ok(saved>0);console.log({total,pathsWithSavedLoad:saved});
});
test('only three anchored edits; no whole qn=1 branch removal or new storage',()=>{
 let round=after;
 round=round.replace(recipe.edits[2][1],recipe.edits[2][0]).replace(recipe.edits[1][1],recipe.edits[1][0]);
 const anchor='\tsub\ta8, a8, a11\t# tmp892, bits, *_711';
 // The removed MOV precedes its own source comment, before the SUB comment.
 const parentWithoutMove=before.replace(recipe.edits[0][0],'');assert.equal(round,parentWithoutMove);
 assert.match(round,new RegExp(anchor.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')));
 assert.equal((after.match(/Y_OPUS_TELL_FRAC/g)||[]).length,(before.match(/Y_OPUS_TELL_FRAC/g)||[]).length);
 assert.throws(()=>recipe.transform(after));
});
test('backend verifies pinned sources and remains opt-in',()=>{
 require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-cache-reuse-asm');
 const cmake=fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8');
 assert.match(cmake,/set\(YORADIO_OPUS_BACKEND "c"/);
 assert.match(cmake,/bands-cache-reuse-asm/);
});

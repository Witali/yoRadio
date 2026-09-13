const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {component}=require('../tools/esp8266_opus_asm/export.cjs');
const recipe=require('../tools/esp8266_opus_asm/inner4.cjs');
const original=fs.readFileSync(path.join(component,'asm/lx106/gcc/upstream/celt/vq.c.s'),'utf8').replace(/\r\n/g,'\n');
const candidate=recipe.transform(original);
const body=text=>text.match(/^renormalise_vector:[\s\S]*?(?=^\s*\.size\s+renormalise_vector,)/m)[0];
function compile(text){
 const scope=body(text),start='\tmovi.n\ta2, 0\t# xy,\n';
 const finish='# @OPUS@\\upstream\\celt\\vq.c:404:';
 const code=scope.slice(scope.indexOf(start)+start.length,scope.indexOf(finish));
 assert.ok(code.includes('.L182:'));
 const ops=[],labels={};
 for(const raw of code.split('\n')){
  const line=raw.split('#')[0].trim();if(!line)continue;
  if(line.endsWith(':')){labels[line.slice(0,-1)]=ops.length;continue;}
  const [op,...tail]=line.split(/\s+/);ops.push({op,args:tail.join('').split(',')});
 }
 return (samples,address=4096)=>{
  const r=Array.from({length:16},(_,i)=>(0x76543200+i)|0);
  r[2]=0;r[3]=address+samples.length*2;r[6]=address;r[14]=samples.length*2;
  const value=x=>/^a\d+$/.test(x)?r[+x.slice(1)]:Number(x),set=(x,v)=>r[+x.slice(1)]=v|0;
  let pc=0,steps=0,loads=0;
  while(pc<ops.length){
   assert.ok(++steps<samples.length*8+30,'nonterminating loop');
   const {op,args:[d,x,y]}=ops[pc++];
   if(op==='srli')set(d,value(x)>>>value(y));
   else if(op==='slli')set(d,value(x)<<value(y));
   else if(op==='add.n'||op==='addi.n')set(d,value(x)+value(y));
   else if(op==='mull')set(d,Math.imul(value(x),value(y)));
   else if(op==='l16si'){
    const at=(value(x)+value(y)-address)/2;
    assert.equal(at,loads++,'unaligned, duplicate, skipped or out-of-order read');
    assert.ok(at>=0&&at<samples.length,'out-of-bounds read');set(d,samples[at]);
   }
   else if(op==='blti'||op==='bne'||op==='beq'){
    if(op==='blti'?value(d)<value(x):op==='bne'?value(d)!==value(x):value(d)===value(x)){
     assert.ok(Object.hasOwn(labels,y),'unknown branch');pc=labels[y];
    }
   }else throw Error('Unexpected instruction '+op);
  }
  return {r,steps,loads};
 };
}
test('actual ASM inner product: every length/tail, full int16 range and overflow',()=>{
 const a=compile(original),b=compile(candidate);let cases=0,state=12345;
 const lengths=[...Array.from({length:1024},(_,i)=>i+1),1536,2047,2048];
 for(const n of lengths)for(let pattern=0;pattern<6;pattern++){
  const x=Array.from({length:n},(_,i)=>{
   state=(Math.imul(state,1664525)+1013904223)|0;
   return [0,-32768,32767,i%2?-32768:32767,state>>16,((i*997)%65536)-32768][pattern];
  });
  const address=4096+2*(pattern%2),aa=a(x,address),bb=b(x,address);
  let reference=0;for(const sample of x)reference=(reference+Math.imul(sample,sample))|0;
  assert.equal(aa.r[2],reference);assert.equal(bb.r[2],reference);
  for(let r=0;r<16;r++)if(r!==4&&r!==7)assert.equal(bb.r[r],aa.r[r],'live a'+r);
  assert.equal(bb.loads,n);assert.equal(aa.loads,n);
  if(n>=8)assert.ok(bb.steps<aa.steps,'no instruction-count saving at N='+n);
  else assert.equal(bb.steps,aa.steps+1,'short path adds only threshold branch');
  cases++;
 }
 console.log({asmVectorCases:cases,maxN:2048,scope:'actual source instructions, not target cycle timing'});
});
test('only energy loop changed; zero-length guard, scaling, ABI and all other functions preserved',()=>{
 const b=body(original),c=body(candidate),inc=fs.readFileSync(path.join(__dirname,'../tools/esp8266_opus_asm/inner4_loop.inc.s'),'utf8');
 assert.equal(c.replace(inc+'\n','').replace('.Linner4_done:\n',''),b);
 assert.equal(candidate.replace(c,b),original);
 assert.match(c,/blti\ta3, 1, \.L181/);
 assert.doesNotMatch(inc,/\b(?:s32i|s16i|call0|ssl|ssr|s32c1i)\b/);
 // a4 is redefined from gain*rsqrt before its next use. a7 is unused until
 // the next call (caller-saved). All other registers match at the join.
 const join=c.split('.Linner4_done:\n')[1].split('call0\tcelt_rsqrt_norm')[0];
 assert.doesNotMatch(join,/\ba[47]\b/);
 assert.throws(()=>recipe.transform(candidate));
});
test('selectable overlay is pinned and default remains C',()=>{
 require('../tools/esp8266_opus_asm/verify.cjs').verify('bands-inner4-asm');
 const cmake=fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8');
 assert.match(cmake,/set\(YORADIO_OPUS_BACKEND "c"/);
 assert.match(cmake,/bands-inner4-asm/);
 const m=JSON.parse(fs.readFileSync(path.join(component,'asm/lx106/bands-inner4.json')));
 assert.equal(m.files[2].sections_after['.text.renormalise_vector']-m.files[2].sections_before['.text.renormalise_vector'],52);
});

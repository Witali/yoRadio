const assert=require('node:assert/strict');
// Compare actual instructions and branch graph while allowing GAS to insert
// unreachable zero alignment bytes. Never ignore an opcode or a branch target.
function canonical(text){
 const rows=[];
 for(const line of text.split(/\r?\n/)){
  const op=line.match(/^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+([^\s]+)\s*(.*?)\s*$/);
  if(op){
   if(op[3]==='.byte'){
    assert.match(op[4],/^00$/);assert.ok(rows.length&&(/^(?:j|ret(?:\.n)?)$/.test(rows.at(-1).op)),'Alignment on fall-through path');continue;
   }
   rows.push({address:parseInt(op[1],16),op:op[3],args:op[4],reloc:null});continue;
  }
  const reloc=line.match(/^\s*([0-9a-f]+):\s+R_XTENSA_SLOT0_OP\s+(.*)$/);
  if(reloc){assert.equal(rows.at(-1).address,parseInt(reloc[1],16));rows.at(-1).reloc=reloc[2];}
 }
 const index=new Map(rows.map((r,i)=>[r.address,i]));
 return rows.map(r=>{
  let args=r.args;
  const target=args.match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);
  if(target){
   const internal=r.reloc?.match(/^\.text\.[^+]+\+0x([0-9a-f]+)$/);
   let symbol;
   if(internal){const a=parseInt(internal[1],16);assert.ok(index.has(a),'Target is not an instruction');symbol='instruction:'+index.get(a);}
   else {assert.ok(r.reloc,'Unresolved control-flow/literal target');symbol=r.reloc;}
   args=args.slice(0,args.length-target[0].length)+(target[0].startsWith(',')?', ':'')+symbol;
  }else if(r.reloc)args+=' reloc:'+r.reloc;
  let op=r.op.replace(/\.n$/,'');
  // GAS may widen a density MOV to OR rd,rs,rs for instruction alignment.
  // Xtensa has no arithmetic condition flags: these are exactly equivalent.
  const regs=args.split(/,\s*/);
  if(op==='or'&&regs.length===3&&regs[1]===regs[2]){op='mov';args=regs.slice(0,2).join(', ');}
  return op+' '+args;
 });
}
module.exports={canonical};

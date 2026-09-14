// Reachable helper blocks only: never decode linker padding after RET as code.
// JX a4 is an exit; caller must separately prove its literal target is __udivsi3.
const assert=require('node:assert/strict');
function helperDisassembly(start,end,readBlock){
 const pending=[start],rows=new Map();
 while(pending.length){
  const entry=pending.pop();if(rows.has(entry))continue;
  assert.ok(entry>=start&&entry<end,'Helper branch leaves bounds');
  let next=entry,stopped=false;
  for(const line of readBlock(entry,end).split(/\r?\n/)){
   const m=line.match(/^\s*([0-9a-f]+):\s+([0-9a-f]+)\s+(\S+)\s*(.*?)\s*$/);if(!m)continue;
   const address=parseInt(m[1],16);assert.equal(address,next,'Instruction boundary');
   if(rows.has(address)){stopped=true;break;}
   assert.ok([4,6].includes(m[2].length));assert.doesNotMatch(m[3],/^\.|unknown|ill|excw/);
   if(m[3]==='jx')assert.equal(m[4],'a4','Only the explicit fallback register is allowed');
   rows.set(address,line);next+=m[2].length/2;
   if(/^b|^j$/.test(m[3])){const t=m[4].match(/(?:^|,\s*)([0-9a-f]+)\s+<[^>]+>$/);assert.ok(t);pending.push(parseInt(t[1],16));}
   if(/^(j|jx|ret(?:\.n)?)$/.test(m[3])){stopped=true;break;}
  }assert.ok(stopped,'Unexpected helper fall-through');
 }
 return [...rows].sort((a,b)=>a[0]-b[0]).map(([,line])=>line).join('\n');
}
module.exports={helperDisassembly};

// Translate actual ASM instructions, including unchanged normalization, to C.
// Test-only virtual 32-bit addresses; NOT target timing or an alternative codec.
const assert=require('node:assert/strict');
function parse(text){
 const body=text.match(/^ec_dec_bit_logp:[\s\S]*?(?=^\s*\.size\s+ec_dec_bit_logp,)/m)[0];
 const literals=Object.fromEntries([...text.matchAll(/^\s*\.literal\s+(\.LC\d+),\s*(-?\d+)\s*$/gm)].map(m=>[m[1],Number(m[2])>>>0]));
 const ops=[],labels={};
 for(const raw of body.split('\n')){
  const line=raw.split('#')[0].trim();if(!line)continue;
  if(line.endsWith(':')){labels[line.slice(0,-1)]=ops.length;continue;}
  const [op,...tail]=line.split(/\s+/);ops.push({op:op.replace(/\.n$/,''),args:tail.join('').replaceAll('sp','a1').split(',')});
 }
 return {ops,labels,literals};
}
function cModel(text){
 const {ops,labels,literals}=parse(text),c=[];
 const reg=x=>{assert.match(x,/^a(?:[0-9]|1[0-5])$/);return `r[${x.slice(1)}]`;};
 for(const [i,{op,args:a}]of ops.entries()){
  for(const [label,at]of Object.entries(labels))if(at===i)c.push(label.replaceAll('.','_')+':;');
  const r=j=>reg(a[j]),imm=j=>{assert.ok(Number.isInteger(Number(a[j])));return Number(a[j]);};
  const label=x=>{assert.ok(Object.hasOwn(labels,x));return x.replaceAll('.','_');};
  c.push(`/* ${op} ${a.join(', ')} */`);
  switch(op){
   case 'mov':c.push(`${r(0)}=${r(1)};`);break;
   case 'movi':c.push(`${r(0)}=(uint32_t)${imm(1)};`);break;
   case 'l32r':assert.ok(Object.hasOwn(literals,a[1]));c.push(`${r(0)}=${literals[a[1]]}u;`);break;
   case 'ssr':c.push(`sar=${r(0)}&31;`);break;
   case 'srl':c.push(`${r(0)}=${r(1)}>>sar;`);break;
   case 'slli':c.push(`${r(0)}=${r(1)}<<${imm(2)};`);break;
   case 'srai':c.push(`${r(0)}=(uint32_t)((int32_t)${r(1)}>>${imm(2)});`);break;
   case 'extui':c.push(`${r(0)}=(${r(1)}>>${imm(2)})&((1u<<${imm(3)})-1);`);break;
   case 'add':case 'sub':case 'or':case 'xor':case 'and':c.push(`${r(0)}=${r(1)}${{add:'+',sub:'-',or:'|',xor:'^',and:'&'}[op]}${r(2)};`);break;
   case 'addi':c.push(`${r(0)}=${r(1)}+(uint32_t)${imm(2)};`);break;
   case 'l32i':case 'l8ui':c.push(`${r(0)}=yl_read(w,stack,ctx->buf,ctx->storage,${r(1)}+${imm(2)},${op==='l32i'?4:1});`);break;
   case 's32i':c.push(`yl_write(w,stack,${r(1)}+${imm(2)},${r(0)});`);break;
   case 'bltu':case 'bgeu':c.push(`if(${r(0)}${op==='bltu'?'<':'>='}${r(1)})goto ${label(a[2])};`);break;
   case 'j':c.push(`goto ${label(a[0])};`);break;
   case 'ret':c.push('goto model_done;');break;
   default:throw Error('Unmodelled opcode '+op);
  }
 }
 return `/* Generated from the complete candidate ASM ec_dec_bit_logp. */
#include <assert.h>
#include <stdint.h>
static uint32_t yl_read(uint32_t *w,uint32_t *stack,const unsigned char *packet,uint32_t size,uint32_t addr,int width){
 if(width==4){assert(!(addr&3));if(addr>=256&&addr<304)return w[(addr-256)/4];assert(addr>=4080&&addr<4096);return stack[(addr-4080)/4];}
 assert(width==1&&addr>=65536&&addr-65536<size);return packet[addr-65536];
}
static void yl_write(uint32_t *w,uint32_t *stack,uint32_t addr,uint32_t value){
 assert(!(addr&3));if(addr>=256&&addr<304)w[(addr-256)/4]=value;
 else {assert(addr>=4080&&addr<4096);stack[(addr-4080)/4]=value;}
}
int ec_dec_bit_logp(ec_dec *ctx,unsigned logp){
 uint32_t w[12]={65536,ctx->storage,ctx->end_offs,ctx->end_window,ctx->nend_bits,ctx->nbits_total,ctx->offs,ctx->rng,ctx->val,ctx->ext,ctx->rem,ctx->error};
 uint32_t r[16],stack[4]={0},sar=0;for(unsigned i=0;i<16;i++)r[i]=0x76543000u+i;
 r[1]=4096;r[2]=256;r[3]=logp;
 ${c.join('\n ')}
model_done:
 assert(r[0]==0x76543000u&&r[1]==4096);for(unsigned i=12;i<16;i++)assert(r[i]==0x76543000u+i);
 assert(w[0]==65536&&w[1]==ctx->storage&&w[2]==ctx->end_offs&&w[3]==ctx->end_window&&w[4]==(uint32_t)ctx->nend_bits&&w[9]==ctx->ext&&w[11]==(uint32_t)ctx->error);
 ctx->nbits_total=w[5];ctx->offs=w[6];ctx->rng=w[7];ctx->val=w[8];ctx->rem=w[10];return (int)r[2];
}
`;
}
module.exports={parse,cModel};

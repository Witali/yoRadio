/* Translate the ACTUAL candidate instruction text into a host semantics model.
 * Not a cycle emulator and not target execution. Fail on unknown instructions. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component}=require('./export.cjs');
function generateModel(output=path.join(root,'.build/opus-asm-model/entropy_model.c')) {
  const source=fs.readFileSync(path.join(__dirname,'ec_dec_update.inc.s'),'utf8');
  const reg=x=>{assert.match(x,/^a(?:[0-9]|1[0-5])$/);return `r[${x.slice(1)}]`;};
  const label=x=>x.replaceAll('.','_');
  const c=[];
  for(const raw of source.split(/\r?\n/)) {
    const line=raw.split('#')[0].trim();if(!line)continue;
    if(line.endsWith(':')){c.push(label(line));continue;}
    const [opcode,...rest]=line.split(/\s+/),op=opcode.replace(/\.n$/,''),a=rest.join('').split(',');
    const r=i=>reg(a[i]), imm=i=>{assert.ok(Number.isInteger(Number(a[i])));return Number(a[i]);};
    c.push(`/* ${line} */`);
    switch(op) {
      case 'mov':c.push(`${r(0)}=${r(1)};`);break;
      case 'movi':c.push(`${r(0)}=(uint32_t)${imm(1)};`);break;
      case 'sub':c.push(`${r(0)}=${r(1)}-${r(2)};`);break;
      case 'add':c.push(`${r(0)}=${r(1)}+${r(2)};`);break;
      case 'addi':case 'addmi':c.push(`${r(0)}=${r(1)}+(uint32_t)${imm(2)};`);break;
      case 'mull':c.push(`${r(0)}=${r(1)}*${r(2)};`);break;
      case 'slli':case 'srli':c.push(`${r(0)}=${r(1)}${op==='slli'?'<<':'>>'}${imm(2)};`);break;
      case 'or':c.push(`${r(0)}=${r(1)}|${r(2)};`);break;
      case 'extui':c.push(`${r(0)}=(${r(1)}>>${imm(2)})&((1u<<${imm(3)})-1u);`);break;
      case 'l32i':case 'l8ui':c.push(`${r(0)}=oa_read(w,ctx->buf,ctx->storage,${r(1)}+${imm(2)},${op==='l32i'?4:1});`);break;
      case 's32i':c.push(`oa_write(w,${r(1)}+${imm(2)},${r(0)});`);break;
      case 'beqz':c.push(`if(${r(0)}==0)goto ${label(a[1])};`);break;
      case 'bltu':case 'bgeu':c.push(`if(${r(0)}${op==='bltu'?'<':'>='}${r(1)})goto ${label(a[2])};`);break;
      case 'j':c.push(`goto ${label(a[0])};`);break;
      case 'ret':c.push('goto model_done;');break;
      default:throw Error('Unmodelled opcode '+op);
    }
  }
  const text=`/* Generated from ec_dec_update.inc.s. Test-only virtual 32-bit addresses. */
#include <assert.h>
#include <stdint.h>
#include "entdec.h"
static uint32_t oa_read(uint32_t *w,const unsigned char *packet,uint32_t size,uint32_t addr,int width){
 if(width==4){assert(addr>=256&&addr<304&&!(addr&3));return w[(addr-256)/4];}
 assert(width==1&&addr>=65536&&addr-65536<size);return packet[addr-65536];
}
static void oa_write(uint32_t *w,uint32_t addr,uint32_t value){assert(addr>=256&&addr<304&&!(addr&3));w[(addr-256)/4]=value;}
void ec_dec_update(ec_dec *ctx,unsigned fl,unsigned fh,unsigned ft){
 uint32_t w[12]={65536,ctx->storage,ctx->end_offs,ctx->end_window,ctx->nend_bits,ctx->nbits_total,ctx->offs,ctx->rng,ctx->val,ctx->ext,ctx->rem,ctx->error};
 uint32_t r[16]={0};r[2]=256;r[3]=fl;r[4]=fh;r[5]=ft;
 ${c.join('\n ')}
model_done:
 assert(w[0]==65536&&w[1]==ctx->storage&&w[2]==ctx->end_offs&&w[3]==ctx->end_window&&w[4]==(uint32_t)ctx->nend_bits&&w[9]==ctx->ext&&w[11]==(uint32_t)ctx->error);
 ctx->nbits_total=w[5];ctx->offs=w[6];ctx->rng=w[7];ctx->val=w[8];ctx->rem=w[10];
}
`;
  fs.mkdirSync(path.dirname(output),{recursive:true});fs.writeFileSync(output,text);
  const reference=path.join(path.dirname(output),'entdec_reference.c');
  fs.writeFileSync(reference,fs.readFileSync(path.join(component,'upstream/celt/entdec.c'),'utf8').replace('void ec_dec_update(', 'void ec_dec_update_reference('));
  return {model:output,reference};
}
module.exports={generateModel};if(require.main===module)console.log(generateModel());

// Independent host experiments over the accepted ASM chain's C semantic mirror.
// These are NOT production/ASM overlays. Keep the original C fallback untouched.
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const {root} = require('./export.cjs');
const component = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder');
const kinds = ['n4-prefix', 'inplace-b1', 'inplace-all', 'short-leaf', 'short-leaf-cache', 'observe'];
function once(s, a, b) { assert.equal(s.split(a).length, 2, 'Non-unique anchor: '+a); return s.replace(a,b); }
function functionText(s, signature) {
  const start=s.indexOf(signature); assert.ok(start>=0, signature);
  const end=s.indexOf('\n}',start)+2; assert.ok(end>start);
  return s.slice(start,end);
}
function n4Table() {
  const u=k=>(4*k*k*k-6*k*k+8*k-3)/3;
  const entries=[];
  // Smaller buckets below 512. Each bucket crosses at most one U(4,k) boundary.
  for(const [shift,start,end] of [[6,64,512],[8,512,65536]]) {
    for(let lo=start;lo<end;lo+=2**shift) {
      let k=4; while(u(k+1)<=lo)k++;
      let last=k; while(u(last+1)<=lo+2**shift-1)last++;
      assert.ok(last-k<=1);
      const p=u(k),cut=Math.min(2**shift,u(k+1)-lo);
      assert.ok(k<64&&p<65536&&cut<=256);
      entries.push((k|(p<<6)|(cut<<22))>>>0);
    }
  }
  return {entries,u};
}
function n4Helper() {
  const {entries}=n4Table();
  return `/* N=4: exact table rank, then exact p. No change to entropy coding.
 * Entries: k[5:0], U(4,k)[21:6], next-boundary offset[30:22].
 * Generated offline; domain fallback is not a bitrate restriction. */
static const opus_uint32 research_n4_table[${entries.length}] = {
${entries.map(x=>x+'U').join(',')}
};
static void research_n4_lookup(opus_uint32 index, int *k, opus_uint32 *p) {
 unsigned low=index<512;
 unsigned bucket=low?(index>>6)-1:7+(index>>8)-2;
 opus_uint32 word=research_n4_table[bucket];
 unsigned rank=word&63, value=(word>>6)&65535, cut=word>>22;
 if ((index&(low?63:255))>=cut) { value+=4*rank*rank+2; rank++; }
 *k=(int)rank; *p=value;
}
`;
}
function transformCwrs(text,kind) {
  if(kind==='n4-prefix') {
    const anchor='      else for(p=row[_k];p>_i;p=row[_k])_k--;';
    text=once(text, 'static opus_val32 cwrsi(int _n,int _k,opus_uint32 _i,int *_y){', n4Helper()+'\nstatic opus_val32 cwrsi(int _n,int _k,opus_uint32 _i,int *_y){');
    return once(text,anchor,`      else {
        p=row[_k];
        if (p>_i && _n==4 && _i>=64 && _i<65536) {
          research_n4_lookup(_i,&_k,&p);
        } else while(p>_i) p=row[--_k];
      }`);
  }
  const original=functionText(text,'static opus_val32 cwrsi(int _n,int _k,opus_uint32 _i,int *_y){');
  const copy=original.replace('cwrsi(', 'research_cwrsi16(').replace('int *_y','opus_int16 *_y');
  const api=`\n/* Guarded caller requires 0<K<=32767: every impulse magnitude <=K. */
opus_val32 research_decode16(opus_int16 *y,int n,int k,ec_dec *dec) {
  celt_assert(k>0 && k<=32767);
  return research_cwrsi16(n,k,ec_dec_uint(dec,CELT_PVQ_V(n,k)),y);
}\n`;
  return once(text,original,original+'\n'+copy+api);
}
function transformVq(text,kind) {
  const norm=functionText(text,'static void normalise_residual(');
  const norm16=norm.replace('normalise_residual(int * OPUS_RESTRICT iy, celt_norm * OPUS_RESTRICT X,','research_normalise16(celt_norm *X,').replaceAll('iy[i]','X[i]');
  const mask=functionText(text,'static unsigned extract_collapse_mask(');
  const mask16=mask.replace('extract_collapse_mask(int *iy','research_mask16(celt_norm *iy');
  const before='unsigned alg_unquant(celt_norm *X, int N, int K, int spread, int B,';
  text=once(text,before,`/* No restrict alias: read each raw int16 impulse before overwriting X.
 * X already accepts 16-bit stores in the original normalisation path.
 * Collapse mask MUST precede normalisation/rotation, including gain==0. */
extern opus_val32 research_decode16(opus_int16 *,int,int,ec_dec *);
${norm16}
${mask16}
${before}`);
  const original=functionText(text,before);
  const next=once(original,'   SAVE_STACK;',`   /* No scratch allocation in decode16, mask, normalise or rotation. */
   if (K<=32767${kind==='inplace-b1'?' && B<=1':''}) {
      Ryy=research_decode16(X,N,K,dec);
      collapse_mask=${kind==='inplace-b1'?'1':'research_mask16(X,N,B)'};
      research_normalise16(X,N,Ryy,gain);
      exp_rotation(X,N,-1,B,K,spread);
      return collapse_mask;
   }
   SAVE_STACK;`);
  return once(text,original,next);
}
function transformLeaf(text,withCache=false) {
  const signature='static unsigned quant_partition(struct band_ctx *ctx, celt_norm *X,';
  const original=functionText(text,signature),open=original.indexOf('{');
  const declaration=original.slice(0,open).trim();
  const leafStart=original.indexOf('      /* This is the basic no-split case */');
  const leafEnd=original.lastIndexOf('\n   }\n\n   return cm;');
  assert.ok(leafStart>0&&leafEnd>leafStart);
  let leaf=declaration.replace('quant_partition','research_short_leaf')+`\n{
   const CELTMode *m=ctx->m;
   int i=ctx->i,spread=ctx->spread,encode=0,q,curr_bits;
   ec_ctx *ec=ctx->ec;
   unsigned cm=0;
   const unsigned char *cache=m->cache.bits+y_pvq_index_half(m,(LM+1)*m->nbEBands+i);
   const int y_row_length=y_pvq_word8(m,cache);
${original.slice(leafStart,leafEnd)}
   return cm;
}\n`;
  const full=original.replace('static unsigned quant_partition(', 'static unsigned research_partition_full(');
  let wrapper=declaration+`\n{
   /* N=4 alone is NOT sufficient: LM=-1 proves no further split.
    * Keep pulse budget correction, zero-fill/noise and entropy order intact. */
   if (!band_encode(ctx) && (N==2 || (N==4 && LM==-1)))
      return research_short_leaf(ctx,X,N,b,B,lowband,LM,gain,fill);
   return research_partition_full(ctx,X,N,b,B,lowband,LM,gain,fill);
}\n`;
  if(withCache) {
    leaf=once(leaf,'opus_val16 gain, int fill)','opus_val16 gain, int fill, int y_row_length)');
    leaf=once(leaf,'   const unsigned char *cache=m->cache.bits+y_pvq_index_half(m,(LM+1)*m->nbEBands+i);\n   const int y_row_length=y_pvq_word8(m,cache);','');
    wrapper=declaration+`\n{
   if (!band_encode(ctx) && (N==2 || N==4)) {
      const CELTMode *m=ctx->m;
      const unsigned char *cache=m->cache.bits+y_pvq_index_half(m,(LM+1)*m->nbEBands+ctx->i);
      const int length=y_pvq_word8(m,cache);
      if (N==2 || LM==-1 || b<=y_pvq_word8(m,cache+length)+12)
         return research_short_leaf(ctx,X,N,b,B,lowband,LM,gain,fill,length);
   }
   return research_partition_full(ctx,X,N,b,B,lowband,LM,gain,fill);
}\n`;
  }
  return once(text,original,declaration+';\n'+leaf+full+'\n'+wrapper);
}
function observe(text,unit) {
  const declaration='extern void research_event(int,int,int,int,int);\n';
  if(unit==='celt_decoder') {
    const original=functionText(text,'void celt_synthesis(');
    let updated=once(original,'   ALLOC(freq, N, celt_sig);','   research_event(8,N,LM,0,0);\n   ALLOC(freq, N, celt_sig);');
    updated=once(updated,'   RESTORE_STACK;','   research_event(9,N,LM,0,0);\n   RESTORE_STACK;');
    return declaration+once(text,original,updated);
  }
  if(unit==='bands') {
    const signature='static unsigned quant_partition(struct band_ctx *ctx, celt_norm *X,';
    const original=functionText(text,signature);
    let updated=once(original,'   encode = band_encode(ctx);','   research_event(1,N,LM,B,0);\n   encode = band_encode(ctx);');
    updated=once(updated,'      /* This is the basic no-split case */','      research_event(2,N,LM,B,0);\n      /* This is the basic no-split case */');
    updated=once(updated,'      if (q!=0)','      research_event(3,N,LM,B,q);\n      if (q!=0)');
    updated=once(updated,'   return cm;','   research_event(4,N,LM,B,0);\n   return cm;');
    return once(text,original,declaration+updated);
  }
  const signature='unsigned alg_unquant(celt_norm *X, int N, int K, int spread, int B,';
  const original=functionText(text,signature);
  let updated=once(original,'   ALLOC(iy, N, int);','   research_event(5,N,K,B,0);\n   ALLOC(iy, N, int);');
  updated=once(updated,'   RESTORE_STACK;','   research_event(6,N,K,B,0);\n   RESTORE_STACK;');
  return once(text,original,declaration+updated);
}
function generate(kind,models) {
  assert.ok(kinds.includes(kind));
  const dir=path.join(root,'.build/opus-algorithm-candidates',kind);fs.mkdirSync(dir,{recursive:true});
  const units=kind==='observe'?['bands','vq','celt_decoder']:kind.startsWith('short-leaf')?['bands']:kind.startsWith('inplace')?['cwrs','vq']:['cwrs'];
  return units.map(unit=>{
    const source='upstream/celt/'+unit+'.c',base=models.find(m=>m.source===source)?.file||path.join(component,source);
    let text=fs.readFileSync(base,'utf8').replace(/\r\n/g,'\n');
    text=kind==='observe'?observe(text,unit):unit==='bands'?transformLeaf(text,kind==='short-leaf-cache'):unit==='cwrs'?transformCwrs(text,kind):transformVq(text,kind);
    const file=path.join(dir,unit+'.c');fs.writeFileSync(file,text);
    return {source,file,base};
  });
}
module.exports={kinds,once,functionText,n4Table,transformCwrs,transformVq,transformLeaf,generate};

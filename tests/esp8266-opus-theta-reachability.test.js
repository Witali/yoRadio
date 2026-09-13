const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {root,component,sourceHash}=require('../tools/esp8266_opus_asm/export.cjs');
const read=p=>fs.readFileSync(path.join(component,p),'utf8');
const array=(text,name)=>{
 const body=text.match(new RegExp(name+'\\[[^\\]]*\\] = \\{([\\s\\S]*?)\\};'))?.[1];
 assert.ok(body,name);
 return body.replace(/\/\*[\s\S]*?\*\//g,'').match(/-?\d+/g).map(Number);
};
function domain(){
 const modes=read('upstream/celt/static_modes_fixed.h');
 const e=array(read('upstream/celt/modes.c'),'eband5ms'),l=array(modes,'logN400');
 const index=array(modes,'cache_index50'),bits=array(modes,'cache_bits50');
 assert.equal(e.length,22);assert.equal(l.length,21);assert.equal(index.length,105);
 const rows=[];
 for(let lm=0;lm<=3;lm++)for(let i=0;i<21;i++){
  const N=(e[i+1]-e[i])*(1<<lm);if(N<=2)continue;
  const at=index[(lm+1)*21+i];assert.ok(at>=0);
  rows.push({lm,i,N,first:bits[at+bits[at]]+13,pc:l[i]+(lm-1)*8});
 }
 return rows;
}
function qb(row,b){
 const n2=2*(row.N>>1)-1,offset=(row.pc>>1)-4;
 return Math.min(64,b-row.pc-32,Math.trunc((b+n2*offset)/n2));
}
test('source/table evidence stays pinned until the host proof is rerun',()=>{
 const report=JSON.parse(fs.readFileSync(path.join(root,'tools/esp8266_opus_asm/theta-reachability-results.json')));
 for(const [file,hash]of Object.entries(report.hashes))assert.equal(sourceHash(path.join(component,file)),hash,file);
 assert.equal(sourceHash(path.join(root,'tools/esp8266_opus_asm/theta_reachability.c')),report.harness_sha256_lf);
 assert.equal(report.summary.passed,true);assert.equal(report.firmware_changed,false);
});
test('all standard-mode split budgets exclude qb < 4, independently of bitrate',()=>{
 const rows=domain();assert.equal(rows.length,64);
 let min=Infinity,count=0;
 for(const row of rows){let previous=-Infinity;
  for(let b=row.first;b<=16383;b++){
   const value=qb(row,b);assert.ok(value>=4);assert.ok(value>=previous);previous=value;
   min=Math.min(min,value);count++;
  }
 }
 assert.equal(min,19);assert.equal(count,1032884);
});
test('proof rejects a weakened caller guard; generic low-budget theta is not dead',()=>{
 const rows=domain();assert.ok(rows.some(row=>qb(row,0)<4));
 const source=read('upstream/celt/bands.c');
 assert.match(source,/LM != -1 && b > cache\[cache\[0\]\]\+12 && N>2/);
 assert.match(source,/compute_theta\(ctx, &sctx, X, Y, N, &b, B, B0, LM, 0, &fill\)/);
 assert.match(source,/compute_theta\(ctx, &sctx, X, Y, N, &b, B, B, LM, 1, &fill\)/);
 assert.match(source,/if \(stereo && i>=intensity\)\s+qn = 1/);
 assert.match(source,/inv = ec_dec_bit_logp\(ec, 2\)/);
});
test('screened-out ASM only replaces the no-entropy calculation, not its branch',()=>{
 const recipe=require('../tools/esp8266_opus_asm/tell_zero.cjs');
 const before=read('asm/lx106/bands-tell-inline/upstream/celt/bands.c.s').replace(/\r\n/g,'\n');
 const after=recipe.transform(before);
 assert.equal(after.replace(recipe.replacement(),recipe.oldBlock(before)),before);
 assert.ok(!fs.existsSync(path.join(component,'asm/lx106/bands-tell-zero.json')));
 const cmake=read('CMakeLists.txt');assert.doesNotMatch(cmake,/bands-tell-zero-asm/);
});

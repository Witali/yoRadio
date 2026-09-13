// Offline prototype only: no firmware defaults or ASM baseline changes.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,hash,sourceHash}=require('./export.cjs');
const {execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
function reference(cache,bits){
 let lo=0,hi=cache[0];bits--;
 for(let i=0;i<6;i++){const mid=(lo+hi+1)>>1;if(cache[mid]>=bits)hi=mid;else lo=mid;}
 return bits-(lo===0?-1:cache[lo])<=cache[hi]-bits?lo:hi;
}
function generate(){
 const file=path.join(component,'upstream/celt/static_modes_fixed.h'),src=fs.readFileSync(file,'utf8');
 const array=(name,len)=>{const match=src.match(new RegExp('\\b'+name+'\\['+len+'\\]\\s*=\\s*\\{([^}]+)\\}'));assert.ok(match,name);
  const values=match[1].split(',').map(s=>s.trim()).filter(Boolean).map(Number);assert.equal(values.length,len);assert.ok(values.every(Number.isInteger));return values;};
 const index=array('cache_index50',105),bits=array('cache_bits50',392);
 const offsets=[...new Set(index.filter(v=>v>=0))].sort((a,b)=>a-b);assert.equal(offsets.length,23);
 const map=Array(392).fill(255),rows=offsets.map((off,id)=>{
  map[off]=id;const cache=bits.slice(off,off+bits[off]+1);assert.equal(cache.length,cache[0]+1);
  return Array.from({length:260},(_,b)=>b<=256?reference(cache,b):0);
 });
 let combinations=0;
 for(let r=0;r<rows.length;r++)for(let b=-256;b<16384;b++){
  const q=b<0?0:b>256?bits[offsets[r]]:rows[r][b];assert.equal(q,reference(bits.slice(offsets[r]),b));combinations++;
 }
 const pack=a=>Array.from({length:a.length/4},(_,i)=>(a[i*4]|a[i*4+1]<<8|a[i*4+2]<<16|a[i*4+3]<<24)>>>0);
 const dir=path.join(root,'.build/opus-pulse-inverse');fs.mkdirSync(dir,{recursive:true});
 const definition=(type,name,a)=>'static const '+type+' '+name+'['+a.length+'] = {\n'+a.map((v,i)=>(i%12===0?'\n':'')+(type==='unsigned'?v+'u':v)).join(',')+'\n};\n';
 const header='/* Derived from Xiph Opus cache_bits50; upstream/COPYING applies. */\n'+definition('unsigned char','reference_bits',bits)+definition('int','row_offsets',offsets)+definition('unsigned','inverse_words',pack(rows.flat()))+definition('unsigned','offset_map_words',pack(map));
 fs.writeFileSync(path.join(dir,'inverse.h'),header);
 const bin=path.join(dir,'check');
 execute('gcc',['-O2','-fwrapv','-fsanitize=address,undefined','-fno-sanitize-recover=all',
  '-I'+hostPath(dir),...['upstream/celt','','upstream/include'].map(d=>'-I'+hostPath(path.join(component,d))),
  hostPath(path.join(root,'tests/native/esp8266_opus_pulse_inverse_test.c')),'-o',hostPath(bin)]);
 const actual=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(bin)]));assert.equal(actual.combinations,combinations);assert.equal(actual.passed,true);
 const report={scope:'Offline exact lookup prototype; original C bits2pulses under ASAN/UBSAN. No target speed measured or firmware integration.',source_sha256_lf:sourceHash(file),header_sha256:hash(Buffer.from(header)),rows:rows.length,combinations,lookup_flash_bytes:rows.flat().length+map.length,additional_ram_bytes:0,actual_c_test:actual};
 const art=path.join(root,'firmware/development/esp8266-opus-bands-pulse-inverse');fs.mkdirSync(art,{recursive:true});
 fs.writeFileSync(path.join(art,'prototype.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={reference,generate};if(require.main===module)generate();

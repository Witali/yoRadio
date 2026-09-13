// Read-only code/profile audit, with reproducible JSON output. No speed claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,component,run,hash,sourceHash}=require('./export.cjs');
const {verify}=require('./verify.cjs');
const names=['ec_tell_frac','ec_decode','ec_decode_bin','ec_dec_update','ec_dec_uint',
 'ec_dec_bit_logp','ec_dec_bits','celt_lcg_rand','alg_unquant','decode_pulses'];
function inventory(compiler){
 const profile=path.join(root,'firmware/development/esp8266-opus-functions-192-v2/summary.json');
 const summary=JSON.parse(fs.readFileSync(profile));assert.equal(summary.functions.runs,10);assert.equal(summary.functions.case_id,4);
 const elf=path.join(root,'.build/esp8266-opus-functions-control-v2/yoradio_esp8266_helix_native.elf');
 const symbols=run(path.join(path.dirname(compiler),'xtensa-lx106-elf-nm.exe'),['-S',elf]);
 const texts=verify('gcc-asm').files.map(file=>({file,text:fs.readFileSync(file,'utf8')}));
 const rows=names.map(name=>{
  const definition=texts.map(({file,text})=>({file,body:text.match(new RegExp('^'+name+':[\\s\\S]*?(?=^\\s*\\.size\\s+'+name+',)','m'))?.[0]})).find(x=>x.body);assert.ok(definition,name);
  const instructions=definition.body.split(/\r?\n/).map(l=>l.split('#')[0].trim()).filter(l=>/^[a-z][a-z0-9.]*(?:\s|$)/.test(l)&&!l.endsWith(':'));
  const symbol=symbols.match(new RegExp('^([0-9a-f]+) ([0-9a-f]+) [Tt] '+name+'$','m'));assert.ok(symbol,name);
  const calls=texts.map(({file,text})=>({source:path.relative(component,file).replaceAll('\\','/'),sites:[...text.matchAll(new RegExp('^\\s*call0\\s+'+name+'(?:\\s|$)','gm'))].length})).filter(x=>x.sites);
  const frequency=summary.functions.rows.find(r=>r.name===name);
  return {name,asm_instructions_including_return:instructions.length,linked_text_bytes:parseInt(symbol[2],16),address:symbol[1],
   leaf:!instructions.some(l=>/^call/.test(l)),stack_store_sites:instructions.filter(l=>/^s32i\S*\s+.*\bsp,/.test(l)).length,
   static_call_sites:calls.reduce((n,r)=>n+r.sites,0),callers:calls,cross_object_calls_per_audio_second:frequency?.calls_per_audio_second??null,
   source_sha256_lf:sourceHash(definition.file)};
 });
 const report={scope:'Static GCC ASM instructions/linked text sizes joined to 10-run cross-object 192kbps profile. Counts include cold paths; null frequency means not instrumented, not zero. No inline speed measured.',
  profile_sha256:hash(fs.readFileSync(profile)),elf_sha256:hash(fs.readFileSync(elf)),rows};
 const out=path.join(root,'firmware/development/esp8266-opus-inline-audit');fs.mkdirSync(out,{recursive:true});
 fs.writeFileSync(path.join(out,'inventory.json'),JSON.stringify(report,null,2)+'\n');
 for(const {callers,source_sha256_lf,...row} of rows)console.log(JSON.stringify(row));return report;
}
module.exports={inventory};if(require.main===module)inventory(process.argv[2]);

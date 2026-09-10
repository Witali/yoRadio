const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root}=require('./build_host.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
function audit({before='.build/esp8266-opus-celt192-off',off='.build/esp8266-opus-div192-off',on='.build/esp8266-opus-div192-on',output='tools/esp8266_opus_profile/div-once-target-results.json'}={}) {
  const dump=args=>{const r=spawnSync(defaultObjdump,args,{encoding:'utf8',maxBuffer:8e6});if(r.error)throw r.error;assert.equal(r.status,0,r.stderr);return r.stdout;};
  const object=b=>path.resolve(root,b,'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/upstream/celt/vq.c.obj');
  const code=b=>dump(['-dr',object(b)]).replace(/^.*file format.*$/m,'OBJECT').replace(/\$\d+\b/g,'$ID').trim();
  assert.equal(code(off),code(before),'Disabled macro changed target instructions');
  const sites=b=>Object.fromEntries(['exp_rotation','alg_unquant','stereo_itheta'].map(symbol=>{
    const text=dump(['-dr','-j','.text.'+symbol,object(b)]);
    return [symbol,(text.match(/R_XTENSA_ASM_EXPAND\s+celt_rcp\b/g)||[]).length];
  }));
  const a=sites(off),b=sites(on);assert.equal(a.alg_unquant,3);
  // GCC now outlines the division/rotation body; follow the actual call,
  // rather than mistake zero direct calls for a removed calculation.
  const unquant=dump(['-dr','-j','.text.alg_unquant',object(on)]);
  const clone=unquant.match(/R_XTENSA_ASM_EXPAND\s+(\.text\.exp_rotation\$part\$[^\s]+)/)?.[1];
  assert.ok(clone,'Missing outlined rotation');assert.equal(b.alg_unquant,0);
  const cloneAsm=dump(['-dr','-j',clone,object(on)]);
  const cloneCalls=(cloneAsm.match(/R_XTENSA_ASM_EXPAND\s+celt_rcp\b/g)||[]).length;
  assert.equal(cloneCalls,1);
  assert.equal(a.exp_rotation,3);assert.equal(b.exp_rotation,1);
  const stack=b=>Object.fromEntries(fs.readFileSync(object(b).replace(/\.obj$/,'.su'),'utf8').split(/\r?\n/).filter(Boolean).map(line=>{
    const fields=line.replace(/^.*?:\d+:\d+:/,'').split(/\s+/);return [fields[0],Number(fields[1])];}));
  const sections=b=>Object.fromEntries([...dump(['-h',path.resolve(root,b,'yoradio_esp8266_helix_native.elf')]).matchAll(/^\s*\d+\s+(\.(?:iram0\.(?:text|bss|vectors)|dram0\.(?:data|bss)|flash\.(?:text|rodata)))\s+([\da-f]+)/gm)].map(m=>[m[1],parseInt(m[2],16)]));
  const sa=sections(off),sb=sections(on),delta=Object.fromEntries(Object.entries(sa).map(([k,v])=>[k,sb[k]-v]));
  for(const k of ['.dram0.data','.dram0.bss','.iram0.bss','.iram0.text'])assert.equal(delta[k],0,k);
  const result={passed:true,before,off,on,off_instructions_exact:true,normalization:'GCC dollar-number local symbol IDs only',
    reciprocal_call_sites:{off:a,on:b,outlined_rotation:{section:clone,celt_rcp:cloneCalls}},stack:{off:stack(off),on:stack(on)},sections:{off:sa,on:sb,delta},scope:'Static target audit, not a CPU speed or total live-stack measurement.'};
  fs.writeFileSync(path.resolve(root,output),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));return result;
}
module.exports={audit};if(require.main===module)audit();

const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root}=require('./build_host.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
function audit({before='.build/esp8266-opus-stage-off',off='.build/esp8266-opus-celt-off',on='.build/esp8266-opus-celt-on',output='tools/esp8266_opus_profile/celt-decode-target-results.json'}={}) {
  const cmd=args=>{const r=spawnSync(defaultObjdump,args,{encoding:'utf8',maxBuffer:8e6});assert.equal(r.status,0,r.stderr);return r.stdout;};
  const object=build=>path.resolve(root,build,'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/upstream/celt/bands.c.obj');
  // Adding an inline helper changes GCC's generated symbol IDs, not opcodes.
  // Keep all instruction bytes, offsets, constants and relocation base names.
  const code=build=>cmd(['-dr',object(build)]).replace(/^.*file format.*$/m,'OBJECT').replace(/\$\d+\b/g,'$ID').trim();
  const baseline=code(off),candidate=code(on);
  assert.equal(baseline,code(before),'Macro-off target instructions changed');
  assert.match(baseline,/R_XTENSA_32\s+alg_quant/);
  assert.doesNotMatch(candidate,/R_XTENSA_32\s+(?:alg_quant|ec_enc(?:_|ode))/,'Encoder path remains in bands');
  const stack=build=>fs.readFileSync(object(build).replace(/\.obj$/,'.su'),'utf8').split(/\r?\n/).filter(Boolean)
    .map(line=>line.replace(/^.*?:\d+:\d+:/,''));
  const elf=build=>path.resolve(root,build,'yoradio_esp8266_helix_native.elf');
  const sections=build=>Object.fromEntries([...cmd(['-h',elf(build)]).matchAll(/^\s*\d+\s+(\.(?:iram0\.(?:text|bss|vectors)|dram0\.(?:data|bss)|flash\.(?:text|rodata)))\s+([\da-f]+)/gm)]
    .map(m=>[m[1],parseInt(m[2],16)]));
  const a=sections(off),b=sections(on),delta=Object.fromEntries(Object.entries(a).map(([k,v])=>[k,b[k]-v]));
  for(const key of ['.dram0.data','.dram0.bss','.iram0.bss','.iram0.text'])assert.equal(delta[key],0,key);
  assert.ok(delta['.flash.text']<0,'Specialization did not remove code');
  const symbols=cmd(['-t',elf(on)]);assert.doesNotMatch(symbols,/\salg_quant$/m);
  const result={passed:true,before,off,on,off_instructions_exact:true,normalization:'GCC dollar-number local symbol IDs only',encoder_references_removed:true,alg_quant_linked:false,
    off_stack:stack(off),on_stack:stack(on),off_sections:a,on_sections:b,delta};
  fs.writeFileSync(path.resolve(root,output),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));return result;
}
module.exports={audit};if(require.main===module)audit();

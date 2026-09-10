const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root}=require('./build_host.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
function audit({before='.build/esp8266-opus-block-live',off='.build/esp8266-opus-stage-off',on='.build/esp8266-opus-stage-sdk-bands',output='.build/opus-stage-target.json'}={}) {
  const cmd=(args)=>{const r=spawnSync(defaultObjdump,args,{encoding:'utf8',maxBuffer:8e6});assert.equal(r.status,0,r.stderr);return r.stdout;};
  const result={before,off,on,objects:[]};
  for(const file of ['silk/decode_frame.c','silk/dec_API.c','celt/celt_decoder.c']) {
    const object=build=>path.resolve(root,build,'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/upstream',file+'.obj');
    const text=build=>cmd(['-dr',object(build)]).replace(/^.*file format.*$/m,'OBJECT').trim();
    const previous=text(before),disabled=text(off),enabled=text(on);
    assert.equal(disabled,previous,'disabled instrumentation changed target instructions: '+file);
    const clocks=(enabled.match(/R_XTENSA_32\s+opus_stage_profile_clock/g)||[]).length;
    assert.equal(clocks,file.startsWith('celt')?2:0,'only selected CELT scope may link two SDK clock reads');
    assert.ok(!/\brsr(?:\.ccount)?\s/.test(enabled),'raw CCOUNT must not be used');
    const stack=build=>fs.readFileSync(object(build).replace(/\.obj$/,'.su'),'utf8').split(/\r?\n/).filter(Boolean)
      .map(line=>line.replace(/^.*?:\d+:\d+:/,''));
    result.objects.push({file,off_instructions_exact:true,clock_helper_relocations:clocks,off_stack:stack(off),on_stack:stack(on)});
  }
  const elf=build=>path.resolve(root,build,'yoradio_esp8266_helix_native.elf');
  const sections=build=>Object.fromEntries([...cmd(['-h',elf(build)]).matchAll(/^\s*\d+\s+(\.(?:iram0\.(?:text|bss|vectors)|dram0\.(?:data|bss)|flash\.(?:text|rodata)))\s+([\da-f]+)/gm)]
    .map(m=>[m[1],parseInt(m[2],16)]));
  result.off_sections=sections(off);result.on_sections=sections(on);
  result.delta=Object.fromEntries(Object.entries(result.off_sections).map(([k,v])=>[k,result.on_sections[k]-v]));
  fs.writeFileSync(path.resolve(root,output),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result.delta));return result;
}
if(require.main===module)audit();module.exports={audit};

// Audit experiment only. This does not modify or flash production sources.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {spawnSync}=require('node:child_process');
const {root,component,execute,hostPath}=require('./build_host.cjs');
const {defaultCompiler}=require('./check_xtensa_word_access.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
const {sha256}=require('./fixtures.cjs');
const source=path.join(__dirname,'hoist_reciprocal_probe.c');
function run(output=path.join(__dirname,'hoist-reciprocal-results.json')) {
  const out=path.join(root,'.build/opus-hoist-reciprocal');fs.mkdirSync(out,{recursive:true});
  const includes=['upstream/include','upstream/celt','upstream/silk'].map(p=>path.join(component,p));
  const binary=path.join(out,'probe');
  const flags=['-O3','-std=c99','-fwrapv','-DOPUS_FAST_INT64=0','-ffunction-sections','-fdata-sections'];
  execute('gcc',[...flags,'-DOPUS_HOIST_HOST=1','-fno-pie','-no-pie','-fsanitize=address,undefined',
    '-fno-sanitize-recover=all',...includes.map(p=>'-I'+hostPath(p)),hostPath(source),
    hostPath(path.join(component,'upstream/celt/mathops.c')),'-Wl,--gc-sections',
    '-Wl,--wrap=celt_rcp','-lm','-o',hostPath(binary)]);
  const host=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(binary)]));
  const cmd=(program,args)=>{const r=spawnSync(program,args,{encoding:'utf8',maxBuffer:4e6});
    if(r.error)throw r.error;assert.equal(r.status,0,r.stdout+r.stderr);return r.stdout;};
  const object=path.join(out,'probe.o');
  cmd(defaultCompiler,[...flags,'-mlongcalls',...includes.map(p=>'-I'+p),'-c',source,'-o',object]);
  const symbols=cmd(defaultObjdump,['-t',object]);
  const target=['opus_div_original','opus_div_once'].map(symbol=>{
    const asm=cmd(defaultObjdump,['-dr','-j','.text.'+symbol,object]);
    const calls=(asm.match(/R_XTENSA_ASM_EXPAND\s+celt_rcp\b/g)||[]).length;
    const size=symbols.split(/\r?\n/).find(s=>s.endsWith(' '+symbol)||s.endsWith('\t'+symbol));
    assert.ok(size,'Missing '+symbol);
    const bytes=parseInt(size.trim().split(/\s+/).at(-2),16);
    const stack=Number(asm.match(/addi\s+a1,\s*a1,\s*-(\d+)/)?.[1]||0);
    return {symbol,celt_rcp_call_sites:calls,text_bytes:bytes,stack_bytes:stack,disassembly:asm};
  });
  assert.equal(target[0].celt_rcp_call_sites,3);assert.equal(target[1].celt_rcp_call_sites,1);
  const files=[source,...['mathops.h','mathops.c','fixed_generic.h'].map(p=>path.join(component,'upstream/celt',p))];
  const report={passed:true,scope:'Isolated exact arithmetic + GCC target audit. Not full PCM, board timing or a production change.',
    host_asan_ubsan:host,target,source_sha256_lf:Object.fromEntries(files.map(file=>
      [path.relative(root,file).replace(/\\/g,'/'),sha256(Buffer.from(fs.readFileSync(file,'utf8').replace(/\r\n/g,'\n')))]))};
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({...report,target:target.map(({disassembly,...v})=>v)},null,2));return report;
}
module.exports={run};if(require.main===module)run();

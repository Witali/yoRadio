// Reproducible, non-flashing Xtensa code-generation comparison. This reports
// code/stack size, not CPU time; both sides use the same compiler and wrapper.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {execute}=require('./run_rcpdm_radio');
const root=path.resolve(__dirname,'../..');
const header='esp8266/rtos-sdk-native/main/rc_pdm_feedback.h';
const hash=data=>crypto.createHash('sha256').update(data).digest('hex');
function compare(directory,baseline='8047b47',compilerDirectory) {
  directory=path.resolve(directory);
  const compiler=compilerDirectory||path.join(root,'.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin');
  const tool=name=>path.join(compiler,'xtensa-lx106-elf-'+name+(process.platform==='win32'?'.exe':''));
  const revision=execute('git',['rev-parse','--verify',baseline+'^{commit}'],{cwd:root}).stdout.trim();
  const wrapper=fs.readFileSync(path.join(root,'tests/native/rcpdm_feedback_codegen.c'));
  const flags=['-std=c11','-O3','-Wall','-Wextra','-Werror','-fstack-usage'];
  const result={schema:1,measurement:'code generation only; not board timing',baseline_revision:revision,
    compiler:execute(tool('gcc'),['--version']).stdout.split(/\r?\n/)[0],flags,
    wrapper_sha256:hash(wrapper),variants:{}};
  for(const variant of ['before','after']) {
    const dir=path.join(directory,variant);fs.mkdirSync(dir,{recursive:true});
    const source=variant==='before'?Buffer.from(execute('git',['show',revision+':'+header],{cwd:root}).stdout):fs.readFileSync(path.join(root,header));
    fs.writeFileSync(path.join(dir,'rc_pdm_feedback.h'),source);
    fs.writeFileSync(path.join(dir,'rcpdm_feedback_codegen.c'),wrapper);
    const build=execute(tool('gcc'),[...flags,'-I.','-c','rcpdm_feedback_codegen.c','-o','codegen.o'],{cwd:dir});
    fs.writeFileSync(path.join(dir,'build.log'),build.stdout+build.stderr);
    const nm=execute(tool('nm'),['-S','--size-sort','codegen.o'],{cwd:dir}).stdout;
    const undefinedSymbols=execute(tool('nm'),['-u','codegen.o'],{cwd:dir}).stdout.trim();
    if(undefinedSymbols)throw Error('Unexpected external helper: '+undefinedSymbols);
    const asm=execute(tool('objdump'),['-dr','codegen.o'],{cwd:dir}).stdout;
    fs.writeFileSync(path.join(dir,'codegen.asm.txt'),asm.split(/\r?\n/).map(line=>line.trimEnd()).join('\n').trimEnd()+'\n');
    const stack=fs.readFileSync(path.join(dir,'codegen.su'),'utf8');
    const functions={};
    for(const name of ['rc_feedback_codegen_sample','rc_feedback_codegen_fill']) {
      const size=nm.match(new RegExp('^\\S+\\s+([0-9a-f]+)\\s+T\\s+'+name+'$','mi'));
      const usage=stack.match(new RegExp(':'+name+'\\t(\\d+)\\tstatic'));
      if(!size||!usage)throw Error('Missing code/stack size: '+name);
      functions[name]={code_bytes:parseInt(size[1],16),stack_bytes:Number(usage[1])};
    }
    result.variants[variant]={algorithm_sha256:hash(source),functions,undefined_symbols:[]};
  }
  fs.writeFileSync(path.join(directory,'comparison.json'),JSON.stringify(result,null,2)+'\n');
  return result;
}
module.exports={compare};
if(require.main===module)console.log(JSON.stringify(compare(process.argv[2]||path.join(root,'.build/rcpdm-feedback-codegen'),process.argv[3],process.argv[4]),null,2));

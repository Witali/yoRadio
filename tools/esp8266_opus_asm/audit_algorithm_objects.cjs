// Cross-compile semantic prototypes for LX106. Object sizes/frame are not
// linked firmware, proof of an ASM patch, whole-stack maxima, or speed results.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,run,words,sourceHash}=require('./export.cjs');
const candidate=require('./algorithm_candidates.cjs');
function audit() {
 const database=path.join(root,'.build/esp8266-opus-early-reserve-c-20260917/compile_commands.json');
 const commands=JSON.parse(fs.readFileSync(database)),models=require('./ebands_final.cjs').cModels();
 const norm=s=>s.replaceAll('\\','/'),report={scope:'GCC LX106 object-only audit, not accepted frozen ASM or live stack/CPU measurement.',database_sha256:sourceHash(database),variants:[]};
 for(const kind of candidate.kinds.filter(k=>k!=='observe')) {
  const changes=candidate.generate(kind,models),units=[];
  for(const change of changes) {
   const entry=commands.find(e=>norm(e.file).endsWith('/'+change.source));assert.ok(entry);
   const args=words(entry.command),compiler=args.shift(),flags=[];
   for(let i=0;i<args.length;i++) {
    if(['-o','-MF','-MT','-MQ'].includes(args[i])){i++;continue;}
    if(['-c','-MD','-MMD','-MP','-fstack-usage'].includes(args[i])||args[i].startsWith('-g')||norm(args[i])===norm(entry.file))continue;
    let a=args[i];if(a.startsWith('-I')&&!path.isAbsolute(a.slice(2)))a='-I'+norm(path.resolve(entry.directory,a.slice(2)));
    if(a.startsWith('-DIDF_VER='))a='-DIDF_VER="v3.4"';flags.push(a);
   }
   const pair={source:change.source,flags};
   for(const [role,file]of [['control',change.base],['candidate',change.file]]) {
    const dir=path.join(path.dirname(change.file),'lx106');fs.mkdirSync(dir,{recursive:true});
    const stem=path.join(dir,role+'.'+path.basename(change.file,'.c')),object=stem+'.o';
    run(compiler,['-I'+norm(path.join(root,'esp8266/rtos-sdk-native/components/opus_decoder/upstream/celt')),...flags,'-g0','-fstack-usage','-c',file,'-o',object],entry.directory);
    const dump=path.join(path.dirname(compiler),'xtensa-lx106-elf-objdump.exe');
    const sections=Object.fromEntries([...run(dump,['-h',object]).matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>[m[1],parseInt(m[2],16)]));
    const dis=run(dump,['-dr',object]);fs.writeFileSync(stem+'.disassembly.txt',dis);
    const stack=fs.readFileSync(stem+'.su','utf8');fs.writeFileSync(stem+'.stack.txt',stack);
    pair[role]={source_sha256:sourceHash(file),sections,stack:stack.trim().split(/\r?\n/),disassembly_sha256:sourceHash(stem+'.disassembly.txt')};
   }
   units.push(pair);
  }
  report.variants.push({kind,units});console.log(kind,'LX106 objects compiled');
 }
 fs.writeFileSync(path.join(root,'.build/opus-algorithm-candidates/lx106.json'),JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={audit};if(require.main===module)audit();

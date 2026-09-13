/* Generate a reviewable GCC baseline, not a pretend handwritten decoder.
 * All generated source writes are reproducible compiler/artifact outputs. */
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const assert = require('node:assert/strict');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '../..');
const component = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder');
const norm = p => p.replaceAll('\\', '/');
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const sourceHash = p => hash(fs.readFileSync(p, 'utf8').replace(/\r\n/g, '\n'));
function run(exe, args, cwd) {
  const r = spawnSync(exe, args, {cwd, encoding:'utf8', maxBuffer:16e6});
  if(r.error) throw r.error;
  assert.equal(r.status, 0, `${exe}: ${r.stdout}\n${r.stderr}`);
  return r.stdout;
}
// CMake compile_commands on Windows: no shell execution and no eval.
function words(s) {
  const tokens = []; let word = '', quoted = false;
  for(let i=0;i<s.length;i++) {
    if(s[i]==='\\' && s[i+1]==='"') {word+='"';i++;}
    else if(s[i]==='"') quoted=!quoted;
    else if(/\s/.test(s[i])&&!quoted) {if(word){tokens.push(word);word='';}}
    else word+=s[i];
  }
  if(word)tokens.push(word);
  assert.equal(quoted,false,'Unterminated command quote');
  return tokens;
}
const roles = {
  entdec:'Range/entropy decoding shared by SILK and CELT; exact bitstream state is mandatory.',
  entcode:'Entropy bit accounting and integer arithmetic shared by decoder modules.',
  celt_decoder:'CELT frame decode, synthesis, packet-loss concealment and postprocessing.',
  bands:'CELT spectral-band decoding, allocation and recursive pulse vector processing.',
  vq:'CELT pulse-vector normalization, rotations and collapse masks.',
  mdct:'Modified discrete cosine transform and overlap synthesis.',
  kiss_fft:'Fixed-point FFT used by CELT inverse transforms.',
  opus_decoder:'Opus packet/frame dispatch across SILK, hybrid and CELT; public decoder API.',
  decode_core:'SILK short/long-term prediction and PCM synthesis.',
  PLC:'SILK packet-loss concealment and state recovery.',
};
function annotate(asm, relative, c) {
  const moduleName=path.basename(relative,'.c');
  const symbols=[...asm.matchAll(/^\s*\.type\s+([^,\s]+),\s*@function/gm)].map(m=>m[1]);
  const sourceLines=c.split(/\r?\n/);
  for(const symbol of symbols) {
    const original=symbol.split('.')[0];
    const start=sourceLines.findIndex(l=>new RegExp('\\b'+original+'\\s*\\(').test(l));
    // Include source context, not invented register assignments for IPA clones.
    const context=start<0?[]:sourceLines.slice(Math.max(0,start-3),start+5);
    const description=[`Function: ${symbol}`, `Module: ${relative}`,
      roles[moduleName] || `Fixed-point Opus ${relative.includes('/silk/')?'SILK':'CELT/support'} processing; see C source context below.`,
      'ABI: LX106 call0, arguments a2..a7 then caller stack; result a2 (a2/a3 for 64-bit).',
      'Callee preserves a12..a15 and a1; leaf/stack use is visible in the prologue.',
      'GCC-specialized clones may remove/reorder arguments: use annotated operands below.',
      'Memory: retain exact load/store widths. IRAM data requires aligned 32-bit accesses.',
      ...context.map(l=>'C context: '+l.trim())];
    asm=asm.replace(new RegExp('^'+symbol.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+':','m'),description.map(l=>'# '+l).join('\n')+'\n'+symbol+':');
  }
  return (`# Generated GCC baseline; DO NOT edit. Optimize with reviewed overlay patches.\n# Origin: ${relative}; upstream licenses remain in upstream/COPYING and source headers.\n# Flags and hashes: asm/lx106/manifest.json. This is compiler output, not handwritten ASM.\n`+asm).replace(/[ \t]+$/gm,'');
}
function exportAsm({database, output=path.join(component,'asm/lx106'), artifact=path.join(root,'firmware/development/esp8266-opus-asm-library')}) {
  database=path.resolve(database);
  const commands=JSON.parse(fs.readFileSync(database,'utf8'));
  const entries=commands.filter(e=>norm(e.file).includes('/components/opus_decoder/upstream/')&&e.file.endsWith('.c'));
  assert.ok(entries.length>80,'Expected full Opus component, not one hot kernel');
  fs.mkdirSync(output,{recursive:true}); fs.mkdirSync(artifact,{recursive:true});
  const objectsDir=path.join(root,'.build/opus-asm-export/objects');fs.mkdirSync(objectsDir,{recursive:true});
  const compiler=words(entries[0].command)[0], bin=path.dirname(compiler);
  const objdump=path.join(bin,'xtensa-lx106-elf-objdump.exe'), ar=path.join(bin,'xtensa-lx106-elf-ar.exe');
  const files=[], objects=[], protectedSources=new Map();
  const featureDefines=new Set();
  for(const entry of entries) {
    const original=norm(entry.file), originalComponent=original.split('/upstream/')[0];
    const relative=original.slice(originalComponent.length+1), source=path.join(component,relative);
    const args=words(entry.command).slice(1), flags=[];
    for(let i=0;i<args.length;i++) {
      if(['-o','-MF','-MT','-MQ'].includes(args[i])){i++;continue;}
      if(['-c','-MD','-MMD','-MP','-fstack-usage'].includes(args[i])||args[i].startsWith('-g')||norm(args[i])===original)continue;
      let a=norm(args[i]).replaceAll(originalComponent,norm(component));
      if(a.startsWith('-I')&&!path.isAbsolute(a.slice(2)))a='-I'+norm(path.resolve(entry.directory,a.slice(2)));
      if(a.startsWith('-DIDF_VER='))a='-DIDF_VER="v3.4"';
      if(a.startsWith('-DYORADIO_OPUS_'))featureDefines.add(a.slice(2));
      flags.push(a);
    }
    const asmFile=path.join(output,'gcc',relative+'.s'), rawFile=asmFile+'.raw';
    fs.mkdirSync(path.dirname(asmFile),{recursive:true});
    run(compiler,[...flags,'-g0','-S','-fverbose-asm','-MMD','-MF',rawFile+'.d',source,'-o',rawFile],entry.directory);
    const dependencies=fs.readFileSync(rawFile+'.d','utf8').replace(/\\\r?\n/g,' ').split(/\s+/).filter(p=>!p.endsWith(':')&&norm(p).startsWith(norm(component)+'/')&&!norm(p).startsWith(norm(output)+'/'));
    for(const p of dependencies)protectedSources.set(norm(path.relative(component,p)),sourceHash(p));
    protectedSources.set(relative,sourceHash(source));
    // Normalize comments only: never rewrite a runtime string or constant.
    let text=fs.readFileSync(rawFile,'utf8').split('\n').map(line=>line.trimStart().startsWith('#')?line.replaceAll(norm(component),'@OPUS@').replaceAll(component,'@OPUS@'):line).join('\n');
    text=annotate(text,relative,fs.readFileSync(source,'utf8'));
    fs.writeFileSync(asmFile,text);
    const object=path.join(objectsDir,relative.replaceAll('/','__')+'.o');
    run(compiler,['-mlongcalls','-c','-x','assembler',asmFile,'-o',object],entry.directory);
    // Independent C -> object control verifies the serialization/annotation step.
    const control=object+'.control';
    run(compiler,[...flags,'-g0','-c',source,'-o',control],entry.directory);
    const dump=p=>run(objdump,['-dr',p]).split('\n').slice(3).join('\n');
    assert.equal(dump(object),dump(control),relative+': ASM round-trip changes instructions/relocations');
    const contents=p=>run(objdump,['-s',p]).split('\n').slice(3).join('\n');
    assert.equal(contents(object),contents(control),relative+': ASM round-trip changes section contents');
    const sizeText=run(objdump,['-h',object]);
    const sections=[...sizeText.matchAll(/^\s*\d+\s+(\S+)\s+([0-9a-f]+)\s/gm)].map(m=>({name:m[1],bytes:parseInt(m[2],16)}));
    files.push({source:relative,asm:'gcc/'+relative+'.s',source_sha256_lf:sourceHash(source),asm_sha256_lf:sourceHash(asmFile),functions:[...text.matchAll(/^\s*\.type\s+([^,\s]+),\s*@function/gm)].map(m=>m[1]),sections,roundtrip_exact:true,section_contents_exact:true});
    objects.push(object);
    fs.unlinkSync(rawFile);fs.unlinkSync(rawFile+'.d');
    if(files.length%10===0)console.log(`Exported and checked ${files.length}/${entries.length} translation units`);
  }
  const library=path.join(artifact,'libopus-gcc-asm.a');
  // ar q into a fresh temporary archive avoids retaining stale removed members.
  const temporary=library+'.new';if(fs.existsSync(temporary))fs.unlinkSync(temporary);
  for(let i=0;i<objects.length;i+=20)run(ar,['qD',temporary,...objects.slice(i,i+20)]);
  run(ar,['sD',temporary]);fs.renameSync(temporary,library);
  const manifest={schema:1,compiler:run(compiler,['--version']).split(/\r?\n/)[0],cpu:'LX106',abi:'call0',optimization:'O3',fixed_point:true,kind:'GCC-generated baseline, not handwritten',feature_defines:[...featureDefines].sort(),source_commit:run('git',['rev-parse','HEAD'],root).trim(),protected_sources:Object.fromEntries([...protectedSources].sort()),files,library_sha256:hash(fs.readFileSync(library)),library_bytes:fs.statSync(library).size,roundtrip_exact:true};
  fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  fs.copyFileSync(path.join(output,'manifest.json'),path.join(artifact,'manifest.json'));
  console.log(`Saved ${files.length} ASM units and ${manifest.library_bytes}-byte standalone archive`);
  return manifest;
}
module.exports={exportAsm,words,annotate,hash,sourceHash,root,component,run};
if(require.main===module){const i=process.argv.indexOf('--compile-commands');assert.ok(i>=0,'--compile-commands PATH required');exportAsm({database:process.argv[i+1]});}

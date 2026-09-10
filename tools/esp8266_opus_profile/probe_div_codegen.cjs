// Local compiler experiment only: no firmware linking, flashing or timing claim.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component}=require('./build_host.cjs');
const {sha256}=require('./fixtures.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
const {parseDisassembly,parseSymbols}=require('./audit_target.cjs');
const build=path.join(root,'.build/esp8266-opus-div192-on');
const out=path.join(root,'.build/opus-div-codegen');fs.mkdirSync(out,{recursive:true});
const entry=JSON.parse(fs.readFileSync(path.join(build,'compile_commands.json'),'utf8')).find(e=>/[/\\]celt[/\\]vq\.c$/.test(e.file));
assert.ok(entry);assert.doesNotMatch(entry.command,/[&|<>\r\n]/);
assert.doesNotMatch(entry.command,/(?:^|\s)-M(?:D|MD|F|T)(?:\s|$)/,'Do not overwrite build dependency outputs');
const cases=[['configured',[]],['no-partial',['-fno-partial-inlining']],
  ['inline-1000',['-finline-limit=1000']],['no-partial-inline-1000',['-fno-partial-inlining','-finline-limit=1000']]];
const reports=[];
for(const [name,flags] of cases) {
  const object=path.join(out,name+'.o').replaceAll('\\','/');assert.ok(!/\s/.test(object));
  const command=entry.command.replace(/\s-o\s+\S+/,` ${flags.join(' ')} -o ${object}`);
  assert.notEqual(command,entry.command);
  const r=spawnSync(command,{shell:true,cwd:entry.directory,encoding:'utf8',maxBuffer:4e6});
  if(r.error)throw r.error;assert.equal(r.status,0,r.stdout+r.stderr);
  const dump=args=>{const d=spawnSync(defaultObjdump,args,{encoding:'utf8',maxBuffer:4e6});assert.equal(d.status,0,d.stderr);return d.stdout;};
  const asm=dump(['-dr',object]);fs.writeFileSync(path.join(out,name+'.asm'),asm);
  const symbols=parseSymbols(dump(['-t',object]));
  const functions=parseDisassembly(asm).map(f=>({name:f.name,bytes:symbols.get(f.name)?.bytes,calls:f.calls}));
  const stack=fs.readFileSync(object.replace(/\.o$/,'.su'),'utf8').split(/\r?\n/).filter(Boolean).map(s=>s.replace(/^.*?:\d+:\d+:/,''));
  reports.push({name,flags,object_sha256:sha256(fs.readFileSync(object)),functions,stack});
  console.log(name,JSON.stringify(functions.filter(f=>f.name==='alg_unquant'||f.name.startsWith('exp_rotation'))));
}
const sources=['upstream/celt/vq.c','upstream/celt/mathops.h','upstream/celt/fixed_generic.h'];
const result={scope:'Compiler-only candidates, not accepted optimization or board speed evidence.',
  build:path.relative(root,build).replaceAll('\\','/'),command:entry.command,
  source_sha256_lf:Object.fromEntries(sources.map(file=>[file,sha256(Buffer.from(fs.readFileSync(path.join(component,file),'utf8').replace(/\r\n/g,'\n')))])),
  reports};
fs.writeFileSync(path.join(__dirname,'div-codegen-results.json'),JSON.stringify(result,null,2)+'\n');

/* Offline LX106 correctness runner. No network, serial, OTA or firmware writes. */
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),zlib=require('node:zlib');
const {spawnSync}=require('node:child_process');
const {root,hash}=require('../esp8266_opus_asm/export.cjs');
const {sections}=require('../esp8266_opus_asm/frozen_div.cjs');
const {patchElf}=require('../esp8266_opus_asm/frozen_reloads.cjs');
const defaultBin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
function command(exe,args,options={}) {
 const r=spawnSync(exe,args,{encoding:'utf8',maxBuffer:64*1024*1024,timeout:60000,...options});
 if(r.error)throw r.error;
 assert.equal(r.status,0,`${exe}: ${r.status}\n${r.stdout?.slice(-2500)}\n${r.stderr}`);return r.stdout;
}
function symbols(elf,bin) {
 return Object.fromEntries([...command(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',elf]).matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
}
function parseOutput(output,selected,{selfTests=true}={}) {
 const cases=[];let current=null,parts=[],stateBytes,stackBytes,recoveries=0,passed=false;
 for(const line of output.trim().split(/\r?\n/)) {
  if(/^STATE [0-9a-f]{8} $/.test(line)){assert.equal(stateBytes,undefined);stateBytes=parseInt(line.slice(6),16);}
  else if(line.startsWith('BEGIN ')){assert.equal(current,null);current=line.slice(6);assert.ok(selected.some(f=>f.name===current));assert.ok(!cases.some(f=>f.name===current));parts=[];}
  else if(/^P (?:[0-9a-f]{4}){1,32}$/.test(line)){assert.ok(current);parts.push(Buffer.from(line.slice(2),'hex'));}
  else if(/^END (?:[0-9a-f]{8} ){4}$/.test(line)){
   const values=line.slice(4).trim().split(/\s+/).map(x=>parseInt(x,16)),pcm=Buffer.concat(parts),f=selected.find(x=>x.name===current);assert.ok(f);
   assert.equal(hash(pcm),f.pcm_sha256,current+' PCM');assert.equal(pcm.length,f.pcm_bytes);assert.equal(values[0],f.samples);assert.equal(values[1],f.packet_count);
   assert.ok(values[2]<=6144&&values[3]<=16384);cases.push({name:current,pcm_sha256:hash(pcm),samples:values[0],packets:values[1],byte_peak:values[2],word_peak:values[3],pcm});current=null;
  } else if(line==='RECOVERY PASS'){assert.equal(current,null);++recoveries;}
  else if(/^STACK_USED [0-9a-f]{8} $/.test(line)){assert.equal(stackBytes,undefined);stackBytes=parseInt(line.slice(11),16);assert.ok(stackBytes>0&&stackBytes<8192);}
  else if(line==='PASS'){assert.equal(passed,false);passed=true;}
  else throw Error('Unexpected QEMU output: '+line.slice(0,150));
 }
 assert.ok(passed);assert.equal(current,null);assert.ok(stateBytes>0&&stateBytes<=24000);assert.ok(stackBytes);
 assert.equal(cases.length,selected.length);assert.equal(recoveries,selfTests?selected.length:0);
 return {cases,state_bytes:stateBytes,stack_used_in_harness:stackBytes,oom_recovery_cases:recoveries};
}
async function main(args=process.argv.slice(2)) {
 const values=new Set(['--variant','--fixture','--qemu','--toolchain']);
 const flags=new Set(['--extended','--no-self-tests','--fault-guard','--trace-pvq']);
 for(let i=0;i<args.length;++i) {
  if(values.has(args[i])){assert.ok(args[i+1]&&!args[i+1].startsWith('--'),'Missing value for '+args[i]);++i;}
  else assert.ok(flags.has(args[i]),'Unknown option '+args[i]);
 }
 const get=(n,d)=>{const i=args.indexOf(n);return i<0?d:args[i+1];};
 const variant=get('--variant','esp8266-opus-ebands-final-candidate-v2');assert.match(variant,/^[a-z0-9-]+$/);
 const qemu=get('--qemu','C:/Work/QEMU-ESP32/bin/qemu-system-xtensa.exe'),bin=get('--toolchain',defaultBin);
 const out=path.join(root,'.build/opus-qemu',variant);fs.mkdirSync(out,{recursive:true});
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify({passed:false,status:'in_progress',variant},null,2)+'\n');
 const artifact=path.join(root,'firmware/development',variant),proof=JSON.parse(fs.readFileSync(path.join(artifact,'preflight.json')));
 const parent=zlib.gunzipSync(fs.readFileSync(path.join(artifact,'parent.elf.gz')));assert.equal(hash(parent),proof.parent_elf_sha256);
 const source=patchElf(parent,proof.patches);assert.equal(hash(source),proof.candidate_elf_sha256);
 const elf=path.join(out,'decoder.elf');fs.writeFileSync(elf,source);
 const ss=sections(source),syms=symbols(elf,bin);
 assert.ok(ss.some(s=>s.name==='.flash.text'));
 const fixtureDir=path.join(root,'firmware/development/esp8266-opus-asm-library/fixtures');
 const manifest=JSON.parse(fs.readFileSync(path.join(fixtureDir,'manifest.json')));
 let available=manifest.fixtures.map(f=>({...f,file:path.join(fixtureDir,f.name+'.opuspkt')}));
 let extendedReference;
 if(args.includes('--extended')) {
  const {buildHost,execute,hostPath}=require('../esp8266_opus_profile/build_host.cjs');
  const {grouped}=require('../esp8266_opus_profile/run_block_regressions.cjs');
  console.log('Building/checking generic32 host PCM oracle (no target hardware)');
  const host=await buildHost({bounded:true,fastInt64:0,firFlashWord:true,sanitize:true});
  extendedReference={kind:'Vendored generic32 bounded C, ASan/UBSan, not a pristine independent decoder',binary_sha256:hash(fs.readFileSync(host.binary))};
  const extra=require('../esp8266_opus_asm/high_fixtures.cjs').generate();
  const phase=path.join(root,'tests/fixtures/opus_native/phase');
  for(const name of fs.readdirSync(phase).filter(n=>n.endsWith('.opuspkt')).sort())extra.push({name:'phase-'+name,file:path.join(phase,name)});
  for(const [name,file,count] of [['192-120ms',available.find(f=>f.name==='stereo-192').file,6],['320-120ms',extra.find(f=>f.name==='stereo-320-20ms').file,6],['320-48frames',extra.find(f=>f.name==='stereo-320-2.5ms').file,48]]) {
   const dest=path.join(out,name+'.opuspkt');fs.writeFileSync(dest,grouped(fs.readFileSync(file),count));extra.push({name,file:dest});
  }
  const mixed=path.join(out,'mixed.opuspkt');
  fs.writeFileSync(mixed,Buffer.concat(['mono-12','mono-24','stereo-64','stereo-192','mono-12'].map(n=>fs.readFileSync(available.find(f=>f.name===n).file))));
  extra.push({name:'mixed',file:mixed});
  for(const f of extra) {
   const pcmFile=path.join(out,f.name+'.reference.pcm');
   const reference=JSON.parse(execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(host.binary),hostPath(f.file),hostPath(pcmFile),'--self-test']));
   const data=fs.readFileSync(f.file),pcm=fs.readFileSync(pcmFile);let packets=0;
   for(let p=0;p<data.length;){assert.ok(p+2<=data.length);const n=data.readUInt16LE(p);assert.ok(n&&p+2+n<=data.length);p+=2+n;++packets;}
   available.push({...f,selected_opuspkt_sha256:hash(data),pcm_sha256:hash(pcm),pcm_bytes:pcm.length,samples:pcm.length/2,packet_count:packets,reference});
  }
 }
 const selected=available.filter(f=>!get('--fixture','')||f.name===get('--fixture',''));
 assert.ok(selected.length);
 let header='struct fixture { const char *name; const unsigned char *data; unsigned bytes; };\n';
 for(const [i,f] of selected.entries()) {
  const data=fs.readFileSync(f.file);assert.equal(hash(data),f.selected_opuspkt_sha256);
  fs.writeFileSync(path.join(out,f.name+'.input.opuspkt'),data);
  header+=`static const unsigned char fixture_${i}[]={${[...data].join(',')}};\n`;
 }
 header+=`#define FIXTURE_COUNT ${selected.length}\nstatic const struct fixture fixtures[]={\n`+selected.map((f,i)=>`{"${f.name}",fixture_${i},sizeof(fixture_${i})}`).join(',\n')+'};\n';
 fs.writeFileSync(path.join(out,'fixtures.h'),header);
 const apis=['opus_decoder_get_size','opus_decoder_init','yoradio_opus_memory_bind','yoradio_opus_decode_bounded','yoradio_opus_scratch_peak_bytes','yoradio_opus_scratch_peak_words'];
 const rom={memcpy:'q_memcpy',memmove:'q_memmove',memset:'q_memset',__udivsi3:'q_udiv',__umodsi3:'q_umod',__divsi3:'q_sdiv',__muldi3:'q_muldi'};
 let shim='',script='ENTRY(qemu_start)\nSECTIONS {\n';
 for(const [name,target] of Object.entries(rom)) {
  assert.ok(syms[name]>=0x40000000&&syms[name]<0x40100000,name);
  script+=`.rom_${name} 0x${(syms[name]-4).toString(16)} : { KEEP(*(.rom_${name})) }\n`;
  shim+=`.section .rom_${name},"ax"\n.align 4\n.L${name}: .word ${target}\nl32r a8, .L${name}\njx a8\n`;
 }
 // All exception vectors enter a bounded fail-fast report, never a silent hang.
 for(const addr of [0x40000030,0x40000050,0x40000070]) {
  script+=`.trap_${addr} 0x${(addr-4).toString(16)} : { KEEP(*(.trap_${addr})) }\n`;
  shim+=`.section .trap_${addr},"ax"\n.align 4\n.L${addr}: .word qemu_exception\nl32r a8, .L${addr}\njx a8\n`;
 }
 shim+='.section .text.qemu_exception,"ax"\n.literal_position\n.global qemu_exception\nqemu_exception:\nrsr a2, exccause\nrsr a3, epc1\nrsr a4, excvaddr\ncall0 qemu_trap\n1: j 1b\n';
 script+=' .text 0x60000000 : { *(.literal .literal.*) *(.entry) *(.text .text.*) *(.rodata .rodata.*) }\n'+
  '.data 0x3ffc0000 : { *(.data .data.*) }\n.bss 0x3ffc1000 (NOLOAD) : { *(.bss .bss.* COMMON) }\n'+
  'ASSERT(. < 0x3ffe8000,"Harness overlaps original firmware data")\n/DISCARD/ : { *(.comment) *(.note*) *(.eh_frame*) }\n}\n';
 for(const name of apis){assert.ok(syms[name]);script+=`${name} = 0x${syms[name].toString(16)};\n`;}
 // Reject overlap with every loaded firmware section, not just a guessed map.
 for(const s of ss.filter(s=>(s.flags&2)&&s.bytes)) {
  for(const [start,end] of [[0x3ffc0000,0x3ffe8000],[0x3fff6000,0x3fff8000],[0x40108000,0x4010c010],[0x60000000,0x60800000]])
   assert.ok(s.address+s.bytes<=start||s.address>=end,'Harness overlaps '+s.name);
 }
 fs.writeFileSync(path.join(out,'harness.ld'),script);fs.writeFileSync(path.join(out,'rom.S'),shim);
 const gcc=path.join(bin,'xtensa-lx106-elf-gcc.exe');
 const selfTests=!args.includes('--no-self-tests');
 command(gcc,['-O2','-g','-mlongcalls','-mtext-section-literals','-ffreestanding','-fno-builtin','-fno-tree-loop-distribute-patterns','-ffunction-sections','-fdata-sections','-nostdlib',
  '-DQEMU_SELF_TESTS='+Number(selfTests),'-DQEMU_FAULT_GUARD='+Number(args.includes('--fault-guard')),
  '-I',out,path.join(__dirname,'boot.S'),path.join(__dirname,'harness.c'),path.join(out,'rom.S'),'-Wl,-T,'+path.join(out,'harness.ld'),'-Wl,--gc-sections','-o',path.join(out,'harness.elf')]);
 const argv=['-M','sim','-cpu','lx106','-m','8M','-nographic','-monitor','none','-serial','none','-nic','none','-semihosting',
  '-device','loader,file='+elf,'-device','loader,file='+path.join(out,'harness.elf')+',cpu-num=0'];
 if(args.includes('--trace-pvq')) {
  assert.equal(selected.length,1,'Trace one fixture at a time');assert.equal(selfTests,false,'Use --no-self-tests for instruction comparisons');
  argv.push('-d','in_asm,exec,nochain','-dfilter',require('./trace.cjs').traceFilter(proof,variant),'-D',path.join(out,'trace.log'));
 }
 console.log('QEMU LX106:',variant,selected.map(f=>f.name).join(', '));
 const r=spawnSync(qemu,argv,{encoding:'utf8',maxBuffer:64*1024*1024,timeout:60000});
 fs.writeFileSync(path.join(out,'stdout.log'),r.stdout||'');fs.writeFileSync(path.join(out,'stderr.log'),r.stderr||'');
 if(r.error)throw r.error;assert.equal(r.status,0,`QEMU ${r.status}: ${r.stdout?.slice(-2000)} ${r.stderr}`);
 const parsed=parseOutput(r.stdout,selected,{selfTests});
 const cases=parsed.cases.map(({pcm,...c})=>{fs.writeFileSync(path.join(out,c.name+'.pcm'),pcm);return c;});
 const report={passed:true,scope:'QEMU LX106 instruction execution and PCM correctness; NOT hardware timing or full ESP8266 emulation',variant,elf_sha256:hash(source),qemu:command(qemu,['--version']).trim(),qemu_sha256:hash(fs.readFileSync(qemu)),
  compiler:command(gcc,['--version']).split(/\r?\n/)[0],harness_elf_sha256:hash(fs.readFileSync(path.join(out,'harness.elf'))),
  recipe_hashes:Object.fromEntries(['run.cjs','harness.c','boot.S','trace.cjs'].map(n=>[n,hash(fs.readFileSync(path.join(__dirname,n),'utf8').replace(/\r\n/g,'\n'))])),
  rom_substitutes:Object.keys(rom),extended_reference:extendedReference,fixtures:selected.map(f=>({name:f.name,packet_sha256:f.selected_opuspkt_sha256,pcm_sha256:f.pcm_sha256})),...parsed,cases};
 if(args.includes('--trace-pvq')) {
  // Pure SILK packets (TOC configurations 0..11) do not call CELT PVQ.
  // Permit an empty trace only after exact PCM and packet-mode verification.
  const {packets}=require('../esp8266_opus_profile/run_block_regressions.cjs');
  const silkOnly=selected.every(f=>packets(fs.readFileSync(f.file)).every(p=>(p[0]>>>3)<12));
  const trace=fs.readFileSync(path.join(out,'trace.log'),'utf8'),summary=require('./trace.cjs').summarize(trace,{helperName:variant.includes('n4-prefix')?'N4':'N3',allowEmpty:silkOnly});
  fs.writeFileSync(path.join(out,'trace-summary.json'),JSON.stringify(summary,null,2)+'\n');
  report.instruction_trace={sha256:hash(trace),silk_only:silkOnly,...summary};delete report.instruction_trace.pc_counts;
 }
 fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));return report;
}
module.exports={main,symbols,parseOutput};if(require.main===module)main().catch(e=>{console.error(e);process.exitCode=1;});

const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {root,run,hash}=require('./export.cjs'),{inspect,linkedGraph}=require('./report_layout.cjs');
const {wordAt}=require('./audit_update_link.cjs'),{helperDisassembly}=require('./small_div_link.cjs');
const variant=process.argv[2]||'esp8266-opus-division-micro-v2',dest=path.join(root,'firmware/development',variant);
function preflight(){
 require('./verify.cjs').verify('bands-small-div-asm');
 const read=p=>JSON.parse(fs.readFileSync(p));
 const m=read(path.join(dest,'manifest.json')),app=fs.readFileSync(path.join(dest,'app.bin'));
 assert.equal(m.bytes,app.length);assert.equal(hash(app),m.app_sha256.toLowerCase());
 assert.ok(app.length<=0xf0000);assert.equal(m.opus_division_benchmark,true);
 assert.equal(m.opus_backend,'bands-small-div-asm');assert.equal(m.diagnostic,true);
 assert.equal(m.opus_benchmark_output,false);assert.equal(m.opus_function_profile,false);assert.equal(m.opus_profile_stage,0);
 const census=path.join(root,'.build/opus-bands-division-census');
 assert.equal(hash(fs.readFileSync(path.join(census,'opus_division_fixtures.h'))),m.opus_division_header_sha256.toLowerCase());
 assert.equal(hash(fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/opus_division_benchmark.inc'))),m.opus_division_source_sha256.toLowerCase());
 const old=read(path.join(root,'firmware/development/esp8266-opus-bands-small-div-v1/preflight.json'));
 const current=inspect(variant,['ec_decode','quant_partition']);
 for(const [s,n]of Object.entries(old.candidate.sections).filter(([s])=>!s.startsWith('.flash.')))assert.equal(current.sections[s],n,s);
 const elf=path.join(root,'.build',variant,'yoradio_esp8266_helix_native.elf');
 const bin='C:/Work/yoRadio/.build/esp8266-tools/tools/xtensa-lx106-elf/esp-2020r3-49-gd5524c1-8.4.0/xtensa-lx106-elf/bin';
 const symbols=Object.fromEntries([...run(path.join(bin,'xtensa-lx106-elf-nm.exe'),['-n',elf]).matchAll(/^([0-9a-f]+)\s+\S\s+(\S+)$/gm)].map(m=>[m[2],parseInt(m[1],16)]));
 const dump=(start,end)=>run(path.join(bin,'xtensa-lx106-elf-objdump.exe'),['-d','--start-address=0x'+start.toString(16),'--stop-address=0x'+end.toString(16),elf]);
 const start=symbols.yoradio_opus_small_udiv,dis=helperDisassembly(start,start+114,dump);
 const graph=linkedGraph(dis,n=>wordAt(elf,n),n=>n===symbols.yoradio_opus_small_div_table?'yoradio_opus_small_div_table':n===symbols.__udivsi3?'__udivsi3':'0x'+n.toString(16)).graph;
 assert.deepEqual(graph,old.helper.graph);
 for(const [i,n]of require('./small_div.cjs').table.entries())assert.equal(wordAt(elf,symbols.yoradio_opus_small_div_table+4*i),n);
 const pairs=fs.readFileSync(path.join(census,'operands.bin'));
 for(let i=0;i<pairs.length;i+=4)assert.equal(wordAt(elf,symbols._ZL19opus_division_pairs+i),pairs.readUInt32LE(i));
 const batchName=Object.keys(symbols).find(s=>s.includes('division_batch'));
 const next=Object.values(symbols).filter(n=>n>symbols[batchName]).sort((a,b)=>a-b)[0];
 const batch=dump(symbols[batchName],next);assert.equal((batch.match(/\bcallx0\b/g)||[]).length,1);
 assert.equal(symbols.__udivsi3,0x4000e21c);
 const report={passed:true,manifest:m,static_ram_delta:0,sections:current.sections,helper_graph:graph,
  rom_address:symbols.__udivsi3,helper_address:start,batch_disassembly:batch,operand_bytes:pairs.length,
  scope:'Same-image helper arithmetic timing only, NOT raw decoder CPU'};
 fs.writeFileSync(path.join(dest,'preflight.json'),JSON.stringify(report,null,2)+'\n');console.log('PASS',m.bytes,'bytes; same helper/table; all operands exact; static RAM unchanged');
}
if(require.main===module)preflight();

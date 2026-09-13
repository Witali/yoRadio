const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {profiles,checkCommands,literalSites}=require('../tools/esp8266_opus_asm/report_literals.cjs');
test('literal profile differs only by placement and artifact identity',()=>{
 const a={opus_backend:'bands-tell-inline-asm',diagnostic:true,opus_benchmark:true,opus_benchmark_output:false,opus_function_profile:false,opus_profile_stage:0,bytes:1,cpu_mhz:160},b={...a,opus_bands_text_literals:true,bytes:2};
 profiles(a,b);assert.throws(()=>profiles(a,{...b,cpu_mhz:80}));assert.throws(()=>profiles(a,{...b,opus_backend:'c'}));assert.throws(()=>profiles(a,{...b,opus_bands_text_literals:false}));
});
test('text literal option is scoped to exactly one pinned bands ASM unit',()=>{
 const c={file:'C:/repo/asm/lx106/bands-tell-inline/upstream/celt/bands.c.s',command:'gcc -Wa,--text-section-literals'};
 checkCommands([c,{file:'other.c',command:'gcc'}]);assert.throws(()=>checkCommands([]));assert.throws(()=>checkCommands([c,c]));assert.throws(()=>checkCommands([{...c,file:'other.c'}]));
});
test('literal offsets are recorded without claiming cache misses',()=>{
 assert.deepEqual(literalSites({disassembly:'40200110: 000021 l32r a2, 40200100 <literal>\n'}),[{pc:0x40200110,register:'a2',pool:0x40200100,distance:16}]);
});
test('build flag defaults OFF and protects production/C fallback',()=>{
 const c=fs.readFileSync(path.join(__dirname,'../esp8266/rtos-sdk-native/components/opus_decoder/CMakeLists.txt'),'utf8');
 assert.match(c,/option\(YORADIO_OPUS_BANDS_TEXT_LITERALS [^\n]+ OFF\)/);
 assert.match(c,/NOT YORADIO_ESP8266_DIAGNOSTIC OR NOT YORADIO_OPUS_BACKEND STREQUAL "bands-tell-inline-asm"/);
 assert.match(c,/set_property\(SOURCE "\$\{src\}" APPEND PROPERTY COMPILE_OPTIONS "-Wa,--text-section-literals"\)/);
});

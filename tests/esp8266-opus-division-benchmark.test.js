const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {validate}=require('../tools/esp8266_opus_asm/run_division.cjs');
const {root}=require('../tools/esp8266_opus_asm/export.cjs');
function sample(){
 const census={cases:[{calls:193}]};
 const result={division_microbenchmark:true,clock_hz:1000000,state:3,error:0,results:[],run:1,warm:false,rounds:10,
  divisions:[{id:0,error:0,calls:1930,batches:20,reference_hash:7,candidate_hash:7,min_dram:1000,stack_free_lifetime:1000,reference_ticks:500,candidate_ticks:400}]};
 return {census,result};
}
test('paired helper validator checks every operand count/hash and distinct schema',()=>{
 const {census,result}=sample();validate(result,census);
 for(const field of ['calls','batches','candidate_hash','error']){
  const r=structuredClone(result);r.divisions[0][field]++;assert.throws(()=>validate(r,census));
 }
 const raw=structuredClone(result);raw.results=[{}];assert.throws(()=>validate(raw,census));
});
test('microbenchmark remains opt-in, bounded, cancellation-aware and without UART/cache tricks',()=>{
 const text=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/opus_division_benchmark.inc'),'utf8');
 assert.match(text,/sizeof\(opus_benchmark_case_t\)==44/);
 assert.match(text,/heap_caps_malloc\(kPacketBytes,MALLOC_CAP_8BIT\)/);
 assert.match(text,/heap_caps_free\(pairs\)/);assert.match(text,/current\(generation\)/);
 assert.match(text,/noinline,noclone/);assert.match(text,/vTaskDelay\(1\)/);
 assert.match(text,/esp_timer_get_time\(\)/);
 assert.doesNotMatch(text,/rsr.*ccount/);
 assert.doesNotMatch(text,/\b(xTaskCreate|uart_write|Cache_Read_Disable|portDISABLE_INTERRUPTS)\s*\(/);
 const main=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/opus_benchmark.cpp'),'utf8');
 assert.match(main,/#if YORADIO_ESP8266_OPUS_DIVISION_BENCHMARK\n#include "opus_division_benchmark.inc"\n#else/);
});

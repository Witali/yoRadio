const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {root,component,execute,hostPath}=require('../tools/esp8266_opus_profile/build_host.cjs');
const {names,analyzeFunctions}=require('../tools/esp8266_opus_profile/function_profile_result.cjs');
function sample(){
 const rows=names.map((_,id)=>({id,calls:0,cpu_us:0,self_cpu_us:0,max_cpu_us:0,wall_us:0,self_wall_us:0,max_wall_us:0}));
 Object.assign(rows[0],{calls:2,cpu_us:100,self_cpu_us:70,max_cpu_us:60,wall_us:150,self_wall_us:100,max_wall_us:80});
 Object.assign(rows[2],{calls:2,cpu_us:30,self_cpu_us:20,max_cpu_us:20,wall_us:50,self_wall_us:30,max_wall_us:30});
 Object.assign(rows[3],{calls:2,cpu_us:10,self_cpu_us:10,max_cpu_us:5,wall_us:20,self_wall_us:20,max_wall_us:10});
 return {state:3,error:0,function_error:0,function_clock_hz:1000000,function_case:0,functions:rows,
  results:[{packets:2,samples:1920,task_us:120,wall_us:180}]};
}
test('function shares use disjoint self time and calls per second of source audio',()=>{
 const r=analyzeFunctions(sample());assert.equal(r.rows[0].calls_per_audio_second,50);
 assert.equal(r.rows[2].self_cpu_percent,20);assert.equal(r.rows[2].inclusive_cpu_percent,30);
 assert.equal(r.rows.reduce((n,x)=>n+x.self_cpu_percent,0),100);
 for(const change of [s=>s.function_error=1,s=>s.state=2,s=>s.functions[2].self_cpu_us++,
  s=>s.functions[0].calls++,s=>s.functions[3].max_cpu_us=100,s=>s.results[0].task_us=10]){
  const s=sample();change(s);assert.throws(()=>analyzeFunctions(s));
 }
});
test('nested CPU and wall scopes, preemption, wrap, overflow and OOM remain coherent',()=>{
 const out=path.join(root,'.build/opus-function-profile-test');fs.mkdirSync(out,{recursive:true});
 const binary=path.join(out,'test');
 execute('gcc',['-std=c99','-O2','-Wall','-Wextra','-Werror','-DYORADIO_OPUS_FUNCTION_PROFILE=1',
  '-I'+hostPath(component),hostPath(path.join(root,'tests/native/esp8266_opus_function_profile_test.c')),
  hostPath(path.join(component,'opus_function_profile.c')),'-o',hostPath(binary)]);
 execute(hostPath(binary),[]);
});
test('profiling remains diagnostic-only and outside upstream ASM sources',()=>{
 const cm=fs.readFileSync(path.join(component,'CMakeLists.txt'),'utf8');
 assert.match(cm,/option\(YORADIO_OPUS_FUNCTION_PROFILE[^\n]+OFF\)/);
 assert.match(cm,/Function profile requires fixed160 diagnostic raw-only/);
 const adapter=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/cmake/opus_task_clock.c.in'),'utf8');
 assert.match(adapter,/pxCurrentTCB->ulRunTimeCounter \+ \(now - ulTaskSwitchedInTime\)/);
 assert.match(adapter,/taskENTER_CRITICAL/);assert.match(adapter,/taskEXIT_CRITICAL/);
 const bench=fs.readFileSync(path.join(root,'esp8266/rtos-sdk-native/main/opus_benchmark.cpp'),'utf8');
 assert.match(bench,/yoradio_opus_function_clock\(&start, &clock_cpu\)/);
 assert.match(bench,/yoradio_opus_function_clock\(&end, &clock_cpu\)/);
});

const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {parseOutput,main}=require('../tools/esp8266_opus_qemu/run.cjs');
const {summarize,traceFilter}=require('../tools/esp8266_opus_qemu/trace.cjs');
const {hash}=require('../tools/esp8266_opus_asm/export.cjs');
const fixture={name:'test',pcm_sha256:hash(Buffer.from([0,0,1,0])),pcm_bytes:4,samples:2,packet_count:1};
const output='STATE 000019b6 \nBEGIN test\nP 00000100\nEND 00000002 00000001 00001570 00003cf0 \nRECOVERY PASS\nSTACK_USED 00000a14 \nPASS\n';
test('PCM, bounded peaks and explicit OOM recovery are required',()=>{
 const r=parseOutput(output,[fixture]);assert.equal(r.state_bytes,6582);assert.equal(r.oom_recovery_cases,1);assert.equal(r.cases[0].word_peak,15600);
});
for(const [name,change] of Object.entries({
 'wrong PCM':s=>s.replace('P 00000100','P 00000200'),
 'invalid hex':s=>s.replace('P 00000100','P 0000zz00'),
 'missing final PASS':s=>s.replace(/\nPASS\n$/,'\n'),
 'missing recovery':s=>s.replace('RECOVERY PASS\n',''),
 'incorrect sample count':s=>s.replace('END 00000002','END 00000003'),
 'unbounded arena':s=>s.replace('00001570','00010000'),
 'stack overflow':s=>s.replace('00000a14','00002000'),
 'unexpected trap':s=>s.replace('PASS\n','TRAP\n'),
 'duplicate fixture':s=>s.replace('STACK_USED',s.slice(s.indexOf('BEGIN'),s.indexOf('STACK_USED'))+'STACK_USED'),
}))test('reject '+name,()=>assert.throws(()=>parseOutput(change(output),[fixture])));
const trace='----------------\nIN: decode_pulses\n0x40253329: addi a15, a15, -4\n0x4025332c: l32i a8, a15, 0\nTrace 0: 1234 [00000000/0000000040253329/00018010/ff000200]\nTrace 0: 1234 [00000000/0000000040253329/00018010/ff000200]\n';
test('count repeated executed blocks, not just translated instructions',()=>{const r=summarize(trace);assert.equal(r.totals.pvq.instructions,4);assert.equal(r.totals.pvq.load_instructions,2);});
test('trace scope rejects different ELF layouts and uses exact function bounds',()=>{
 const variant='esp8266-opus-ebands-final-candidate-v2';
 const proof={actual_functions:{decode_pulses:{address:0x402531c0,bytes:985}}};
 assert.equal(traceFilter(proof,variant),'0x402531c0+985,0x40251024+94');
 assert.throws(()=>traceFilter(proof,'other-layout'));
 proof.actual_functions.decode_pulses.bytes=986;assert.throws(()=>traceFilter(proof,variant));
 proof.actual_functions.decode_pulses.bytes=985;proof.actual_functions.decode_pulses.address++;
 assert.throws(()=>traceFilter(proof,variant));
});
test('reject missing disassembly and unfinished translations',()=>{
 assert.throws(()=>summarize('Trace 0: 1234 [00000000/0000000040253329/00018010/ff000200]\n'));
 assert.throws(()=>summarize(trace+'0x40253330: ret.n\n'));
});
test('runner rejects unrelated modes and path traversal before spawning',async()=>{
 await assert.rejects(main(['--ota']));await assert.rejects(main(['--variant','../main']));await assert.rejects(main(['--qemu']));
});
test('runner is offline and retains original ELF proof/hash gates',()=>{
 const s=fs.readFileSync(path.join(__dirname,'../tools/esp8266_opus_qemu/run.cjs'),'utf8');
 assert.match(s,/'-nic','none'/);assert.match(s,/'-serial','none'/);assert.match(s,/proof\.candidate_elf_sha256/);
 assert.match(s,/source=patchElf\(parent,proof\.patches\)/);assert.match(s,/trace-pvq/);
 assert.doesNotMatch(s,/check_prefill_board|esptool|read-serial|run_station_series/);
});

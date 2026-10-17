/* Exercise the actual exported page script with controlled HTTP acknowledgements. */
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const page = process.argv[2];
if (!page) throw new Error('Pass the actual generated photo.html path');
const html = readFileSync(page, 'utf8');
const code = [...html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi)].map(m=>m[1]).join('\n');
const checks = [];
const successTimers = [];
const bytes = n=>Uint8Array.from({length:n}, (_,i)=>(i*73+(i>>8)*19)&255);

function pageScope(fetcher, timers=[]) {
    /* Register, but never run, DOM initialization; execute the real transfer functions. */
    const scope = vm.createContext({Blob, FormData, Uint8Array,
        document:{addEventListener(){}, querySelector(){return null;}},
        console:{log(){},warn(){},error(){}}, fetch:fetcher,
        setTimeout(callback, milliseconds){timers.push(milliseconds);queueMicrotask(callback);return 0;}});
    new vm.Script(code+'\nthis.upload=uploadImageInChunks;this.download=downloadImageInChunks;').runInContext(scope);
    return scope;
}

async function check(name, run) {
    /* Preserve every failed assertion, allowing the before-change run to explain its failure. */
    try {await run();checks.push({case:name,passed:true});}
    catch(error) {checks.push({case:name,passed:false,error:error.message});}
}

async function until(predicate) {
    /* Let real Blob promises settle while an HTTP response is deliberately held. */
    for(let attempt=0;attempt<30;attempt++) {
        if(predicate()) return;
        await new Promise(setImmediate);
    }
    throw new Error('The expected acknowledgement boundary was not reached');
}

for(const size of [4096,8192+37,25*4096]) {
    await check('ordered-upload-no-success-sleep-'+size,async()=>{
        const source=bytes(size),received=[],calls=[],timers=[];
        const total=Math.ceil(size/4096);
        const scope=pageScope(async(path,options)=>{
            calls.push(path);
            if(path==='/start_upload') {
                assert.deepEqual(JSON.parse(options.body),{file_number:5,file_size:size,total_chunks:total});
            } else if(path==='/upload_chunk') {
                const form=options.body;
                assert.equal(form.get('file_number'),'5');
                assert.equal(form.get('total_chunks'),String(total));
                assert.equal(form.get('chunk_index'),String(received.length));
                received.push(new Uint8Array(await form.get('chunk').arrayBuffer()));
            } else {
                assert.equal(path,'/finish_upload');
                assert.equal(received.length,total);
                assert.deepEqual(JSON.parse(options.body),{file_number:5,file_name:'file5.jpg'});
            }
            return {ok:true};
        },timers);
        await scope.upload(new Blob([source]),5);
        assert.equal(calls[0],'/start_upload');
        assert.equal(calls.at(-1),'/finish_upload');
        assert.equal(calls.length,total+2);
        assert.deepEqual(Buffer.concat(received.map(r=>Buffer.from(r))),Buffer.from(source));
        successTimers.push({bytes:size,chunks:total,requested_delays_ms:[...timers]});
        assert.deepEqual(timers,[],'Successful acknowledgements must not add software sleeps');
    });
}

await check('next-chunk-and-finish-wait-for-ack',async()=>{
    const pending=[],calls=[];
    const scope=pageScope(async(path,options)=>{
        calls.push(path);
        if(path==='/upload_chunk') {
            const index=Number(options.body.get('chunk_index'));
            assert.equal(index,pending.length);
            return await new Promise(resolve=>pending.push(resolve));
        }
        if(path==='/finish_upload') assert.equal(pending.length,3);
        return {ok:true};
    });
    const task=scope.upload(new Blob([bytes(8192+37)]),5);
    for(let index=0;index<3;index++) {
        await until(()=>pending.length===index+1);
        assert.equal(calls.length,index+2,'Another request escaped before the current ACK');
        assert(!calls.includes('/finish_upload'));
        pending[index]({ok:true});
    }
    await task;
    assert.equal(calls.at(-1),'/finish_upload');
});

for(const failure of ['http','network']) {
    await check(failure+'-retry-keeps-identical-chunk',async()=>{
        const timers=[],chunks=[];
        let attempts=0,finished=false;
        const scope=pageScope(async(path,options)=>{
            if(path==='/upload_chunk') {
                chunks.push(Buffer.from(await options.body.get('chunk').arrayBuffer()));
                if(attempts++<2) {
                    if(failure==='network') throw new Error('Synthetic lost reply');
                    return {ok:false,status:503};
                }
            }
            if(path==='/finish_upload') finished=true;
            return {ok:true};
        },timers);
        await scope.upload(new Blob([bytes(97)]),5);
        assert.equal(attempts,3);assert(finished);
        assert(chunks.every(chunk=>chunk.equals(Buffer.from(bytes(97)))));
        assert.deepEqual(timers,[500,1000],'Keep retry backoff, without a successful-chunk sleep');
    });
}

await check('five-failures-remain-bounded-and-do-not-finish',async()=>{
    let attempts=0,finished=false;
    const timers=[];
    const scope=pageScope(async(path)=>{
        if(path==='/upload_chunk') {attempts++;return{ok:false,status:503};}
        if(path==='/finish_upload') finished=true;
        return {ok:true};
    },timers);
    await assert.rejects(scope.upload(new Blob([bytes(97)]),5),/failed after retries: HTTP 503/);
    assert.equal(attempts,5);assert(!finished);
    assert.deepEqual(timers,[500,1000,1500,2000],'Do not sleep after the final failed attempt');
});

await check('start-failure-does-not-write-any-chunk',async()=>{
    const calls=[],timers=[];
    const scope=pageScope(async(path)=>{calls.push(path);return{ok:false,status:400};},timers);
    await assert.rejects(scope.upload(new Blob([bytes(97)]),5),/Failed to start upload session/);
    assert.deepEqual(calls,['/start_upload']);assert.deepEqual(timers,[]);
});

await check('finish-failure-is-not-reported-as-success',async()=>{
    const calls=[];
    const scope=pageScope(async(path)=>{calls.push(path);return{ok:path!=='/finish_upload'};});
    await assert.rejects(scope.upload(new Blob([bytes(97)]),5),/Finish upload command failed/);
    assert.deepEqual(calls,['/start_upload','/upload_chunk','/finish_upload']);
});

await check('preview-download-keeps-exact-bytes-and-order',async()=>{
    const source=bytes(20497),calls=[],timers=[];
    const scope=pageScope(async(path)=>{
        const query=new URL(path,'http://127.0.0.1').searchParams;
        assert.equal(query.get('file'),'4');assert.equal(query.get('size'),'10240');
        const index=Number(query.get('chunk'));assert.equal(index,calls.length);calls.push(path);
        return{ok:true,arrayBuffer:async()=>source.slice(index*10240,(index+1)*10240).buffer};
    },timers);
    assert.deepEqual(Buffer.from(await scope.download(4,source.length)),Buffer.from(source));
    assert.equal(calls.length,3);assert.deepEqual(timers,[10]);
});

await check('preview-http-error-stops-the-download',async()=>{
    let calls=0;
    const scope=pageScope(async()=>{calls++;return{ok:false,status:404};});
    await assert.rejects(scope.download(4,20497),/Download chunk 0 failed/);
    assert.equal(calls,1);
});

const report={passed:checks.every(r=>r.passed),checks,successful_transfer_timers:successTimers,
    page_sha256:crypto.createHash('sha256').update(html).digest('hex'),
    scope:'Actual generated page JavaScript, controlled acknowledgements, exact multipart bytes and bounded retry behavior; no real browser or guest flash claim.'};
console.log(JSON.stringify(report));
process.exitCode=report.passed?0:1;

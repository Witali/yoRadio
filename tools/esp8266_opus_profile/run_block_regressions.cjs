const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {buildHost,runProbe,execute,hostPath,root,component}=require('./build_host.cjs');
const {prepareReference,defaultOutput}=require('./prepare_generic32_reference.cjs');
const {fixtureDirectory,sha256,inspectPackets}=require('./fixtures.cjs');
const {framed}=require('./generate_phase_fixtures.cjs');
const {comparePcm}=require('./run_regressions.cjs');
function packets(data) {let p=0,r=[];while(p<data.length){assert.ok(p+2<=data.length);let n=data.readUInt16LE(p);p+=2;
  assert.ok(n&&p+n<=data.length);r.push(data.subarray(p,p+n));p+=n;}return r;}
function sizeCode(n){assert.ok(n<=1275);return n<252?[n]:[252+(n&3),(n-252-(n&3))/4];}
function pack(frames,vbr=false,padding=0) {
  assert.ok(frames.length&&frames.length<=48);
  const toc=frames[0][0];assert.equal(toc&3,0);assert.ok(frames.every(f=>f[0]===toc));
  const data=frames.map(f=>f.subarray(1));assert.ok(vbr||data.every(f=>f.length===data[0].length));
  assert.ok(padding>=0&&padding<255);
  if(frames.length===2&&!padding)return Buffer.concat([Buffer.from([(toc&252)|(vbr?2:1)]),
    ...(vbr?[Buffer.from(sizeCode(data[0].length))]:[]),...data]);
  return Buffer.concat([Buffer.from([(toc&252)|3,frames.length|(vbr?128:0)|(padding?64:0)]),
    ...(padding?[Buffer.from([padding])]:[]),...(vbr?data.slice(0,-1).map(f=>Buffer.from(sizeCode(f.length))):[]),
    ...data,Buffer.alloc(padding)]);
}
function grouped(data,count,vbr=false,padding=0) {
  const source=packets(data),result=[];
  // Preserve mode changes and the final short group; unlike modes cannot be
  // combined. Never silently discard packets to make the regression pass.
  for(let i=0;i<source.length;) {
    let end=i+1;while(end<source.length&&end-i<count&&source[end][0]===source[i][0])end++;
    const group=source.slice(i,end);
    const variable=vbr||group.some(f=>f.length!==group[0].length);
    result.push(group.length===1?group[0]:pack(group,variable,padding));i=end;
  }
  return framed(result);
}
async function run({output=path.join(__dirname,'block-results.json'),capture}={}) {
  prepareReference();await buildHost({upstreamRoot:defaultOutput,fastInt64:0});
  const build=await buildHost({bounded:true,fastInt64:0,firFlashWord:true});
  const out=path.join(root,'.build/opus-block-regression');fs.mkdirSync(out,{recursive:true});
  const object=path.join(out,'block_probe.o'),binary=path.join(out,'block_probe');
  execute('gcc',[...build.flags,'-Wall','-Wextra','-Werror','-c',hostPath(path.join(__dirname,'block_probe.c')),'-o',hostPath(object)]);
  execute('gcc',[...build.objects.filter(f=>!f.endsWith('probe.c.o')).map(hostPath),hostPath(object),
    '-Wl,--gc-sections','-Wl,--wrap=malloc','-Wl,--wrap=calloc','-Wl,--wrap=realloc','-lm','-o',hostPath(binary)]);
  const inputs=[];
  const elementary=file=>{
    const output=path.join(out,path.basename(file)+'.unpacked');
    execute(hostPath(binary),['--unpack',hostPath(file),hostPath(output)]);
    return fs.readFileSync(output);
  };
  for(const [name,count] of [['mono-12',2],['mono-12',6],['mono-24',3],['mono-24',6],['stereo-64',3],['stereo-64',6],['stereo-128',3]]) {
    const data=elementary(path.join(fixtureDirectory,name+'.opuspkt'));
    inputs.push({name:name+'-packed'+count*20,data:grouped(data,count)});
  }
  for(const [name,count,vbr,pad] of [['stereo-10ms-vbr',2,true,0],['stereo-10ms-vbr',6,true,17],['stereo-2_5ms',48,false,0]]) {
    const data=elementary(path.join(fixtureDirectory,'phase',name+'.opuspkt'));
    // Repeat the short corpus for the48-frame packet; it remains our own audio.
    inputs.push({name:name+'-packed'+count+'-pad'+pad,data:grouped(Buffer.concat([data,data]),count,vbr,pad)});
  }
  inputs.push({name:'mixed-long-silk-hybrid-celt',data:Buffer.concat(inputs.slice(0,7).map(i=>i.data))});
  if(capture)inputs.push({name:'private-live-capture',data:fs.readFileSync(capture)});
  const cases=[];
  for(const test of inputs) {
    const input=path.join(out,test.name+'.opuspkt'),reference=path.join(out,test.name+'.reference.pcm'),actual=path.join(out,test.name+'.block.pcm');
    fs.writeFileSync(input,test.data);
    const before=inspectPackets(test.data);
    const expected=runProbe({upstreamRoot:defaultOutput,fastInt64:0,fixture:input,output:reference,selfTest:false});
    const result=JSON.parse(execute(hostPath(binary),[hostPath(input),hostPath(actual)]));
    assert.equal(result.samples,expected.samples);assert.equal(result.packets,before.packets);
    assert.equal(result.allocations,0);assert.equal(result.pcm_bytes,1920);assert.ok(result.largest_block<=960);
    assert.ok(result.scratch_bytes<=6144&&result.scratch_words<=16384);
    const pcm=comparePcm(fs.readFileSync(reference),fs.readFileSync(actual));assert.equal(pcm.exact,true,test.name);
    cases.push({name:test.name,input_sha256:sha256(test.data),...before,result,pcm});
    process.stderr.write(`${test.name}: exact; ${result.blocks} blocks, scratch ${result.scratch_bytes}/${result.scratch_words}\n`);
  }
  const sources=['native_opus.c','native_opus.h','opus_memory.c','opus_memory.h','upstream/src/opus_decoder.c'];
  const report={passed:true,scope:'Host generic32 pristine full-packet PCM versus FIR-enabled bounded frame callbacks; mono48k. No board speed claim.',
    source_sha256_lf:Object.fromEntries(sources.map(f=>[f,sha256(Buffer.from(fs.readFileSync(path.join(component,f),'utf8').replace(/\r\n/g,'\n')))])),cases};
  fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');return report;
}
module.exports={pack,packets,grouped,run};
if(require.main===module){const args=process.argv.slice(2),value=k=>{const i=args.indexOf(k);return i<0?undefined:args[i+1];};
  run({output:value('--output'),capture:value('--capture')}).then(r=>console.log('PASS '+r.cases.length+' block cases')).catch(e=>{console.error(e.stack);process.exitCode=1;});}

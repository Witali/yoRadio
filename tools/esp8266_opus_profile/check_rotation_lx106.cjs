const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {root,component,execute,hostPath}=require('./build_host.cjs');
const {defaultCompiler}=require('./check_xtensa_word_access.cjs');
const {defaultObjdump}=require('./check_xtensa_iram.cjs');
const {sha256}=require('./fixtures.cjs');
const source=path.join(component,'opus_rotation_lx106.S');

// Instruction semantics model of the actual source, not a speed emulator.
// Target execution / golden PCM still requires a physical-board run.
function model(text,vector) {
  const instructions=[],labels=new Map();
  for(const line of text.replace(/\/\*[\s\S]*?\*\//g,'').split(/\r?\n/).map(s=>s.trim()).filter(Boolean)) {
    if(line.endsWith(':')){labels.set(line.slice(0,-1),instructions.length);continue;}
    if(line.startsWith('.')||line.startsWith('#'))continue;
    const [op,...rest]=line.split(/\s+/);instructions.push([op,rest.join('').split(',')]);
  }
  const r=new Int32Array(16),initial=new Int32Array(16),memory=Buffer.alloc(65536),base=4096,stack=32768;
  for(let i=0;i<16;i++)r[i]=(0x123456+i*713)|0;
  r[1]=stack;r[2]=base+8;r[3]=vector.n;r[4]=vector.stride;r[5]=vector.c;r[6]=vector.s;initial.set(r);
  for(let i=0;i<vector.n+8;i++)memory.writeUInt16LE(0x5aa5,base+i*2);
  vector.samples.forEach((v,i)=>memory.writeInt16LE(v,base+8+i*2));
  const reg=a=>{assert.match(a,/^a(?:[0-9]|1[0-5])$/);return Number(a.slice(1));};
  const val=a=>a.startsWith('a')?r[reg(a)]:Number(a);
  const address=(a,b,width)=>{const p=(val(a)+Number(b))>>>0;
    assert.ok(p%width===0&&((p>=base&&p+width<=base+2*(vector.n+8))||(p>=stack-16&&p+width<=stack)),'out-of-range/alignment '+p);return p;};
  let pc=0,steps=0;
  while(pc<instructions.length){assert.ok(++steps<100000);const [op,a]=instructions[pc++];
    const set=v=>{r[reg(a[0])]=v;};
    switch(op){
      case 'bge':if(val(a[0])>=val(a[1]))pc=labels.get(a[2]);break;
      case 'blti':if(val(a[0])<val(a[1]))pc=labels.get(a[2]);break;
      case 'bnez':if(val(a[0])!==0)pc=labels.get(a[1]);break;
      case 'add':case 'addi':case 'addmi':set(val(a[1])+val(a[2]));break;
      case 'sub':set(val(a[1])-val(a[2]));break;
      case 'neg':set(-val(a[1]));break;
      case 'slli':set(val(a[1])<<val(a[2]));break;
      case 'srai':set(val(a[1])>>val(a[2]));break;
      case 'mul16s':set(Math.imul((val(a[1])<<16)>>16,(val(a[2])<<16)>>16));break;
      case 'l16ui':set(memory.readUInt16LE(address(a[1],a[2],2)));break;
      case 's16i':memory.writeUInt16LE(val(a[0])&65535,address(a[1],a[2],2));break;
      case 'l32i':set(memory.readInt32LE(address(a[1],a[2],4)));break;
      case 's32i':memory.writeInt32LE(val(a[0]),address(a[1],a[2],4));break;
      case 'ret':pc=instructions.length;break;
      default:throw Error('Unmodelled opcode '+op);
    }
    assert.ok(Number.isInteger(pc));
  }
  for(const i of [0,1,12,13,14,15])assert.equal(r[i],initial[i],'ABI register a'+i);
  return memory.subarray(base,base+2*(vector.n+8));
}
function run(output=path.join(__dirname,'rotation-lx106-results.json')) {
  const out=path.join(root,'.build/opus-rotation-unit');fs.mkdirSync(out,{recursive:true});
  let seed=0x7349;const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed;};
  const vectors=[];
  for(const n of [1,2,3,4,5,8,15,16,31,32,60,120,240,480,960])
    for(const stride of [...new Set([1,2,3,Math.floor(n/2),n])].filter(s=>s>0&&s<=n))
      for(const [c,s] of [[32767,0],[0,32767],[23170,23170],[-32768,-32768],[32767,-32768],[32767,32767],[-1,1],[(random()<<16)>>16,(random()<<16)>>16]])
        vectors.push({n,stride,c,s,samples:Array.from({length:n},(_,i)=>i%7===0?-32768:i%7===1?32767:(random()<<16)>>16)});
  const input=path.join(out,'vectors.bin'),reference=path.join(out,'reference.bin');
  fs.writeFileSync(input,Buffer.concat(vectors.map(v=>{const b=Buffer.alloc(16+v.n*2);[v.n,v.stride,v.c,v.s].forEach((x,i)=>b.writeInt32LE(x,i*4));v.samples.forEach((x,i)=>b.writeInt16LE(x,16+i*2));return b;})));
  const includes=['','upstream/include','upstream/celt','upstream/silk'].map(p=>'-I'+hostPath(path.join(component,p)));
  const binary=path.join(out,'reference');
  execute('gcc',['-O3','-std=c99','-fwrapv','-ffunction-sections','-fdata-sections','-fno-pie','-no-pie','-fsanitize=address,undefined','-fno-sanitize-recover=all',
    '-DYORADIO_OPUS_BOUNDED=1','-DYORADIO_OPUS_ROTATION_LX106=1',...includes,hostPath(path.join(__dirname,'rotation_reference.c')),'-Wl,--gc-sections','-lm','-o',hostPath(binary)]);
  execute('env',['ASAN_OPTIONS=detect_leaks=0',hostPath(binary),hostPath(input),hostPath(reference)]);
  const actual=Buffer.concat(vectors.map(v=>model(fs.readFileSync(source,'utf8'),v)));
  assert.deepEqual(actual,fs.readFileSync(reference),'Assembly instruction model differs from original C');
  const cmd=(program,args)=>{const r=spawnSync(program,args,{encoding:'utf8',maxBuffer:4e6});assert.equal(r.status,0,r.stderr);return r.stdout;};
  const sdk=path.join(root,'.worktree/esp8266-native-port/.build/esp8266-rtos-sdk/components/esp8266/include');
  const object=path.join(out,'rotation.o');cmd(defaultCompiler,['-DYORADIO_OPUS_ROTATION_LX106=1','-I'+component,'-I'+sdk,'-c',source,'-o',object]);
  const asm=cmd(defaultObjdump,['-dr',object]);
  assert.equal((asm.match(/\smul16s\s/g)||[]).length,8);assert.doesNotMatch(asm,/\s(?:mull|call\w*|rsil|memw)\s/);
  const report={passed:true,source_sha256_lf:sha256(Buffer.from(fs.readFileSync(source,'utf8').replace(/\r\n/g,'\n'))),
    cases:vectors.length,samples:vectors.reduce((n,v)=>n+v.n,0),c_fallback_asan_ubsan:true,instruction_model_exact:true,callee_saved_registers_checked:true,
    target_assembled:true,mul16s_sites:8,stack_bytes:16,scope:'C fallback execution plus a local instruction-semantics model, not physical assembly execution or speed. Physical golden PCM / A/B remains required.'};
  fs.writeFileSync(path.join(out,'rotation.asm'),asm);fs.writeFileSync(output,JSON.stringify(report,null,2)+'\n');console.log(report);return report;
}
module.exports={run,model};if(require.main===module)run();

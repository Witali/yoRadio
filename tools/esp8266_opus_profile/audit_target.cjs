// Static target-code inventory, NOT a runtime/hotness profile. Read-only on the
// firmware/build; the optional output is the audit report, not a rebuilt image.
const fs = require('node:fs'), path = require('node:path');
const {spawnSync} = require('node:child_process');
const {defaultObjdump} = require('./check_xtensa_iram.cjs');
const {root} = require('./build_host.cjs');
const files = ['celt/entdec', 'celt/rate', 'celt/bands', 'celt/vq', 'celt/cwrs',
  'celt/quant_bands', 'celt/celt', 'celt/celt_decoder', 'celt/mdct', 'celt/kiss_fft',
  'silk/decode_frame', 'silk/decode_core', 'silk/decode_indices', 'silk/decode_pulses',
  'silk/decode_parameters', 'silk/NLSF_decode', 'silk/NLSF_stabilize', 'silk/dec_API',
  'silk/resampler_private_up2_HQ', 'silk/resampler_private_IIR_FIR', 'src/opus_decoder'];
function parseDisassembly(text) {
  const functions = [];
  let current;
  for (const line of text.split(/\r?\n/)) {
    const symbol = line.match(/^\s*[0-9a-f]+ <([^>]+)>:$/);
    if (symbol) {
      current = symbol[1].startsWith('.') ? null : {name:symbol[1], instructions:0,
        narrow_load_sites:0, memw_sites:0, software_division_sites:0,
        software_multiply64_sites:0, calls:{}};
      if (current) functions.push(current);
    }
    if (!current) continue;
    const instruction = line.match(/^\s*[0-9a-f]+:\s+[0-9a-f]+\s+([a-z][\w.]*)\b/);
    if (instruction) {
      ++current.instructions;
      if (/^l(?:8ui|16ui|16si)$/.test(instruction[1])) ++current.narrow_load_sites;
      if (instruction[1] === 'memw') ++current.memw_sites;
    }
    // ASM_EXPAND is the call relocation here; SLOT0_OP describes the same call
    // again on this toolchain and must not be counted twice.
    const call = line.match(/R_XTENSA_ASM_EXPAND\s+([\w.$]+)/);
    if (call) {
      current.calls[call[1]] = (current.calls[call[1]] || 0) + 1;
      if (/^__(?:u?div|u?mod)(?:si|di)3$/.test(call[1])) ++current.software_division_sites;
      if (call[1] === '__muldi3') ++current.software_multiply64_sites;
    }
  }
  return functions;
}
function parseSymbols(text) {
  const symbols = new Map();
  for (const line of text.split(/\r?\n/)) {
    const m = line.match(/^([0-9a-f]+)\s+\w\s+[FO]\s+(\S+)\s+([0-9a-f]+)\s+(.+)$/);
    if (m) symbols.set(m[4].trim(), {address:'0x'+m[1], section:m[2], bytes:parseInt(m[3],16)});
  }
  return symbols;
}
function audit(build, objdump = defaultObjdump) {
  function dump(args) {
    const result = spawnSync(objdump,args,{encoding:'utf8',maxBuffer:16*1024*1024});
    if (result.error) throw result.error;
    if (result.status !== 0) throw Error(result.stderr || 'objdump failed');
    return result.stdout;
  }
  const elf = path.join(build,'yoradio_esp8266_helix_native.elf');
  const symbols = parseSymbols(dump(['-t',elf]));
  const objects = files.map(file => {
    const object = path.join(build,'esp-idf/opus_decoder/CMakeFiles/__idf_opus_decoder.dir/upstream',file+'.c.obj');
    return {file,functions:parseDisassembly(dump(['-dr',object])).map(fn =>
      ({...fn, linked_symbol:symbols.get(fn.name) || null}))};
  });
  return {date:new Date().toISOString(),build:path.relative(root,build).replace(/\\/g,'/'),
    kind:'static instruction/call sites, not execution counts, CPU time or proof of invalid access',
    notes:['Narrow loads can be correct DRAM/stack accesses; trace the source pointer before changing them.',
      'Object inventory includes encoder/PLC paths; linked_symbol does not prove normal decode executes a function.',
      'Instruction counts omit literals and are not flash byte size or runtime cost.'],
    resampler_table:symbols.get('silk_resampler_frac_FIR_12'),objects};
}
module.exports = {parseDisassembly,parseSymbols,audit};
if (require.main === module) {
  const args = process.argv.slice(2), opt = (key,d) => args.includes(key) ? args[args.indexOf(key)+1] : d;
  const result = audit(path.resolve(opt('--build','.build/esp8266-opus-flash-output512')));
  const output = opt('--output');
  if (output) fs.writeFileSync(output,JSON.stringify(result,null,2)+'\n');
  else console.log(JSON.stringify(result,null,2));
}

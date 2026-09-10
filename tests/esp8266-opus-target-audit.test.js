const {test} = require('node:test');
const assert = require('node:assert/strict');
const {parseDisassembly,parseSymbols} = require('../tools/esp8266_opus_profile/audit_target.cjs');
test('static audit skips literals and does not count paired call relocations twice', () => {
  const result = parseDisassembly(`00000000 <.literal.fn>:
   0: 000000 l8ui a2, a3, 0
00000000 <fn>:
   0: 000032 l8ui a3, a2, 0
   3: 001242 l16si a4, a2, 0
   6: 002252 l16ui a5, a2, 4
   9: 0020c0 memw
   c: 000005 call0 0
      c: R_XTENSA_ASM_EXPAND __udivsi3
      c: R_XTENSA_SLOT0_OP __udivsi3
  10: 000005 call0 0
      10: R_XTENSA_ASM_EXPAND __muldi3
00000000 <next>:
   0: f00d ret.n
`);
  assert.equal(result.length,2);
  assert.equal(result[0].instructions,6);
  assert.equal(result[0].narrow_load_sites,3);
  assert.equal(result[0].memw_sites,1);
  assert.equal(result[0].software_division_sites,1);
  assert.equal(result[0].software_multiply64_sites,1);
  assert.equal(result[0].calls.__udivsi3,1);
  assert.equal(result[1].software_division_sites,0);
});
test('static audit preserves linked locations and hexadecimal sizes', () => {
  const s = parseSymbols('402d8424 g     O .flash.rodata\t00000060 silk_resampler_frac_FIR_12\r\n402468e0 g     F .flash.text\t0000003f ec_decode\r\n');
  assert.equal(s.get('silk_resampler_frac_FIR_12').bytes,96);
  assert.equal(s.get('ec_decode').bytes,63);
  assert.equal(s.get('ec_decode').section,'.flash.text');
});

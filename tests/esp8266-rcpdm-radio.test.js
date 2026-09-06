const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {build,execute} = require('../tools/esp8266_audio_profile/run_rcpdm_radio');

test('desktop fixed/state-aware/entry-only RCPDM runs preserve every bit and RC state', t => {
  const temporary = fs.mkdtempSync(path.join(os.tmpdir(),'rcpdm-real-radio-test-'));
  t.after(()=>fs.rmSync(temporary,{recursive:true,force:true}));
  const exe = build(temporary);
  const result = JSON.parse(execute(exe,['--self-test']).stdout);
  assert.equal(result.pass,true);
  assert.equal(result.variants,14);
  assert.equal(result.wordStateComparisons,8305024);
  assert.equal(result.bulkWordsPerVariant,8193);
  // Public CI test uses generated synthetic PCM, never copyrighted broadcasts.
  const pcm = Buffer.alloc(1024*4);
  for (let i=0;i<1024;++i) { pcm.writeInt16LE((i*997)%65536-32768,i*4); pcm.writeInt16LE(32767-(i*719)%65536,i*4+2); }
  const file = path.join(temporary,'stereo.s16le'); fs.writeFileSync(file,pcm);
  for (const rate of [22050,44100,48000]) {
    const out = JSON.parse(execute(exe,[file,String(rate),'2','128','3',path.join(temporary,'output'),'--save']).stdout);
    assert.equal(out.samples,Math.floor(1024*48000/rate));
    assert.equal(out.bitMismatches,0); assert.equal(out.stateMismatches,0);
    assert.deepEqual(fs.readFileSync(path.join(temporary,'output.original.rcpdm32le')),fs.readFileSync(path.join(temporary,'output.state4.rcpdm32le')));
    for (const variant of out.variants) {
      assert.ok(variant.coveredBitsPercent >= 0 && variant.coveredBitsPercent <= 100);
      assert.ok(variant.highGroups <= variant.groups);
      assert.equal(variant.roundUs.length,3);
    }
  }
});

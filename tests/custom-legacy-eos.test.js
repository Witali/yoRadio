const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const assert = require('node:assert/strict');

const source = fs.readFileSync(path.join(
  __dirname, '..', 'idf', 'components', 'custom_legacy_codecs',
  'custom_legacy_adapter.cpp'), 'utf8');

test('custom AAC waits for a complete ADTS header', () => {
  const headerWait = source.indexOf('if (decoder->input_size < 7) return 1;');
  const frameParse = source.indexOf(
    'size_t frame_size = adts_frame_size(decoder->input, decoder->input_size);');

  assert.notEqual(headerWait, -1);
  assert.notEqual(frameParse, -1);
  assert.ok(headerWait < frameParse,
            'an incomplete ADTS header must not be reported as invalid');
});

test('custom codec adapters discard only an incomplete final frame at EOS', () => {
  assert.match(source,
    /if \(result == 1\) \{\s*if \(!eos\) return 1;\s*consume_input\(decoder, decoder->input_size, stats\);\s*return 0;\s*\}/);
  assert.doesNotMatch(source, /\(void\)eos/);

  const invalidFrame = source.indexOf(
    'if (!frame_size || frame_size > kMaximumInputCapacity) return -11;');
  assert.notEqual(invalidFrame, -1,
    'complete malformed ADTS headers must remain decoder errors');
});

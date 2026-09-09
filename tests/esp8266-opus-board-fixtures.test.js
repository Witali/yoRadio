const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { fixtureDirectory, cases, sha256 } = require('../tools/esp8266_opus_profile/fixtures.cjs');
const { defaultProbe, fnv1a32, selectPackets, packPackets, renderHeader, goldenCaseIndex, validateReference, buildBoardFixtures } =
  require('../tools/esp8266_opus_profile/build_board_fixtures.cjs');

test('board PCM FNV-1a32 hashes little-endian bytes with unsigned wrap', () => {
  assert.equal(fnv1a32(Buffer.alloc(0)), 0x811c9dc5);
  assert.equal(fnv1a32(Buffer.from('hello')), 0x4f9f2cab);
  const pcm = Buffer.from([0, 0, 0xff, 0xff, 0, 0x80, 0xff, 0x7f]);
  let reference = 2166136261n;
  for (const byte of pcm) reference = ((reference ^ BigInt(byte)) * 16777619n) & 0xffffffffn;
  assert.equal(fnv1a32(pcm), Number(reference));
});

test('board reference rejects host-default arithmetic and bounded decoder', () => {
  assert.throws(() => validateReference({ flags: ['-O2'] }), /OPUS_FAST_INT64=0/);
  assert.throws(() => validateReference({ flags: ['-DOPUS_FAST_INT64=1'] }), /OPUS_FAST_INT64=0/);
  assert.throws(() => validateReference({ flags: ['-DOPUS_FAST_INT64=0', '-DYORADIO_OPUS_BOUNDED=1'] }), /unbounded/);
  assert.throws(() => validateReference({ flags: ['-DOPUS_FAST_INT64=0', '-DOPUS_FAST_INT64=1'] }), /Conflicting/);
  assert.doesNotThrow(() => validateReference({ flags: ['-O2', '-DOPUS_FAST_INT64=0'] }));
});

test('board packet prefix rejects truncated, empty, oversized and bad-duration input', () => {
  for (const data of [Buffer.alloc(0), Buffer.from([1]), Buffer.from([0, 0]),
    Buffer.from([2, 0, 0x78]), Buffer.from([1, 0, 3]), Buffer.from([2, 0, 3, 0])])
    assert.throws(() => selectPackets(data, 1));
  const oversized = Buffer.alloc(1539);
  oversized.writeUInt16LE(1537);
  assert.throws(() => selectPackets(oversized, 1), /oversized/);
  assert.throws(() => selectPackets(Buffer.from([1, 0, 0x78]), 2), /insufficient/);
  assert.throws(() => selectPackets(Buffer.alloc(0), 0), /positive/);
});

test('five board prefixes retain exact raw bytes and zero-pad each packet to a word', () => {
  const selected = cases.map(([name]) => selectPackets(fs.readFileSync(path.join(fixtureDirectory, name + '.opuspkt'))));
  const packets = selected.flatMap(fixture => fixture.packets);
  const { payload, entries } = packPackets(packets);
  assert.equal(packets.length, 60);
  assert.equal(payload.length, 22176);
  assert.equal(payload.length % 4, 0);
  for (let index = 0; index < entries.length; index++) {
    const { offset, length } = entries[index];
    const end = index + 1 < entries.length ? entries[index + 1].offset : payload.length;
    assert.equal(offset % 4, 0);
    assert.equal(length, packets[index].data.length);
    assert.deepEqual(payload.subarray(offset, offset + length), packets[index].data);
    assert.deepEqual(payload.subarray(offset + length, end), Buffer.alloc(end - offset - length));
    assert.equal(packets[index].samples, 960);
  }
  const header = renderHeader(payload, entries, selected.map((fixture, index) => ({
    name: cases[index][0], first_packet: index * 12, packet_count: 12,
    samples: 11520, expected_hash: 0xffffffff, bitrate_kbps: cases[index][1],
  })));
  assert.match(header, /#define OPUS_BENCH_FIXTURE_COUNT 5U/);
  assert.match(header, /uint32_t offset, length/);
  assert.equal((header.match(/__attribute__\(\(aligned\(4\)\)\)/g) || []).length, 4);
  assert.match(header, /#define OPUS_BENCH_GOLDEN_CASE UINT32_MAX/);
  assert.match(header, /#define OPUS_BENCH_GOLDEN_SAMPLES 0U/);
  assert.match(header, /opus_bench_golden_pcm\[\][^{]*\{\s*0x00000000U,\s*\}/);
  assert.doesNotMatch(header, /uint8_t|uint16_t|char\s|\bmalloc\b/);
  const payloadText = header.split('opus_bench_payload[]')[1].split('};')[0];
  const words = [...payloadText.matchAll(/0x([a-f0-9]{8})U/g)].map(match => parseInt(match[1], 16));
  const recovered = Buffer.alloc(payload.length);
  words.forEach((word, index) => recovered.writeUInt32LE(word, index * 4));
  assert.deepEqual(recovered, payload);
});

test('golden fixture selection accepts all canonical names and compact aliases', () => {
  assert.equal(goldenCaseIndex(undefined), -1);
  cases.forEach(([name], index) => {
    assert.equal(goldenCaseIndex(name), index);
    assert.equal(goldenCaseIndex(name.replaceAll('-', '')), index);
  });
  assert.throws(() => goldenCaseIndex('mono-99'), /Unknown golden fixture/);
});

test('existing pristine probe generates deterministic fresh-decoder board hashes without a rebuild', {
  skip: !fs.existsSync(defaultProbe) && 'Build the pristine host probe once to enable this test.',
  timeout: 60000,
}, () => {
  const out = fs.mkdtempSync(path.join(os.tmpdir(), 'yoradio-opus-board-fixtures-'));
  try {
    const probeBefore = sha256(fs.readFileSync(defaultProbe));
    const report = buildBoardFixtures({ output: out });
    const header = fs.readFileSync(path.join(out, 'opus_board_fixtures.h'), 'utf8');
    assert.equal(report.fixture_count, 5);
    assert.equal(report.packet_count, 60);
    assert.equal(report.payload_bytes + report.table_bytes, 22756);
    assert.equal(sha256(header), report.header_sha256);
    assert.deepEqual(report.fixtures.map(fixture => fixture.bitrate_kbps), [12, 24, 64, 128, 510]);
    for (const fixture of report.fixtures) {
      assert.equal(fixture.samples, 11520);
      assert.equal(fixture.pcm_bytes, 23040);
      assert.equal(fixture.packet_count, 12);
      const pcm = fs.readFileSync(path.join(out, fixture.name + '.pcm'));
      assert.equal(fixture.expected_hash, fnv1a32(pcm));
      assert.equal(fixture.pcm_sha256, sha256(pcm));
      // Existing full pristine evidence starts from the same fresh state. Its
      // prefix independently catches accidentally using a warmed-up decoder.
      const fullPcm = path.resolve(__dirname, '../.build/esp8266-opus-regression-int64-0', fixture.name + '.pristine.pcm');
      if (fs.existsSync(fullPcm)) assert.deepEqual(pcm, fs.readFileSync(fullPcm).subarray(0, pcm.length));
    }
    assert.deepEqual(buildBoardFixtures({ output: out }), report);
    assert.equal(report.reference.opus_fast_int64, 0);
    assert.deepEqual(report.fixtures.map(fixture => fixture.expected_hash),
      [0x35905648, 0xbfb8d5fa, 0x8b59452b, 0x5b181a8e, 0xe690bf22]);
    assert.equal(report.golden, null);
    assert.equal(report.golden_storage_bytes, 4);
    const golden = buildBoardFixtures({ output: out, golden: 'mono24' });
    assert.deepEqual(golden.fixtures, report.fixtures);
    assert.equal(golden.payload_sha256, report.payload_sha256);
    assert.equal(golden.golden_storage_bytes, 23040);
    assert.equal(golden.golden.case_index, 1);
    assert.equal(golden.golden.samples, 11520);
    assert.equal(golden.golden.pcm_sha256, report.fixtures[1].pcm_sha256);
    const goldenHeader = fs.readFileSync(path.join(out, 'opus_board_fixtures.h'), 'utf8');
    assert.match(goldenHeader, /#define OPUS_BENCH_GOLDEN_CASE 1U/);
    assert.match(goldenHeader, /#define OPUS_BENCH_GOLDEN_SAMPLES 11520U/);
    const goldenText = goldenHeader.split('opus_bench_golden_pcm[]')[1].split('};')[0];
    const words = [...goldenText.matchAll(/0x([a-f0-9]{8})U/g)].map(match => parseInt(match[1], 16));
    const recovered = Buffer.alloc(words.length * 4);
    words.forEach((word, index) => recovered.writeUInt32LE(word, index * 4));
    assert.deepEqual(recovered, fs.readFileSync(path.join(out, 'mono-24.pcm')));
    assert.equal(fnv1a32(recovered), report.fixtures[1].expected_hash);
    assert.equal(sha256(fs.readFileSync(defaultProbe)), probeBefore);
  } finally { fs.rmSync(out, { recursive: true, force: true }); }
});

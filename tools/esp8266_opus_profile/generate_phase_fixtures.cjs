const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const { root } = require('./build_host.cjs');
const { inspectPackets, sha256 } = require('./fixtures.cjs');

const directory = path.join(root, 'tests/fixtures/opus_native/phase');
function framed(packets) {
  return Buffer.concat(packets.flatMap(packet => {
    const size = Buffer.alloc(2); size.writeUInt16LE(packet.length); return [size, packet];
  }));
}
function oggPackets(data) {
  let position = 0, partial = [];
  const packets = [];
  while (position < data.length) {
    assert.equal(data.toString('ascii', position, position + 4), 'OggS');
    const lacing = data.subarray(position + 27, position + 27 + data[position + 26]);
    position += 27 + lacing.length;
    for (const size of lacing) {
      partial.push(data.subarray(position, position + size)); position += size;
      if (size < 255) {
        const packet = Buffer.concat(partial); partial = [];
        if (!['OpusHead', 'OpusTags'].includes(packet.toString('ascii', 0, 8))) packets.push(packet);
      }
    }
  }
  assert.equal(partial.length, 0);
  return packets;
}
function repacketize(packets, count, vbr = false) {
  const output = [];
  for (let index = 0; index + count <= packets.length; index += count) {
    const group = packets.slice(index, index + count), toc = group[0][0];
    assert.equal(toc & 3, 0, 'Expected single-frame encoder packets');
    assert.ok(group.every(packet => packet[0] === toc), 'Cannot combine different Opus configurations');
    const payloads = group.map(packet => packet.subarray(1));
    if (vbr) {
      assert.equal(count, 2);
      const length = payloads[0].length;
      const size = length < 252 ? Buffer.from([length]) : Buffer.from([252 + (length & 3), (length - 252 - (length & 3)) / 4]);
      output.push(Buffer.concat([Buffer.from([(toc & 252) | 2]), size, ...payloads]));
    } else {
      assert.ok(payloads.every(packet => packet.length === payloads[0].length));
      output.push(Buffer.concat([Buffer.from(count === 2 ? [(toc & 252) | 1] : [(toc & 252) | 3, count]), ...payloads]));
    }
  }
  return output;
}
function generate() {
  const samples = 15360, signal = Buffer.alloc(samples * 2 * 4);
  let random = 7349;
  for (let index = 0; index < samples; index++) {
    const t = index / 48000, envelope = Math.floor(index / 1920) % 4 === 0 ? 0.6 : 0.04;
    for (let channel = 0; channel < 2; channel++) {
      random ^= random << 13; random ^= random >>> 17; random ^= random << 5;
      const noise = (random >>> 0) / 4294967296 - 0.5;
      const sample = envelope * (noise + 0.2 * Math.sin(2 * Math.PI * (channel ? 1703 : 997) * t));
      signal.writeFloatLE(sample, (index * 2 + channel) * 4);
    }
  }
  const version = spawnSync('ffmpeg', ['-version'], { encoding: 'utf8' });
  if (version.error) throw version.error;
  assert.equal(version.status, 0, version.stderr);
  fs.mkdirSync(directory, { recursive: true });
  const fixtures = [];
  const save = (name, packets, source) => {
    const data = framed(packets);
    fs.writeFileSync(path.join(directory, name + '.opuspkt'), data);
    fixtures.push({ name, source, opuspkt_sha256: sha256(data), bytes: data.length, ...inspectPackets(data) });
  };
  for (const duration of [2.5, 5, 10, 20]) {
    const name = 'stereo-' + String(duration).replace('.', '_') + 'ms';
    const args = ['-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', '48000', '-ac', '2', '-i', 'pipe:0',
      '-c:a', 'libopus', '-application', 'lowdelay', '-b:a', '128k', '-vbr', 'off', '-frame_duration', String(duration), '-f', 'ogg', 'pipe:1'];
    const encoded = spawnSync('ffmpeg', args, { input: signal, maxBuffer: 4 * 1024 * 1024 });
    if (encoded.error) throw encoded.error;
    assert.equal(encoded.status, 0, encoded.stderr.toString());
    const packets = oggPackets(encoded.stdout);
    save(name, packets, { application: 'lowdelay', frame_ms: duration, channels: 2, bitrate: 128000, vbr: false });
    if (duration < 20) save(name + '-packed20', repacketize(packets, 20 / duration), { parent: name, packing: 'CBR', frames: 20 / duration });
  }
  for (const [name, channels, vbr] of [['mono-20ms', 1, false], ['stereo-10ms-vbr', 2, true]]) {
    const duration = vbr ? 10 : 20;
    const encoded = spawnSync('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-f', 'f32le', '-ar', '48000', '-ac', '2', '-i', 'pipe:0',
      '-ac', String(channels), '-c:a', 'libopus', '-application', 'lowdelay', '-b:a', '128k', '-vbr', vbr ? 'on' : 'off',
      '-frame_duration', String(duration), '-f', 'ogg', 'pipe:1'], { input: signal, maxBuffer: 4 * 1024 * 1024 });
    assert.equal(encoded.status, 0, encoded.stderr.toString());
    const packets = oggPackets(encoded.stdout);
    save(name, packets, { application: 'lowdelay', frame_ms: duration, channels, bitrate: 128000, vbr });
    if (vbr) save(name + '-packed20', repacketize(packets, 2, true), { parent: name, packing: 'VBR', frames: 2 });
  }
  const report = { schema_version: 1, generator: 'tools/esp8266_opus_profile/generate_phase_fixtures.cjs',
    encoder: version.stdout.split(/\r?\n/)[0], pcm_sha256: sha256(signal),
    signal: 'Own deterministic stereo xorshift32 noise (seed 7349), 997/1703-Hz tones and abrupt 40-ms envelope steps; 15360 frames, f32le 48 kHz.', fixtures };
  fs.writeFileSync(path.join(directory, 'manifest.json'), JSON.stringify(report, null, 2) + '\n');
  return report;
}
module.exports = { generate, framed, oggPackets, repacketize, directory };
if (require.main === module) {
  try { console.log(JSON.stringify(generate(), null, 2)); }
  catch (error) { console.error(error.stack); process.exitCode = 1; }
}

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const fixtureDirectory = path.resolve(__dirname, '../../tests/fixtures/opus_native');
const cases = [
  ['mono-12', 12, 1, 20, 'voip'],
  ['mono-24', 24, 1, 20, 'voip'],
  ['stereo-64', 64, 2, 20, 'audio'],
  ['stereo-128', 128, 2, 20, 'audio'],
  ['stereo-510', 510, 2, 20, 'audio'],
];
const sha256 = data => crypto.createHash('sha256').update(data).digest('hex');

function inspectPackets(data) {
  const modes = { SILK: 0, hybrid: 0, CELT: 0 }, durations = {}, channelCounts = {};
  let offset = 0, packets = 0, samples = 0, maxPacketBytes = 0;
  while (offset < data.length) {
    if (offset + 2 > data.length) throw Error('Truncated packet length');
    const length = data.readUInt16LE(offset);
    offset += 2;
    if (!length || offset + length > data.length) throw Error('Invalid packet length');
    const toc = data[offset], config = toc >> 3, code = toc & 3;
    if (code === 3 && length < 2) throw Error('Missing frame-count byte');
    const count = code === 0 ? 1 : code === 3 ? data[offset + 1] & 63 : 2;
    const frameMs = config < 12 ? [10, 20, 40, 60][config & 3] :
      config < 16 ? [10, 20][config & 1] : [2.5, 5, 10, 20][config & 3];
    const duration = frameMs * count;
    if (!count || duration > 120) throw Error('Invalid Opus packet duration');
    modes[config < 12 ? 'SILK' : config < 16 ? 'hybrid' : 'CELT']++;
    durations[duration] = (durations[duration] || 0) + 1;
    const channels = (toc & 4) ? 2 : 1;
    channelCounts[channels] = (channelCounts[channels] || 0) + 1;
    samples += duration * 48;
    packets++;
    maxPacketBytes = Math.max(maxPacketBytes, length);
    offset += length;
  }
  if (!packets) throw Error('Empty packet fixture');
  return { packets, samples, modes, packet_durations_ms: durations, packet_channels: channelCounts, max_packet_bytes: maxPacketBytes };
}

function createManifest() {
  return {
    format: 'uint16 little-endian length followed by raw Opus packet; repeated until EOF',
    source: 'Locally synthesized tones (997/10007 Hz left, 1703 Hz right) plus white noise with seed 7349; no recorded audio.',
    source_duration_seconds: 1.2,
    source_sample_rate: 48000,
    encoder: 'FFmpeg 8.1.1 libopus, CBR, see generate_fixtures.cjs',
    output: 'Decode all packets to 48 kHz signed 16-bit little-endian mono, including encoder pre-skip/tail samples.',
    fixtures: cases.map(([name, bitrate, channels, duration, application]) => {
      const packets = fs.readFileSync(path.join(fixtureDirectory, name + '.opuspkt'));
      const ogg = fs.readFileSync(path.join(fixtureDirectory, name + '.opus'));
      return { name, bitrate_kbps: bitrate, encoder_channels: channels, frame_duration_ms: duration, application,
        opuspkt_sha256: sha256(packets), ogg_sha256: sha256(ogg), ...inspectPackets(packets) };
    }),
  };
}
module.exports = { fixtureDirectory, cases, sha256, inspectPackets, createManifest };
if (require.main === module) {
  const json = JSON.stringify(createManifest(), null, 2) + '\n';
  if (process.argv.includes('--write-manifest')) fs.writeFileSync(path.join(fixtureDirectory, 'manifest.json'), json);
  else process.stdout.write(json);
}

#!/usr/bin/env node
const fs = require('node:fs'), path = require('node:path'), crypto = require('node:crypto');
const {spawnSync} = require('node:child_process');
const {makeWave} = require('./generate_composite_mp3.cjs');
const args = process.argv.slice(2);
function option(key, fallback) { const i=args.indexOf(key); return i<0 ? fallback : args[i+1]; }
const out = path.resolve(option('--output', 'tests/fixtures/aac_composite'));
const ffmpeg = option('--ffmpeg', 'ffmpeg');
const wave = makeWave();
const sha256 = b => crypto.createHash('sha256').update(b).digest('hex');
if (!wave.equals(fs.readFileSync('tests/fixtures/mp3_composite/tone-noise.wav')))
  throw new Error('AAC and MP3 must use the identical source WAV');
fs.mkdirSync(out, {recursive:true});
const version = spawnSync(ffmpeg, ['-version'], {encoding:'utf8'});
if (version.status !== 0) throw new Error('FFmpeg unavailable');
const manifest = {generator:'generate_composite_aac.cjs', source_wav:'../mp3_composite/tone-noise.wav',
  source_sha256:sha256(wave), source_rate:44100, source_channels:2, source_seconds:1,
  codec:'AAC-LC', container:'ADTS', encoder:version.stdout.split(/\r?\n/)[0], files:{}};
for (const bitrate of [48,64,96]) {
  const name = 'mix-'+String(bitrate).padStart(3,'0')+'.aac';
  const result = spawnSync(ffmpeg, ['-hide_banner','-loglevel','error','-y',
    '-i','pipe:0','-map_metadata','-1','-c:a','aac','-profile:a','aac_low',
    '-b:a',bitrate+'k','-ar','44100','-ac','2','-f','adts',path.join(out,name)],
    {input:wave});
  if (result.status !== 0) throw new Error(result.stderr.toString());
  const bytes = fs.readFileSync(path.join(out,name));
  manifest.files[name] = {target_kbps:bitrate, bytes:bytes.length, sha256:sha256(bytes)};
}
fs.writeFileSync(path.join(out,'manifest.json'), JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify(manifest,null,2));

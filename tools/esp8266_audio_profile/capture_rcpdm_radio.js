// Capture short local-only broadcasts; never include live network time in the benchmark.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {spawn} = require('node:child_process');
const output = path.resolve(process.argv[2] || 'radio_output/rcpdm-real-radio-20260906');
const sources = [
  ['retro', 'Retro FM', 'http://retroserver.streamr.ru:8043/retro128', 'mp3'],
  ['mayak', 'Radio Mayak', 'https://icecast-vgtrk.cdnvideo.ru/mayakfm', 'mp3'],
  ['vesti', 'Vesti FM', 'http://icecast.vgtrk.cdnvideo.ru/vestifm_mp3_192kbps', 'mp3'],
  ['record', 'Record', 'https://radiorecord.hostingradio.ru/rr_main96.aacp', 'aac'],
  ['symphony', 'Record Symphony', 'https://radiorecord.hostingradio.ru/symph96.aacp', 'aac'],
];
function run(command, args, timeout = 60000) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {windowsHide:true});
    let stdout = '', stderr = '';
    child.stdout.on('data', x => stdout += x);
    child.stderr.on('data', x => stderr += x);
    const timer = setTimeout(() => child.kill(), timeout);
    child.on('error', error => { clearTimeout(timer); reject(error); });
    child.on('close', code => { clearTimeout(timer); code === 0 ? resolve({stdout, stderr}) : reject(new Error(`${command}: ${code}: ${stderr}`)); });
  });
}
const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
async function main() {
  fs.mkdirSync(output, {recursive:true});
  if (fs.existsSync(path.join(output, 'manifest.json'))) throw Error('Choose a new directory; existing captures are immutable.');
  const manifest = {capturedUtc:new Date().toISOString(), durationRequestedSeconds:12,
    decoder:(await run('ffmpeg', ['-version'])).stdout.split('\n')[0].trim(),
    provenance:'URLs from tools/radio_stream_collector/curated_stations.m3u; local research snippets, not licensed for redistribution.', clips:[]};
  await Promise.all(sources.map(async ([id, name, url, extension]) => {
    const file = `${id}.${extension}`, pcm = `${id}.s16le`;
    const args = ['-hide_banner', '-loglevel', 'warning', '-n', '-rw_timeout', '10000000',
      '-i', url, '-map', '0:a:0', '-t', '12', '-c:a', 'copy', '-f', extension === 'aac' ? 'adts' : 'mp3', path.join(output, file)];
    const clip = {id, name, url, file, pcm, capturedUtc:new Date().toISOString(), captureArgs:args.slice(0,-1).concat(file)};
    try {
      const capture = await run('ffmpeg', args);
      clip.captureWarnings = capture.stderr;
      clip.probe = JSON.parse((await run('ffprobe', ['-v', 'error', '-show_streams', '-show_format', '-of', 'json', path.join(output, file)])).stdout);
      const decodeArgs = ['-hide_banner', '-loglevel', 'warning', '-n', '-i', path.join(output,file), '-map', '0:a:0', '-c:a', 'pcm_s16le', '-f', 's16le', path.join(output,pcm)];
      clip.decodeWarnings = (await run('ffmpeg', decodeArgs)).stderr;
      clip.sha256 = sha256(path.join(output,file));
      clip.pcmSha256 = sha256(path.join(output,pcm));
      clip.bytes = fs.statSync(path.join(output,file)).size;
      clip.pcmBytes = fs.statSync(path.join(output,pcm)).size;
      const stream = clip.probe.streams[0];
      clip.sampleRate = Number(stream.sample_rate); clip.channels = stream.channels;
      clip.pcmSeconds = clip.pcmBytes / (2 * clip.channels * clip.sampleRate);
      clip.ok = clip.pcmSeconds >= 10;
      console.log(`${id}: ${stream.codec_name}/${stream.profile}, ${clip.sampleRate} Hz, ${clip.channels} ch, ${clip.pcmSeconds.toFixed(3)} s`);
    } catch (error) { clip.ok = false; clip.error = error.message; console.error(`${id}: ${error.message}`); }
    manifest.clips.push(clip);
  }));
  manifest.clips.sort((a,b) => a.id.localeCompare(b.id));
  fs.writeFileSync(path.join(output,'manifest.json'), JSON.stringify(manifest,null,2)+'\n');
  if (manifest.clips.filter(x => x.ok).length < 3) process.exitCode = 1;
}
main().catch(error => { console.error(error); process.exitCode = 1; });

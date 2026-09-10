const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{spawnSync}=require('node:child_process');
const {fixtureDirectory,sha256,inspectPackets}=require('./fixtures.cjs');
const {inspect}=require('./inspect_ogg_packets.cjs');
const out=path.join(fixtureDirectory,'through192');fs.mkdirSync(out,{recursive:true});
const file=path.join(out,'stereo-192.opus');
// Same own deterministic tones/noise as the earlier corpus; do not rewrite
// the existing five fixtures or alter their archived benchmark identities.
const args=['-hide_banner','-loglevel','error','-y','-f','lavfi','-i',
 'aevalsrc=0.24*sin(2*PI*997*t)+0.04*sin(2*PI*10007*t)|0.19*sin(2*PI*1703*t):s=48000:d=1.2',
 '-f','lavfi','-i','anoisesrc=color=white:amplitude=0.025:seed=7349:r=48000:d=1.2',
 '-filter_complex','[0:a][1:a]amix=inputs=2:normalize=0','-ac','2','-c:a','libopus','-application','audio',
 '-b:a','192k','-vbr','off','-frame_duration','20',file];
const r=spawnSync('ffmpeg',args,{encoding:'utf8'});assert.equal(r.status,0,r.stderr);
const ogg=fs.readFileSync(file),parsed=inspect(ogg);assert.equal(parsed.report.trailing_bytes,0);
fs.writeFileSync(path.join(out,'stereo-192.opuspkt'),parsed.raw);
const legacy=JSON.parse(fs.readFileSync(path.join(fixtureDirectory,'manifest.json')));
const fixtures=legacy.fixtures.filter(f=>f.bitrate_kbps<=192).map(f=>({...f,packet_file:'../'+f.name+'.opuspkt'}));
fixtures.push({name:'stereo-192',bitrate_kbps:192,encoder_channels:2,frame_duration_ms:20,application:'audio',
 opuspkt_sha256:sha256(parsed.raw),ogg_sha256:sha256(ogg),...inspectPackets(parsed.raw)});
assert.deepEqual(fixtures.map(f=>f.bitrate_kbps),[12,24,64,128,192]);
const version=spawnSync('ffmpeg',['-version'],{encoding:'utf8'});assert.equal(version.status,0);
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({...legacy,encoder:version.stdout.split(/\r?\n/)[0],
 purpose:'Physical speed tests through192 kbps. No runtime decoder bitrate restriction.',command:['ffmpeg',...args.slice(0,-1),'stereo-192.opus'],fixtures},null,2)+'\n');
console.log('Saved through192 corpus:',parsed.report.packets,'new192kbps packets');

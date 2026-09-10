const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { spawn, spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '../..');
const component = path.join(root, 'esp8266/rtos-sdk-native/components/opus_decoder');
const upstream = path.join(component, 'upstream');
const windows = process.platform === 'win32';
const hostPath = file => windows ? '/mnt/' + file[0].toLowerCase() + file.slice(2).replace(/\\/g, '/') : file;
const nativePath = file => windows ? file.replace(/^\/mnt\/([a-z])\//, (_, drive) => drive.toUpperCase() + ':/') : file;

function command(program, args) {
  return windows ? ['wsl.exe', ['--exec', program, ...args]] : [program, args];
}
function execute(program, args) {
  const [file, argv] = command(program, args);
  const result = spawnSync(file, argv, { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 });
  if (result.error) throw result.error;
  if (result.status !== 0) throw Error(`${program} failed (${result.status}):\n${result.stdout}${result.stderr}`);
  return result.stdout;
}
function compile(args) {
  const [file, argv] = command('gcc', args);
  return new Promise((resolve, reject) => {
    const child = spawn(file, argv, { stdio: ['ignore', 'pipe', 'pipe'] });
    let output = '';
    child.stdout.on('data', text => { output += text; });
    child.stderr.on('data', text => { output += text; });
    child.on('error', reject);
    child.on('close', code => code === 0 ? resolve() : reject(Error(`gcc failed (${code}):\n${output}`)));
  });
}

function dependencies(depfile) {
  if (!fs.existsSync(depfile)) return [];
  const text = fs.readFileSync(depfile, 'utf8').replace(/\\\r?\n/g, ' ');
  // All files used by this repository have no whitespace in their paths.
  return text.slice(text.indexOf(':') + 1).trim().split(/\s+/).filter(Boolean).map(nativePath);
}

async function buildHost({ bounded = false, noBuild = false, jobs = 4, upstreamRoot, fastInt64, firFlashWord = false, profileStage = 0, celtDecodeOnly = false } = {}) {
  if (celtDecodeOnly && !bounded) throw Error('celtDecodeOnly requires bounded decoder.');
  if (!Number.isInteger(profileStage) || profileStage < 0 || profileStage > 11 || (profileStage && !bounded)) throw Error('profileStage requires bounded and 0..11.');
  if (firFlashWord && !bounded) throw Error('firFlashWord requires bounded decoder.');
  if (bounded && upstreamRoot) throw Error('--upstream is for a pristine unbounded baseline only.');
  if (fastInt64 !== undefined && fastInt64 !== 0 && fastInt64 !== 1) throw Error('fastInt64 must be 0 or 1.');
  const sourceRoot = upstreamRoot ? path.resolve(upstreamRoot) : upstream;
  if (fastInt64 !== undefined && !fs.readFileSync(path.join(sourceRoot, 'celt/arch.h'), 'utf8').includes('#ifndef OPUS_FAST_INT64'))
    throw Error('Selected upstream does not support an OPUS_FAST_INT64 override; use a documented diagnostic copy.');
  const out = path.join(root, '.build/esp8266-opus-host' + (bounded ? '-bounded' : upstreamRoot ? '-pristine' : '') +
    (fastInt64 === undefined ? '' : '-int64-' + fastInt64) + (firFlashWord ? '-fir-word' : '') + (profileStage ? '-stage-' + profileStage : '') + (celtDecodeOnly ? '-celt-decode-only' : ''));
  const binary = path.join(out, 'probe');
  const sources = ['src', 'celt', 'silk', 'silk/fixed'].flatMap(dir =>
    fs.readdirSync(path.join(sourceRoot, dir)).filter(file => file.endsWith('.c')).sort()
      .map(file => path.join(sourceRoot, dir, file)));
  if (bounded) sources.push(path.join(component, 'opus_memory.c'));
  if (profileStage) sources.push(path.join(component, 'opus_stage_profile.c'));
  sources.push(path.join(__dirname, 'probe.c'));
  const flags = ['-O2', '-std=c99', '-fwrapv', '-ffunction-sections', '-fdata-sections',
    ...(fastInt64 === undefined ? [] : ['-DOPUS_FAST_INT64=' + fastInt64]),
    ...(bounded ? ['-DYORADIO_OPUS_BOUNDED=1', '-I' + hostPath(component)] : []),
    ...(firFlashWord ? ['-DYORADIO_OPUS_FIR_FLASH_WORD=1'] : []),
    ...(celtDecodeOnly ? ['-DYORADIO_OPUS_CELT_DECODE_ONLY=1'] : []),
    ...(profileStage ? ['-DYORADIO_OPUS_PROFILE_STAGE=' + profileStage] : []),
    ...['include', 'celt', 'silk', 'silk/fixed', 'src'].map(dir => '-I' + hostPath(path.join(sourceRoot, dir)))];
  const objects = sources.map(source => path.join(out, 'objects',
    source.startsWith(sourceRoot + path.sep) ? path.join('upstream', path.relative(sourceRoot, source)) + '.o' :
      source.startsWith(component + path.sep) ? path.relative(component, source) + '.o' : 'probe.c.o'));
  const buildfile = path.join(out, 'build.json');
  const previous = fs.existsSync(buildfile) ? JSON.parse(fs.readFileSync(buildfile, 'utf8')) : null;
  if (noBuild) {
    if (!fs.existsSync(binary) || !previous) throw Error(`No incremental host build in ${out}; omit --no-build once.`);
    if (JSON.stringify(previous.flags) !== JSON.stringify(flags) || JSON.stringify(previous.sources) !== JSON.stringify(sources))
      throw Error('Existing host cache uses different flags or sources; omit --no-build.');
    return { binary, out, objects, flags, compiler: previous.compiler, compiled: 0, linked: false, reused: true };
  }
  fs.mkdirSync(out, { recursive: true });
  const compiler = execute('gcc', ['--version']).split(/\r?\n/)[0];
  const signature = crypto.createHash('sha256').update(JSON.stringify({ compiler, flags, sources })).digest('hex');
  const pending = sources.flatMap((source, index) => {
    const object = objects[index], deps = dependencies(object + '.d');
    const stamp = fs.existsSync(object) ? fs.statSync(object).mtimeMs : 0;
    const stale = previous?.signature !== signature || !stamp || !deps.length || deps.some(dep =>
      !fs.existsSync(dep) || fs.statSync(dep).mtimeMs > stamp);
    return stale ? [{ source, object }] : [];
  });
  let cursor = 0;
  await Promise.all(Array.from({ length: Math.min(Math.max(1, jobs), pending.length) }, async () => {
    while (cursor < pending.length) {
      const { source, object } = pending[cursor++];
      fs.mkdirSync(path.dirname(object), { recursive: true });
      await compile([...flags, '-MMD', '-MF', hostPath(object + '.d'), '-c', hostPath(source), '-o', hostPath(object)]);
    }
  }));
  const linked = pending.length > 0 || !fs.existsSync(binary);
  if (linked) execute('gcc', [...objects.map(hostPath), '-Wl,--gc-sections', '-lm', '-o', hostPath(binary)]);
  fs.writeFileSync(buildfile, JSON.stringify({ signature, compiler, flags, sources }, null, 2) + '\n');
  process.stderr.write(`${bounded ? 'bounded' : 'baseline'}: compiled ${pending.length}/${sources.length} objects; ${linked ? 'linked' : 'link reused'}\n`);
  return { binary, out, objects, flags, compiler, compiled: pending.length, linked, reused: false };
}

function runProbe({ bounded = false, fixture, output, selfTest = true, upstreamRoot, fastInt64, firFlashWord = false, profileStage = 0, celtDecodeOnly = false }) {
  const out = path.join(root, '.build/esp8266-opus-host' + (bounded ? '-bounded' : upstreamRoot ? '-pristine' : '') +
    (fastInt64 === undefined ? '' : '-int64-' + fastInt64) + (firFlashWord ? '-fir-word' : '') + (profileStage ? '-stage-' + profileStage : '') + (celtDecodeOnly ? '-celt-decode-only' : ''));
  const args = fixture ? [hostPath(path.resolve(fixture)), hostPath(path.resolve(output || path.join(out, 'decoded.pcm'))),
    ...(selfTest ? ['--self-test'] : [])] : [];
  return JSON.parse(execute(hostPath(path.join(out, 'probe')), args).trim());
}

module.exports = { buildHost, runProbe, hostPath, execute, root, component };
if (require.main === module) {
  const bounded = process.argv.includes('--bounded');
  const upstreamIndex = process.argv.indexOf('--upstream');
  const upstreamRoot = upstreamIndex < 0 ? undefined : process.argv[upstreamIndex + 1];
  const fastInt64Index = process.argv.indexOf('--fast-int64');
  const fastInt64 = fastInt64Index < 0 ? undefined : Number(process.argv[fastInt64Index + 1]);
  buildHost({ bounded, noBuild: process.argv.includes('--no-build'), upstreamRoot, fastInt64 }).then(() => {
    const fixture = process.argv.find(arg => arg.endsWith('.opuspkt'));
    const outputIndex = process.argv.indexOf('--output');
    console.log(JSON.stringify(runProbe({ bounded, fixture, upstreamRoot, fastInt64, output: outputIndex < 0 ? undefined : process.argv[outputIndex + 1] }), null, 2));
  }).catch(error => { console.error(error.message); process.exitCode = 1; });
}

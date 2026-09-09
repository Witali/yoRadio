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

async function buildHost({ bounded = false, noBuild = false, jobs = 4, upstreamRoot } = {}) {
  if (bounded && upstreamRoot) throw Error('--upstream is for a pristine unbounded baseline only.');
  const sourceRoot = upstreamRoot ? path.resolve(upstreamRoot) : upstream;
  const out = path.join(root, '.build/esp8266-opus-host' + (bounded ? '-bounded' : upstreamRoot ? '-pristine' : ''));
  const binary = path.join(out, 'probe');
  const sources = ['src', 'celt', 'silk', 'silk/fixed'].flatMap(dir =>
    fs.readdirSync(path.join(sourceRoot, dir)).filter(file => file.endsWith('.c')).sort()
      .map(file => path.join(sourceRoot, dir, file)));
  if (bounded) sources.push(path.join(component, 'opus_memory.c'));
  sources.push(path.join(__dirname, 'probe.c'));
  const flags = ['-O2', '-std=c99', '-fwrapv', '-ffunction-sections', '-fdata-sections',
    ...(bounded ? ['-DYORADIO_OPUS_BOUNDED=1', '-I' + hostPath(component)] : []),
    ...['include', 'celt', 'silk', 'silk/fixed', 'src'].map(dir => '-I' + hostPath(path.join(sourceRoot, dir)))];
  const objects = sources.map(source => path.join(out, 'objects',
    source.startsWith(sourceRoot + path.sep) ? path.join('upstream', path.relative(sourceRoot, source)) + '.o' :
      source.startsWith(component + path.sep) ? path.relative(component, source) + '.o' : 'probe.c.o'));
  const buildfile = path.join(out, 'build.json');
  const previous = fs.existsSync(buildfile) ? JSON.parse(fs.readFileSync(buildfile, 'utf8')) : null;
  if (noBuild) {
    if (!fs.existsSync(binary) || !previous) throw Error(`No incremental host build in ${out}; omit --no-build once.`);
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

function runProbe({ bounded = false, fixture, output, selfTest = true, upstreamRoot }) {
  const out = path.join(root, '.build/esp8266-opus-host' + (bounded ? '-bounded' : upstreamRoot ? '-pristine' : ''));
  const args = fixture ? [hostPath(path.resolve(fixture)), hostPath(path.resolve(output || path.join(out, 'decoded.pcm'))),
    ...(selfTest ? ['--self-test'] : [])] : [];
  return JSON.parse(execute(hostPath(path.join(out, 'probe')), args).trim());
}

module.exports = { buildHost, runProbe, hostPath, execute, root, component };
if (require.main === module) {
  const bounded = process.argv.includes('--bounded');
  const upstreamIndex = process.argv.indexOf('--upstream');
  const upstreamRoot = upstreamIndex < 0 ? undefined : process.argv[upstreamIndex + 1];
  buildHost({ bounded, noBuild: process.argv.includes('--no-build'), upstreamRoot }).then(() => {
    const fixture = process.argv.find(arg => arg.endsWith('.opuspkt'));
    const outputIndex = process.argv.indexOf('--output');
    console.log(JSON.stringify(runProbe({ bounded, fixture, upstreamRoot, output: outputIndex < 0 ? undefined : process.argv[outputIndex + 1] }), null, 2));
  }).catch(error => { console.error(error.message); process.exitCode = 1; });
}

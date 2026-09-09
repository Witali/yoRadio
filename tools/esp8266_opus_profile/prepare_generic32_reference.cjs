const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const { root } = require('./build_host.cjs');
const { sha256 } = require('./fixtures.cjs');

const provenanceName = 'opus-generic32-provenance.json';
const defaultSource = path.join(root, '.build/upstream-radio-review-2026-09-09/esp8266audio/src/libopus');
const defaultOutput = path.join(root, '.build/esp8266-opus-pristine-generic32');
const selection = `/* Assume that all LP64 architectures have fast 64-bit types; also x86_64
   (which can be ILP32 for x32) and Win64 (which is LLP64). */
#if defined(__x86_64__) || defined(__LP64__) || defined(_WIN64)
#define OPUS_FAST_INT64 1
#else
#define OPUS_FAST_INT64 0
#endif`;

function addOverrideGuard(data) {
  const text = data.toString('utf8');
  assert.ok(!text.includes('#ifndef OPUS_FAST_INT64'), 'Source already has an arithmetic override; use the pristine tree');
  const newline = text.includes('\r\n') ? '\r\n' : '\n';
  const old = selection.replaceAll('\n', newline) + newline;
  assert.equal(text.split(old).length, 2, 'Unrecognized or duplicate architecture selection in pristine arch.h');
  // Like apply_patch, normalize line endings only inside the edited block.
  const guarded = selection.replace('#if defined(__x86_64__)', '#ifndef OPUS_FAST_INT64\n#if defined(__x86_64__)') + '\n#endif';
  return Buffer.from(text.replace(old, guarded + '\n'));
}

function listFiles(directory, prefix = '') {
  return fs.readdirSync(path.join(directory, prefix), { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name, 'en')).flatMap(entry => {
    assert.ok(!entry.isSymbolicLink(), 'Reference trees must not contain symlinks: ' + entry.name);
    const name = prefix ? prefix + '/' + entry.name : entry.name;
    return entry.isDirectory() ? listFiles(directory, name) : [name];
  }).sort();
}

function prepareReference({ source = defaultSource, output = defaultOutput } = {}) {
  const from = fs.realpathSync(source), to = path.resolve(output);
  const overlaps = (a, b) => { const relative = path.relative(a, b); return relative === '' || (!relative.startsWith('..' + path.sep) && relative !== '..' && !path.isAbsolute(relative)); };
  assert.ok(!overlaps(from, to) && !overlaps(to, from), 'Source and diagnostic destination must not overlap');
  const names = listFiles(from);
  assert.ok(names.includes('celt/arch.h') && names.includes('src/opus_decoder.c'), 'Source is not a libopus tree');
  assert.ok(!names.includes(provenanceName), 'Source is already a diagnostic copy');
  const prepared = names.map(name => {
    const original = fs.readFileSync(path.join(from, name));
    const data = name === 'celt/arch.h' ? addOverrideGuard(original) : original;
    return { path: name, data, source_sha256: sha256(original), copy_sha256: sha256(data) };
  });
  const existed = fs.existsSync(to);
  if (existed) {
    assert.ok(!fs.lstatSync(to).isSymbolicLink(), 'Diagnostic destination must not be a symlink');
    assert.deepEqual(listFiles(to).filter(name => name !== provenanceName), names, 'Existing diagnostic file inventory differs; refusing to overwrite');
    for (const file of prepared)
      assert.equal(sha256(fs.readFileSync(path.join(to, file.path))), file.copy_sha256, 'Existing diagnostic file changed: ' + file.path);
  }
  const files = prepared.map(({ data, ...file }) => file);
  const treeHash = key => sha256(Buffer.from(files.map(file => file.path + '\0' + file[key] + '\n').join('')));
  const provenance = {
    schema_version: 1,
    source: path.relative(root, from).replaceAll('\\', '/'),
    destination: path.relative(root, to).replaceAll('\\', '/'),
    purpose: 'Select unchanged generic 32-bit Opus arithmetic on a 64-bit host with -DOPUS_FAST_INT64=0; not a 32-bit host ABI.',
    allowed_change: 'Only celt/arch.h: wrap architecture detection in #ifndef OPUS_FAST_INT64; LF in the edited block, all other bytes unchanged.',
    changed_files: files.filter(file => file.source_sha256 !== file.copy_sha256).map(file => file.path),
    source_tree_sha256: treeHash('source_sha256'), copy_tree_sha256: treeHash('copy_sha256'),
    tree_hash_format: 'SHA256 of sorted relative path + NUL + file SHA256 + LF, UTF-8',
    file_count: files.length, files,
  };
  assert.deepEqual(provenance.changed_files, ['celt/arch.h']);
  const manifest = path.join(to, provenanceName);
  if (fs.existsSync(manifest))
    assert.deepEqual(JSON.parse(fs.readFileSync(manifest, 'utf8')), provenance, 'Existing provenance changed or source location differs');
  if (!existed) {
    fs.mkdirSync(to, { recursive: true });
    for (const file of prepared) {
      fs.mkdirSync(path.dirname(path.join(to, file.path)), { recursive: true });
      fs.writeFileSync(path.join(to, file.path), file.data, { flag: 'wx' });
    }
  }
  if (!fs.existsSync(manifest)) fs.writeFileSync(manifest, JSON.stringify(provenance, null, 2) + '\n', { flag: 'wx' });
  return provenance;
}

module.exports = { prepareReference, addOverrideGuard, selection, provenanceName, defaultSource, defaultOutput };
if (require.main === module) {
  const value = key => { const i = process.argv.indexOf(key); return i < 0 ? undefined : process.argv[i + 1]; };
  try {
    const result = prepareReference({ source: value('--source'), output: value('--output') });
    console.log(JSON.stringify({ ...result, files: undefined }, null, 2));
  } catch (error) { console.error(error.message); process.exitCode = 1; }
}

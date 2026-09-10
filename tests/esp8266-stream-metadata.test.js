const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {execute, hostPath, root} = require('../tools/esp8266_opus_profile/build_host.cjs');

test('real PCM callback publishes source channels while output and frame accounting stay mono', t => {
  const main = path.join(root, 'esp8266/rtos-sdk-native/main');
  const audio = fs.readFileSync(path.join(main, 'audio_service.c'), 'utf8');
  const web = fs.readFileSync(path.join(main, 'web_service.c'), 'utf8');
  const start = audio.indexOf('static bool pcm_output(');
  const end = audio.indexOf('\n#if YORADIO_ESP8266_KARADIO_PIPELINE', start);
  const contextEnd = audio.indexOf('} output_context_t;') + '} output_context_t;'.length;
  const contextStart = audio.lastIndexOf('typedef struct {', contextEnd);
  const formatStart = web.indexOf('static void format_stream(');
  const formatEnd = web.indexOf('\nstatic bool format_status(', formatStart);
  assert.ok(start > 0 && end > start && contextStart > 0 && formatEnd > formatStart);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'esp8266-stream-metadata-'));
  t.after(() => fs.rmSync(dir, {recursive: true, force: true}));
  fs.writeFileSync(path.join(dir, 'metadata_under_test.inc'),
    audio.slice(contextStart, contextEnd) + '\n' + audio.slice(start, end) + '\n' + web.slice(formatStart, formatEnd));
  const executable = path.join(dir, 'test');
  execute('gcc', ['-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
    '-fsanitize=address,undefined', '-fno-sanitize-recover=all', '-fno-pie', '-no-pie',
    '-I' + hostPath(dir),
    '-I' + hostPath(path.join(root, 'esp8266/rtos-sdk-native/components/helix_codecs')),
    hostPath(path.join(__dirname, 'native/esp8266_stream_metadata_test.c')), '-o', hostPath(executable)]);
  const output = execute(hostPath(executable), []);
  assert.match(output, /Stream metadata PASS/);
  t.diagnostic(output.trim());
});

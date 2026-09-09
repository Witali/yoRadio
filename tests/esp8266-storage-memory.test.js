const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const main = path.join(root, 'esp8266/rtos-sdk-native/main');

test('native storage mount keeps five slots, recovery and nonformatting failures', () => {
  const source = fs.readFileSync(path.join(main, 'storage_service.c'), 'utf8');
  const body = source.slice(source.indexOf('esp_err_t storage_service_init(void)'));
  const dir = fs.mkdtempSync(path.join(root, '.build/storage-memory-'));
  const unit = path.join(dir, 'test.c'), binary = path.join(dir, 'test');
  fs.writeFileSync(unit, `
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
typedef int esp_err_t;
enum { ESP_OK=0, ESP_FAIL=-1 };
typedef struct { const char *base_path, *partition_label; unsigned max_files;
                 bool format_if_mount_failed; } esp_vfs_spiffs_conf_t;
#define STORAGE_ROOT "/spiffs"
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
static int mount_result, info_result, fail_recovery;
static unsigned recoveries, infos;
static esp_err_t esp_vfs_spiffs_register(const esp_vfs_spiffs_conf_t *c) {
  assert(c->max_files == 5 && !c->format_if_mount_failed);
  assert(!strcmp(c->base_path, "/spiffs") && !strcmp(c->partition_label, "spiffs"));
  return mount_result;
}
static bool file_recover(const char *p) {
  assert(!strncmp(p, "/spiffs/", 8));
  return ++recoveries != (unsigned)fail_recovery;
}
static esp_err_t esp_spiffs_info(const char *label, size_t *total, size_t *used) {
  assert(!strcmp(label,"spiffs")); ++infos; *total=100; *used=20; return info_result;
}
${body}
int main(void) {
  assert(storage_service_init() == ESP_OK && recoveries == 13 && infos == 1);
  recoveries=infos=0; mount_result=-12;
  assert(storage_service_init() == -12 && !recoveries && !infos);
  mount_result=0; fail_recovery=3;
  assert(storage_service_init() == ESP_FAIL && recoveries == 3 && !infos);
  recoveries=0; fail_recovery=0; info_result=-13;
  assert(storage_service_init() == -13 && recoveries == 13 && infos == 1);
  return 0;
}
`);
  const windows = process.platform === 'win32';
  const host = p => windows ? '/mnt/' + p[0].toLowerCase() + p.slice(2).replace(/\\/g, '/') : p;
  const args = ['-std=c11', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined', host(unit), '-o', host(binary)];
  const run = (command, args) => spawnSync(windows ? 'wsl.exe' : command,
    windows ? ['--exec', command, ...args] : args, {encoding:'utf8'});
  let result = run('gcc', args);
  assert.equal(result.status, 0, result.stdout + result.stderr);
  result = run(host(binary), []);
  assert.equal(result.status, 0, result.stdout + result.stderr);
});

test('five slots save 1620 bytes while retaining one beyond the four-handle bound', () => {
  const source = fs.readFileSync(path.join(main, 'storage_service.c'), 'utf8');
  const slots = Number(source.match(/\.max_files = (\d+)/)[1]);
  const bytes = n => n * 48 + 20 + n * (20 + 256);
  assert.equal(slots, 5);
  assert.equal(bytes(10) - bytes(slots), 1620);
  assert.equal(slots - Math.max(2 + 1 + 1, 2 + 1 + 1), 1);
  const settings = fs.readFileSync(path.join(main, 'persistent_settings.c'), 'utf8');
  assert.doesNotMatch(settings, /\b(?:fopen|open)\(/);
  const cache = fs.readFileSync(path.join(main, 'playlist_web_cache.c'), 'utf8');
  assert.match(cache, /if \(fd >= 0\) close\(fd\);\s*bool reused = ok && cached\(w\)/);
  assert.match(cache, /if \(fclose\(w->output\) != 0\) ok = false;\s*if \(ok\) ok = file_replace/);
  const upload = fs.readFileSync(path.join(main, 'web_upload.c'), 'utf8');
  assert.match(upload, /fclose\(u->file\)[^]*?u->file = NULL;[^]*?playlist_service_validate/);
});

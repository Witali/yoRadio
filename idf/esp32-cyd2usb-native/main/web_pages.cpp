#include "web_pages.h"

extern "C" const char *web_native_page(void) {
    return R"HTML(<!doctype html>
<html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ёRadio · CYD</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#131719;color:#eef1ed}
body{max-width:48rem;margin:2rem auto;padding:0 1rem}h1{font-size:1.6rem}h2{font-size:1.15rem}
section{background:#22292c;border-radius:1rem;padding:1.2rem;margin:1rem 0}
fieldset{border:0;padding:0;margin:0;min-width:0}h3{font-size:1rem;margin:1rem 0 .4rem}
button,input{font:inherit;border:1px solid #65716e;border-radius:.4rem;padding:.5rem;background:#182022;color:inherit}
button{cursor:pointer;background:#d6c86d;color:#161b19}button:disabled{opacity:.45;cursor:wait}
label{display:inline-flex;align-items:center;gap:.5rem;margin:.4rem .6rem .4rem 0}input[type=number]{width:5rem}
.row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}p{overflow-wrap:anywhere}small,a{color:#c4d2cc}
#message{min-height:1.5rem;color:#e7d877}#title{font-size:1.2rem}#details{font-variant-numeric:tabular-nums}
input[type=file]{max-width:100%;min-width:0;box-sizing:border-box}.upload-form{border-top:1px solid #65716e;padding-top:.4rem;margin-top:1rem}
.upload-form label{display:flex;flex-wrap:wrap;max-width:100%}
progress{width:24rem;max-width:100%}
</style>
<h1>ёRadio · ESP32 CYD</h1><p id="connection" role="status">Подключение…</p>
<p id="message" role="alert"></p>
<section><h2 id="station">Радио</h2><p id="title"></p><p id="details"></p>
<div class="row"><button data-radio="previous" disabled>Предыдущая</button><button data-radio="toggle" disabled>Старт / стоп</button>
<button data-radio="next" disabled>Следующая</button><button data-radio="stop" disabled>Стоп</button></div>
<form id="station-form"><label>Станция <input id="station-number" type="number" min="1" max="65535" required value="1"></label>
<button disabled>Включить</button><small id="station-count"></small></form>
<label><input id="smartstart" type="checkbox" disabled>Включать последнюю станцию после запуска</label></section>
<section><h2>Звук</h2><form id="audio-form">
<label>Громкость <input id="volume" type="number" min="0" max="254" required></label>
<label>Баланс <input id="balance" type="number" min="-16" max="16" required></label><br>
<label><input id="normalization" type="checkbox">Нормализация</label><br>
<label>Усиление, дБ <input id="normgain" type="number" min="0" max="20" required></label>
<label>Цель, dBFS <input id="normtarget" type="number" min="-20" max="0" required></label>
<label>Время, мс <input id="normtime" type="number" min="100" max="10000" required></label>
<button disabled>Сохранить</button></form></section>
<p><button id="reconnect" disabled>Переподключить Wi-Fi</button> · <a href="/api/native/health">Диагностика</a></p>
<section id="uploads" hidden><h2>Файлы и Wi-Fi</h2><p id="upload-limits"></p>
<form id="playlist-form" class="upload-form" action="/upload" method="post" enctype="multipart/form-data" hidden>
<fieldset id="playlist-fields" disabled><h3>Плейлист</h3>
<label>Файл CSV <input id="playlist-file" name="plfile" type="file" accept=".csv,text/csv,text/tab-separated-values" required></label>
<button id="playlist-submit" disabled>Сохранить плейлист</button></fieldset></form>
<form id="assets-form" class="upload-form" action="/webboard" method="post" enctype="multipart/form-data" hidden>
<fieldset id="assets-fields" disabled><h3>Файлы веб-интерфейса</h3>
<label>Файлы .gz <input id="asset-files" name="www" type="file" accept=".gz,application/gzip" multiple></label><br>
<label id="asset-playlist-label">Плейлист CSV (необязательно) <input id="asset-playlist" name="data" type="file" accept=".csv"></label><br>
<label id="asset-wifi-label">Wi-Fi CSV (необязательно) <input id="asset-wifi" name="data" type="file" accept=".csv"></label><br>
<small>Выбранные CSV сохраняются как playlist.csv и wifi.csv. Wi-Fi CSV: имя сети и пароль через табуляцию.</small><br>
<button id="assets-submit" disabled>Сохранить файлы</button></fieldset></form>
<form id="wifi-form" class="upload-form" action="/" method="post" enctype="multipart/form-data" hidden>
<fieldset id="wifi-fields" disabled><h3>Подключение Wi-Fi</h3>
<label>Имя сети (SSID) <input id="wifi-ssid" name="ssid" maxlength="31" autocomplete="off" required></label>
<label>Пароль <input id="wifi-password" name="pass" type="password" maxlength="63" autocomplete="new-password"></label><br>
<small id="wifi-limits"></small><br><button id="wifi-submit" disabled>Сохранить Wi-Fi</button>
</fieldset></form></section>
<section id="firmware" hidden><h2>Обновление прошивки</h2>
<form id="firmware-form" action="/update" method="post" enctype="multipart/form-data">
<fieldset id="firmware-fields" disabled><p id="firmware-limits"></p>
<label>Application app.bin для ESP32 CYD <input id="firmware-file" type="file" accept=".bin,application/octet-stream" required></label>
<p><small>На время установки звук остановится. Настройки и файлы радио сохранятся.
Не отключайте питание до перезапуска.</small></p>
<button id="firmware-submit" disabled>Установить прошивку</button></fieldset></form>
<p id="firmware-status" role="status"></p><progress id="firmware-progress" max="100" value="0" hidden></progress>
<p><a id="firmware-refresh" href="/" hidden>Открыть радио после перезапуска</a></p></section>
<small id="backend"></small>
<script>
// NATIVE_UI_BEGIN
'use strict';
const el = id => document.getElementById(id);
let socket, retryTimer, retryDelay = 1000, lastSeen = 0, ready = false, settingsDirty = false;
let capabilities = {}, uploadBusy = false, firmwareBusy = false, awaitingRestart = false;
const message = text => { el('message').textContent = text; };
async function api(path, query, method = 'GET') {
  const suffix = query ? '?' + new URLSearchParams(query).toString() : '';
  const response = await fetch('/api/native/' + path + suffix, {method, cache: 'no-store'});
  if (!response.ok) throw new Error(await response.text() || 'Ошибка запроса');
  return response.json();
}
function renderStatus(state) {
  el('station').textContent = state.station || 'Радио';
  el('title').textContent = state.title || '';
  el('details').textContent = [state.connecting ? 'Подключение к станции…' : state.audio ? 'Воспроизведение' : 'Остановлено',
    state.format, state.bitrate ? state.bitrate + ' кбит/с' : ''].filter(Boolean).join(' · ');
  if (typeof state.current === 'number') renderRadio(state);
  if (typeof state.normalization === 'boolean') renderSettings(state, false);
}
function renderRadio(radio) {
  el('station-count').textContent = 'из ' + radio.count;
  el('station-number').max = String(Math.max(1, radio.count));
  if (document.activeElement !== el('station-number') && radio.current)
    el('station-number').value = radio.current;
  el('smartstart').checked = radio.smartstart;
}
function renderSettings(settings, force = true) {
  if (!force && settingsDirty) return;
  settingsDirty = false;
  for (const key of ['volume','balance','normgain','normtarget','normtime']) {
    if (document.activeElement !== el(key)) el(key).value = settings[key];
  }
  el('normalization').checked = settings.normalization;
}
async function action(work) {
  if (firmwareBusy || awaitingRestart) { message('Дождитесь перезапуска радио'); return; }
  message('');
  try { await work(); } catch (error) { message(error.message); }
}
for (const button of document.querySelectorAll('[data-radio]'))
  button.addEventListener('click', () => action(async () => {
    renderRadio(await api('radio', {action: button.dataset.radio}, 'POST'));
    renderStatus(await api('status'));
  }));
el('station-form').addEventListener('submit', event => {
  event.preventDefault();
  action(async () => {
    renderRadio(await api('radio', {action:'play', station:el('station-number').value}, 'POST'));
    renderStatus(await api('status'));
  });
});
el('smartstart').addEventListener('change', () => action(async () => {
  try { renderRadio(await api('radio', {action:'smartstart', enabled:el('smartstart').checked ? 1 : 0}, 'POST')); }
  catch (error) { renderRadio(await api('radio')); throw error; }
}));
el('audio-form').addEventListener('submit', event => {
  event.preventDefault();
  const values = {normalization:el('normalization').checked ? 1 : 0};
  for (const key of ['volume','balance','normgain','normtarget','normtime']) values[key] = el(key).value;
  action(async () => {
    try { renderSettings(await api('settings', values, 'POST')); message('Настройки сохранены'); }
    catch (error) { renderSettings(await api('settings')); throw error; }
  });
});
el('audio-form').addEventListener('input', () => { settingsDirty = true; });
el('reconnect').addEventListener('click', () => action(async () => {
  await api('reconnect', null, 'POST'); message('Переподключение Wi-Fi запрошено');
}));
const byteLength = text => new TextEncoder().encode(text).length;
const uploadLimit = (name, fallback) => Number.isSafeInteger(capabilities[name]) && capabilities[name] > 0 ? capabilities[name] : fallback;
function updateUploadControls() {
  const blocked = uploadBusy || awaitingRestart;
  let available = false;
  for (const [name, capability] of [['playlist','playlist_upload'],['assets','asset_upload'],['wifi','wifi_upload']]) {
    const supported = capabilities[capability] === true;
    available ||= supported;
    el(name + '-form').hidden = !supported;
    el(name + '-fields').disabled = !ready || blocked || !supported;
    el(name + '-submit').disabled = !ready || blocked || !supported;
  }
  el('uploads').hidden = !available;
  for (const [name, capability] of [['playlist','playlist_upload'],['wifi','wifi_upload']]) {
    el('asset-' + name + '-label').hidden = capabilities[capability] !== true;
    el('asset-' + name).disabled = blocked || capabilities[capability] !== true;
  }
  el('upload-limits').textContent = 'До ' + uploadLimit('upload_max_bytes', 98304) +
    ' байт на запрос, включая оформление формы; до ' + uploadLimit('upload_max_files', 16) +
    ' файлов. Имена файлов .gz — до ' + uploadLimit('upload_name_max_bytes', 22) +
    ' байт. Wi-Fi CSV — до ' + uploadLimit('wifi_file_max_bytes', 799) + ' байт.';
  el('wifi-limits').textContent = 'SSID — до ' + uploadLimit('wifi_ssid_max_bytes', 31) +
    ' байт, пароль — до ' + uploadLimit('wifi_password_max_bytes', 63) +
    ' байт. Пустой пароль — открытая сеть. После сохранения радио перезапустится.';
  const firmware = capabilities.ota === true;
  el('firmware').hidden = !firmware;
  el('firmware-fields').disabled = !ready || blocked || !firmware;
  el('firmware-submit').disabled = !ready || blocked || !firmware;
  el('firmware-limits').textContent = 'Текущий аудиовыход: ' + (capabilities.audio_output || '—') +
    '. Размер app.bin — до ' + uploadLimit('ota_max_bytes', 1769472) +
    ' байт. Образы ESP32-C3, bootloader и полного flash не подходят.';
}
function checkedFile(file, maximum) {
  if (!file || !file.size) throw new Error('Выберите непустой файл');
  if (file.size > maximum) throw new Error('Файл превышает допустимый размер: ' + file.name);
  return file;
}
function uploadForm(kind) {
  const form = new FormData();
  let wifi = false, playlist = false;
  const maximum = uploadLimit('upload_max_bytes', 98304);
  if (kind === 'playlist') {
    form.append('plfile', checkedFile(el('playlist-file').files[0], maximum));
    playlist = true;
  } else if (kind === 'assets') {
    const files = [...el('asset-files').files];
    const csv = el('asset-playlist').files[0], credentials = el('asset-wifi').files[0];
    if (files.length + (csv ? 1 : 0) > uploadLimit('upload_max_files', 16))
      throw new Error('Выбрано слишком много файлов');
    if (new Set(files.map(file => file.name)).size !== files.length)
      throw new Error('Имена выбранных файлов должны различаться');
    for (const file of files) {
      checkedFile(file, maximum);
      if (!/^[A-Za-z0-9._-]+\.gz$/.test(file.name) || file.name.includes('..') ||
          /\.(gz|bak|tmp)\.gz$/.test(file.name) ||
          byteLength(file.name) > uploadLimit('upload_name_max_bytes', 22))
        throw new Error('Недопустимое имя файла .gz: ' + file.name);
      form.append('www', file);
    }
    if (csv) {
      if (capabilities.playlist_upload !== true) throw new Error('Загрузка плейлиста недоступна');
      form.append('data', checkedFile(csv, maximum), 'playlist.csv'); playlist = true;
    }
    if (credentials) {
      if (capabilities.wifi_upload !== true) throw new Error('Сохранение Wi-Fi недоступно');
      form.append('data', checkedFile(credentials, uploadLimit('wifi_file_max_bytes', 799)), 'wifi.csv'); wifi = true;
    }
    if (!files.length && !csv && !credentials) throw new Error('Выберите файлы для сохранения');
  } else {
    const ssid = el('wifi-ssid').value, password = el('wifi-password').value;
    if (!ssid || byteLength(ssid) > uploadLimit('wifi_ssid_max_bytes', 31) ||
        byteLength(password) > uploadLimit('wifi_password_max_bytes', 63) || /[\t\r\n\0]/.test(ssid + password))
      throw new Error('Проверьте имя сети и пароль: превышен размер или есть недопустимые символы');
    form.append('ssid', ssid); form.append('pass', password); wifi = true;
  }
  return {form, wifi, playlist};
}
async function sendUpload(kind, path, capability) {
  if (uploadBusy || awaitingRestart) { message('Дождитесь завершения текущей загрузки и перезапуска'); return; }
  if (!ready || capabilities[capability] !== true) { message('Эта загрузка недоступна'); return; }
  uploadBusy = true; updateUploadControls(); message('Проверка файлов…');
  let saved = false;
  try {
    const upload = uploadForm(kind);
    // Let the browser create the multipart boundary and Content-Type. Check
    // the exact encoded body, including headers, before sending it to CYD.
    const request = new Request(new URL(path, location.href), {method:'POST', body:upload.form, cache:'no-store'});
    const maximum = kind === 'wifi' ? uploadLimit('wifi_body_max_bytes', 4096) : uploadLimit('upload_max_bytes', 98304);
    if ((await request.clone().arrayBuffer()).byteLength > maximum)
      throw new Error('Размер запроса с оформлением формы превышает ' + maximum + ' байт');
    message('Загрузка файлов…');
    const response = await fetch(request);
    if (!response.ok) throw new Error(await response.text() || 'Ошибка загрузки HTTP ' + response.status);
    saved = true;
    if (upload.wifi) {
      el('wifi-password').value = '';
      message('Wi-Fi сохранён. Радио перезапустится; подключитесь к выбранной сети и откройте его страницу снова.');
    } else {
      if (upload.playlist) { renderRadio(await api('radio')); renderStatus(await api('status')); }
      message('Файлы сохранены');
    }
  } catch (error) {
    message(saved ? 'Файлы сохранены. Не удалось обновить состояние: ' + error.message : error.message);
  } finally {
    uploadBusy = false; updateUploadControls();
  }
}
for (const [kind, path, capability] of [['playlist','/upload','playlist_upload'],['assets','/webboard','asset_upload'],['wifi','/','wifi_upload']])
  el(kind + '-form').addEventListener('submit', event => { event.preventDefault(); sendUpload(kind, path, capability); });
function updateFirmwareControls() {
  for (const button of document.querySelectorAll('button'))
    button.disabled = !ready || firmwareBusy || awaitingRestart;
  el('smartstart').disabled = !ready || firmwareBusy || awaitingRestart || !capabilities.smartstart;
  el('reconnect').disabled = !ready || firmwareBusy || awaitingRestart || !capabilities.wifi_reconnect;
  updateUploadControls();
}
async function sendFirmware() {
  if (uploadBusy || awaitingRestart) { message('Дождитесь завершения текущей загрузки и перезапуска'); return; }
  if (!ready || capabilities.ota !== true) { message('Обновление прошивки недоступно'); return; }
  let selected;
  try {
    selected = checkedFile(el('firmware-file').files[0], uploadLimit('ota_max_bytes', 1769472));
    if (!/\.bin$/i.test(selected.name)) throw new Error('Выберите application app.bin для ESP32 CYD');
  } catch (error) { message(error.message); return; }
  firmwareBusy = uploadBusy = true;
  updateFirmwareControls(); message('');
  clearTimeout(retryTimer);
  const previous = socket; socket = null;
  if (previous) previous.close();
  el('connection').textContent = 'Обновление прошивки…';
  el('firmware-progress').hidden = false; el('firmware-progress').value = 0;
  el('firmware-status').textContent = 'Передача файла…';
  try {
    const form = new FormData();
    form.append('updatetarget', 'fw');
    form.append('update', selected, 'app.bin');
    await new Promise((resolve, reject) => {
      const request = new XMLHttpRequest();
      request.open('POST', '/update', true);
      request.timeout = 190000;
      request.upload.onprogress = event => {
        if (!event.lengthComputable || !event.total) return;
        const percent = Math.max(0, Math.min(100, Math.floor(event.loaded * 100 / event.total)));
        el('firmware-progress').value = percent;
        el('firmware-status').textContent = 'Передача файла — ' + percent + '%';
      };
      request.upload.onload = () => { el('firmware-status').textContent = 'Файл передан. Проверка образа…'; };
      request.onload = () => request.status >= 200 && request.status < 300 ? resolve() :
        reject(new Error(request.responseText || 'Обновление отклонено: HTTP ' + request.status));
      request.onerror = () => reject(new Error('Связь прервана. Радио могло начать перезапуск; откройте его страницу перед повторной попыткой.'));
      request.ontimeout = () => reject(new Error('Время ожидания истекло. Проверьте страницу радио перед повторной попыткой.'));
      request.onabort = () => reject(new Error('Передача отменена. Проверьте состояние радио перед повторной попыткой.'));
      // The browser supplies Content-Type and its matching multipart boundary.
      request.send(form);
    });
    awaitingRestart = true;
    el('firmware-status').textContent = 'Образ проверен. Радио перезапускается…';
    el('firmware-progress').value = 100;
    el('firmware-refresh').hidden = false;
    message('После перезапуска откройте страницу радио. Успешный запуск новой прошивки ещё нужно проверить.');
  } catch (error) {
    el('firmware-status').textContent = 'Проверьте результат перед повторной установкой';
    el('firmware-progress').hidden = true;
    el('firmware-refresh').hidden = false;
    message(error.message);
  } finally {
    firmwareBusy = uploadBusy = false; updateFirmwareControls();
    if (!awaitingRestart && capabilities.websocket) connect();
  }
}
el('firmware-form').addEventListener('submit', event => { event.preventDefault(); sendFirmware(); });
function connect() {
  if (firmwareBusy || awaitingRestart) return;
  const current = new WebSocket((location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host + '/ws');
  socket = current;
  current.onopen = () => {
    if (socket !== current) return;
    retryDelay = 1000; lastSeen = Date.now();
    el('connection').textContent = 'Подключено';
  };
  current.onmessage = event => {
    if (socket !== current) return;
    try {
      const data = JSON.parse(event.data);
      lastSeen = Date.now();
      if (data.status) renderStatus(data.status);
      else if (Array.isArray(data.payload)) {
        const values = Object.fromEntries(data.payload.map(item => [item.id, item.value]));
        renderStatus({station:values.nameset,title:values.meta,format:values.fmt,bitrate:values.bitrate,
          connecting:values.upst === 'connecting',audio:values.playerwrap === 'playing'});
      }
    } catch (error) { message('Не удалось прочитать состояние радио'); }
  };
  current.onerror = () => current.close();
  current.onclose = () => {
    if (socket !== current) return;
    socket = null; el('connection').textContent = 'Связь прервана. Повторное подключение…';
    clearTimeout(retryTimer); retryTimer = setTimeout(connect, retryDelay);
    retryDelay = Math.min(retryDelay * 2, 10000);
  };
}
setInterval(() => {
  if (!ready || uploadBusy || awaitingRestart) return;
  if (socket && socket.readyState === WebSocket.OPEN && Date.now() - lastSeen > 6000) socket.close();
  if (!socket || socket.readyState !== WebSocket.OPEN)
    action(async () => { renderStatus(await api('status')); renderRadio(await api('radio')); });
}, 3000);
(async () => {
  try {
    // Sequential startup keeps two browser tabs within the socket budget.
    const caps = await api('capabilities');
    capabilities = caps;
    const status = await api('status');
    const radio = await api('radio');
    const settings = await api('settings');
    renderStatus(status); renderRadio(radio); renderSettings(settings);
    el('backend').textContent = 'Аудиовыход: ' + caps.audio_output;
    for (const button of document.querySelectorAll('button')) button.disabled = false;
    el('smartstart').disabled = !caps.smartstart;
    el('reconnect').disabled = !caps.wifi_reconnect;
    ready = true;
    updateUploadControls();
    if (caps.websocket) connect();
    else el('connection').textContent = 'Подключено';
  } catch (error) { message(error.message); el('connection').textContent = 'Сервис недоступен. Обновите страницу.'; }
})();
// NATIVE_UI_END
</script></html>)HTML";
}

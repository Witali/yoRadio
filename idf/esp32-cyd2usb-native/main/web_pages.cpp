#include "web_pages.h"

extern "C" const char *web_native_page(void) {
    return R"HTML(<!doctype html>
<html lang="ru"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ёRadio · CYD</title>
<style>
:root{color-scheme:dark;font-family:system-ui,sans-serif;background:#131719;color:#eef1ed}
body{max-width:48rem;margin:2rem auto;padding:0 1rem}h1{font-size:1.6rem}h2{font-size:1.15rem}
section{background:#22292c;border-radius:1rem;padding:1.2rem;margin:1rem 0}
button,input{font:inherit;border:1px solid #65716e;border-radius:.4rem;padding:.5rem;background:#182022;color:inherit}
button{cursor:pointer;background:#d6c86d;color:#161b19}button:disabled{opacity:.45;cursor:wait}
label{display:inline-flex;align-items:center;gap:.5rem;margin:.4rem .6rem .4rem 0}input[type=number]{width:5rem}
.row{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center}p{overflow-wrap:anywhere}small,a{color:#c4d2cc}
#message{min-height:1.5rem;color:#e7d877}#title{font-size:1.2rem}#details{font-variant-numeric:tabular-nums}
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
<small id="backend"></small>
<script>
// NATIVE_UI_BEGIN
'use strict';
const el = id => document.getElementById(id);
let socket, retryTimer, retryDelay = 1000, lastSeen = 0, ready = false, settingsDirty = false;
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
function connect() {
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
  if (!ready) return;
  if (socket && socket.readyState === WebSocket.OPEN && Date.now() - lastSeen > 6000) socket.close();
  if (!socket || socket.readyState !== WebSocket.OPEN)
    action(async () => { renderStatus(await api('status')); renderRadio(await api('radio')); });
}, 3000);
(async () => {
  try {
    // Sequential startup keeps two browser tabs within the socket budget.
    const caps = await api('capabilities');
    const status = await api('status');
    const radio = await api('radio');
    const settings = await api('settings');
    renderStatus(status); renderRadio(radio); renderSettings(settings);
    el('backend').textContent = 'Аудиовыход: ' + caps.audio_output;
    for (const button of document.querySelectorAll('button')) button.disabled = false;
    el('smartstart').disabled = !caps.smartstart;
    el('reconnect').disabled = !caps.wifi_reconnect;
    ready = true;
    if (caps.websocket) connect();
    else el('connection').textContent = 'Подключено';
  } catch (error) { message(error.message); el('connection').textContent = 'Сервис недоступен. Обновите страницу.'; }
})();
// NATIVE_UI_END
</script></html>)HTML";
}

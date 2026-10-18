/* BEGIN NATIVE WIFI EDITOR: tools/web/native_wifi_editor.js */
let nativeWiFiState = null;

function nativeWiFiMode() {
  // This shared asset also serves the separately maintained ESP8266 native
  // firmware. Its existing protocol remains an explicit compatibility branch.
  if (typeof yoVersion === 'string' && yoVersion === 'esp8266-native' &&
      typeof nativeWiFiApi === 'undefined') return false;
  return (typeof nativeFirmwareOnly !== 'undefined' && nativeFirmwareOnly === true) ||
    typeof nativeWiFiApi !== 'undefined';
}
function nativeWiFiStatus(text, ready) {
  let status = getId('native-wifi-status');
  if (!status) {
    status = document.createElement('p');
    status.id = 'native-wifi-status';
    const group = getId('group_wifi');
    if (group) group.appendChild(status);
  }
  status.textContent = text;
  const save = document.querySelector('[data-command="wifiupload"]');
  if (save) {
    save.setAttribute('aria-disabled', ready ? 'false' : 'true');
    save.style.pointerEvents = ready ? '' : 'none';
    save.style.opacity = ready ? '' : '.5';
  }
}
function nativeWiFiMetadata(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) ||
      Object.keys(value).some(key => !['revision', 'profiles'].includes(key)) ||
      typeof value.revision !== 'string' || !/^[0-9a-f]{16}-[0-9a-f]{16}$/.test(value.revision) ||
      !Array.isArray(value.profiles) || value.profiles.length > 5) return false;
  const ids = new Set();
  return value.profiles.every(row => {
    if (!row || typeof row !== 'object' || Array.isArray(row) ||
        Object.keys(row).some(key => !['id', 'ssid', 'ssid_utf8'].includes(key)) ||
        typeof row.id !== 'string' || !/^r[1-5]$/.test(row.id) || ids.has(row.id) ||
        typeof row.ssid !== 'string' || !row.ssid || typeof row.ssid_utf8 !== 'boolean') return false;
    ids.add(row.id);
    return true;
  });
}
function nativeWiFiRows() { return Array.from(document.getElementsByClassName('credential')); }
function nativeWiFiInstall(value) {
  if (!nativeWiFiMetadata(value)) throw new Error('Unsupported Wi-Fi metadata');
  nativeWiFiState = value;
  nativeWiFiRows().forEach((item, index) => {
    const inputs = item.getElementsByTagName('input');
    const previous = value.profiles[index];
    if (inputs.length < 2) return;
    inputs[0].value = previous ? previous.ssid : '';
    inputs[0].maxLength = 31;
    inputs[1].value = '';
    inputs[1].type = 'password';
    inputs[1].maxLength = 63;
    inputs[1].removeAttribute('data-pass');
    inputs[1].placeholder = previous ? 'Saved password stays on radio' : 'New password';
    let action = getId('native-wifi-action-' + index);
    if (!action) {
      action = document.createElement('select');
      action.id = 'native-wifi-action-' + index;
      action.setAttribute('aria-label', 'Password action');
      inputs[1].parentNode.appendChild(action);
      inputs[1].addEventListener('input', () => {
        if (inputs[1].value) action.value = 'set';
      });
      action.addEventListener('change', () => {
        if (action.value !== 'set') inputs[1].value = '';
      });
    }
    action.replaceChildren();
    const choices = previous ? [['keep', 'Keep saved password'], ['set', 'Set new password'], ['open', 'Open network (no password)']] :
      [['set', 'Set new password'], ['open', 'Open network (no password)']];
    choices.forEach(([key, label]) => {
      const option = document.createElement('option'); option.value = key; option.textContent = label; action.appendChild(option);
    });
    action.value = previous ? 'keep' : 'set';
    inputs[0].title = previous && !previous.ssid_utf8 ? 'Legacy encoding: leave this name unchanged to preserve its original bytes.' : '';
  });
  const exportButton = document.querySelector('[data-command="wifiexport"]');
  if (exportButton) exportButton.textContent = 'Export SSIDs';
  nativeWiFiStatus('Saved passwords stay on the radio. Export contains network names only.', true);
}
function getNativeWiFi() {
  nativeWiFiState = null;
  nativeWiFiStatus('Loading Wi-Fi network names...', false);
  if (typeof nativeWiFiApi !== 'string' || nativeWiFiApi !== '/api/native/wifi') {
    nativeWiFiStatus('This firmware does not support private Wi-Fi editing. Update the firmware first.', false);
    return Promise.resolve();
  }
  return fetch(nativeWiFiApi, {cache: 'no-store', credentials: 'same-origin'})
    .then(response => { if (!response.ok) throw new Error('Wi-Fi metadata unavailable'); return response.json(); })
    .then(value => nativeWiFiInstall(value))
    .catch(() => {
      nativeWiFiState = null;
      nativeWiFiStatus('Wi-Fi metadata unavailable. Reload before saving; saved passwords were not downloaded.', false);
    });
}
function nativeWiFiField(value, maximum, allowEmpty) {
  return (allowEmpty || value !== '') && !/[\0\t\r\n]/.test(value) && new TextEncoder().encode(value).length <= maximum;
}
function submitNativeWiFi() {
  if (!nativeWiFiState) {
    nativeWiFiStatus('Load Wi-Fi metadata successfully before saving.', false);
    return Promise.resolve();
  }
  const profiles = [];
  let hasEdgeWhitespace = false;
  for (const [index, item] of nativeWiFiRows().entries()) {
    const inputs = item.getElementsByTagName('input');
    if (inputs.length < 2 || inputs[0].value === '') continue;
    const previous = nativeWiFiState.profiles[index];
    const ssid = inputs[0].value;
    if (ssid !== ssid.trim()) hasEdgeWhitespace = true;
    const row = previous ? {id: previous.id} : {};
    if (!previous || ssid !== previous.ssid) {
      if (!nativeWiFiField(ssid, 31, false)) { window.alert('Wi-Fi names must contain 1–31 UTF-8 bytes without tabs or newlines.'); return Promise.resolve(); }
      row.ssid = ssid;
    }
    const action = getId('native-wifi-action-' + index);
    const selected = action ? action.value : '';
    if (selected === 'keep' && previous && inputs[1].value === '') row.password_action = 'keep';
    else if (selected === 'open' && inputs[1].value === '') { row.password_action = 'set'; row.password = ''; }
    else if (selected === 'set' && nativeWiFiField(inputs[1].value, 63, false)) {
      row.password_action = 'set'; row.password = inputs[1].value;
    } else {
      window.alert('Choose Keep, enter a new password, or explicitly select Open network.'); return Promise.resolve();
    }
    profiles.push(row);
  }
  if (profiles.length > 5) { window.alert('At most five Wi-Fi networks can be saved.'); return Promise.resolve(); }
  if (hasEdgeWhitespace && !window.confirm(SSID_WARNING_TEXT)) return Promise.resolve();
  if (!profiles.length && !window.confirm('Delete all saved Wi-Fi networks? After reboot, the radio will start its access point.')) return Promise.resolve();
  const payload = JSON.stringify({revision: nativeWiFiState.revision, profiles});
  if (new TextEncoder().encode(payload).length > 4096) { window.alert('Wi-Fi update exceeds the request limit.'); return Promise.resolve(); }
  nativeWiFiStatus('Saving Wi-Fi settings...', false);
  return fetch(nativeWiFiApi, {method: 'POST', credentials: 'same-origin', cache: 'no-store',
    headers: {'Content-Type': 'application/json'}, body: payload})
    .then(response => { if (!response.ok) throw new Error('Wi-Fi save not confirmed'); return response.json(); })
    .then(result => {
      if (!result || result.saved !== true || result.rebooting !== true) throw new Error('Wi-Fi save not confirmed');
      nativeWiFiRows().forEach(item => { const inputs = item.getElementsByTagName('input'); if (inputs[1]) inputs[1].value = ''; });
      nativeWiFiState = null;
      rebootSystem('Wi-Fi settings saved. Rebooting...');
    })
    .catch(() => {
      nativeWiFiState = null;
      nativeWiFiStatus('Wi-Fi save could not be confirmed. Settings may already be saved; reload after the radio restarts before trying again.', false);
    });
}
function exportNativeWiFi() {
  if (!nativeWiFiState) { window.alert('Load Wi-Fi metadata before exporting network names.'); return; }
  const data = {format: 'yoradio-ssid-list-v1', profiles: nativeWiFiState.profiles.map(row => ({ssid: row.ssid, ssid_utf8: row.ssid_utf8}))};
  const url = URL.createObjectURL(new Blob([JSON.stringify(data, null, 2)], {type: 'application/json'}));
  const link = document.createElement('a'); link.href = url; link.download = 'wifi-network-names.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}
/* END NATIVE WIFI EDITOR */

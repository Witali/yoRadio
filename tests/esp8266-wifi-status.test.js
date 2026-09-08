const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
test('Wi-Fi connection captures initial RSSI and logs numeric disconnect reason', () => {
  const source = fs.readFileSync(path.join(__dirname,
    '../esp8266/rtos-sdk-native/main/network_service.c'),'utf8');
  const gotIp = source.slice(source.indexOf('id == IP_EVENT_STA_GOT_IP'),
    source.indexOf('static void supervisor_task'));
  assert.match(gotIp, /esp_wifi_sta_get_ap_info\(&access_point\)/);
  assert.match(gotIp, /native_state_set_wifi_rssi\(access_point.rssi\)/);
  assert.match(source, /Wi-Fi disconnected: reason=%u/);
});

test('a lost client link clears DHCP state and arms recovery only once', () => {
  const c = fs.readFileSync(path.join(__dirname,
    '../esp8266/rtos-sdk-native/main/network_service.c'),'utf8');
  const lost = c.slice(c.indexOf('id == WIFI_EVENT_STA_DISCONNECTED'),
    c.indexOf('id == IP_EVENT_STA_GOT_IP'));
  assert.match(lost, /if \(s_connected\) \{\s*s_disconnected_since = xTaskGetTickCount\(\);\s*s_recovery_after_dhcp = true;/);
  assert.match(lost, /xEventGroupClearBits\(s_events, WIFI_CONNECTED_BIT\)/);
  assert.match(lost, /native_state_set_network\(NETWORK_STARTING\)/);
  assert.match(lost, /native_state_set_ip\("0.0.0.0"\)/);
  assert.match(c, /s_connected = true;\s*s_recovery_after_dhcp = false;/);
});

test('post-DHCP recovery uses the existing app poll and bounded retry cadence', () => {
  const c = fs.readFileSync(path.join(__dirname,
    '../esp8266/rtos-sdk-native/main/network_service.c'),'utf8');
  const poll = c.slice(c.indexOf('void network_service_poll'),
    c.indexOf('esp_err_t network_service_start'));
  assert.match(poll, /now - s_disconnected_since >= pdMS_TO_TICKS\(WIFI_CONNECT_TIMEOUT_MS\)/);
  assert.match(poll, /start_access_point\(\)/);
  assert.match(poll, /next_recovery_retry = now \+ pdMS_TO_TICKS\(5000U\)/);
  assert.match(poll, /s_connected && s_access_point[\s\S]*tcpip_adapter_get_ip_info/);
  assert.doesNotMatch(poll, /xTaskCreate|xTimerCreate|malloc/);
});

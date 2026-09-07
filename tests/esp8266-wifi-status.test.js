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

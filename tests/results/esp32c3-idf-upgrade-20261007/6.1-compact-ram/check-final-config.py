import hashlib
import json
from pathlib import Path

expected = {
    **{'CONFIG_YORADIO_AAC_'+k:'y' for k in ('PLUS','COMPACT_SBR','HIGH_HISTORY',
        'HIGH_HISTORY_PC19','SMOOTHING_HISTORY','LOW_WORKSPACE','ASYMMETRIC_OWNER','LATE_SBR')},
    'CONFIG_YORADIO_COMPACT_SERVICE_STACKS':'y',
    'CONFIG_ESP_WIFI_STATIC_RX_BUFFER_NUM':'6',
    'CONFIG_ESP_WIFI_DYNAMIC_RX_BUFFER_NUM':'16',
    'CONFIG_ESP_WIFI_DYNAMIC_TX_BUFFER_NUM':'16',
    'CONFIG_MBEDTLS_SSL_IN_CONTENT_LEN':'16384',
}
rows=[]
for variant in ('production','profile','deep-sleep','rtc32k'):
    path=Path('firmware/development/esp32c3-idf-6.1-compact-ram-'+variant)/'sdkconfig'
    data=path.read_bytes()
    config=dict(line.split('=',1) for line in data.decode().splitlines() if line.startswith('CONFIG_') and '=' in line)
    assert all(config.get(key)==value for key,value in expected.items()),variant
    for key in ('CONFIG_YORADIO_QEMU','CONFIG_SPI_FLASH_AUTO_SUSPEND',
                'CONFIG_HEAP_PLACE_FUNCTION_INTO_FLASH'):
        assert config.get(key)!='y',(variant,key)
    assert (config.get('CONFIG_YORADIO_DEEP_SLEEP_CLOCK')=='y')==(variant in ('deep-sleep','rtc32k'))
    rows.append(dict(variant=variant,sdkconfig_sha256=hashlib.sha256(data).hexdigest(),features=expected,passed=True))
Path('.build/idf-upgrade/default-config-6.1-compact-ram.json').write_text(json.dumps(rows,indent=2)+'\n')
print('All four saved compact RAM configurations match the intended feature chain')

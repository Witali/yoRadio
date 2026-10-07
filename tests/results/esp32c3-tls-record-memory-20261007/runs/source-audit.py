import hashlib, json
from pathlib import Path
root=Path('C:/Work/yoRadio/.idf/v6.1')
names=['components/mbedtls/port/dynamic/esp_mbedtls_dynamic_impl.c',
       'components/mbedtls/port/dynamic/esp_ssl_tls.c',
       'components/esp_http_client/esp_http_client.c',
       'components/tcp_transport/transport_ssl.c',
       'components/mbedtls/esp_crt_bundle/gen_crt_bundle.py']
result=dict(idf='v6.1',files={name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names},
    findings=[
        'Dynamic RX allocates based on each peeked record length and may release the previous buffer before the allocation.',
        'The dynamic RX allocator returns MBEDTLS_ERR_SSL_ALLOC_FAILED on failure; no record-size cap was changed for this experiment.',
        'esp_http_client_read returns already accumulated bytes (ridx) after some fatal transport errors; a later application read can reach TLS again.',
        'The application breaks on a negative non-EAGAIN read; it cannot see an error hidden by a positive partial return.',
        'The alternate-size run logged a second 46622-byte request after a failed 16749-byte request. These sources suggest an error-retry/state issue; its exact cause has not been reproduced independently.',
        'cpu_profiler failed-allocation free/largest metrics use the same capabilities mask as the failed request.'
    ])
Path('.build/c3-tls-records-20261007/source-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('SDK source hashes and scoped observations saved')

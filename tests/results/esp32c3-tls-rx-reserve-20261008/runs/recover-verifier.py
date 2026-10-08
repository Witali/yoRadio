import hashlib
from pathlib import Path
p=Path('tools/esp32c3_tests/verify_adaptive_input_link.py')
s=p.read_text()
s=s.replace("    parser.add_argument('--tls-rx-object', type=Path,\n                        help='Generated SDK RX object, required for RX-only reserve')\n",'')
s=s.replace('found, seen, pending = set(), set(), [entry]','found, pending = set(), [entry]')
s=s.replace("    calls = reachable('__wrap_esp_mbedtls_mem_calloc')\n    rx_routes = None\n    rx_object_sha256 = None\n", "    seen = set()\n    calls = reachable('__wrap_esp_mbedtls_mem_calloc')\n")
start=s.index('            assert args.tls_rx_object')
end=s.index('        else:\n            assert',start)
s=s[:start]+'''            for name in ('esp_mbedtls_dynamic_set_rx_buf_static',
                         'esp_mbedtls_reset_add_rx_buffer',
                         'esp_mbedtls_add_rx_buffer', 'esp_mbedtls_free_rx_buffer'):
                assert '<yoradio_tls_rx_calloc>' in functions[name], name + ' misses RX hook'
'''+s[end:]
s=s.replace('        rx_routes=rx_routes, rx_object_sha256=rx_object_sha256,\n','')
expected='34d937597cf6ac5f259cf60a3cc0d12552952634f32f2e8fcc62349665b16e9b'
for data in (s.encode(),s.replace('\n','\r\n').encode()):
    if hashlib.sha256(data).hexdigest()==expected:
        out=Path('.build/c3-reserve-soak-20261008/historical')/expected/p.name
        out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
        print('Recovered exact historical verifier',expected)
        break
else: raise AssertionError('Historical verifier hash mismatch')

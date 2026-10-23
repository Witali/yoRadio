"""Create a new qualifier from the prior immutable matrix, without editing it."""
from pathlib import Path

root = Path.cwd()
source = (root / '.build/qualify-output-telemetry-sdk.py').read_text()
def replace(before, after):
    global source
    assert source.count(before) == 1, before
    source = source.replace(before, after)
replace("OUT=ROOT/'tests/results/cyd-output-telemetry-20261020'", "OUT=ROOT/'tests/results/cyd-input-reclaim-20261020'")
replace("assert head.startswith('0f2a37c89'),head", "assert head==json.loads((ROOT/'.build/input-reclaim-production-source.json').read_text())['source_commit'],head")
replace("for custom in (False,True):\n    for backend in ('pdm','continuous','legacy'):",
        "for profile in json.loads((ROOT/'.build/input-reclaim-production-profiles.json').read_text()):\n    for backend in (profile['backend'],):\n        custom,enabled=profile['custom_flac'],profile['enabled']")
replace("variant='esp32-cyd2usb-native-output-telemetry-'+suffix", "variant=profile['variant']\n        suffix=profile['name']")
replace("previous=json.loads((ROOT/'firmware/development'/('esp32-cyd2usb-native-network-settings-'+suffix)/'sdkconfig.json').read_text())",
        "previous=json.loads((Path(profile['baseline'])/'sdkconfig.json').read_text())")
replace("assert changes=={'YORADIO_HTTP_REQUEST_BUFFER_RELEASE':{'previous':None,'current':True}},(variant,changes)",
        "assert changes=={'YORADIO_TLS_INPUT_RECLAIM':{'previous':None,'current':enabled}},(variant,changes)\n        assert bool(config.get('YORADIO_TLS_INPUT_RECLAIM'))==enabled")
replace("assert 'native_output_metrics_snapshot' in symbols and 'native_output_metrics_end_write' in symbols",
        """assert 'native_output_metrics_snapshot' in symbols and 'native_output_metrics_end_write' in symbols
        assert ('__wrap_esp_mbedtls_mem_calloc' in symbols)==enabled
        assert ('native_input_reclaim_bind' in symbols)==enabled
        for required in ('mbedtls_calloc_func','mbedtls_free_func','esp_mbedtls_mem_calloc','esp_mbedtls_mem_free'):
            assert required in symbols,(variant,required)
        pointer_proof={}
        phoff=struct.unpack_from('<I',raw,28)[0]
        phsize,phcount=struct.unpack_from('<HH',raw,42)
        segments=[struct.unpack_from('<8I',raw,phoff+i*phsize) for i in range(phcount)]
        for pointer,expected in [('mbedtls_calloc_func','__wrap_esp_mbedtls_mem_calloc' if enabled else 'esp_mbedtls_mem_calloc'),('mbedtls_free_func','esp_mbedtls_mem_free')]:
            address=symbols[pointer]['address']
            assert symbols[pointer]['bytes']==4
            segment=next(row for row in segments if row[0]==1 and row[2]<=address<row[2]+row[4])
            value=struct.unpack_from('<I',raw,segment[1]+address-segment[2])[0]
            assert value==symbols[expected]['address'],(variant,pointer,expected)
            pointer_proof[pointer]={'address':address,'initial_value':value,'expected_symbol':expected}
""")
replace("compile_rows=json.loads((build/'compile_commands.json').read_text())",
        """compile_rows=json.loads((build/'compile_commands.json').read_text())
        reclaim_rows=[row for row in compile_rows if Path(row['file']).name=='native_input_reclaim.c']
        assert len(reclaim_rows)==int(enabled)
        if enabled:
            assert Path(reclaim_rows[0]['file']).resolve()==(ROOT/'idf/esp32-cyd2usb-native/main/native_input_reclaim.c').resolve()
            assert 'xtensa-esp32-elf-gcc' in reclaim_rows[0]['command']
        ninja_text=(build/'build.ninja').read_text()
        for flag in ('--wrap=esp_mbedtls_mem_calloc','--undefined=__wrap_esp_mbedtls_mem_calloc'):
            assert (flag in ninja_text)==enabled,(variant,flag)
""")
replace("app_bytes=len(image),ota_slot_bytes=limit,ota_free_bytes=limit-len(image),",
        "app_bytes=len(image),ota_slot_bytes=limit,ota_free_bytes=limit-len(image),reclaim_enabled=enabled,\n            sdk_allocator_pointer_proof=pointer_proof,reclaim_compile_rows=reclaim_rows,")
replace("scope='Six complete GCC Xtensa application exports, image/checksum/OTA/config/codec symbols and final integrated PDM callback/helper IRAM plus state/lock DRAM. No physical IRQ latency, DMA behavior, live heap savings, task runtime or audio-quality claim.'",
        "scope='Seven complete GCC Xtensa application exports: six opt-in vendor/custom FLAC times PDM/continuous/legacy, and disabled PDM control. Actual SDK calloc/free function pointer initializer proof, canonical module/link flags, image/checksum/OTA/config/codec symbols, PDM IRAM/counters DRAM and unchanged task bindings. No physical memory, IRQ/DMA, timing or audio-quality claim.'")
(root / '.build/qualify-input-reclaim-sdk.py').write_text(source)
print('Created new seven-image qualifier')

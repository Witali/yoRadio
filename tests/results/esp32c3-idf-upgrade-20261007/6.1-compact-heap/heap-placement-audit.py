"""Record the reviewed C3 ISR scope and the compiled flash-heap configuration."""
import hashlib
import json
from pathlib import Path

project=Path('idf/esp32c3-oled-native')
config_path=project/'build-idf-6.1-compact-heap-profile/sdkconfig'
config=dict(line.split('=',1) for line in config_path.read_text().splitlines()
            if line.startswith('CONFIG_') and '=' in line)
required={'CONFIG_HEAP_PLACE_FUNCTION_INTO_FLASH':'y'}
disabled=('CONFIG_SPI_FLASH_AUTO_SUSPEND','CONFIG_SPI_MASTER_ISR_IN_IRAM',
          'CONFIG_I2C_ISR_IRAM_SAFE','CONFIG_I2S_ISR_IRAM_SAFE',
          'CONFIG_YORADIO_DIRECT_DMA_PCM')
assert all(config.get(k)==v for k,v in required.items())
assert all(config.get(k)!='y' for k in disabled)
paths=[project/'main/app_main.c',project/'main/encoder_input.c',
       project/'main/native_audio_output_dma.c',project/'main/board_config.h',
       Path('C:/Work/yoRadio/.idf/v6.1/components/heap/Kconfig'),
       Path('C:/Work/yoRadio/.idf/v6.1/docs/en/api-guides/performance/ram-usage.rst')]
result=dict(sdkconfig_sha256=hashlib.sha256(config_path.read_bytes()).hexdigest(),
    required=required,disabled=list(disabled),
    reviewed_scope=[
        'GPIO ISR service uses flags 0; encoder handlers sample GPIO/ticks and submit to an existing queue without heap calls.',
        'I2C OLED and I2S PDM cache-independent ISR options are disabled.',
        'Direct-DMA callback experiment is not linked; the optional callback only counts overruns.',
        'No application SPI-master or SPI-slave client is initialized in this board source.',
        'SPI flash driver placement and Auto Suspend remain unchanged; only supported heap placement is selected.',
        'The SDK RAM guide permits flash heap routines when SPI_MASTER_ISR_IN_IRAM is off and cache-disabled ISRs do not call heap APIs.'
    ],
    source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
    limitation='Manual source/configuration review for this board; physical OTA and load qualification are recorded separately.')
Path('.build/idf-upgrade/heap-placement-6.1-compact-heap.json').write_text(json.dumps(result,indent=2)+'\n')
print('Recorded C3 heap-placement audit and source fingerprints')

"""Generate the CYD synchronous DAC fix from the pinned SDK source."""
import argparse
import hashlib
from pathlib import Path


SOURCE_SHA = '663e602b1f4c7a79d089a3c6eec85035a4987f3afe3d91d49f7efb892e40e616'
WRITE = b'esp_err_t dac_continuous_write(dac_continuous_handle_t handle,'
START = b'dac_dma_periph_dma_trans_start((uint32_t)(STAILQ_FIRST(&handle->head)));'
RUNNING = b'atomic_store(&handle->is_running, true);'
SPIN = b'        while (atomic_load(&handle->is_running)) {}'
WAIT = b'''        TimeOut_t stop_timeout;
        TickType_t remaining = timeout_tick;
        vTaskSetTimeOutState(&stop_timeout);
        while (atomic_load(&handle->is_running)) {
            if (!remaining || xTaskCheckForTimeOut(&stop_timeout, &remaining)) {
                ret = ESP_ERR_TIMEOUT;
                goto err;
            }
            vTaskDelay(1);
        }'''


def overlay(raw):
    source = raw.replace(b'\r\n', b'\n')
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA or source.count(WRITE) != 1:
        raise ValueError('DAC overlay requires the pinned ESP-IDF 6.0.2 source')
    prefix, write = source.split(WRITE, 1)
    if write.count(SPIN) != 1:
        raise ValueError('Expected one synchronous DAC stop wait')
    write = write.replace(SPIN, WAIT, 1)
    prefix = prefix.replace(b'#include "freertos/semphr.h"\n',
                            b'#include "freertos/semphr.h"\n#include "freertos/task.h"\n', 1)
    for indent in (b'        ', b'            '):
        before = indent + START + b'\n' + indent + RUNNING
        after = indent + RUNNING + b'\n' + indent + START
        if write.count(b'\n' + before) != 1:
            raise ValueError('Expected one synchronous DAC start at each indentation')
        write = write.replace(b'\n' + before, b'\n' + after, 1)
    return prefix + WRITE + write


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    generated = overlay(args.input.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(generated)


if __name__ == '__main__':
    main()

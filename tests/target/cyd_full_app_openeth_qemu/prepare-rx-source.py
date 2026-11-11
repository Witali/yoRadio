"""Generate the diagnostic-only OpenETH RX overlay for the pinned SDK source."""
import argparse
import hashlib
from pathlib import Path


SOURCE_SHA = 'b0526b76120abffe37ee8bd87b9e204880da18a5c02383e5d39b8e001bbcbb7d'
BEFORE = b'''    uint32_t length = 0;
    while (1) {
        if (ulTaskNotifyTake(pdFALSE, portMAX_DELAY)) {
            while (true) {
                length = ETH_MAX_PACKET_SIZE;
                buffer = malloc(length);
                if (!buffer) {
                    ESP_LOGE(TAG, "no mem for receive buffer");
                } else if (emac_opencores_receive(&emac->parent, buffer, &length) == ESP_OK) {
'''
AFTER = b'''    uint32_t length = 0;
    bool waiting_for_memory = false;
    while (1) {
        if (ulTaskNotifyTake(pdFALSE, portMAX_DELAY)) {
            while (true) {
                // The MAC owns an empty descriptor. Only allocate for a frame.
                const openeth_rx_desc_t desc = *(const volatile openeth_rx_desc_t *)openeth_rx_desc(emac->cur_rx_desc);
                if (desc.e) {
                    break;
                }
                length = ETH_MAX_PACKET_SIZE;
                buffer = malloc(length);
                if (!buffer) {
                    if (!waiting_for_memory) {
                        ESP_LOGW(TAG, "CYD_OPENETH_RX_WAIT request=%" PRIu32 " heap=%u largest=%u dma=%u",
                                 length, (unsigned)heap_caps_get_free_size(MALLOC_CAP_8BIT),
                                 (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_8BIT),
                                 (unsigned)heap_caps_get_largest_free_block(MALLOC_CAP_DMA));
                        waiting_for_memory = true;
                    }
                    // Retain the descriptor and let the scheduler run before retrying.
                    vTaskDelay(1);
                    continue;
                }
                if (waiting_for_memory) {
                    ESP_LOGI(TAG, "CYD_OPENETH_RX_RECOVERED");
                    waiting_for_memory = false;
                }
                if (emac_opencores_receive(&emac->parent, buffer, &length) == ESP_OK) {
'''


def overlay(raw):
    source = raw.replace(b'\r\n', b'\n')
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA or source.count(BEFORE) != 1:
        raise ValueError('OpenETH RX overlay requires the pinned ESP-IDF 6.0.2 source')
    return source.replace(b'#include "esp_intr_alloc.h"\n',
                          b'#include "esp_intr_alloc.h"\n#include "esp_heap_caps.h"\n', 1).replace(BEFORE, AFTER, 1)


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

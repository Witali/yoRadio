/*
 * SPDX-FileCopyrightText: 2019-2024 Espressif Systems (Shanghai) CO LTD
 *
 * SPDX-License-Identifier: Apache-2.0
 */

/* Exact pre-fix diagnostic RX task/receive excerpts.
 * Source SHA256: 77827f4605a712e9057484fe5999c8a3405e3e617f3f45e52ca8933d96be6cca.
 * The runner proves these excerpts match the pinned prior overlay. */

static void emac_opencores_rx_task(void *arg)
{
    emac_opencores_t *emac = (emac_opencores_t *)arg;
    uint8_t *buffer = NULL;
    uint32_t length = 0;
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
                    // pass the buffer to the upper layer
                    if (length) {
                        emac->eth->stack_input(emac->eth, buffer, length);
                    } else {
                        free(buffer);
                    }
                } else {
                    free(buffer);
                    break;
                }
            }
        }
    }
    vTaskDelete(NULL);
}

static esp_err_t emac_opencores_receive(esp_eth_mac_t *mac, uint8_t *buf, uint32_t *length)
{
    esp_err_t ret = ESP_OK;
    emac_opencores_t *emac = __containerof(mac, emac_opencores_t, parent);

    openeth_rx_desc_t *desc_ptr = openeth_rx_desc(emac->cur_rx_desc);
    openeth_rx_desc_t desc_val = *desc_ptr;
    ESP_LOGV(TAG, "%s: desc %d (%p) e=%" PRIu16 " len=%" PRIu16" wr=%" PRIu16, __func__, emac->cur_rx_desc, desc_ptr, desc_val.e, desc_val.len, desc_val.wr);
    if (desc_val.e) {
        ret = ESP_ERR_INVALID_STATE;
        goto err;
    }
    size_t rx_length = desc_val.len;
    ESP_GOTO_ON_FALSE(*length >= rx_length, ESP_ERR_INVALID_SIZE, err, TAG, "RX length too large");
    *length = rx_length;
    memcpy(buf, desc_val.rxpnt, *length);
    desc_val.e = 1;
    *desc_ptr = desc_val;

    emac->cur_rx_desc = (emac->cur_rx_desc + 1) % RX_BUF_COUNT;
    return ESP_OK;
err:
    return ret;
}

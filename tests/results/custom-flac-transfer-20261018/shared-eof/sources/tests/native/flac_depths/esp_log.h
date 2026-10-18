#pragma once
extern unsigned flac_test_errors;
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGE(...) (++flac_test_errors)
#define ESP_LOGW(...) (++flac_test_errors)

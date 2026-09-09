#pragma once
void test_codec_enter_critical(void);
void test_codec_exit_critical(void);
#define taskENTER_CRITICAL() test_codec_enter_critical()
#define taskEXIT_CRITICAL() test_codec_exit_critical()

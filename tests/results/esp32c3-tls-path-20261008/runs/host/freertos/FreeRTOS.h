#pragma once
typedef int portMUX_TYPE;
#define portMUX_INITIALIZER_UNLOCKED 0
void test_enter(void *); void test_exit(void *);
#define portENTER_CRITICAL test_enter
#define portEXIT_CRITICAL test_exit

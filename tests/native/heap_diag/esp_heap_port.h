#pragma once
void test_heap_lock(void);
void test_heap_unlock(void);
#define _heap_caps_lock(n) test_heap_lock()
#define _heap_caps_unlock(n) test_heap_unlock()

/* Race-free environment probe, independent of all firmware/harness code. */
#include <pthread.h>
#include <stdio.h>
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static unsigned value;
static void *worker(void *unused) {
    (void)unused;
    pthread_mutex_lock(&lock); ++value; pthread_mutex_unlock(&lock); return NULL;
}
int main(void) {
    pthread_t thread;
    if (pthread_create(&thread, NULL, worker, NULL) || pthread_join(thread, NULL)) return 2;
    if (value != 1) return 3;
    puts("TSAN_CONTROL_OK"); return 0;
}

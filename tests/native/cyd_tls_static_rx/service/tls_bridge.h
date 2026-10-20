#pragma once
#include "tls_types.h"
void tls_check(bool condition,const char *name);
int tls_open(mbedtls_ssl_context *ssl,mbedtls_ssl_config *conf);
void tls_close(mbedtls_ssl_context *ssl);
bool tls_is_ordinary(void *pointer);
void tls_independent_client(void);
void tls_assert_drained(void);
unsigned tls_loans(void);
unsigned tls_loan_count(void);
unsigned tls_setups(void);
unsigned tls_attaches(void);
unsigned tls_ordinary_setups(void);
unsigned tls_allocator_calls(void);
void tls_set_attach_result(int result);
void tls_set_nested_attach(bool enabled);
void tls_fail_next_allocation(void);

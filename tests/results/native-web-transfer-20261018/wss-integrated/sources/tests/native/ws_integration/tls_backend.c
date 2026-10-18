/* Appended to the frozen ESP-TLS host fixture's platform prefix. SDK crypto,
 * ESP-TLS and native transport above are the actual tested implementations.
 * No HTTPD type crosses this module boundary: public session APIs are supplied
 * by the SDK lifecycle translation unit, and config stays private here. */
static httpd_config_t integration_tls_config;
void integration_tls_prepare(const char *path) {
    FILE *file=fopen(path,"rb");assert(file&&!fseek(file,0,SEEK_END));
    long count=ftell(file);assert(count>0&&count<32768&&!fseek(file,0,SEEK_SET));
    uint8_t *bytes=malloc((size_t)count);assert(bytes&&fread(bytes,1,(size_t)count,file)==(size_t)count&&!fclose(file));
    assert(native_web_transport_provision(bytes,(size_t)count)==ESP_OK);
    wipe(bytes,(size_t)count);free(bytes);
    integration_tls_config=(httpd_config_t){.stack_size=10240};
    assert(native_web_transport_prepare(&integration_tls_config)==ESP_OK&&native_web_transport_secure());
    assert(integration_tls_config.open_fn&&integration_tls_config.close_fn);
}
int integration_tls_open(void *server,int fd) {return integration_tls_config.open_fn(server,fd);}
void integration_tls_close(void *server,int fd) {integration_tls_config.close_fn(server,fd);}
void integration_tls_release(void) {
    assert(native_web_transport_release()==ESP_OK);
    wipe(nvs_blob,nvs_size);free(nvs_blob);nvs_blob=NULL;nvs_size=0;mbedtls_psa_crypto_free();
}

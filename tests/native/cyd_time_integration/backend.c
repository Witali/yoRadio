/* Appended to the qualified public ESP-TLS/native transport platform prefix. */
static httpd_config_t integration_config;
void integration_transport_prepare(const char *path,bool secure) {
    if(secure){
        FILE *file=fopen(path,"rb");assert(file&&!fseek(file,0,SEEK_END));long size=ftell(file);
        assert(size>0&&size<32768&&!fseek(file,0,SEEK_SET));uint8_t *bytes=malloc((size_t)size);
        assert(bytes&&fread(bytes,1,(size_t)size,file)==(size_t)size&&!fclose(file));
        assert(native_web_transport_provision(bytes,(size_t)size)==ESP_OK);wipe(bytes,(size_t)size);free(bytes);
    }
    integration_config=(httpd_config_t){.stack_size=10240};
    assert(native_web_transport_prepare(&integration_config)==ESP_OK&&native_web_transport_secure()==secure);
    assert((integration_config.open_fn!=NULL)==secure&&(integration_config.close_fn!=NULL)==secure);
}
int integration_transport_open(void *server,int fd) {return integration_config.open_fn?integration_config.open_fn(server,fd):ESP_OK;}
void integration_transport_close(void *server,int fd) {assert(integration_config.close_fn);integration_config.close_fn(server,fd);}
void integration_transport_release(void) {
    assert(native_web_transport_release()==ESP_OK);
    if(nvs_blob){wipe(nvs_blob,nvs_size);free(nvs_blob);nvs_blob=NULL;nvs_size=0;}
    mbedtls_psa_crypto_free();
}

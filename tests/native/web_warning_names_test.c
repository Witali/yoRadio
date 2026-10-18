#include <assert.h>
#include <stdio.h>
#include "form-production.h"
static bool begin(unsigned slot,void *context) {(void)slot;(void)context;return true;}
int main(void) {
    web_file_form_t form={.mode=WEB_FORM_UPLOAD,.sink={.begin=begin}};
    const char *playlist="Content-Disposition: form-data; name=\"plfile\"; filename=\"playlist.csv\"\r\n";
    bool accepted=web_file_form_part(MP_BEGIN,(const uint8_t *)playlist,0,&form);
    assert(accepted==(CONFIG_SPIFFS_OBJ_NAME_LEN>=13));
    if(accepted)assert(!strcmp(form.names[0],"playlist.csv"));
    memset(&form,0,sizeof(form));form.mode=WEB_FORM_UPLOAD;
    const char *wifi="Content-Disposition: form-data; name=\"wifile\"; filename=\"wifi.csv\"\r\n";
    accepted=web_file_form_part(MP_BEGIN,(const uint8_t *)wifi,0,&form);
    assert(accepted==(CONFIG_SPIFFS_OBJ_NAME_LEN>=9));
    printf("PASS C3 upload name capacity %u\n",CONFIG_SPIFFS_OBJ_NAME_LEN);
    return 0;
}

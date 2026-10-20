#include "c3_time_service_platform.h"
#include "json_buffer.h"
typedef struct {unsigned marker;} httpd_req_t;
static runtime_time_settings_t desired={.timezone_hour=-5,.timezone_minute=30,.sync_interval_min=120,.servers={"first.example","second.example"}};
static int failure;
static unsigned snapshots,sends;
static char response[640];
esp_err_t runtime_settings_get_time_snapshot(runtime_time_settings_t *out,uint32_t timeout){assert(timeout==100);++snapshots;if(failure)return failure;*out=desired;return ESP_OK;}
static size_t strlcpy(char *to,const char *from,size_t capacity){size_t n=strlen(from);if(capacity){size_t k=n<capacity?n:capacity-1;memcpy(to,from,k);to[k]=0;}return n;}
static esp_err_t ws_send_request(httpd_req_t *request,const char *payload){assert(request&&request->marker==42);strlcpy(response,payload,sizeof(response));++sends;return ESP_OK;}
#include "timezone.inc"
int main(void){httpd_req_t request={42};assert(send_timezone_settings(&request)==ESP_OK);assert(snapshots==1&&sends==1);
    assert(!strcmp(response,"{\"tzh\":-5,\"tzm\":30,\"sntp1\":\"first.example\",\"sntp2\":\"second.example\",\"timeint\":120,\"timeintrtc\":24}"));
    failure=ESP_ERR_TIMEOUT;assert(send_timezone_settings(&request)==ESP_ERR_TIMEOUT);assert(snapshots==2&&sends==1);
    failure=ESP_ERR_INVALID_STATE;assert(send_timezone_settings(&request)==ESP_ERR_INVALID_STATE);assert(snapshots==3&&sends==1);
    puts("PASS C3 timezone WS: actual serializer + shared JSON; one checked snapshot; no reply on timeout/invalid state");return 0;}

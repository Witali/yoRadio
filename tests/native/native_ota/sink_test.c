#include "host.h"
#include "native_ota_sink.h"

static esp_partition_t active,spare;
static uint8_t flash[0x1d1000],image[0x1d1000];
static size_t written,expected_length;
static unsigned groups,begins,writes,ends,aborts,selects,maintenance,next_calls;
static int inject,fail_write;
static bool owned,no_running,no_spare;
const esp_partition_t *esp_ota_get_running_partition(void){return no_running?NULL:&active;}
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *running){assert(running==&active&&!no_running);++next_calls;return no_spare?NULL:&spare;}
static esp_err_t before_flash(void *context){assert(context==&groups&&!begins&&!maintenance);++maintenance;return inject==1?ESP_FAIL:ESP_OK;}
esp_err_t esp_ota_begin(const esp_partition_t *partition,size_t size,esp_ota_handle_t *handle){assert(partition==&spare&&size==OTA_WITH_SEQUENTIAL_WRITES&&maintenance==1&&!owned);++begins;if(inject==2)return ESP_ERR_NO_MEM;owned=true;*handle=42;return ESP_OK;}
esp_err_t esp_ota_write(esp_ota_handle_t handle,const void *data,size_t size){assert(owned&&handle==42&&size&&size<=4096&&written+size<=spare.size);++writes;if((int)writes==fail_write)return ESP_FAIL;memcpy(flash+written,data,size);written+=size;return ESP_OK;}
esp_err_t esp_ota_end(esp_ota_handle_t handle){assert(owned&&handle==42);owned=false;++ends;return inject==3?ESP_ERR_OTA_VALIDATE_FAILED:ESP_OK;}
esp_err_t esp_ota_abort(esp_ota_handle_t handle){assert(owned&&handle==42);owned=false;++aborts;return ESP_OK;}
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *partition){assert(partition==&spare&&!owned&&ends==1);++selects;return inject==6?ESP_FAIL:ESP_OK;}
esp_err_t esp_image_verify(esp_image_load_mode_t mode,const esp_partition_pos_t *position,esp_image_metadata_t *metadata){assert(mode==ESP_IMAGE_VERIFY&&position->offset==spare.address&&position->size==written&&!owned);metadata->image_len=expected_length+(inject==5?1U:0U);return inject==4?ESP_ERR_IMAGE_FLASH_FAIL:ESP_OK;}
static native_ota_policy_t reset(unsigned chip,size_t length){
    active=(esp_partition_t){.address=0x10000,.size=0x1b0000,.type=0,.subtype=0x10,.flash_chip=(void *)1};
    spare=(esp_partition_t){.address=0x1c0000,.size=sizeof(flash),.type=0,.subtype=0x11,.flash_chip=(void *)1};
    begins=writes=ends=aborts=selects=maintenance=next_calls=0;written=0;expected_length=length;owned=no_running=no_spare=false;inject=fail_write=0;
    native_ota_policy_t policy={.expected_chip=chip,.image_limit=0x1b0000,.before_flash=before_flash,.context=&groups};
    strcpy(policy.expected_project,chip?"yoradio_esp32c3_oled_native":"yoradio_cyd2usb_native");
    memset(image,0x57,length);memset(flash,0xa5,sizeof(flash));
    esp_image_header_t header={.magic=ESP_IMAGE_HEADER_MAGIC,.chip_id=chip,.segment_count=1,.hash_appended=1};
    esp_image_segment_header_t segment={.load_addr=0x3f400020,.data_len=256};
    esp_app_desc_t description={.magic_word=ESP_APP_DESC_MAGIC_WORD};memcpy(description.project_name,policy.expected_project,32);
    memcpy(image,&header,sizeof(header));memcpy(image+24,&segment,8);memcpy(image+32,&description,sizeof(description));return policy;
}
static bool receive(native_ota_sink_t *sink,size_t length,size_t step){for(size_t offset=0;offset<length;){size_t count=length-offset;if(count>step)count=step;if(!native_ota_sink_feed(sink,image+offset,count))return false;offset+=count;}return native_ota_sink_finish(sink);}
static void cleanup(native_ota_sink_t *sink){native_ota_sink_abort(sink);native_ota_sink_abort(sink);assert(!owned);++groups;}
int main(void){
    native_ota_sink_t sink;
    for(unsigned chip=0;chip<=5;chip+=5)for(size_t step=1;step<=600;++step){native_ota_policy_t policy=reset(chip,10000);assert(native_ota_sink_init(&sink,&policy));assert(receive(&sink,10000,step));assert(begins==1&&maintenance==1&&ends==1&&!aborts&&!selects&&sink.verified&&!sink.started);assert(written==10000&&!memcmp(flash,image,10000));assert(native_ota_sink_finish(&sink)&&ends==1);assert(!native_ota_sink_feed(&sink,image,1));assert(native_ota_sink_activate(&sink)&&native_ota_sink_activate(&sink)&&selects==1);cleanup(&sink);assert(sink.activated&&!aborts);}
    for(size_t length=0;length<288;++length){native_ota_policy_t policy=reset(0,10000);assert(native_ota_sink_init(&sink,&policy));assert(native_ota_sink_feed(&sink,image,length));assert(!native_ota_sink_finish(&sink)&&!begins&&!maintenance&&!selects);cleanup(&sink);}
    // Split the validated prefix at the exact point before the first callback.
    native_ota_policy_t policy=reset(0,10000);assert(native_ota_sink_init(&sink,&policy));assert(native_ota_sink_feed(&sink,image,287)&&!begins&&!maintenance);assert(native_ota_sink_feed(&sink,image+287,1)&&begins==1&&maintenance==1);cleanup(&sink);assert(aborts==1);
    const size_t offsets[]={0,1,12,23,32,80};
    for(size_t i=0;i<sizeof(offsets)/sizeof(offsets[0]);++i){policy=reset(0,10000);image[offsets[i]]^=0x40;assert(native_ota_sink_init(&sink,&policy));assert(!receive(&sink,10000,111)&&!maintenance&&!begins&&!selects);cleanup(&sink);}
    for(int mode=0;mode<5;++mode){policy=reset(0,10000);esp_image_header_t *header=(void *)image;esp_image_segment_header_t *segment=(void *)(image+24);if(mode==0)header->segment_count=0;if(mode==1)header->segment_count=17;if(mode==2)segment->data_len=252;if(mode==3)segment->data_len=257;if(mode==4)segment->data_len=0xfffffffcU;assert(native_ota_sink_init(&sink,&policy));assert(!receive(&sink,10000,512)&&!begins&&!maintenance);cleanup(&sink);}
    for(int mode=0;mode<12;++mode){policy=reset(0,10000);if(mode==0)no_running=true;if(mode==1)no_spare=true;if(mode==2)spare.type=ESP_PARTITION_TYPE_DATA;if(mode==3)spare.subtype=0;if(mode==4)spare.subtype=ESP_PARTITION_SUBTYPE_APP_OTA_MAX;if(mode==5)spare.address=active.address;if(mode==6)spare.address=active.address+active.size-1;if(mode==7)spare.flash_chip=(void *)2;if(mode==8)spare.size=287;if(mode==9)policy.image_limit=0;if(mode==10)policy.before_flash=NULL;if(mode==11)memset(policy.expected_project,'X',32);assert(!native_ota_sink_init(&sink,&policy)&&!begins&&!maintenance);if(mode==0)assert(!next_calls);cleanup(&sink);}
    for(int error=1;error<=6;++error){policy=reset(0,10000);inject=error;assert(native_ota_sink_init(&sink,&policy));bool ok=receive(&sink,10000,777);assert(!(ok&&native_ota_sink_activate(&sink)));const char *first=sink.error;assert(first&&!native_ota_sink_feed(&sink,image,1));cleanup(&sink);assert(sink.error==first&&!owned&&aborts==0&&selects==(error==6?1U:0U));}
    for(int point=1;point<=3;++point){policy=reset(0,10000);fail_write=point;assert(native_ota_sink_init(&sink,&policy));assert(!receive(&sink,10000,777)&&!ends&&!selects);cleanup(&sink);assert(aborts==1);}
    for(int mode=0;mode<4;++mode){size_t length=mode==0?0x1b0000:mode==1?0x1b0001:mode==2?4095:4097;policy=reset(0,length);if(mode>=2)spare.size=(uint32_t)length;assert(native_ota_sink_init(&sink,&policy));bool ok=receive(&sink,length,1024);assert(ok==(mode!=1));if(ok)assert(written==length);cleanup(&sink);}
    policy=reset(5,10000);policy.image_limit=0x1d0000;assert(native_ota_sink_init(&sink,&policy)&&sink.limit==0x1d0000);cleanup(&sink);
    policy=reset(0,10000);policy.expected_project[0]=0;assert(!native_ota_sink_init(&sink,&policy));cleanup(&sink);
    assert(!native_ota_sink_init(NULL,&policy));assert(!native_ota_sink_init(&sink,NULL));cleanup(&sink);
    policy=reset(0,10000);assert(native_ota_sink_init(&sink,&policy));assert(native_ota_sink_feed(&sink,NULL,0));assert(!native_ota_sink_feed(&sink,NULL,1)&&!begins);cleanup(&sink);
    printf("PASS actual native OTA sink: %u groups; chip0/C3 policy, prefix-before-maintenance-before-begin, bounds/partitions, IO/end ownership, exact length, activation/abort lifecycle\n",groups);
}

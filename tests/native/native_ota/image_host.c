// Host flash/HAL/OTA ownership seams around the exact pinned image verifier.
// No target loading, eFuse, secure boot, encryption or physical flash claim.
#include "host.h"
#include "native_ota_sink.h"
#include "psa/crypto.h"
#include "psa/crypto_extra.h"
#include <inttypes.h>
#define ESP_LOGE(...) ((void)0)
#define ESP_LOGW(...) ((void)0)
#define ESP_LOGI(...) ((void)0)
#define ESP_LOGD(...) ((void)0)
#define ESP_LOGV(...) ((void)0)
#define ESP_LOG_ATTR_STR(value) (value)
#define WORD_ALIGNED_ATTR __attribute__((aligned(4)))
#define ESP_FAULT_ASSERT assert
#define SECURE_BOOT_CHECK_SIGNATURE 0
#define ESP_IMAGE_MAX_FLASH_ADDR_SIZE 0x1000000U
#define ESP_ROM_CHECKSUM_INITIAL 0xefU
#define HASH_LEN 32
#define SPI_FLASH_MMU_PAGE_SIZE 0x10000U
#define MMAP_ALIGNED_MASK (SPI_FLASH_MMU_PAGE_SIZE-1U)
#define ESP_PRIMARY_BOOTLOADER_OFFSET 0x1000U
#define RESET_REASON_CORE_DEEP_SLEEP 5
#define MIN(left,right) ((left)<(right)?(left):(right))
#include "soc-addresses.inc"
typedef psa_hash_operation_t *bootloader_sha256_handle_t;
static unsigned hashes_live;
static bool hash_oom;
static bootloader_sha256_handle_t bootloader_sha256_start(void){if(hash_oom)return NULL;psa_hash_operation_t *hash=malloc(sizeof(*hash));assert(hash);*hash=psa_hash_operation_init();assert(psa_hash_setup(hash,PSA_ALG_SHA_256)==PSA_SUCCESS);++hashes_live;return hash;}
static void bootloader_sha256_data(bootloader_sha256_handle_t hash,const void *data,size_t size){assert(psa_hash_update(hash,data,size)==PSA_SUCCESS);}
static void bootloader_sha256_finish(bootloader_sha256_handle_t hash,uint8_t *digest){if(digest){size_t length;assert(psa_hash_finish(hash,digest,32,&length)==PSA_SUCCESS&&length==32);}else assert(psa_hash_abort(hash)==PSA_SUCCESS);free(hash);assert(hashes_live);--hashes_live;}
static void bootloader_debug_buffer(const void *data,size_t size,const char *label){(void)data;(void)size;(void)label;}
static bool esp_cpu_dbgr_is_attached(void){return false;}
static int esp_rom_get_reset_reason(int cpu){assert(cpu==0);return 1;}
static uint32_t s_bootloader_partition_offset=ESP_PRIMARY_BOOTLOADER_OFFSET;
typedef enum {ESP_IMAGE_BOOTLOADER,ESP_IMAGE_APPLICATION} esp_image_type;
static esp_err_t bootloader_common_check_chip_validity(const esp_image_header_t *header,esp_image_type type){assert(type==ESP_IMAGE_APPLICATION);return header->chip_id==HOST_CHIP?ESP_OK:ESP_ERR_IMAGE_INVALID;}
static esp_err_t bootloader_common_check_efuse_blk_validity(unsigned minimum,unsigned maximum){(void)minimum;(void)maximum;return ESP_OK;}

#define FLASH_CAPACITY 0x1d0000U
#define SLOT_ADDRESS 0x1e0000U
static uint8_t flash[FLASH_CAPACITY] __attribute__((aligned(16)));
static esp_partition_t active={.address=0x10000,.size=0x1b0000,.type=0,.subtype=0x10,.flash_chip=(void *)1};
static esp_partition_t spare={.address=SLOT_ADDRESS,.size=FLASH_CAPACITY,.type=0,.subtype=0x11,.flash_chip=(void *)1};
static unsigned reads,maps,fail_read,fail_map,free_pages=2;
static unsigned maintenance,begins,ends,aborts,selects,writes;
static size_t written;
static bool owned;
static esp_err_t end_verification;
static bool flash_range(uint32_t address,size_t size){return address>=SLOT_ADDRESS&&(uint64_t)address+size<=(uint64_t)SLOT_ADDRESS+sizeof(flash);}
static esp_err_t bootloader_flash_read(uint32_t address,void *output,size_t size,bool decrypted){assert(decrypted);++reads;if(reads==fail_read||!flash_range(address,size))return ESP_ERR_IMAGE_FLASH_FAIL;memcpy(output,flash+address-SLOT_ADDRESS,size);return ESP_OK;}
static const void *bootloader_mmap(uint32_t address,uint32_t size){++maps;if(maps==fail_map||!flash_range(address,size))return NULL;return flash+address-SLOT_ADDRESS;}
static void bootloader_munmap(const void *address){assert((const uint8_t *)address>=flash&&(const uint8_t *)address<flash+sizeof(flash));}
static uint32_t bootloader_mmap_get_free_pages(void){return free_pages;}
#include "sdk-image-prototypes.inc"
#include "sdk-image-functions.inc"

const esp_partition_t *esp_ota_get_running_partition(void){return &active;}
const esp_partition_t *esp_ota_get_next_update_partition(const esp_partition_t *running){assert(running==&active);return &spare;}
static esp_err_t before_flash(void *context){assert(context==&maintenance&&!maintenance&&!begins);++maintenance;return ESP_OK;}
esp_err_t esp_ota_begin(const esp_partition_t *partition,size_t size,esp_ota_handle_t *handle){assert(partition==&spare&&size==OTA_WITH_SEQUENTIAL_WRITES&&maintenance==1&&!owned);owned=true;++begins;*handle=7;return ESP_OK;}
esp_err_t esp_ota_write(esp_ota_handle_t handle,const void *data,size_t size){assert(owned&&handle==7&&written+size<=spare.size);memcpy(flash+written,data,size);written+=size;++writes;return ESP_OK;}
esp_err_t esp_ota_end(esp_ota_handle_t handle){assert(owned&&handle==7);esp_partition_pos_t position={spare.address,spare.size};esp_image_metadata_t metadata;end_verification=esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata);owned=false;++ends;return end_verification;}
esp_err_t esp_ota_abort(esp_ota_handle_t handle){assert(owned&&handle==7);owned=false;++aborts;return ESP_OK;}
esp_err_t esp_ota_set_boot_partition(const esp_partition_t *partition){assert(partition==&spare&&!owned);esp_partition_pos_t position={spare.address,spare.size};esp_image_metadata_t metadata;++selects;return esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata);}
#include "image_test.c"

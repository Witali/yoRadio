typedef struct {
  uint32_t start_addr;   /* Start address of image */
  esp_image_header_t image; /* Header for entire image */
  esp_image_segment_header_t segments[ESP_IMAGE_MAX_SEGMENTS]; /* Per-segment header data */
  uint32_t segment_data[ESP_IMAGE_MAX_SEGMENTS]; /* Data offsets for each segment */
  uint32_t image_len; /* Length of image on flash, in bytes */
  uint8_t image_digest[32]; /* appended SHA-256 digest */
  uint32_t secure_version; /* secure version for anti-rollback, it is covered by sha256 (set if CONFIG_BOOTLOADER_APP_ANTI_ROLLBACK=y) */
  uint32_t mmu_page_size; /* Flash MMU page size per binary header */
} esp_image_metadata_t;
typedef enum {
    ESP_IMAGE_VERIFY,            /* Verify image contents, not load to memory, load metadata. Print errors. */
    ESP_IMAGE_VERIFY_SILENT,     /* Verify image contents, not load to memory, load metadata. Don't print errors. */
#ifdef BOOTLOADER_BUILD
    ESP_IMAGE_LOAD,              /* Verify image contents, load to memory, load metadata. Print errors. */
    ESP_IMAGE_LOAD_NO_VALIDATE,  /* Not verify image contents, load to memory, load metadata. Print errors. */
#endif
} esp_image_load_mode_t;

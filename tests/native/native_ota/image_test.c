static uint8_t image[FLASH_CAPACITY+64] __attribute__((aligned(16)));
static unsigned groups;
static size_t image_length,checksum_offset;
static native_ota_policy_t policy;
static size_t make_image(bool hash,size_t payload){
    assert(payload>=4096&&payload%4==0&&payload+96<=sizeof(image));
    esp_image_header_t header={.magic=ESP_IMAGE_HEADER_MAGIC,.chip_id=HOST_CHIP,.segment_count=2,.hash_appended=hash};
    memcpy(image,&header,24);size_t offset=24;uint8_t checksum=0xef;
    for(unsigned index=0;index<2;++index){size_t length=index?payload-4096:4096;esp_image_segment_header_t segment={.load_addr=index?0:SOC_DROM_LOW+32,.data_len=(uint32_t)length};memcpy(image+offset,&segment,8);offset+=8;for(size_t n=0;n<length;++n)image[offset+n]=(uint8_t)(n*71U+index);
        if(!index){esp_app_desc_t description={.magic_word=ESP_APP_DESC_MAGIC_WORD};strcpy(description.project_name,HOST_CHIP?"yoradio_esp32c3_oled_native":"yoradio_cyd2usb_native");memcpy(image+offset,&description,256);}
        for(size_t n=0;n<length;++n)checksum^=image[offset+n];
        offset+=length;
    }
    size_t padded=(offset+16U)&~15U;memset(image+offset,0,padded-offset);image[padded-1]=checksum;checksum_offset=padded-1;offset=padded;
    if(hash){size_t size;assert(psa_hash_compute(PSA_ALG_SHA_256,image,offset,image+offset,32,&size)==PSA_SUCCESS&&size==32);offset+=32;}
    image_length=offset;return offset;
}
static void reset_image(void){
    assert(!owned&&!hashes_live);memset(flash,0xff,sizeof(flash));written=0;maintenance=begins=ends=aborts=selects=writes=reads=maps=fail_read=fail_map=0;free_pages=2;hash_oom=false;end_verification=ESP_FAIL;
    policy=(native_ota_policy_t){.expected_chip=HOST_CHIP,.image_limit=HOST_CHIP?0x1d0000:0x1b0000,.before_flash=before_flash,.context=&maintenance};strcpy(policy.expected_project,HOST_CHIP?"yoradio_esp32c3_oled_native":"yoradio_cyd2usb_native");
}
static bool upload(native_ota_sink_t *sink,size_t length,size_t step){assert(native_ota_sink_init(sink,&policy));for(size_t offset=0;offset<length;){size_t size=length-offset;if(size>step)size=step;if(!native_ota_sink_feed(sink,image+offset,size))return false;offset+=size;}return native_ota_sink_finish(sink);}
static void done(native_ota_sink_t *sink){native_ota_sink_abort(sink);assert(!owned&&!hashes_live);++groups;}
int main(int argc,char **argv){
    assert(argc==2&&psa_crypto_init()==PSA_SUCCESS);native_ota_sink_t sink;
    for(unsigned hash=0;hash<2;++hash)for(unsigned step=1;step<=512;++step){reset_image();make_image(hash,10240);assert(upload(&sink,image_length,step)&&sink.verified&&!selects&&end_verification==ESP_OK);assert(native_ota_sink_activate(&sink)&&selects==1);assert(written==image_length&&!memcmp(flash,image,image_length));done(&sink);}
    reset_image();make_image(true,10240);FILE *fixture=fopen(argv[1],"wb");assert(fixture&&fwrite(image,1,image_length,fixture)==image_length&&!fclose(fixture));
    // Real checksum rejection without an appended hash, then real SHA rejection
    // with the byte checksum intact (two equal XOR changes cancel).
    reset_image();make_image(false,10240);image[400]^=1;assert(!upload(&sink,image_length,333)&&ends==1&&!selects);done(&sink);
    reset_image();make_image(true,10240);image[400]^=1;image[404]^=1;assert(!upload(&sink,image_length,333)&&ends==1&&!selects);done(&sink);
    reset_image();make_image(true,10240);image[image_length-1]^=1;assert(!upload(&sink,image_length,333)&&ends==1&&!selects);done(&sink);
    reset_image();make_image(false,10240);image[checksum_offset]^=1;assert(!upload(&sink,image_length,333)&&ends==1&&!selects);done(&sink);
    // A valid retained later flash sector can make SDK end succeed on a cut
    // upload. The sink's second verifier uses the uploaded length and refuses.
    for(size_t cut=4096;cut<=8192;cut+=4096){reset_image();make_image(true,10240);memcpy(flash,image,image_length);assert(!upload(&sink,cut,777)&&end_verification==ESP_OK&&!selects&&ends==1);done(&sink);}
    for(size_t extra=1;extra<=32;++extra){reset_image();make_image(true,10240);memset(image+image_length,0xff,extra);assert(!upload(&sink,image_length+extra,777)&&end_verification==ESP_OK&&!selects&&ends==1);done(&sink);}
    // Each actual binary truncation offset. Clean erased flash must not turn a
    // partially received header, segment, checksum or digest into a valid app.
    for(size_t cut=0;cut<image_length;++cut){reset_image();make_image(true,10240);assert(!upload(&sink,cut,1024)&&!selects);done(&sink);}
    // Actual SDK structural failures after the accepted 288-byte prefix.
    for(unsigned mode=0;mode<3;++mode){reset_image();make_image(false,10240);esp_image_segment_header_t second;memcpy(&second,image+24+8+4096,8);if(mode==0)second.data_len=3;if(mode==1)second.data_len=0xfffffffcU;if(mode==2){esp_image_segment_header_t first;memcpy(&first,image+24,8);first.load_addr+=4;memcpy(image+24,&first,8);}else memcpy(image+24+8+4096,&second,8);assert(!upload(&sink,image_length,1024)&&!selects);done(&sink);}
    // Exercise every memory-flash read/mapping operation of the pinned parser.
    reset_image();make_image(true,10240);memcpy(flash,image,image_length);esp_partition_pos_t position={SLOT_ADDRESS,spare.size};esp_image_metadata_t metadata;assert(esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata)==ESP_OK&&metadata.image_len==image_length);unsigned read_points=reads,map_points=maps;
    for(unsigned point=1;point<=read_points;++point){reads=maps=0;fail_read=point;assert(esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata)!=ESP_OK&&!hashes_live);++groups;}fail_read=0;
    for(unsigned point=1;point<=map_points;++point){reads=maps=0;fail_map=point;assert(esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata)!=ESP_OK&&!hashes_live);++groups;}fail_map=0;
    hash_oom=true;assert(esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata)==ESP_ERR_NO_MEM&&!hashes_live);hash_oom=false;++groups;
    free_pages=0;assert(esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata)!=ESP_OK&&!hashes_live);free_pages=2;++groups;
    reset_image();size_t cap=policy.image_limit;make_image(true,cap-80);assert(image_length==cap&&upload(&sink,image_length,4096));done(&sink);
    // metadata-only deliberately does not verify the checksum: this assertion
    // ensures that the host gate never substitutes it for the real verifier.
    reset_image();make_image(false,10240);image[400]^=1;memcpy(flash,image,image_length);assert(esp_image_get_metadata(&position,&metadata)==ESP_OK);assert(esp_image_verify(ESP_IMAGE_VERIFY,&position,&metadata)!=ESP_OK);++groups;
    assert(!hashes_live);mbedtls_psa_crypto_free();printf("PASS pinned image verifier: %u groups; chip=%u, checksum/SHA, all binary truncations, retained old tail, trailing bytes, exact board cap, read/map/hash OOM; %u read/%u map fault points\n",groups,(unsigned)HOST_CHIP,read_points,map_points);return 0;
}

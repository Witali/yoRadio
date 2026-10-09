// Included after unchanged production staged output and guarded DMA stubs.
int main(int argc, char **argv) {
    assert(argc==2);
    assert(native_audio_output_init()==ESP_OK);
    assert(native_audio_output_configure(48000)==ESP_OK);
    capture=fopen(argv[1],"w+b");assert(capture);
    int16_t first[128*2], second[384*2];
    for(unsigned i=0;i<128*2;++i) first[i]=1234;
    for(unsigned i=0;i<384*2;++i) second[i]=-2345;
    assert(native_audio_output_write_pcm((uint8_t *)first,sizeof(first),16,2)==ESP_OK);
    assert(s_buffered_frames==128 && captured==0);
    // The staged EOF branch in output_task currently only publishes status
    // and returns the EOS packet. The idle function is all that runs next.
    for(unsigned i=0;i<1000;++i) { test_now_us+=5000; native_audio_output_idle(); }
    printf("after_eof_idle pending_frames=%zu dma_audio_bytes=%zu\n",s_buffered_frames,captured);
    // Same-rate configure must not be used to manufacture a reset in this
    // reproduction. Production output_task doesn't even call it at this rate.
    assert(native_audio_output_configure(48000)==ESP_OK);
    assert(native_audio_output_write_pcm((uint8_t *)second,sizeof(second),16,2)==ESP_OK);
    assert(captured==512*4 && s_buffered_frames==0);
    rewind(capture); int16_t block[512*2];
    assert(fread(block,sizeof(block),1,capture)==1);
    unsigned old_frames=0,new_frames=0;
    for(unsigned i=0;i<512;++i) {
        assert(block[2*i]==block[2*i+1]);
        old_frames+=(block[2*i]==1234);
        new_frames+=(block[2*i]==-2345);
    }
    printf("same_rate_replacement old_frames=%u new_frames=%u\n",old_frames,new_frames);
    assert(old_frames==128 && new_frames==384);
    fclose(capture);capture=NULL;
    puts("REPRODUCED staged tail retained at EOF and copied into next same-rate stream");
    return 0;
}

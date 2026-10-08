// Included after the actual production output source and DMA writer.
static uint32_t rng=12345;
static int16_t random_sample(void){rng^=rng<<13;rng^=rng>>17;rng^=rng<<5;return (int16_t)rng;}
static void driver_failure_tests(void){
    size_t written;int16_t source[2048]={0};copy_t context={(uint8_t *)source};
    channel.dma.curr_ptr=NULL;queue.fail=true;
    assert(native_i2s_write_generated(&channel,512,fill_copy,&context,false,&written)==ESP_ERR_TIMEOUT);
    assert(!written && context.data==(uint8_t *)source && !binary_lock.held);
    queue.fail=false;binary_lock.fail=true;
    assert(native_i2s_write_generated(&channel,512,fill_copy,&context,false,&written)==ESP_ERR_INVALID_STATE);
    assert(!written);binary_lock.fail=false;
    // The queue has overtaken a partial buffer. The stock writer must acquire
    // a fresh block; it must not resume writing into the stale address.
    channel.dma.curr_ptr=blocks[3].pcm;channel.dma.rw_pos=100;
    queue.next=0;queue.spaces=1;
    assert(native_i2s_write_generated(&channel,7,fill_copy,&context,false,&written)==0);
    assert(written==7 && channel.dma.curr_ptr==blocks[0].pcm && channel.dma.rw_pos==28);
    queue.spaces=4;
    channel.state=I2S_CHAN_STATE_READY;
    assert(native_i2s_write_generated(&channel,7,fill_copy,&context,false,&written)==ESP_ERR_INVALID_STATE);
    assert(!written && !binary_lock.held);channel.state=I2S_CHAN_STATE_RUNNING;
}
#ifndef BASELINE
typedef struct { native_audio_pcm_lease_t lease; int16_t pcm[]; } test_item_t;
static unsigned outstanding, released;
static void release_test(native_audio_pcm_lease_t *lease) {
    assert(!binary_lock.held && !mutex_lock.held);
    assert(outstanding);--outstanding;++released;
    free(lease);
}
static test_item_t *new_item(size_t samples) {
    test_item_t *item=calloc(1,sizeof(*item)+samples*sizeof(int16_t));assert(item);
    ++outstanding;return item;
}
static void lease_failure_tests(void) {
    assert(native_audio_output_configure(44100)==0);
    test_item_t *a=new_item(20);
    assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,40,16,2,release_test)==0);
    assert(outstanding==1);native_audio_output_discard_pcm();assert(!outstanding);
    for(unsigned kind=0;kind<3;++kind) {
        a=new_item(20);
        assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,40,16,2,release_test)==0);
        test_item_t *b=new_item(4096);
        if(kind==0)queue.fail=true;
        if(kind==1)binary_lock.fail=true;
        if(kind==2)channel.state=I2S_CHAN_STATE_READY;
        assert(native_audio_output_submit_pcm(&b->lease,(uint8_t *)b->pcm,8192,16,2,release_test)!=0);
        assert(!outstanding && !s_pending_head && !s_pending_frames);
        queue.fail=binary_lock.fail=false;channel.state=I2S_CHAN_STATE_RUNNING;
    }
    a=new_item(20);
    assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,39,16,2,release_test)!=0);
    assert(!outstanding);
    a=new_item(20);
    assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,40,16,2,release_test)==0);
    assert(native_audio_output_configure(48000)==0 && !outstanding);
    a=new_item(20);
    assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,40,16,2,release_test)==0);
    assert(native_audio_output_suspend()==0 && !outstanding);
    assert(native_audio_output_init()==0);
    assert(native_audio_output_configure(48000)==0);
    size_t before=full_blocks;
    for(unsigned i=0;i<3;++i) {
        a=new_item(1024);
        assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,2048,16,2,release_test)==0);
        assert(full_blocks==before+(i==2?3:0));
    }
    assert(!outstanding);native_audio_output_discard_pcm();
    a=new_item(1024);
    assert(native_audio_output_submit_pcm(&a->lease,(uint8_t *)a->pcm,2048,16,2,release_test)==0);
    assert(outstanding==1);test_now_us+=32000;native_audio_output_idle();
    assert(!outstanding);native_audio_output_discard_pcm();
}
#endif
int main(int argc,char **argv){
    assert(argc==2);
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
    test_callback_registration_result = ESP_FAIL;
    assert(native_audio_output_init() == ESP_FAIL && !s_pdm && !s_pdm_running);
    test_callback_registration_result = ESP_OK;
#endif
    assert(native_audio_output_init()==0);
#if defined(CONFIG_YORADIO_PIPELINE_PROFILE) || defined(CONFIG_YORADIO_STAGED_DMA_PROFILE)
    uint32_t overruns = native_audio_output_dma_overruns();
    assert(test_callbacks.on_send_q_ovf);
    assert(!test_callbacks.on_send_q_ovf(&channel, NULL, NULL));
    assert(native_audio_output_dma_overruns() == overruns + 1);
#endif
#ifdef CONFIG_YORADIO_STAGED_DMA_PROFILE
    // Real staged write path: counters must retain SDK errors and wall time,
    // and reading/reporting must not reset an ISR-owned cumulative counter.
    int16_t profile_pcm[1024] = {0};
    memset(&s_dma_write_profile, 0, sizeof(s_dma_write_profile));
    test_write_delay_us = 37;
    assert(pdm_write_block(profile_pcm, 512) == ESP_OK);
    assert(s_dma_write_profile.writes == 1 && s_dma_write_profile.written_bytes == 2048);
    assert(s_dma_write_profile.write_us == 37 && s_dma_write_profile.max_write_us == 37);
    channel.dma.curr_ptr = NULL;
    queue.fail = true;
    test_write_delay_us = 61;
    assert(pdm_write_block(profile_pcm, 512) == ESP_ERR_TIMEOUT);
    assert(s_dma_write_profile.writes == 2 && s_dma_write_profile.errors == 1);
    assert(s_dma_write_profile.written_bytes == 2048 && s_dma_write_profile.write_us == 98);
    assert(s_dma_write_profile.max_write_us == 61);
    queue.fail = false;
    test_short_write_bytes = 1024;
    assert(pdm_write_block(profile_pcm, 512) == ESP_FAIL);
    assert(s_dma_write_profile.writes == 3 && s_dma_write_profile.errors == 2);
    assert(s_dma_write_profile.written_bytes == 3072);
    test_short_write_bytes = 0;
    staged_dma_report();
    assert(native_audio_output_dma_overruns() == overruns + 1);
    queue.fail = false;
    test_write_delay_us = 0;
    test_now_us = 0;
#endif
    driver_failure_tests();
#ifndef BASELINE
    lease_failure_tests();
#endif
    capture=fopen(argv[1],"wb");assert(capture);
    const unsigned rates[]={8000,11025,12000,16000,22050,24000,32000,44100,48000};
    const unsigned chunks[]={1,2,3,17,511,512,513,896,7};
    const unsigned volumes[]={0,1,127,254};
    unsigned cases=0;
    for(unsigned r=0;r<9;++r)for(unsigned ch=1;ch<=2;++ch)
    for(unsigned v=0;v<4;++v)for(int b=-16;b<=16;b+=16)
    for(unsigned norm=0;norm<2;++norm){
        volume=volumes[v];balance=b;normalize=norm;
        s_input_sample_rate=0;assert(native_audio_output_configure(rates[r])==0);
        size_t begin=captured;unsigned calls=normalizer_calls;
        for(unsigned c=0;c<sizeof(chunks)/sizeof(chunks[0]);++c){
#ifdef BASELINE
            int16_t data[896*2];
#else
            test_item_t *item=new_item(chunks[c]*ch);int16_t *data=item->pcm;
#endif
            for(unsigned i=0;i<chunks[c]*ch;++i)data[i]=random_sample();
            // Emulate the queue catching up while waiting for source packets.
            // A partial DMA writer loses the remaining block space here.
            queue.spaces=1;
#ifdef BASELINE
            assert(native_audio_output_write_pcm((uint8_t *)data,chunks[c]*ch*2,16,ch)==0);
#else
            assert(native_audio_output_submit_pcm(&item->lease,(uint8_t *)data,
                chunks[c]*ch*2,16,ch,release_test)==0);
            assert(s_pending_frames < (s_stream_started ? 512U : 1536U));
#endif
        }
#ifdef BASELINE
        if(s_buffered_frames){
            memset(s_frame_buffer+s_buffered_frames*2,0,(512-s_buffered_frames)*4);
            assert(pdm_write_block(s_frame_buffer,512)==0);
        }
        s_buffered_frames=0;
#else
        assert(native_audio_output_flush_pcm()==0 && !outstanding);
#endif
        assert(normalizer_calls-calls==sizeof(chunks)/sizeof(chunks[0]));
        printf("case=%u rate=%u channels=%u volume=%u balance=%d normalization=%u offset=%zu bytes=%zu peak=%u\n",
               cases++,rates[r],ch,volume,b,norm,begin,captured-begin,last_peak);
    }
    size_t before=captured;
    assert(native_audio_output_suspend()==0);
    assert(native_audio_output_init()==0);
    printf("ramps offset=%zu bytes=%zu\n",before,captured-before);
    fclose(capture);printf("PASS cases=%u bytes=%zu\n",cases,captured);
}

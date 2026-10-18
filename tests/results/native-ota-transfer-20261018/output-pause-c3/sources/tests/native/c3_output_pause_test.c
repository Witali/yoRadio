/* Appended to production output + production DMA writer and guarded driver
 * seams. The direct backend must release every retained source PCM lease. */
int main(void) {
    unsigned cases=0;
    assert(native_audio_output_init()==ESP_OK);
    assert(native_audio_output_configure(16000)==ESP_OK);++cases;
#ifdef BASELINE
    uint8_t pcm[40]={0};assert(native_audio_output_write_pcm(pcm,sizeof(pcm),16,2)==ESP_OK);
    assert(s_buffered_frames);
#else
    test_item_t *item=new_item(20);
    assert(native_audio_output_submit_pcm(&item->lease,(uint8_t *)item->pcm,40,16,2,release_test)==ESP_OK);
    assert(outstanding==1);
#endif
    native_audio_output_request_pause(true);
#ifdef BASELINE
    assert(native_audio_output_write_pcm(pcm,sizeof(pcm),16,2)==ESP_ERR_INVALID_STATE);
#else
    item=new_item(20);
    assert(native_audio_output_submit_pcm(&item->lease,(uint8_t *)item->pcm,40,16,2,release_test)==ESP_ERR_INVALID_STATE);
    assert(outstanding==1);
#endif
    ++cases;fail_pause_disable=true;
    assert(native_audio_output_pause()!=ESP_OK);
    assert(s_pdm && s_pdm_running && channel.state==I2S_CHAN_STATE_RUNNING);++cases;
#ifndef BASELINE
    assert(!outstanding && !s_pending_frames && !s_pending_head);++cases;
#else
    assert(!s_buffered_frames);++cases;
#endif
    fail_pause_disable=false;fail_pause_delete=true;
    assert(native_audio_output_pause()!=ESP_OK);
    assert(s_pdm && !s_pdm_running && channel.state==I2S_CHAN_STATE_READY);++cases;
    assert(native_audio_output_configure(16000)!=ESP_OK);
    assert(s_pdm && !s_pdm_running);++cases;
    fail_pause_delete=false;
    assert(native_audio_output_pause()==ESP_OK && !s_pdm && !s_pdm_running);++cases;
    assert(native_audio_output_pause()==ESP_OK);++cases;
    native_audio_output_request_pause(false);
    assert(native_audio_output_configure(16000)==ESP_OK && s_pdm_running);++cases;
    assert(native_audio_output_pause()==ESP_OK);++cases;
#ifdef BASELINE
    // Startup callback failure must retain a channel if its cleanup fails.
    test_callback_registration_result=ESP_FAIL;fail_pause_delete=true;
    assert(native_audio_output_configure(16000)!=ESP_OK);
    assert(s_pdm && !s_pdm_running);++cases;
    test_callback_registration_result=ESP_OK;fail_pause_delete=false;
    assert(native_audio_output_pause()==ESP_OK && !s_pdm);++cases;
#endif
    printf("PASS C3 checked pause %u cases; production output and DMA writer; platform driver seams\n",cases);
    return 0;
}

    if(!strncmp(scenario,"tls_",4)) {
        const char *selected_url=test_url;
        if(!strcmp(scenario,"tls_plain"))selected_url="http://radio.example.invalid/direct";
        if(!strcmp(scenario,"tls_occupied"))occupy_userdata=true;
        if(!strcmp(scenario,"tls_numeric"))numeric_userdata=true;
        if(!strcmp(scenario,"tls_attach_error"))tls_set_attach_result(-123);
        if(!strcmp(scenario,"tls_nested"))tls_set_nested_attach(true);
        if(!strcmp(scenario,"tls_init_error"))fail_init=true;
        if(!strcmp(scenario,"tls_open_before_error"))fail_open_before=true;
        if(!strcmp(scenario,"tls_open_after_error"))fail_open_after=true;
        if(!strcmp(scenario,"tls_setup_error"))fail_tls_setup=true;
        if(!strcmp(scenario,"tls_headers_error"))fail_headers=true;
        if(!strcmp(scenario,"tls_redirect_error")){fail_redirect=true;redirect_once=true;}
        if(!strcmp(scenario,"tls_redirect_https"))redirect_once=true;
        if(!strcmp(scenario,"tls_redirect_plain")){redirect_once=true;redirect_destination="http://other.example.invalid/";}
        if(!strcmp(scenario,"tls_redirect_to_https")){selected_url="http://radio.example.invalid/direct";redirect_once=true;redirect_destination=test_url;}
        bool error_case=strstr(scenario,"error")!=NULL&&strcmp(scenario,"tls_attach_error");
        tls_independent_client();unsigned old_setups=tls_setups(),old_loans=tls_loan_count(),old_attaches=tls_attaches();
        arm(error_case?"cleanup":(!strcmp(scenario,"tls_cancel_open")?"tls_open":"read"));
        if(fail_init)arm(NULL);
        tls_check(audio_service_play(selected_url,NATIVE_CODEC_FLAC)==ESP_OK,"service_play_accepted");
        if(fail_init) {
            await_play(0);begin_ok();
            tls_check(tls_setups()==old_setups&&tls_attaches()==old_attaches,"init_failure_before_tls_setup");
        } else {
            await_barrier();
            if(!error_case) {
                bool plain=!strncmp(selected_url,"http://",7)&&strcmp(scenario,"tls_redirect_to_https");
                bool final_plain=!strcmp(scenario,"tls_redirect_plain")||plain;
                bool marked=CONFIG_YORADIO_TLS_STATIC_RX_RESERVE&&strcmp(scenario,"tls_attach_error");
                tls_check(tls_loans()==(unsigned)(marked&&!final_plain),"live_radio_loan_matches_transport");
                if(!strcmp(scenario,"tls_plain"))tls_check(tls_attaches()==old_attaches,"plain_http_skips_tls_callback");
                tls_independent_client();
                tls_check(tls_loans()==(unsigned)(marked&&!final_plain),"unrelated_does_not_steal_radio_loan");
            }
            if(!strcmp(scenario,"tls_cancel_open"))audio_service_stop();
            begin_async(1500);vTaskDelay(30);tls_check(!begin_done,"owner_cleanup_barrier_respected");
            release_barrier();join_begin(ESP_OK);
        }
        tls_assert_drained();
        if(!strcmp(scenario,"tls_reopen")) {
            unsigned previous=http_inits;old_loans=tls_loan_count();arm("read");end_ok(true);await_play(previous);await_barrier();
            tls_check(tls_loan_count()==old_loans+(unsigned)CONFIG_YORADIO_TLS_STATIC_RX_RESERVE,"reopen_reacquires_same_slot");
            begin_async(1500);release_barrier();join_begin(ESP_OK);tls_assert_drained();
        }
        (void)old_loans;
    }
    else

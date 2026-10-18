static inline void esp_mbedtls_net_init(esp_tls_t *tls)
{
    mbedtls_net_init(&tls->server_fd);
}
void esp_mbedtls_cleanup(esp_tls_t *tls)
{
    if (!tls) {
        return;
    }
    if (tls->cacert_ptr != global_cacert) {
        mbedtls_x509_crt_free(tls->cacert_ptr);
    }
    tls->cacert_ptr = NULL;
    mbedtls_x509_crt_free(&tls->cacert);
    mbedtls_x509_crt_free(&tls->clientcert);

    /* For opaque keys, mbedtls_pk_free() does not release the underlying PSA
     * key — ownership is tracked separately. Dispatch on ownership, not on the
     * key lifetime: a caller-supplied key (ESP_KEY_SOURCE_PSA, e.g. a
     * pre-provisioned secure element) is owned externally and must never be
     * destroyed on connection close — at most purge it to drop the cached slot
     * (a no-op for a volatile key). A key esp-tls created itself is always
     * volatile and is destroyed to release its slot. mbedtls_pk_wrap_psa() sets
     * the pk_info to mbedtls_{rsa,ecdsa}_opaque_info, both of type
     * MBEDTLS_PK_OPAQUE, so one runtime check covers every opaque path (DS
     * peripheral, hardware ECDSA, and caller-supplied PSA keys). clientkey and
     * serverkey share storage via union, so one branch suffices. */
    if (mbedtls_pk_get_type(&tls->clientkey) == MBEDTLS_PK_OPAQUE) {
        psa_key_id_t kid = tls->clientkey.MBEDTLS_PRIVATE(priv_id);
        if (kid != PSA_KEY_ID_NULL) {
            if (tls->opaque_key_is_external) {
                psa_purge_key(kid);
            } else {
                psa_destroy_key(kid);
            }
            tls->clientkey.MBEDTLS_PRIVATE(priv_id) = PSA_KEY_ID_NULL;
        }
    }

    mbedtls_pk_free(&tls->clientkey);
    mbedtls_ssl_config_free(&tls->conf);
    mbedtls_ssl_free(&tls->ssl);
}
static esp_err_t set_ca_cert(esp_tls_t *tls, const unsigned char *cacert, size_t cacert_len)
{
    assert(tls);
    tls->cacert_ptr = &tls->cacert;
    mbedtls_x509_crt_init(tls->cacert_ptr);
    int ret = mbedtls_x509_crt_parse(tls->cacert_ptr, cacert, cacert_len);
    if (ret < 0) {
        ESP_LOGE(TAG, "mbedtls_x509_crt_parse of CA cert returned -0x%04X", -ret);
        mbedtls_print_error_msg(ret);
        ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
        return ESP_ERR_MBEDTLS_X509_CRT_PARSE_FAILED;
    }
    if (ret > 0) {
        /* This will happen if the CA chain contains one or more invalid certs, going ahead as the hadshake
         * may still succeed if the other certificates in the CA chain are enough for the authentication */
        ESP_LOGW(TAG, "mbedtls_x509_crt_parse was partly successful. No. of failed certificates: %d", ret);
    }
    mbedtls_ssl_conf_authmode(&tls->conf, MBEDTLS_SSL_VERIFY_REQUIRED);
    mbedtls_ssl_conf_ca_chain(&tls->conf, tls->cacert_ptr, NULL);
    return ESP_OK;
}
static esp_err_t set_pki_context(esp_tls_t *tls, const esp_tls_pki_t *pki)
{
    assert(tls);
    assert(pki);
    int ret;

    if (pki->publiccert_pem_buf != NULL &&
        pki->public_cert != NULL &&
        pki->pk_key != NULL) {

        mbedtls_x509_crt_init(pki->public_cert);
        mbedtls_pk_init(pki->pk_key);

        ret = mbedtls_x509_crt_parse(pki->public_cert, pki->publiccert_pem_buf, pki->publiccert_pem_bytes);
        if (ret < 0) {
            ESP_LOGE(TAG, "mbedtls_x509_crt_parse of public cert returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_X509_CRT_PARSE_FAILED;
        }

#ifdef CONFIG_ESP_TLS_USE_DS_PERIPHERAL
        if (pki->esp_ds_data != NULL) {
            ret = esp_mbedtls_init_pk_ctx_for_ds(pki);
            if (ret != ESP_OK) {
                ESP_LOGE(TAG, "Failed to initialize pk context for esp_rsa_ds");
                return ret;
            }
        } else
#endif
#ifdef CONFIG_MBEDTLS_HARDWARE_ECDSA_SIGN
        if (tls->use_ecdsa_peripheral) {
            esp_ecdsa_curve_t curve = ESP_ECDSA_CURVE_MAX;
            size_t curve_bits = 0;
            psa_algorithm_t sha_alg = 0;
            psa_algorithm_t ecdsa_alg = 0;
            // Determine the curve group ID based on user preference
            esp_err_t esp_ret = esp_tls_ecdsa_curve_to_esp_ecdsa_curve(tls->ecdsa_curve, &curve, &curve_bits, &sha_alg);
            if (esp_ret != ESP_OK || curve == ESP_ECDSA_CURVE_MAX || curve_bits == 0 || sha_alg == 0) {
                return esp_ret;
            }

#if CONFIG_MBEDTLS_ECDSA_DETERMINISTIC && SOC_ECDSA_SUPPORT_DETERMINISTIC_MODE
            ecdsa_alg = PSA_ALG_DETERMINISTIC_ECDSA(sha_alg);
#else
            ecdsa_alg = PSA_ALG_ECDSA(sha_alg);
#endif

            psa_key_id_t priv_key_id = 0;
            psa_key_attributes_t key_attr = PSA_KEY_ATTRIBUTES_INIT;
            // Set attributes for opaque private key
            psa_set_key_type(&key_attr, PSA_KEY_TYPE_ECC_KEY_PAIR(PSA_ECC_FAMILY_SECP_R1));
            psa_set_key_bits(&key_attr, curve_bits);
            psa_set_key_usage_flags(&key_attr, PSA_KEY_USAGE_SIGN_HASH);
            psa_set_key_algorithm(&key_attr, ecdsa_alg);
            psa_set_key_lifetime(&key_attr, PSA_KEY_LIFETIME_ESP_ECDSA_VOLATILE);

            esp_ecdsa_opaque_key_t opaque_key = {
                .curve = curve,
                .efuse_block = tls->ecdsa_efuse_blk,
#if SOC_KEY_MANAGER_SUPPORTED
                .key_recovery_info = NULL,
#endif /* SOC_KEY_MANAGER_SUPPORTED */
            };

            // Import opaque key reference
            psa_status_t status = psa_import_key(&key_attr, (uint8_t*) &opaque_key, sizeof(opaque_key), &priv_key_id);
            psa_reset_key_attributes(&key_attr);
            if (status != PSA_SUCCESS) {
                ESP_LOGE(TAG, "Failed to import opaque key reference");
                return ESP_ERR_MBEDTLS_PK_PARSE_KEY_FAILED;
            }
            mbedtls_pk_init(pki->pk_key);
            ret = mbedtls_pk_wrap_psa(pki->pk_key, priv_key_id);
            if (ret != 0) {
                ESP_LOGE(TAG, "Failed to wrap opaque key reference");
                psa_destroy_key(priv_key_id);
                return ret;
            }
        } else
#endif
        if (pki->privkey_pem_buf != NULL) {
            ret = mbedtls_pk_parse_key(pki->pk_key, pki->privkey_pem_buf, pki->privkey_pem_bytes,
                                       pki->privkey_password, pki->privkey_password_len);
        } else {
            return ESP_ERR_INVALID_ARG;
        }

        if (ret < 0) {
            ESP_LOGE(TAG, "mbedtls_pk_parse_keyfile returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_PK_PARSE_KEY_FAILED;
        }

        ret = mbedtls_ssl_conf_own_cert(&tls->conf, pki->public_cert, pki->pk_key);
        if (ret < 0) {
            ESP_LOGE(TAG, "mbedtls_ssl_conf_own_cert returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_SSL_CONF_OWN_CERT_FAILED;
        }
    } else {
        return ESP_ERR_INVALID_ARG;
    }
    return ESP_OK;
}
static esp_err_t set_server_config(esp_tls_cfg_server_t *cfg, esp_tls_t *tls)
{
    assert(cfg != NULL);
    assert(tls != NULL);
    int ret;
    esp_err_t esp_ret;
    if ((ret = mbedtls_ssl_config_defaults(&tls->conf,
                    MBEDTLS_SSL_IS_SERVER,
                    MBEDTLS_SSL_TRANSPORT_STREAM,
                    MBEDTLS_SSL_PRESET_DEFAULT)) != 0) {
        ESP_LOGE(TAG, "mbedtls_ssl_config_defaults returned -0x%04X", -ret);
        mbedtls_print_error_msg(ret);
        ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
        return ESP_ERR_MBEDTLS_SSL_CONFIG_DEFAULTS_FAILED;
    }

    mbedtls_ssl_conf_set_user_data_p(&tls->conf, cfg->userdata);

#ifdef CONFIG_MBEDTLS_SSL_ALPN
    if (cfg->alpn_protos) {
        mbedtls_ssl_conf_alpn_protocols(&tls->conf, cfg->alpn_protos);
    }
#endif

#if defined(CONFIG_ESP_TLS_SERVER_CERT_SELECT_HOOK)
    if (cfg->cert_select_cb != NULL) {
        ESP_LOGI(TAG, "Initializing server side cert selection cb");
        mbedtls_ssl_conf_cert_cb(&tls->conf, cfg->cert_select_cb);
    }
#endif

    if (cfg->cacert_buf != NULL) {
        esp_ret = set_ca_cert(tls, cfg->cacert_buf, cfg->cacert_bytes);
        if (esp_ret != ESP_OK) {
            return esp_ret;
        }
#ifdef CONFIG_ESP_TLS_SERVER_MIN_AUTH_MODE_OPTIONAL
        if (cfg->client_cert_authmode_optional) {
            mbedtls_ssl_conf_authmode(&tls->conf, MBEDTLS_SSL_VERIFY_OPTIONAL);
        }
#endif // CONFIG_ESP_TLS_SERVER_MIN_AUTH_MODE_OPTIONAL
    }

    /* use_secure_element is deprecated and non-functional: the cryptoauthlib
     * mbedTLS-ALT integration is not compatible with the PSA-based mbedTLS.
     * The field is kept for source compatibility only. */
    if (cfg->use_secure_element) {
        ESP_LOGE(TAG, "use_secure_element is no longer supported. Use server_key (esp_key_config_t) with "
                 "CONFIG_MBEDTLS_SECURE_ELEMENT_DRIVER_ENABLED instead. See the ESP-TLS migration guide.");
        return ESP_ERR_NOT_SUPPORTED;
    }

    if (cfg->server_key != NULL && cfg->server_key->source == ESP_KEY_SOURCE_BUFFER) {
        /* Unified key config with buffer source */
        esp_tls_pki_t pki = {
            .public_cert = &tls->servercert,
            .pk_key = &tls->serverkey,
            .publiccert_pem_buf = cfg->servercert_buf,
            .publiccert_pem_bytes = cfg->servercert_bytes,
            .privkey_pem_buf = cfg->server_key->buffer.data,
            .privkey_pem_bytes = cfg->server_key->buffer.len,
            .privkey_password = (const unsigned char *)cfg->server_key->buffer.password,
            .privkey_password_len = cfg->server_key->buffer.password_len,
        };
        esp_ret = set_pki_context(tls, &pki);
        if (esp_ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to set server pki context");
            return esp_ret;
        }
    } else if (cfg->server_key != NULL && cfg->server_key->source == ESP_KEY_SOURCE_PSA) {
        if (cfg->servercert_buf == NULL) {
            ESP_LOGE(TAG, "Server certificate is required when using a PSA-backed server key");
            return ESP_ERR_INVALID_ARG;
        }
        mbedtls_svc_key_id_t key_id = cfg->server_key->psa.key_id;
        mbedtls_pk_init(&tls->serverkey);
        tls->opaque_key_is_external = true;
        ret = mbedtls_pk_wrap_psa(&tls->serverkey, key_id);
        if (ret != 0) {
            ESP_LOGE(TAG, "mbedtls_pk_wrap_psa returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_PK_PARSE_KEY_FAILED;
        }
        ret = mbedtls_x509_crt_parse(&tls->servercert, cfg->servercert_buf, cfg->servercert_bytes);
        if (ret < 0) {
            ESP_LOGE(TAG, "mbedtls_x509_crt_parse returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_X509_CRT_PARSE_FAILED;
        }
        ret = mbedtls_ssl_conf_own_cert(&tls->conf, &tls->servercert, &tls->serverkey);
        if (ret != 0) {
            ESP_LOGE(TAG, "mbedtls_ssl_conf_own_cert returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_SSL_CONF_OWN_CERT_FAILED;
        }
    } else if (cfg->use_ecdsa_peripheral) {
#ifdef CONFIG_MBEDTLS_HARDWARE_ECDSA_SIGN
        tls->use_ecdsa_peripheral = cfg->use_ecdsa_peripheral;
#if SOC_ECDSA_SUPPORT_CURVE_P384
        tls->ecdsa_efuse_blk = HAL_ECDSA_COMBINE_KEY_BLOCKS(cfg->ecdsa_key_efuse_blk_high, cfg->ecdsa_key_efuse_blk);
#else
        tls->ecdsa_efuse_blk = cfg->ecdsa_key_efuse_blk;
#endif
        tls->ecdsa_curve = cfg->ecdsa_curve;
        esp_tls_pki_t pki = {
            .public_cert = &tls->servercert,
            .pk_key = &tls->serverkey,
            .publiccert_pem_buf = cfg->servercert_buf,
            .publiccert_pem_bytes = cfg->servercert_bytes,
            .privkey_pem_buf = NULL,
            .privkey_pem_bytes = 0,
            .privkey_password = NULL,
            .privkey_password_len = 0,
        };
        esp_err_t esp_ret = set_pki_context(tls, &pki);
        if (esp_ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to set client pki context");
            return esp_ret;
        }
#else
        ESP_LOGE(TAG, "Please enable the support for signing using ECDSA peripheral in menuconfig.");
        return ESP_FAIL;
#endif
    } else if (cfg->servercert_buf != NULL && cfg->serverkey_buf != NULL) {
        esp_tls_pki_t pki = {
            .public_cert = &tls->servercert,
            .pk_key = &tls->serverkey,
            .publiccert_pem_buf = cfg->servercert_buf,
            .publiccert_pem_bytes = cfg->servercert_bytes,
            .privkey_pem_buf = cfg->serverkey_buf,
            .privkey_pem_bytes = cfg->serverkey_bytes,
            .privkey_password = cfg->serverkey_password,
            .privkey_password_len = cfg->serverkey_password_len,
        };
        esp_ret = set_pki_context(tls, &pki);
        if (esp_ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to set server pki context");
            return esp_ret;
        }
#if defined(CONFIG_ESP_TLS_PSK_VERIFICATION)
    } else if (cfg->psk_hint_key) {
        ESP_LOGD(TAG, "PSK authentication");
        if (cfg->psk_hint_key->hint == NULL) {
            ESP_LOGE(TAG, "Failed to use psk_hint_key");
            return ESP_ERR_MBEDTLS_SSL_CONF_PSK_FAILED;
        }
        ret = mbedtls_ssl_conf_psk(&tls->conf, cfg->psk_hint_key->key, cfg->psk_hint_key->key_size,
                                   (const unsigned char *)cfg->psk_hint_key->hint, strlen(cfg->psk_hint_key->hint));
        if (ret != 0) {
            ESP_LOGE(TAG, "mbedtls_ssl_conf_psk returned -0x%04X", -ret);
            mbedtls_print_error_msg(ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            return ESP_ERR_MBEDTLS_SSL_CONF_PSK_FAILED;
        }
#endif
    } else {
#if defined(CONFIG_ESP_TLS_SERVER_CERT_SELECT_HOOK)
        if (cfg->cert_select_cb == NULL) {
            ESP_LOGE(TAG, "No cert select cb is defined");
        } else {
            /* At this point Callback MUST ALWAYS call mbedtls_ssl_set_hs_own_cert, or the handshake will abort! */
            ESP_LOGD(TAG, "Missing server cert and/or key, but cert selection cb is defined.");
            return ESP_OK;
        }
#else
        ESP_LOGE(TAG, "Missing server certificate and/or key");
#endif
        return ESP_ERR_INVALID_STATE;
    }

#ifdef CONFIG_ESP_TLS_SERVER_SESSION_TICKETS
    if (cfg->ticket_ctx) {
        ESP_LOGD(TAG, "Enabling server-side tls session ticket support");

        mbedtls_ssl_conf_session_tickets_cb( &tls->conf,
                esp_mbedtls_server_session_ticket_write,
                esp_mbedtls_server_session_ticket_parse,
                &cfg->ticket_ctx->ticket_ctx );
    }
#endif

    // Configure per-service TLS version
    const esp_tls_proto_ver_t tls_ver = cfg->tls_version;
    if (tls_ver == ESP_TLS_VER_TLS_1_3) {
#if CONFIG_MBEDTLS_SSL_PROTO_TLS1_3
        ESP_LOGI(TAG, "Setting server TLS version to 0x%4x", MBEDTLS_SSL_VERSION_TLS1_3);
        mbedtls_ssl_conf_min_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_3);
        mbedtls_ssl_conf_max_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_3);
#else
        ESP_LOGE(TAG, "TLS 1.3 is not enabled in config");
        return ESP_ERR_INVALID_ARG;
#endif
    } else if (tls_ver == ESP_TLS_VER_TLS_1_2) {
        ESP_LOGD(TAG, "Setting server TLS version to 0x%4x", MBEDTLS_SSL_VERSION_TLS1_2);
        mbedtls_ssl_conf_min_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_2);
        mbedtls_ssl_conf_max_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_2);
    }

    if (cfg->ciphersuites_list != NULL && cfg->ciphersuites_list[0] != 0) {
        ESP_LOGD(TAG, "Set the server ciphersuites list (user-provided)");
        mbedtls_ssl_conf_ciphersuites(&tls->conf, cfg->ciphersuites_list);
    } else {
        ESP_LOGD(TAG, "No custom cipher suites provided - using default");
    }
    return ESP_OK;
}
esp_err_t esp_create_mbedtls_handle(const char *hostname, size_t hostlen, const void *cfg, esp_tls_t *tls, void *server_params)
{
    assert(cfg != NULL);
    assert(tls != NULL);
    int ret;
    esp_err_t esp_ret = ESP_FAIL;

    tls->server_fd.fd = tls->sockfd;
    mbedtls_ssl_init(&tls->ssl);
    mbedtls_ssl_config_init(&tls->conf);

#if CONFIG_MBEDTLS_DYNAMIC_BUFFER
    tls->esp_tls_dyn_buf_strategy = ((esp_tls_cfg_t *)cfg)->esp_tls_dyn_buf_strategy;
#endif

    if (tls->role == ESP_TLS_CLIENT) {
        esp_ret = set_client_config(hostname, hostlen, (esp_tls_cfg_t *)cfg, tls);
        if (esp_ret != ESP_OK) {
            ESP_LOGE(TAG, "Failed to set client configurations, returned [0x%04X] (%s)", esp_ret, esp_err_to_name(esp_ret));
            goto exit;
        }
        const esp_tls_proto_ver_t tls_ver = ((esp_tls_cfg_t *)cfg)->tls_version;
        if (tls_ver == ESP_TLS_VER_TLS_1_3) {
#if CONFIG_MBEDTLS_SSL_PROTO_TLS1_3
            ESP_LOGD(TAG, "Setting TLS version to 0x%4x", MBEDTLS_SSL_VERSION_TLS1_3);
            mbedtls_ssl_conf_min_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_3);
            mbedtls_ssl_conf_max_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_3);
#else
            ESP_LOGW(TAG, "TLS 1.3 is not enabled in config, continuing with default TLS protocol");
#endif
        } else if (tls_ver == ESP_TLS_VER_TLS_1_2) {
            ESP_LOGD(TAG, "Setting TLS version to 0x%4x", MBEDTLS_SSL_VERSION_TLS1_2);
            mbedtls_ssl_conf_min_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_2);
            mbedtls_ssl_conf_max_tls_version(&tls->conf, MBEDTLS_SSL_VERSION_TLS1_2);
        } else if (tls_ver != ESP_TLS_VER_ANY) {
            ESP_LOGE(TAG, "Unsupported protocol version");
            esp_ret = ESP_ERR_INVALID_ARG;
            goto exit;
        }
    } else if (tls->role == ESP_TLS_SERVER) {
        if (server_params == NULL) {
            /* Server params cannot be NULL when TLS role is server */
            return ESP_ERR_INVALID_ARG;
        }
        esp_tls_server_params_t *input_server_params = server_params;
        esp_ret = input_server_params->set_server_cfg((esp_tls_cfg_server_t *) cfg, tls);
        if (esp_ret != 0) {
            ESP_LOGE(TAG, "Failed to set server configurations, returned [0x%04X] (%s)", esp_ret, esp_err_to_name(esp_ret));
            goto exit;
        }
    }

#ifdef CONFIG_MBEDTLS_DEBUG
    mbedtls_esp_enable_debug_log(&tls->conf, CONFIG_MBEDTLS_DEBUG_LEVEL);
#endif

    if ((ret = mbedtls_ssl_setup(&tls->ssl, &tls->conf)) != 0) {
        ESP_LOGE(TAG, "mbedtls_ssl_setup returned -0x%04X", -ret);
        mbedtls_print_error_msg(ret);
        ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
        esp_ret = ESP_ERR_MBEDTLS_SSL_SETUP_FAILED;
        goto exit;
    }
    mbedtls_ssl_set_bio(&tls->ssl, &tls->server_fd, mbedtls_net_send, mbedtls_net_recv, NULL);

    return ESP_OK;

exit:
    esp_mbedtls_cleanup(tls);
    return esp_ret;
}
void *esp_mbedtls_get_ssl_context(esp_tls_t *tls)
{
    if (tls == NULL) {
        ESP_LOGE(TAG, "Invalid arguments");
        return NULL;
    }
    return (void*)&tls->ssl;
}
ssize_t esp_mbedtls_read(esp_tls_t *tls, char *data, size_t datalen)
{

    ssize_t ret = mbedtls_ssl_read(&tls->ssl, (unsigned char *)data, datalen);
#if defined(CONFIG_MBEDTLS_SSL_PROTO_TLS1_3)
    /*
     * As per RFC 8446, section 4.6.1 the server may send a NewSessionTicket message at any time after the
     * client Finished message.
     * If a post-handshake message is received, connection state is changed to `MBEDTLS_SSL_TLS1_3_NEW_SESSION_TICKET`
     * Call mbedtls_ssl_read() till state is `MBEDTLS_SSL_TLS1_3_NEW_SESSION_TICKET` or return code is `MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET`
     * to process session tickets in TLS 1.3 connection.
     * This handshake message should be processed by mbedTLS and not by the application.
     */
    int iterations = 0;
    if (mbedtls_ssl_get_version_number(&tls->ssl) == MBEDTLS_SSL_VERSION_TLS1_3) {
        while (ret == MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET || tls->ssl.MBEDTLS_PRIVATE(state) == MBEDTLS_SSL_TLS1_3_NEW_SESSION_TICKET) {
            if (++iterations > ESP_TLS_MBEDTLS_MAX_NEW_SESSION_TICKETS) {
                ESP_LOGE(TAG, "Too many iterations waiting for new session ticket in TLS 1.3 connection");
                ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_INVALID_RESPONSE);
                return -1;
            }
            ESP_LOGD(TAG, "got session ticket in TLS 1.3 connection, retry read");
#if CONFIG_ESP_TLS_CLIENT_SESSION_TICKETS
            if (ret == MBEDTLS_ERR_SSL_RECEIVED_NEW_SESSION_TICKET) {
                esp_tls_client_session_t *tls13_saved_client_session = calloc(1, sizeof(esp_tls_client_session_t));
                if (tls13_saved_client_session == NULL) {
                    ESP_LOGE(TAG, "Failed to allocate memory for client session ctx");
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_NO_MEM);
                    return -1;
                }

                ret = mbedtls_ssl_get_session(&tls->ssl, &tls13_saved_client_session->saved_session);
                if (ret != 0) {
                    ESP_LOGE(TAG, "Error in getting the client ssl session");
                    mbedtls_ssl_session_free(&tls13_saved_client_session->saved_session);
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED);
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
                    return -1;
                }
                ESP_LOGD(TAG, "Session ticket received");

                size_t session_ticket_len = 0;
                ret = mbedtls_ssl_session_save(&tls13_saved_client_session->saved_session, NULL, 0, &session_ticket_len);
                if (ret != MBEDTLS_ERR_SSL_BUFFER_TOO_SMALL) {
                    ESP_LOGE(TAG, "Error in getting the client ssl session length");
                    mbedtls_ssl_session_free(&tls13_saved_client_session->saved_session);
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED);
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
                    return -1;
                }

                ESP_LOGD(TAG, "Session ticket length: %zu", session_ticket_len);
                if (tls->client_session != NULL) {
                    mbedtls_platform_zeroize(tls->client_session, tls->client_session_len);
                    free(tls->client_session);
                    tls->client_session = NULL;
                    tls->client_session_len = 0;
                }
                /* Allocate memory for the session ticket */
                tls->client_session = calloc(1, session_ticket_len);
                if (tls->client_session == NULL) {
                    ESP_LOGE(TAG, "Failed to allocate memory for client session ctx");
                    mbedtls_ssl_session_free(&tls13_saved_client_session->saved_session);
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_NO_MEM);
                    return -1;
                }
                /* mbedtls_ssl_session_save() may update session_ticket_len in/out, so
                 * remember the allocated size for the on-failure zeroize below. */
                size_t client_session_alloc_len = session_ticket_len;
                ret = mbedtls_ssl_session_save(&tls13_saved_client_session->saved_session, (unsigned char *)tls->client_session, client_session_alloc_len, &session_ticket_len);
                if (ret != 0) {
                    ESP_LOGE(TAG, "Error in saving the client ssl session");
                    mbedtls_print_error_msg(ret);
                    mbedtls_platform_zeroize(tls->client_session, client_session_alloc_len);
                    free(tls->client_session);
                    tls->client_session = NULL;
                    tls->client_session_len = 0;
                    mbedtls_ssl_session_free(&tls13_saved_client_session->saved_session);
                    free(tls13_saved_client_session);
                    tls13_saved_client_session = NULL;
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED);
                    ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
                    return -1;
                }

                ESP_LOGD(TAG, "Session ticket saved in the client session context");
                tls->client_session_len = session_ticket_len;
                mbedtls_ssl_session_free(&tls13_saved_client_session->saved_session);
                free(tls13_saved_client_session);
                tls13_saved_client_session = NULL;
            }
#endif // CONFIG_ESP_TLS_CLIENT_SESSION_TICKETS
            /* After handling the session ticket, we need to attempt to read again
             * to either get application data or process another ticket */
            ret = mbedtls_ssl_read(&tls->ssl, (unsigned char *)data, datalen);
        }
    }
#endif // CONFIG_MBEDTLS_SSL_PROTO_TLS1_3
    if (ret < 0) {
        if (ret == MBEDTLS_ERR_SSL_PEER_CLOSE_NOTIFY) {
            return 0;
        }
        if (ret != ESP_TLS_ERR_SSL_WANT_READ  && ret != ESP_TLS_ERR_SSL_WANT_WRITE) {
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
            ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_READ_FAILED);
            ESP_LOGE(TAG, "read error :-0x%04"NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT, -ret);
            mbedtls_print_error_msg(ret);
        }
    }
    return ret;
}
ssize_t esp_mbedtls_write(esp_tls_t *tls, const char *data, size_t datalen)
{
    size_t written = 0;
    size_t write_len = datalen;
    while (written < datalen) {
        if (write_len > MBEDTLS_SSL_OUT_CONTENT_LEN) {
            write_len = MBEDTLS_SSL_OUT_CONTENT_LEN;
        }
        if (datalen > MBEDTLS_SSL_OUT_CONTENT_LEN) {
            ESP_LOGD(TAG, "Fragmenting data of excessive size :%"NEWLIB_NANO_SIZE_T_COMPAT_FORMAT", offset: %"NEWLIB_NANO_SIZE_T_COMPAT_FORMAT", size %"NEWLIB_NANO_SIZE_T_COMPAT_FORMAT,
                    NEWLIB_NANO_SIZE_T_COMPAT_CAST(datalen), NEWLIB_NANO_SIZE_T_COMPAT_CAST(written), NEWLIB_NANO_SIZE_T_COMPAT_CAST(write_len));
        }
        ssize_t ret = mbedtls_ssl_write(&tls->ssl, (unsigned char*) data + written, write_len);
        if (ret <= 0) {
            if (ret != ESP_TLS_ERR_SSL_WANT_READ  && ret != ESP_TLS_ERR_SSL_WANT_WRITE && ret != 0) {
                ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
                ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_WRITE_FAILED);
                ESP_LOGE(TAG, "write error :-0x%04"NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT, -ret);
                mbedtls_print_error_msg(ret);
                return ret;
            } else {
                // Exiting the tls-write process as less than desired datalen are writable
                ESP_LOGD(TAG, "mbedtls_ssl_write() returned -0x%04"NEWLIB_NANO_SSIZE_T_COMPAT_FORMAT", already written %"NEWLIB_NANO_SIZE_T_COMPAT_FORMAT", exiting...", -ret, NEWLIB_NANO_SIZE_T_COMPAT_CAST(written));
                mbedtls_print_error_msg(ret);
                return (written > 0) ? written : ret;
            }
        }
        written += ret;
        write_len = datalen - written;
    }
    return written;
}
ssize_t esp_mbedtls_get_bytes_avail(esp_tls_t *tls)
{
    if (!tls) {
        ESP_LOGE(TAG, "empty arg passed to esp_tls_get_bytes_avail()");
        return ESP_FAIL;
    }
    return mbedtls_ssl_get_bytes_avail(&tls->ssl);
}
esp_err_t esp_mbedtls_server_session_init(esp_tls_cfg_server_t *cfg, int sockfd, esp_tls_t *tls)
{
    if (tls == NULL || cfg == NULL) {
        return ESP_ERR_INVALID_ARG;
    }
    tls->role = ESP_TLS_SERVER;
    tls->sockfd = sockfd;
    esp_tls_server_params_t server_params = {};
    server_params.set_server_cfg = &set_server_config;
    esp_err_t esp_ret = esp_create_mbedtls_handle(NULL, 0, cfg, tls, &server_params);
    if (esp_ret != ESP_OK) {
        ESP_LOGE(TAG, "create_ssl_handle failed, returned [0x%04X] (%s)", esp_ret, esp_err_to_name(esp_ret));
        ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, esp_ret);
        tls->conn_state = ESP_TLS_FAIL;
        return ESP_FAIL;
    }

    tls->read = esp_mbedtls_read;
    tls->write = esp_mbedtls_write;
    return ESP_OK;
}
int esp_mbedtls_server_session_continue_async(esp_tls_t *tls)
{
    int ret = mbedtls_ssl_handshake(&tls->ssl);
    if (ret != 0 && ret != ESP_TLS_ERR_SSL_WANT_READ && ret != ESP_TLS_ERR_SSL_WANT_WRITE) {
        ESP_LOGE(TAG, "mbedtls_ssl_handshake returned -0x%04X", -ret);
        mbedtls_print_error_msg(ret);
        ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_MBEDTLS, -ret);
        ESP_INT_EVENT_TRACKER_CAPTURE(tls->error_handle, ESP_TLS_ERR_TYPE_ESP, ESP_ERR_MBEDTLS_SSL_HANDSHAKE_FAILED);
        tls->conn_state = ESP_TLS_FAIL;
        return ret;
    }
    return ret;
}
void esp_mbedtls_server_session_delete(esp_tls_t *tls)
{
    if (tls != NULL) {
        esp_mbedtls_cleanup(tls);
        esp_tls_internal_event_tracker_destroy(tls->error_handle);
        free(tls);
    }
}
esp_tls_t *esp_tls_init(void)
{
    esp_tls_t *tls = (esp_tls_t *)calloc(1, sizeof(esp_tls_t));
    if (!tls) {
        return NULL;
    }
    tls->error_handle = esp_tls_internal_event_tracker_create();
    if (!tls->error_handle) {
        free(tls);
        return NULL;
    }
    _esp_tls_net_init(tls);
    tls->sockfd = -1;
#if CONFIG_MBEDTLS_SSL_PROTO_TLS1_3 && CONFIG_ESP_TLS_CLIENT_SESSION_TICKETS
    tls->client_session = NULL;
    tls->client_session_len = 0;
#endif // CONFIG_MBEDTLS_SSL_PROTO_TLS1_3 && CONFIG_ESP_TLS_CLIENT_SESSION_TICKETS
    return tls;
}
esp_err_t esp_tls_server_session_init(esp_tls_cfg_server_t *cfg, int sockfd, esp_tls_t *tls)
{
    return _esp_tls_server_session_init(cfg, sockfd, tls);
}
int esp_tls_server_session_continue_async(esp_tls_t *tls)
{
    return _esp_tls_server_session_continue_async(tls);
}
void esp_tls_server_session_delete(esp_tls_t *tls)
{
    return _esp_tls_server_session_delete(tls);
}
ssize_t esp_tls_get_bytes_avail(esp_tls_t *tls)
{
    return _esp_tls_get_bytes_avail(tls);
}
void *esp_tls_get_ssl_context(esp_tls_t *tls)
{
    return _esp_tls_get_ssl_context(tls);
}
esp_err_t esp_tls_set_conn_state(esp_tls_t *tls, esp_tls_conn_state_t conn_state)
{
    if (!tls || conn_state < ESP_TLS_INIT || conn_state > ESP_TLS_DONE) {
        ESP_LOGE(TAG, "Invalid arguments passed");
        return ESP_ERR_INVALID_ARG;
    }
    tls->conn_state = conn_state;
    return ESP_OK;
}
ssize_t esp_tls_conn_read(esp_tls_t *tls, void  *data, size_t datalen)
{
    if (!tls) {
        return -1;
    }
    if (!tls->read) {
        return -1;
    }
#if CONFIG_MBEDTLS_DYNAMIC_BUFFER
    if (tls->is_tls && tls->conn_state != ESP_TLS_DONE) {
        ESP_LOGE(TAG, "TLS handshake has not completed, read operation not permitted");
        return -1;
    }
#endif
    return tls->read(tls, (char *)data, datalen);
}
ssize_t esp_tls_conn_write(esp_tls_t *tls, const void  *data, size_t datalen)
{
    if (!tls || !data) {
        return -1;
    }
    if (!tls->write) {
        return -1;
    }
#if CONFIG_MBEDTLS_DYNAMIC_BUFFER
    if (tls->is_tls && tls->conn_state != ESP_TLS_DONE) {
        ESP_LOGE(TAG, "TLS handshake has not completed, write operation not permitted");
        return -1;
    }
#endif
    return tls->write(tls, (char *)data, datalen);
}

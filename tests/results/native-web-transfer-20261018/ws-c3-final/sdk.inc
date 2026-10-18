static size_t httpd_recv_pending(httpd_req_t *r, char *buf, size_t buf_len)
{
    struct httpd_req_aux *ra = r->aux;
    size_t offset = sizeof(ra->sd->pending_data) - ra->sd->pending_len;

    /* buf_len must not be greater than remaining_len */
    buf_len = MIN(ra->sd->pending_len, buf_len);
    memcpy(buf, ra->sd->pending_data + offset, buf_len);

    ra->sd->pending_len -= buf_len;
    return buf_len;
}

int httpd_recv_with_opt(httpd_req_t *r, char *buf, size_t buf_len, httpd_recv_opt_t opt)
{
    ESP_LOGD(TAG, LOG_FMT("requested length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(buf_len));

    size_t pending_len = 0;
    struct httpd_req_aux *ra = r->aux;

    /* First fetch pending data from local buffer */
    if (ra->sd->pending_len > 0) {
        ESP_LOGD(TAG, LOG_FMT("pending length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(ra->sd->pending_len));
        pending_len = httpd_recv_pending(r, buf, buf_len);
        buf     += pending_len;
        buf_len -= pending_len;

        /* If buffer filled then no need to recv.
         * If asked to halt after receiving pending data then
         * return with received length */
        if (!buf_len || opt == HTTPD_RECV_OPT_HALT_AFTER_PENDING) {
            return pending_len;
        }
    }

    /* Receive data of remaining length */
    size_t recv_len = pending_len;
    do {
        int ret = ra->sd->recv_fn(ra->sd->handle, ra->sd->fd, buf, buf_len, 0);
        if (ret <= 0) {
            ESP_LOGD(TAG, LOG_FMT("error in recv_fn"));
            if ((ret == HTTPD_SOCK_ERR_TIMEOUT) && (pending_len != 0)) {
                /* If recv() timeout occurred, but pending data is
                * present, return length of pending data.
                * This behavior is similar to that of socket recv()
                * function, which, in case has only partially read the
                * requested length, due to timeout, returns with read
                * length, rather than error */
                return pending_len;
            }
            return ret;
        }

        recv_len += ret;
        buf      += ret;
        buf_len  -= ret;
    } while (buf_len > 0 && opt == HTTPD_RECV_OPT_BLOCKING);

    ESP_LOGD(TAG, LOG_FMT("received length = %"NEWLIB_NANO_COMPAT_FORMAT), NEWLIB_NANO_COMPAT_CAST(recv_len));
    return recv_len;
}


#define HTTPD_WS_CONTINUE       0x00U
#define HTTPD_WS_FIN_BIT        0x80U
#define HTTPD_WS_RSV1_BIT       0x40U
#define HTTPD_WS_RSV2_BIT       0x20U
#define HTTPD_WS_RSV3_BIT       0x10U
#define HTTPD_WS_OPCODE_BITS    0x0fU
#define HTTPD_WS_MASK_BIT       0x80U
#define HTTPD_WS_LENGTH_BITS    0x7fU

/* RFC 6455 §7.4 close status codes used for protocol-error Close frames */
#define HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR 1002U
#define HTTPD_WS_CLOSE_CODE_TOO_BIG       1009U

static esp_err_t httpd_ws_check_req(httpd_req_t *req)
{
    /* Probe if input parameters are valid or not */
    if (!req || !req->aux) {
        ESP_LOGW(TAG, LOG_FMT("Argument is null"));
        return ESP_ERR_INVALID_ARG;
    }

    /* Detect handshake - reject if handshake was NOT YET performed */
    struct httpd_req_aux *req_aux = req->aux;
    if (!req_aux->sd->ws_handshake_done) {
        ESP_LOGW(TAG, LOG_FMT("State is invalid - No handshake performed"));
        return ESP_ERR_INVALID_STATE;
    }

    return ESP_OK;
}

/* RFC 6455 §5.5: opcodes 0x8-0xA (CLOSE, PING, PONG) are control frames.
 * Reserved control opcodes 0xB-0xF are rejected earlier in httpd_ws_get_frame_type,
 * so an explicit whitelist is used here instead of a `>= CLOSE` range compare. */
static inline bool httpd_ws_is_control_opcode(httpd_ws_type_t type)
{
    return type == HTTPD_WS_TYPE_CLOSE ||
           type == HTTPD_WS_TYPE_PING  ||
           type == HTTPD_WS_TYPE_PONG;
}

/* Mark the session's pending frame as a CLOSE so the request layer tears the
 * socket down after the current request completes. */
static inline void httpd_ws_mark_closing(struct httpd_req_aux *aux)
{
    aux->ws_final = true;
    aux->ws_type = HTTPD_WS_TYPE_CLOSE;
}

/* Send a Close frame with the given status code and mark the session as closing.
 * Always returns ESP_FAIL so callers can write: return httpd_ws_fail_connection(...).
 * RFC 6455 §7.1.7
 */
static esp_err_t httpd_ws_fail_connection(httpd_req_t *req, uint16_t close_code)
{
    esp_err_t ret = ESP_FAIL;
    if (!req || !req->aux) {
        return ret;
    }

    struct httpd_req_aux *aux = req->aux;
    if (!aux->sd) {
        return ret;
    }

    httpd_ws_mark_closing(aux);

    bool already_closing = aux->sd->ws_close;
    aux->sd->ws_close = true;

    if (aux->sd->ws_handshake_done && !already_closing) {
        uint8_t close_payload[2] = {
            (uint8_t)(close_code >> 8U),
            (uint8_t)(close_code & 0xffU),
        };
        httpd_ws_frame_t close_frame = {
            .final = true,
            .fragmented = false,
            .type = HTTPD_WS_TYPE_CLOSE,
            .payload = close_payload,
            .len = sizeof(close_payload),
        };
        esp_err_t ret = httpd_ws_send_frame(req, &close_frame);
        if (ret != ESP_OK) {
            ESP_LOGW(TAG, LOG_FMT("Failed to send CLOSE frame with code %u"), close_code);
        }
    }

    return ret;
}

static esp_err_t httpd_ws_unmask_payload(uint8_t *payload, size_t len, const uint8_t *mask_key, size_t mask_offset)
{
    if (len < 1 || !payload) {
        ESP_LOGW(TAG, LOG_FMT("Invalid payload provided"));
        return ESP_ERR_INVALID_ARG;
    }

    for (size_t idx = 0; idx < len; idx++) {
        payload[idx] = (payload[idx] ^ mask_key[(idx + mask_offset) % 4]);
    }

    return ESP_OK;
}

static esp_err_t httpd_ws_recv_frame_internal(httpd_req_t *req, httpd_ws_frame_t *frame, size_t max_len, bool partial)
{
    esp_err_t ret = httpd_ws_check_req(req);
    if (ret != ESP_OK) {
        return ret;
    }

    struct httpd_req_aux *aux = req->aux;
    if (aux == NULL) {
        ESP_LOGW(TAG, LOG_FMT("Invalid Aux pointer"));
        return ESP_ERR_INVALID_ARG;
    }

    if (!frame) {
        ESP_LOGW(TAG, LOG_FMT("Frame pointer is invalid"));
        return ESP_ERR_INVALID_ARG;
    }
    /* If frame len is 0, will get frame len from req. Otherwise regard frame len already achieved by calling httpd_ws_recv_frame before */
    if (frame->len == 0) {
        /* Assign the frame info from the previous reading */
        frame->type = aux->ws_type;
        frame->final = aux->ws_final;

        /* Grab the second byte */
        uint8_t second_byte = 0;
        int recv_ret = httpd_recv_with_opt(req, (char *)&second_byte, sizeof(second_byte), HTTPD_RECV_OPT_BLOCKING);
        if (recv_ret != (int)sizeof(second_byte)) {
            ESP_LOGW(TAG, LOG_FMT("Failed to receive the second byte"));
            return ESP_FAIL;
        }

        /* Parse the second byte */
        /* Please refer to RFC6455 Section 5.2 for more details */
        bool masked = (second_byte & HTTPD_WS_MASK_BIT) != 0;

        /* Interpret length */
        uint8_t init_len = second_byte & HTTPD_WS_LENGTH_BITS;

#if CONFIG_HTTPD_WS_STRICTER_RFC6455
        /* RFC 6455 §5.5: control frames MUST have payload <= 125 bytes and
         * therefore MUST NOT use the 16- or 64-bit extended length encodings.
         */
        if (httpd_ws_is_control_opcode(frame->type) && init_len > 125) {
            ESP_LOGE(TAG, LOG_FMT("Invalid control frame length encoding"));
            return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
        }
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */

        if (init_len < 126) {
            /* Case 1: If length is 0-125, then this length bit is 7 bits */
            frame->len = init_len;
        } else if (init_len == 126) {
            /* Case 2: If length byte is 126, then this frame's length bit is 16 bits */
            uint8_t length_bytes[2] = { 0 };
            recv_ret = httpd_recv_with_opt(req, (char *)length_bytes, sizeof(length_bytes), HTTPD_RECV_OPT_BLOCKING);
            if (recv_ret != (int)sizeof(length_bytes)) {
                ESP_LOGW(TAG, LOG_FMT("Failed to receive 2 bytes length"));
                return ESP_FAIL;
            }

            uint16_t length = ((uint16_t)(length_bytes[0] << 8U) | (length_bytes[1]));
#if CONFIG_HTTPD_WS_STRICTER_RFC6455
            /* RFC 6455 §5.2: encodings must be minimal; a value < 126 MUST use 7-bit form. */
            if (length < 126) {
                ESP_LOGE(TAG, LOG_FMT("Invalid WS frame length: non-minimal 16-bit encoding"));
                return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
            }
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */
            frame->len = length;
        } else if (init_len == 127) {
            /* Case 3: If length is byte 127, then this frame's length bit is 64 bits */
            uint8_t length_bytes[8] = { 0 };
            recv_ret = httpd_recv_with_opt(req, (char *)length_bytes, sizeof(length_bytes), HTTPD_RECV_OPT_BLOCKING);
            if (recv_ret != (int)sizeof(length_bytes)) {
                ESP_LOGW(TAG, LOG_FMT("Failed to receive 8 bytes length"));
                return ESP_FAIL;
            }

#if CONFIG_HTTPD_WS_STRICTER_RFC6455
            /* RFC 6455 §5.2: MSB must be 0 */
            if (length_bytes[0] & 0x80) {
                ESP_LOGE(TAG, LOG_FMT("Invalid WS frame length: MSB must be 0"));
                return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
            }
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */

            uint64_t length = (uint64_t)length_bytes[0] << 56U |
                    (uint64_t)length_bytes[1] << 48U |
                    (uint64_t)length_bytes[2] << 40U |
                    (uint64_t)length_bytes[3] << 32U |
                    (uint64_t)length_bytes[4] << 24U |
                    (uint64_t)length_bytes[5] << 16U |
                    (uint64_t)length_bytes[6] <<  8U |
                    (uint64_t)length_bytes[7];
#if CONFIG_HTTPD_WS_STRICTER_RFC6455
            /* Encoding must be minimal; values <= UINT16_MAX MUST use 16-bit form */
            if (length <= UINT16_MAX) {
                ESP_LOGE(TAG, LOG_FMT("Invalid WS frame length: non-minimal 64-bit encoding"));
                return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
            }
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */
            if (length > SIZE_MAX) {
                ESP_LOGE(TAG, LOG_FMT("Invalid WS frame length: too large for platform"));
                return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_TOO_BIG);
            }
            frame->len = (size_t)length;
        }
        frame->left_len = frame->len;

        /* If this frame is masked, dump the mask as well */
        if (masked) {
            recv_ret = httpd_recv_with_opt(req, (char *)aux->mask_key, sizeof(aux->mask_key), HTTPD_RECV_OPT_BLOCKING);
            if (recv_ret != (int)sizeof(aux->mask_key)) {
                ESP_LOGW(TAG, LOG_FMT("Failed to receive mask key"));
                return ESP_FAIL;
            }
        } else {
            /* If the WS frame from client to server is not masked, it should be rejected.
             * Please refer to RFC6455 Section 5.2 for more details. */
            ESP_LOGE(TAG, LOG_FMT("WS frame is not properly masked."));
#if CONFIG_HTTPD_WS_STRICTER_RFC6455
            httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */
            return ESP_ERR_INVALID_STATE;
        }
    }
    /* If max_len is 0, regard it OK for userspace to get frame len */
    if (max_len == 0) {
        ESP_LOGD(TAG, "regard max_len == 0 is OK for user to get frame len");
        return ESP_OK;
    }
    if (frame->len > max_len) {
        /* When reading entire packet at once, we only accept the incoming packet length that is smaller than the max_len (or it will overflow the buffer!) */
        if (!partial) {
            ESP_LOGW(TAG, LOG_FMT("WS Message too long"));
            return ESP_ERR_INVALID_SIZE;
        }
        ESP_LOGD(TAG, LOG_FMT("WS Message too long. User will have to call read again"));
    }

    /* Receive buffer */
    /* If there's nothing to receive, return and stop here. */
    if (frame->left_len == 0) {
        return ESP_OK;
    }

    if (frame->payload == NULL) {
        ESP_LOGW(TAG, LOG_FMT("Payload buffer is null"));
        return ESP_FAIL;
    }

    size_t left_len = (max_len < frame->left_len) ? max_len : frame->left_len;
    size_t offset = 0;

    while (left_len > 0) {
        int read_len = httpd_recv_with_opt(req, (char *)frame->payload + offset, left_len, HTTPD_RECV_OPT_NONE);
        if (read_len <= 0) {
            ESP_LOGW(TAG, LOG_FMT("Failed to receive payload"));
            return ESP_FAIL;
        }
        offset += read_len;
        left_len -= read_len;

        ESP_LOGD(TAG, "Frame length: %"NEWLIB_NANO_COMPAT_FORMAT", Bytes Read: %"NEWLIB_NANO_COMPAT_FORMAT, NEWLIB_NANO_COMPAT_CAST(frame->len), NEWLIB_NANO_COMPAT_CAST(offset));
    }

    size_t mask_offset = frame->len - frame->left_len;
    frame->left_len -= offset;

    /* Unmask payload */
    httpd_ws_unmask_payload(frame->payload, offset, aux->mask_key, mask_offset);

    return ESP_OK;
}

esp_err_t httpd_ws_recv_frame(httpd_req_t *req, httpd_ws_frame_t *frame, size_t max_len) {
    return httpd_ws_recv_frame_internal(req, frame, max_len, false);
}

esp_err_t httpd_ws_recv_frame_part(httpd_req_t *req, httpd_ws_frame_t *frame, size_t max_len) {
    return httpd_ws_recv_frame_internal(req, frame, max_len, true);
}

esp_err_t httpd_ws_send_frame(httpd_req_t *req, httpd_ws_frame_t *frame)
{
    esp_err_t ret = httpd_ws_check_req(req);
    if (ret != ESP_OK) {
        return ret;
    }
    return httpd_ws_send_frame_async(req->handle, httpd_req_to_sockfd(req), frame);
}

esp_err_t httpd_ws_send_frame_async(httpd_handle_t hd, int fd, httpd_ws_frame_t *frame)
{
    if (!frame) {
        ESP_LOGW(TAG, LOG_FMT("Argument is invalid"));
        return ESP_ERR_INVALID_ARG;
    }

    struct sock_db *sess = httpd_sess_get(hd, fd);
    if (!sess) {
        return ESP_ERR_INVALID_ARG;
    }

#if CONFIG_HTTPD_WS_STRICTER_RFC6455
    /* RFC 6455 §1.4 / §5.5.1: once a CLOSE has been sent or received the
     * endpoint MUST NOT transmit any further data frames. Only the CLOSE
     * frame itself is permitted so that an in-progress fail-the-connection
     * or close-handshake response can still be emitted. */
    if (sess->ws_close && frame->type != HTTPD_WS_TYPE_CLOSE) {
        ESP_LOGW(TAG, LOG_FMT("Session is closing; refusing non-CLOSE frame (type=0x%02X)"), frame->type);
        return ESP_ERR_INVALID_STATE;
    }
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */

    /* Prepare Tx buffer - maximum length is 14, which includes 2 bytes header, 8 bytes length, 4 bytes mask key */
    uint8_t tx_len = 0;
    uint8_t header_buf[10] = {0 };
    /* Set the `FIN` bit by default if message is not fragmented. Else, set it as per the `final` field */
    header_buf[0] |= (!frame->fragmented) ? HTTPD_WS_FIN_BIT : (frame->final? HTTPD_WS_FIN_BIT: HTTPD_WS_CONTINUE);
    header_buf[0] |= frame->type; /* Type (opcode): 4 bits */

    if (frame->len <= 125) {
        header_buf[1] = frame->len & 0x7fU; /* Length for 7 bits */
        tx_len = 2;
    } else if (frame->len > 125 && frame->len <= UINT16_MAX) {
        header_buf[1] = 126;                /* Length for 16 bits */
        header_buf[2] = (frame->len >> 8U) & 0xffU;
        header_buf[3] = frame->len & 0xffU;
        tx_len = 4;
    } else {
        header_buf[1] = 127;                /* Length for 64 bits */
        uint8_t shift_idx = sizeof(uint64_t) - 1; /* Shift index starts at 7 */
        uint64_t len64 = frame->len; /* Raise variable size to make sure we won't shift by more bits
                                      * than the length has (to avoid undefined behaviour) */
        for (int8_t idx = 2; idx <= 9; idx++) {
            /* Now do shifting (be careful of endianness, i.e. when buffer index is 2, frame length shift index is 7) */
            header_buf[idx] = (len64 >> (shift_idx * 8)) & 0xffU;
            shift_idx--;
        }
        tx_len = 10;
    }

    /* WebSocket server does not required to mask response payload, so leave the MASK bit as 0. */
    header_buf[1] &= (~HTTPD_WS_MASK_BIT);

    /* Send off header */
    if (sess->send_fn(hd, fd, (const char *)header_buf, tx_len, 0) < 0) {
        ESP_LOGW(TAG, LOG_FMT("Failed to send WS header"));
        return ESP_FAIL;
    }

    /* Send off payload */
    if(frame->len > 0 && frame->payload != NULL) {
        if (sess->send_fn(hd, fd, (const char *)frame->payload, frame->len, 0) < 0) {
            ESP_LOGW(TAG, LOG_FMT("Failed to send WS payload"));
            return ESP_FAIL;
        }
    }

    return ESP_OK;
}

esp_err_t httpd_ws_get_frame_type(httpd_req_t *req)
{
    esp_err_t ret = httpd_ws_check_req(req);
    if (ret != ESP_OK) {
        return ret;
    }

    struct httpd_req_aux *aux = req->aux;
    if (aux == NULL) {
        ESP_LOGW(TAG, LOG_FMT("Invalid Aux pointer"));
        return ESP_ERR_INVALID_ARG;
    }

    struct sock_db *sd = aux->sd;
    if (sd == NULL) {
        ESP_LOGW(TAG, LOG_FMT("Invalid sd pointer"));
        return ESP_ERR_INVALID_ARG;
    }

    /* Read the first byte from the frame to get the FIN flag and Opcode */
    /* Please refer to RFC6455 Section 5.2 for more details */
    uint8_t first_byte = 0;
    int recv_ret = httpd_recv_with_opt(req, (char *)&first_byte, sizeof(first_byte), HTTPD_RECV_OPT_BLOCKING);
    if (recv_ret != (int)sizeof(first_byte)) {
        /* If we fail to read exactly one byte, this socket FD is invalid or the frame header is incomplete. */
        /* Here we mark it as a Close message and close it later. */
        ESP_LOGW(TAG, LOG_FMT("Failed to read header byte (socket FD invalid), closing socket now"));
        httpd_ws_mark_closing(aux);
        return ESP_OK;
    }

    ESP_LOGD(TAG, LOG_FMT("First byte received: 0x%02X"), first_byte);

    /* Decode the FIN flag and Opcode from the byte */
    aux->ws_final = (first_byte & HTTPD_WS_FIN_BIT) != 0;
    aux->ws_type = (first_byte & HTTPD_WS_OPCODE_BITS);

#if CONFIG_HTTPD_WS_STRICTER_RFC6455
    /* RFC 6455 §5.2: RSV bits MUST be 0 unless an extension has been negotiated.
     * This implementation does not support extensions, so any set RSV bit is an error.
     */
    if (first_byte & (HTTPD_WS_RSV1_BIT | HTTPD_WS_RSV2_BIT | HTTPD_WS_RSV3_BIT)) {
        ESP_LOGE(TAG, LOG_FMT("RSV1, RSV2 or RSV3 bits are set, closing connection"));
        return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
    }

    /* RFC 6455 §5.2: opcodes 0x3–0x7 and 0xB–0xF are reserved and must not be used. */
    switch (aux->ws_type) {
    case HTTPD_WS_TYPE_CONTINUE:
    case HTTPD_WS_TYPE_TEXT:
    case HTTPD_WS_TYPE_BINARY:
    case HTTPD_WS_TYPE_CLOSE:
    case HTTPD_WS_TYPE_PING:
    case HTTPD_WS_TYPE_PONG:
        break;
    default:
        ESP_LOGE(TAG, LOG_FMT("Invalid WS frame type: 0x%02X"), aux->ws_type);
        return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
    }

    /* RFC 6455 §5.5: control frames MUST NOT be fragmented (FIN bit must be set). */
    if (httpd_ws_is_control_opcode(aux->ws_type) && !aux->ws_final) {
        ESP_LOGE(TAG, LOG_FMT("Invalid fragmented control frame: 0x%02X"), aux->ws_type);
        return httpd_ws_fail_connection(req, HTTPD_WS_CLOSE_CODE_PROTOCOL_ERROR);
    }
#endif /* CONFIG_HTTPD_WS_STRICTER_RFC6455 */

    /* If userspace requests control frames, do not deal with the control frames */
    if (!sd->ws_control_frames) {
        ESP_LOGD(TAG, LOG_FMT("Handler not requests control frames"));

        /* Reply to PING. For PONG and CLOSE, it will be handled elsewhere. */
        if (aux->ws_type == HTTPD_WS_TYPE_PING) {
            ESP_LOGD(TAG, LOG_FMT("Got a WS PING frame, Replying PONG..."));

            /* Read the rest of the PING frame, for PONG to reply back. */
            /* Please refer to RFC6455 Section 5.5.2 for more details */
            httpd_ws_frame_t frame;
            uint8_t frame_buf[128] = { 0 };
            memset(&frame, 0, sizeof(httpd_ws_frame_t));
            frame.payload = frame_buf;

            if (httpd_ws_recv_frame(req, &frame, 126) != ESP_OK) {
                ESP_LOGD(TAG, LOG_FMT("Cannot receive the full PING frame"));
                return ESP_ERR_INVALID_STATE;
            }

            /* Now turn the frame to PONG */
            frame.type = HTTPD_WS_TYPE_PONG;
            return httpd_ws_send_frame(req, &frame);
        } else if (aux->ws_type == HTTPD_WS_TYPE_CLOSE) {
            ESP_LOGD(TAG, LOG_FMT("Got a WS CLOSE frame, Replying CLOSE..."));

            /* Read the rest of the CLOSE frame and response */
            /* Please refer to RFC6455 Section 5.5.1 for more details */
            httpd_ws_frame_t frame;
            uint8_t frame_buf[128] = { 0 };
            memset(&frame, 0, sizeof(httpd_ws_frame_t));
            frame.payload = frame_buf;

            if (httpd_ws_recv_frame(req, &frame, 126) != ESP_OK) {
                ESP_LOGD(TAG, LOG_FMT("Cannot receive the full CLOSE frame"));
                return ESP_ERR_INVALID_STATE;
            }

            frame.len = 0;
            frame.type = HTTPD_WS_TYPE_CLOSE;
            frame.payload = NULL;
            return httpd_ws_send_frame(req, &frame);
        }
    }
    return ESP_OK;
}

static void httpd_ws_send_cb(void *arg)
{
    async_transfer_t *trans = arg;

    esp_err_t err = httpd_ws_send_frame_async(trans->handle, trans->socket, &trans->frame);

    if (trans->blocking) {
        xEventGroupSetBits(trans->transfer_done, err ? WS_SEND_FAILED : WS_SEND_OK);
    } else if (trans->callback) {
        trans->callback(err, trans->socket, trans->arg);
    }

    free(trans);
}

esp_err_t httpd_ws_send_data_async(httpd_handle_t handle, int socket, httpd_ws_frame_t *frame,
                                   transfer_complete_cb callback, void *arg)
{
    async_transfer_t *transfer = calloc(1, sizeof(async_transfer_t));
    if (transfer == NULL) {
        return ESP_ERR_NO_MEM;
    }

    transfer->arg = arg;
    transfer->callback = callback;
    transfer->handle = handle;
    transfer->socket = socket;
    memcpy(&transfer->frame, frame, sizeof(httpd_ws_frame_t));

    esp_err_t err = httpd_queue_work(handle, httpd_ws_send_cb, transfer);

    if (err) {
        free(transfer);
        return err;
    }

    return ESP_OK;
}


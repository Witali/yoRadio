size_t httpd_req_get_url_query_len(httpd_req_t *r)
{
    if (r == NULL) {
        return 0;
    }

    if (!httpd_valid_req(r)) {
        return 0;
    }

    if (r->uri[0] == '\0') {
        ESP_LOGD(TAG, "uri is empty");
        return 0;
    }

    struct httpd_req_aux   *ra  = r->aux;
    struct http_parser_url *res = &ra->url_parse_res;

    /* Check if query field is present in the URL */
    if (res->field_set & (1 << UF_QUERY)) {
        return res->field_data[UF_QUERY].len;
    }
    return 0;
}
esp_err_t httpd_req_get_url_query_str(httpd_req_t *r, char *buf, size_t buf_len)
{
    if (r == NULL || buf == NULL) {
        return ESP_ERR_INVALID_ARG;
    }

    if (!httpd_valid_req(r)) {
        return ESP_ERR_HTTPD_INVALID_REQ;
    }

    if (r->uri[0] == '\0') {
        ESP_LOGD(TAG, "uri is empty");
        return ESP_FAIL;
    }

    struct httpd_req_aux   *ra  = r->aux;
    struct http_parser_url *res = &ra->url_parse_res;

    /* Check if query field is present in the URL */
    if (res->field_set & (1 << UF_QUERY)) {
        const char *qry = r->uri + res->field_data[UF_QUERY].off;

        /* Query data length does not include terminating null */
        size_t data_len = res->field_data[UF_QUERY].len;

        /* Copy data to the caller's buffer. */
        size_t copy_len = MIN(data_len, buf_len - 1);
        if (copy_len < data_len) {
            return ESP_ERR_HTTPD_RESULT_TRUNC;
        }
        memcpy(buf, qry, copy_len);
        buf[copy_len] = '\0';

        return ESP_OK;
    }
    return ESP_ERR_NOT_FOUND;
}

"""Generate project-scoped RFC6455 HTTPD sources from exactly pinned SDK files.

Generated sources retain Espressif Apache-2.0 notices. Shared SDK installations
are read-only. Unknown source bytes fail closed rather than guessing patches.
"""
import argparse
import hashlib
import json
from pathlib import Path

PINNED = {
    '6.0.2': {'httpd_ws.c': '50bc91f7389b40828ab949bac11481d28545a4da2d87d0b1ee99ec0d04645fd3',
              'httpd_parse.c': '5234fd5fc3b566532bf79a6c787664d5077d0aa03001a2d63c0999f063282e90'},
    '6.1': {'httpd_ws.c': '744304f779c54064d6453d2af3dcabde36c3b255a7930cbd903c0e8e4225eb3a',
            'httpd_parse.c': 'e32809f8f0bf820382759756b7fc3bb73fb4cf6ff3410d3fc26f27fc6e6cd280'},
}
PINNED_HEADERS = {
    '6.0.2': {'src/esp_httpd_priv.h': '106a3bf927a885892f66514c6a4075c04e04db068fb64ca11dd8ca4b4253dfc8',
              'include/esp_http_server.h': '3a40def13721f5cb0696308ddefd4c07d4cf986c00c915aef478715fec302124'},
    '6.1': {'src/esp_httpd_priv.h': 'e7032f9425979c2063548360249f58da2d945c86ed3bb6fafd3e5cf6101a708a',
            'include/esp_http_server.h': '70cc75089d4a6a443e88d01cdbc8dff829c952d03bdece657da66d266294d8c7'},
}


def replace(source, old, new):
    assert source.count(old) == 1, old[:100]
    return source.replace(old, new)


def function_span(source, name):
    import re
    match = re.search(r'^(?:static[ \t]+)?(?:inline[ \t]+)?[A-Za-z_]\w*[ \t*]+'+name+r'\(', source, re.M)
    assert match, name
    brace = source.index('{', match.start()); depth = 1; end = brace + 1
    while depth:
        depth += (source[end] == '{') - (source[end] == '}'); end += 1
    return match.start(), end


def generate(sdk, output):
    sdk = Path(sdk); output = Path(output)
    originals = {name:(sdk/'components/esp_http_server/src'/name).read_bytes()
                 for name in ['httpd_ws.c', 'httpd_parse.c']}
    hashes = {name:hashlib.sha256(data).hexdigest() for name, data in originals.items()}
    versions = [version for version, expected in PINNED.items() if hashes == expected]
    if len(versions) != 1:
        raise RuntimeError('Unsupported HTTPD source hashes: '+json.dumps(hashes))
    version = versions[0]
    header_hashes = {name:hashlib.sha256((sdk/'components/esp_http_server'/name).read_bytes()).hexdigest()
                     for name in PINNED_HEADERS[version]}
    if header_hashes != PINNED_HEADERS[version]:
        raise RuntimeError('Unsupported matching HTTPD headers: '+json.dumps(header_hashes))
    ws, parse = (originals[name].decode().replace('\r\n', '\n')
                 for name in ['httpd_ws.c', 'httpd_parse.c'])
    for name in ['ws', 'parse']:
        source = ws if name == 'ws' else parse
        source = replace(source, '#include "esp_httpd_priv.h"',
                         '#include "esp_httpd_priv.h"\n#include "native_httpd_headers.h"')
        if name == 'ws': ws = source
        else: parse = source

    # Actual SDK callbacks exclude folding CRLF from callback lengths. Summing
    # lengths therefore moves the field terminator into the last value bytes.
    # Track the physical span instead, retaining valid implied LWS for parsing.
    value_start, value_end = function_span(parse, 'cb_header_value')
    value_callback = replace(parse[value_start:value_end],
        '    parser_data->last.length += length;',
        '''    if (length) parser_data->last.length =
        (size_t)(at - parser_data->last.at) + length;''')
    parse = parse[:value_start]+value_callback+parse[value_end:]
    if version == '6.0.2':
        parse = replace(parse, '''    /* In absence of body/chunked encoding, http_parser sets content_len to -1 */
    r->content_len = ((int)parser->content_length != -1 ?
                      parser->content_length : 0);''', '''    /* Preserve the same uint32 target body bound as the pinned C3 SDK.
     * The absent-length sentinel must be compared before any narrowing. */
    if (parser->content_length != UINT64_MAX) {
        if (parser->content_length > UINT32_MAX) {
            parser_data->error = HTTPD_413_CONTENT_TOO_LARGE;
            parser_data->status = PARSING_FAILED;
            return ESP_FAIL;
        }
        r->content_len = (size_t)parser->content_length;
    } else {
        r->content_len = 0;
    }''')
    # An empty Content-Length leaves the parser's absent-length sentinel even
    # though its field-present flag is set. It is malformed, not an absent body.
    headers_start, headers_end = function_span(parse, 'cb_headers_complete')
    headers = parse[headers_start:headers_end]
    location = headers.index('    if (parser->content_length != ')
    headers = headers[:location]+'''    if ((parser->flags & F_CONTENTLENGTH) &&
        parser->content_length == UINT64_MAX) {
        parser_data->error = HTTPD_400_BAD_REQUEST;
        parser_data->status = PARSING_FAILED;
        return ESP_FAIL;
    }
'''+headers[location:]
    parse = parse[:headers_start]+headers+parse[headers_end:]

    # Reject HTTP/1.0 before request-line bytes are discarded. Upgrade and
    # Connection are HTTP token lists, including combined/repeated fields.
    start = parse.index('        /* If there\'s no "Upgrade" header field,')
    end = parse.index('        /* Now set handshake flag to true */', start)
    parse = parse[:start]+'''        if (!(parser->http_major == 1 && parser->http_minor == 1) ||
            r->method != HTTP_GET ||
            !native_httpd_header_token(r, "Upgrade", "websocket") ||
            !native_httpd_header_token(r, "Connection", "upgrade")) {
            parser_data->error = HTTPD_400_BAD_REQUEST;
            parser_data->status = PARSING_FAILED;
            return ESP_FAIL;
        }

'''+parse[end:]
    # HTTPD's owner deletes this exact session after the current request. Never
    # enqueue its sock_db pointer and then also delete it on an error return.
    start = parse.index('#if CONFIG_HTTPD_WS_SUPPORT\n    /* Close the socket when a WebSocket Close request is received */')
    end = parse.index('#endif', start)+len('#endif')
    parse = parse[:start]+'''    /* Closing WebSocket sessions are returned to the owning HTTPD loop
     * by httpd_req_new/httpd_req_delete. No deferred session-pointer close. */'''+parse[end:]
    parse = replace(parse, '''    httpd_req_cleanup(r);
    return ESP_OK;
}

/* Validates the request''', '''#if CONFIG_HTTPD_WS_SUPPORT
    bool native_ws_closing = ra->sd && ra->sd->ws_close;
#else
    bool native_ws_closing = false;
#endif
    httpd_req_cleanup(r);
    return native_ws_closing ? ESP_FAIL : ESP_OK;
}

/* Validates the request''')
    parse = replace(parse, '''            ESP_LOGD(TAG, LOG_FMT("WS was marked close"));
            return ESP_OK;''', '''            ESP_LOGD(TAG, LOG_FMT("WS was marked close"));
            httpd_req_cleanup(r);
            return ESP_FAIL;''')

    begin, _ = function_span(ws, 'httpd_ws_respond_server_handshake')
    anchor = ws.index('    /* Detect WS version existence */', begin) if version == '6.0.2' else ws.index('#if CONFIG_HTTPD_WS_STRICTER_RFC6455', begin)
    ws = ws[:anchor]+'''    if (native_httpd_handshake_validate(req) != ESP_OK) return ESP_FAIL;

'''+ws[anchor:]
    start = ws.index('    /* Detect WS version existence */', begin) if version == '6.0.2' else ws.index('#if CONFIG_HTTPD_WS_STRICTER_RFC6455', begin)
    end = ws.index('    /* Prepare server key (Sec-WebSocket-Accept)', start)
    ws = ws[:start]+'''    char sec_key_encoded[25];
    if (!native_httpd_header(req, "Sec-WebSocket-Key", sec_key_encoded,
                            sizeof(sec_key_encoded))) return ESP_FAIL;

'''+ws[end:]
    if version == '6.0.2':
        # Minimal upstream 6.1 frame validation, without its changed partial-read ABI.
        insertion = ws.index('static esp_err_t httpd_ws_unmask_payload(')
        ws = ws[:insertion]+'''static inline bool httpd_ws_is_control_opcode(httpd_ws_type_t type) {
    return type == HTTPD_WS_TYPE_CLOSE || type == HTTPD_WS_TYPE_PING || type == HTTPD_WS_TYPE_PONG;
}

static esp_err_t httpd_ws_fail_connection(httpd_req_t *req, uint16_t code) {
    struct httpd_req_aux *aux = req->aux;
    bool already = aux->sd->ws_close;
    aux->ws_final = true; aux->ws_type = HTTPD_WS_TYPE_CLOSE;
    aux->sd->ws_close = true;
    if (aux->sd->ws_handshake_done && !already) {
        uint8_t payload[2] = {(uint8_t)(code >> 8), (uint8_t)code};
        httpd_ws_frame_t frame = {.final=true,.type=HTTPD_WS_TYPE_CLOSE,
            .payload=payload,.len=sizeof(payload)};
        (void)httpd_ws_send_frame(req, &frame);
    }
    return ESP_FAIL;
}

'''+ws[insertion:]
        ws = replace(ws, '        uint8_t init_len = second_byte & HTTPD_WS_LENGTH_BITS;', '''        uint8_t init_len = second_byte & HTTPD_WS_LENGTH_BITS;
        if (httpd_ws_is_control_opcode(frame->type) && init_len > 125)
            return httpd_ws_fail_connection(req, 1002);''')
        ws = replace(ws, '            frame->len = ((uint32_t)(length_bytes[0] << 8U) | (length_bytes[1]));', '''            frame->len = ((uint32_t)(length_bytes[0] << 8U) | (length_bytes[1]));
            if (frame->len < 126) return httpd_ws_fail_connection(req, 1002);''')
        ws = replace(ws, '            frame->len = (((uint64_t)length_bytes[0] << 56U) |', '''            if (length_bytes[0] & 0x80U) return httpd_ws_fail_connection(req, 1002);
            uint64_t native_length = (((uint64_t)length_bytes[0] << 56U) |''')
        ws = replace(ws, '                    ((uint64_t)length_bytes[7]));', '''                    ((uint64_t)length_bytes[7]));
            if (native_length <= UINT16_MAX) return httpd_ws_fail_connection(req, 1002);
            if (native_length > SIZE_MAX) return httpd_ws_fail_connection(req, 1009);
            frame->len = (size_t)native_length;''')
        ws = replace(ws, '''            ESP_LOGW(TAG, LOG_FMT("WS frame is not properly masked."));
            return ESP_ERR_INVALID_STATE;''', '''            ESP_LOGW(TAG, LOG_FMT("WS frame is not properly masked."));
            return httpd_ws_fail_connection(req, 1002);''')
        ws = replace(ws, '    /* If userspace requests control frames, do not deal with the control frames */', '''    if (first_byte & 0x70U) return httpd_ws_fail_connection(req, 1002);
    switch (aux->ws_type) {
    case HTTPD_WS_TYPE_CONTINUE: case HTTPD_WS_TYPE_TEXT: case HTTPD_WS_TYPE_BINARY:
    case HTTPD_WS_TYPE_CLOSE: case HTTPD_WS_TYPE_PING: case HTTPD_WS_TYPE_PONG: break;
    default: return httpd_ws_fail_connection(req, 1002);
    }
    if (httpd_ws_is_control_opcode(aux->ws_type) && !aux->ws_final)
        return httpd_ws_fail_connection(req, 1002);

    /* If userspace requests control frames, do not deal with the control frames */''')
        ws = replace(ws, 'frame->len > 125 && frame->len < UINT16_MAX',
                     'frame->len > 125 && frame->len <= UINT16_MAX')
        anchor = '    /* Send off header */'
        pos = ws.index(anchor)
        ws = ws[:pos]+'''    if (sess->ws_close && frame->type != HTTPD_WS_TYPE_CLOSE)
        return ESP_ERR_INVALID_STATE;

'''+ws[pos:]
    else:
        ws = replace(ws, '#include "native_httpd_headers.h"', '''#include "native_httpd_headers.h"
#if !CONFIG_HTTPD_WS_STRICTER_RFC6455
#error "Native WebSocket HTTPD overlay requires CONFIG_HTTPD_WS_STRICTER_RFC6455=y on SDK6.1"
#endif''')
        # Mandatory values were fully validated and canonicalized once, with
        # fixed buffers. Keep SDK SHA ownership, avoiding duplicate raw-header
        # reads/allocations and their different whitespace interpretation.
        start, end = function_span(ws, 'httpd_ws_respond_server_handshake')
        handshake = ws[start:end].replace('        free(sec_key_encoded);\n', '').replace('    free(sec_key_encoded);\n', '')
        ws = ws[:start]+handshake+ws[end:]
        start, end = function_span(ws, 'httpd_ws_send_handshake_error')
        ws = ws[:start]+ws[end:]
    ws = replace(ws, 'if (httpd_send(req, tx_buf, fmt_len) < 0)', 'if (httpd_send(req, tx_buf, fmt_len) != fmt_len)')
    ws = replace(ws, 'if (sess->send_fn(hd, fd, (const char *)header_buf, tx_len, 0) < 0)', 'if (sess->send_fn(hd, fd, (const char *)header_buf, tx_len, 0) != tx_len)')
    ws = replace(ws, 'if (sess->send_fn(hd, fd, (const char *)frame->payload, frame->len, 0) < 0)', 'if (sess->send_fn(hd, fd, (const char *)frame->payload, frame->len, 0) != (int)frame->len)')
    output.mkdir(parents=True, exist_ok=True)
    for name, text in [('httpd_ws.c', ws), ('httpd_parse.c', parse)]:
        (output/name).write_text(text, encoding='utf-8', newline='\n')
    report = {'sdk_profile': version, 'sdk_source_sha256': hashes, 'sdk_header_sha256': header_hashes,
              'generated_sha256': {name:hashlib.sha256((output/name).read_bytes()).hexdigest() for name in originals}}
    (output/'manifest.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); print(json.dumps(generate(args.sdk, args.output), indent=2))

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "http_stream_protocol.h"

static void test_url_and_redirects(void) {
    char host[96];
    http_stream_url_t url;
    assert(http_stream_parse_url(
        "http://radio.example:8000/dir/live?q=1#ignored", &url, host,
        sizeof(host)));
    assert(strcmp(host, "radio.example") == 0);
    assert(url.port == 8000);
    assert(url.authority_length == strlen("radio.example:8000"));
    assert(strncmp(url.authority, "radio.example:8000",
                   url.authority_length) == 0);
    assert(url.target_length == strlen("/dir/live?q=1"));
    assert(strncmp(url.target, "/dir/live?q=1", url.target_length) == 0);
    assert(!url.query_only);

    assert(http_stream_parse_url("http://radio.example?quality=low", &url,
                                 host, sizeof(host)));
    assert(url.query_only);
    assert(strncmp(url.target, "?quality=low", url.target_length) == 0);

    char output[256];
    assert(http_stream_resolve_redirect(
        "http://radio.example:8000/dir/live", "next", output,
        sizeof(output)));
    assert(strcmp(output, "http://radio.example:8000/dir/next") == 0);
    assert(http_stream_resolve_redirect(
        "http://radio.example:8000/dir/live", "/new", output,
        sizeof(output)));
    assert(strcmp(output, "http://radio.example:8000/new") == 0);
    assert(http_stream_resolve_redirect(
        "http://radio.example:8000/dir/live", "//other.example:9000/live",
        output, sizeof(output)));
    assert(strcmp(output, "http://other.example:9000/live") == 0);
    assert(http_stream_resolve_redirect(
        "http://radio.example:8000/dir/live?old=1", "?new=1", output,
        sizeof(output)));
    assert(strcmp(output,
                  "http://radio.example:8000/dir/live?new=1") == 0);
    assert(!http_stream_resolve_redirect(
        "http://radio.example/live", "https://other.example/live", output,
        sizeof(output)));
    assert(!http_stream_resolve_redirect(
        "http://radio.example/live", "/ok\r\nInjected: yes", output,
        sizeof(output)));
}

static void test_header_tokens(void) {
    assert(http_stream_header_has_token("Chunked", "chunked"));
    assert(http_stream_header_has_token(" gzip, CHUNKED ", "chunked"));
    assert(!http_stream_header_has_token("xchunked", "chunked"));
}

static void test_fragmented_chunked_body(void) {
    static const char encoded[] =
        "4\r\nWiki\r\n5;source=test\r\npedia\r\n0\r\nX-Test: yes\r\n\r\n";
    char decoded[32];
    size_t decoded_size = 0;
    http_chunk_decoder_t decoder;
    http_chunk_decoder_init(&decoder);
    for (size_t index = 0; index < sizeof(encoded) - 1U; ++index) {
        uint8_t byte = (uint8_t)encoded[index];
        size_t produced = 0;
        assert(http_chunk_decode(&decoder, &byte, 1U, &produced));
        if (produced) decoded[decoded_size++] = (char)byte;
    }
    decoded[decoded_size] = '\0';
    assert(strcmp(decoded, "Wikipedia") == 0);
    assert(http_chunk_decoder_finished(&decoder));

    http_chunk_decoder_init(&decoder);
    uint8_t malformed[] = "1\r\naX";
    size_t produced = 0;
    assert(!http_chunk_decode(&decoder, malformed, sizeof(malformed) - 1U,
                              &produced));
}

int main(void) {
    test_url_and_redirects();
    test_header_tokens();
    test_fragmented_chunked_body();
    puts("ESP8266 HTTP protocol tests passed");
    return 0;
}

#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "web_file_form.h"

static unsigned checks;
static void boundary(const char *input, const char *expected) {
    char output[71];
    memset(output, 0x5a, sizeof(output));
    bool ok = mp_form_data_boundary(input, output, sizeof(output));
    assert(ok == (expected != NULL));
    assert(expected ? !strcmp(output, expected) : output[0] == 0);
    ++checks;
}

static void disposition(const char *input, const char *field,
                        const char *filename, bool have_filename) {
    char name[32], file[128];
    bool have = false;
    bool ok = mp_disposition(input, name, sizeof(name), file, sizeof(file), &have);
    assert(ok == (field != NULL));
    if (field) {
        assert(!strcmp(name, field));
        assert(have == have_filename);
        assert(!strcmp(file, filename ? filename : ""));
        char compatible[128];
        assert(mp_parameter(input, "name", compatible, sizeof(compatible)));
        assert(!strcmp(compatible, name));
        assert(mp_parameter(input, "filename", compatible, sizeof(compatible)) == have);
        if (have) assert(!strcmp(compatible, file));
    }
    ++checks;
}

static unsigned opened, ended;
static unsigned char received[1024];
static size_t received_bytes;
static bool begin(unsigned slot, void *context) {
    (void)context; assert(slot == 0); ++opened; return true;
}
static bool write_file(const uint8_t *data, size_t bytes, void *context) {
    (void)context;
    assert(bytes <= sizeof(received) - received_bytes);
    memcpy(received + received_bytes, data, bytes); received_bytes += bytes;
    return true;
}
static bool end(void *context) { (void)context; ++ended; return true; }

static void body_case(const char *header, const char *epilogue, bool expected) {
    static const unsigned char payload[] = {0, 255, 1, 13, 10, 0, 128};
    unsigned char body[1024];
    int prefix = snprintf((char *)body, sizeof(body), "--test\r\n%s\r\n\r\n", header);
    assert(prefix > 0 && (size_t)prefix < sizeof(body));
    size_t size = (size_t)prefix;
    memcpy(body + size, payload, sizeof(payload)); size += sizeof(payload);
    int tail = snprintf((char *)body + size, sizeof(body) - size,
                        "\r\n--test--%s", epilogue);
    assert(tail >= 0 && (size_t)tail < sizeof(body) - size); size += (size_t)tail;
    for (size_t step = 1; step <= size; ++step) {
        web_multipart_t parser;
        web_file_form_t form = {.mode=WEB_FORM_UPLOAD,
            .sink={begin, write_file, end, NULL}};
        assert(mp_init(&parser, "test", web_file_form_part, &form));
        opened = ended = 0; received_bytes = 0;
        bool ok = true;
        for (size_t offset = 0; ok && offset < size; offset += step) {
            size_t count = size - offset;
            if (count > step) count = step;
            ok = mp_feed(&parser, body + offset, count);
        }
        assert((ok && mp_complete(&parser)) == expected);
        if (expected) {
            assert(opened == 1 && ended == 1 && form.files == 1);
            assert(received_bytes == sizeof(payload));
            assert(!memcmp(received, payload, sizeof(payload)));
        }
        ++checks;
    }
}

int main(void) {
    boundary("multipart/form-data; boundary=test", "test");
    boundary("MuLtIpArT/FoRm-DaTa ; BoUnDaRy = \"test\"", "test");
    boundary("\t multipart/form-data; charset=utf-8; boundary=test; x=\"a;b\" \t", "test");
    boundary("multipart/form-data; boundary=\"a:b /?=()+_,.-'\"", "a:b /?=()+_,.-'");
    boundary("multipart/form-data; boundary=\"a\\:b\"", "a:b");
    const char *bad_types[] = {
        "multipart/form-data", "multipart/form-data;", "multipart/form-dataX; boundary=test",
        "multipart/form-data; x-boundary=test", "multipart/form-data; x=\"boundary=test\"",
        "multipart/form-data; boundary=test; boundary=test",
        "multipart/form-data; boundary=test; BOUNDARY=other",
        "multipart/form-data; boundary=test; x=a; X=b",
        "multipart/form-data; boundary=test trailing", "multipart/form-data; boundary=test; x",
        "multipart/form-data; boundary=test; x=", "multipart/form-data; boundary=test; x=\"broken",
        "multipart/form-data; boundary=\"test\"garbage", "multipart/form-data; boundary=\"test\\\"",
        "multipart/form-data; boundary=\"\"", "multipart/form-data; boundary=\"test \"",
        "multipart/form-data; boundary=a:b", "multipart/form-data; boundary=\"a\\\"b\"",
        "multipart/form-data; boundary=\"a\\\\b\"", "multipart/form-data; boundary=\"a\tb\"",
        "multipart/form-data; boundary=\"a\rb\"", "multipart/form-data; boundary=\"a\nb\"",
        "multipart/form-data; boundary=\"a\x7f" "b\"",
        "multipart/form-data; boundary=\"\xc3\xb6\"", "multipart /form-data; boundary=test",
        "multipart/ form-data; boundary=test", "text/plain; boundary=test",
        "multipart/form-data; boundary=test\r\nX-Test: yes"
    };
    for (size_t i = 0; i < sizeof(bad_types)/sizeof(*bad_types); ++i) boundary(bad_types[i], NULL);
    char type[512], long_boundary[72];
    memset(long_boundary, 'x', 70); long_boundary[70] = 0;
    snprintf(type, sizeof(type), "multipart/form-data; boundary=%s", long_boundary);
    boundary(type, long_boundary);
    long_boundary[70] = 'x'; long_boundary[71] = 0;
    snprintf(type, sizeof(type), "multipart/form-data; boundary=%s", long_boundary);
    boundary(type, NULL);
    for (size_t capacity = 1; capacity <= 72; ++capacity) {
        char output[73]; memset(output, 0x5a, sizeof(output));
        bool ok = mp_form_data_boundary("multipart/form-data; boundary=abc", output, capacity);
        assert(ok == (capacity >= 4)); assert((unsigned char)output[capacity] == 0x5a);
        assert(ok ? !strcmp(output, "abc") : !output[0]); ++checks;
    }
    char output[8];
    assert(!mp_form_data_boundary(NULL, output, sizeof(output)));
    assert(!mp_form_data_boundary("multipart/form-data; boundary=a", NULL, 1));
    assert(!mp_form_data_boundary("multipart/form-data; boundary=a", output, 0));
    memset(type, 'x', sizeof(type)); boundary(type, NULL); /* No NUL in bound. */

    disposition("Content-Disposition: form-data; name=plfile; filename=x.csv", "plfile", "x.csv", true);
    disposition("content-disposition: FORM-DATA; NAME=\"plfile\"\r\nContent-Type: application/octet-stream",
                "plfile", NULL, false);
    disposition("X-Test: name=\"wrong\"\r\nContent-Disposition:\tform-data ; name = \"plfile\" ; filename = \"\"\r\n",
                "plfile", "", true);
    disposition("Content-Disposition: form-data; name=plfile; filename=\"C:\\fakepath\\x.csv\"",
                "plfile", "C:\\fakepath\\x.csv", true);
    disposition("Content-Disposition: form-data; name=\"pl\\file\"; filename=\"x\\\".csv\"",
                "plfile", "x\".csv", true);
    const char *bad_headers[] = {
        "Content-Type: text/plain; name=\"plfile\"", "X-Content-Disposition: form-data; name=plfile",
        "Content-Disposition: attachment; name=plfile", "Content-Disposition: form-dataX; name=plfile",
        "Content-Disposition: form-data; x-name=plfile", "Content-Disposition: form-data; filename=plfile",
        "Content-Disposition: form-data; x=\"name=plfile\"", "Content-Disposition: form-data; name=\"\"",
        "Content-Disposition: form-data; name=plfile; name=other",
        "Content-Disposition: form-data; name=plfile; NAME=plfile",
        "Content-Disposition: form-data; name=plfile; filename=a; FILENAME=b",
        "Content-Disposition: form-data; name=plfile; unknown=a; UNKNOWN=b",
        "Content-Disposition: form-data; name=plfile; name*=utf-8''plfile",
        "Content-Disposition: form-data; name=plfile; filename*=utf-8''a.gz",
        "Content-Disposition: form-data; name=plfile; filename=\"broken",
        "Content-Disposition: form-data; name=plfile; filename=\"good\"bad",
        "Content-Disposition: form-data; name=plfile; filename=",
        "Content-Disposition: form-data; name=plfile; filename=a/b",
        "Content-Disposition: form-data; name=plfile;",
        "Content-Disposition: form-data; name=plfile\r\nContent-Disposition: form-data; name=plfile",
        "Content-Disposition : form-data; name=plfile", " Content-Disposition: form-data; name=plfile",
        "Content-Disposition: form-data; name=plfile\nX-Test: yes",
        "Content-Disposition: form-data; name=plfile\rX-Test: yes",
        "Content-Disposition: form-data; name=plfile\r\n X-Test: yes",
        "Content-Disposition: form-data; name=plfile\r\nInvalid",
        "Content-Disposition: form-data; name=plfile\r\nBad Name: yes",
        "Content-Disposition: form-data; name=plfile\r\nX-Test: \x01",
        "Content-Disposition: form-data; name=\"pl\rfile\"",
        "Content-Disposition: form-data; name=\"pl\\\nfile\""
    };
    for (size_t i = 0; i < sizeof(bad_headers)/sizeof(*bad_headers); ++i)
        disposition(bad_headers[i], NULL, NULL, false);
    for (size_t n = 0; n <= 140; ++n) {
        char header[256], file[141]; memset(file, 'x', n); file[n] = 0;
        snprintf(header, sizeof(header), "Content-Disposition: form-data; name=plfile; filename=\"%s\"", file);
        disposition(header, n < 128 ? "plfile" : NULL, n < 128 ? file : NULL, true);
    }
    for (size_t n = 0; n <= 40; ++n) {
        char header[256], field[41]; memset(field, 'x', n); field[n] = 0;
        snprintf(header, sizeof(header), "Content-Disposition: form-data; name=\"%s\"", field);
        disposition(header, n && n < 32 ? field : NULL, NULL, false);
    }
    memset(type, 'x', sizeof(type)); disposition(type, NULL, NULL, false);
    body_case("Content-Disposition: form-data; name=plfile; filename=x.csv", "\r\n", true);
    body_case("content-disposition: FORM-DATA; NAME=\"plfile\"; filename=\"\"", "", true);
    body_case("Content-Type: application/octet-stream; name=plfile", "\r\n", false);
    body_case("Content-Disposition: form-data; name=plfile; name=other", "\r\n", false);
    body_case("Content-Disposition: form-data; name=plfile", "\r\nextra", false);
    body_case("Content-Disposition: form-data; name=plfile", "\n", false);
    body_case("Content-Disposition: form-data; name=plfile", "\r", false);
    printf("PASS shared multipart headers: %u checks; bounded exact parameters, binary split bodies, strict epilogue\n", checks);
    return 0;
}

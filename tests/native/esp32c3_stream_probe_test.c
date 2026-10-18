#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "stream_probe.h"
#include "audio_completion.h"

typedef enum { NATIVE_CODEC_AUTO, NATIVE_CODEC_MP3, NATIVE_CODEC_AAC,
               NATIVE_CODEC_FLAC, NATIVE_CODEC_OGG } native_codec_t;
static uint8_t captured[8192];
static size_t captured_size;
static bool reject_output;
static native_codec_t captured_codec;
static const uint8_t *corpus_expected;
static size_t corpus_size;
static bool send_encoded(uint32_t generation, native_codec_t codec,
                         const void *data, size_t size, unsigned end) {
    assert(generation == 42 && !end && codec != NATIVE_CODEC_AUTO);
    if (reject_output) return false;
    if (corpus_expected) {
        assert(captured_size + size <= corpus_size);
        assert(memcmp(corpus_expected + captured_size, data, size) == 0);
        captured_size += size;
        captured_codec = codec;
        return true;
    }
    assert(captured_size + size <= sizeof(captured));
    memcpy(captured + captured_size, data, size);
    captured_size += size;
    captured_codec = codec;
    return true;
}
static const char *codec_name(native_codec_t codec) { (void)codec; return "test"; }
#ifndef PROBE_EXPECTS_RUNNING
#define PROBE_EXPECTS_RUNNING 1
#endif
static void state_set_audio(uint32_t generation, bool playing, const char *name) {
    assert(generation == 42 && playing == PROBE_EXPECTS_RUNNING && name);
    assert(captured_size == 0); // A decoder may publish metadata after the first send.
}
#include "stream-send-under-test.h"

static void replay(const uint8_t *data, size_t size, size_t skip,
                   native_codec_t expected) {
    // Every two-part split, then one-byte reads, exercises the real send path.
    for (size_t split = 0; split <= size + 1; ++split) {
        stream_probe_t probe = {0};
        native_codec_t codec = NATIVE_CODEC_AUTO;
        bool first = true;
        captured_size = 0;
        if (split <= size) {
            assert(send_stream_audio(42, &codec, data, split, &first, &probe));
            assert(send_stream_audio(42, &codec, data + split, size - split, &first, &probe));
        } else {
            for (size_t i = 0; i < size; ++i)
                assert(send_stream_audio(42, &codec, data + i, 1, &first, &probe));
        }
        assert(codec == expected && captured_codec == expected && !first);
        assert(captured_size == size - skip);
        assert(memcmp(captured, data + skip, captured_size) == 0);
    }
}

static void corpus(const char *path, native_codec_t expected) {
    FILE *file=fopen(path,"rb"); assert(file);
    assert(fseek(file,0,SEEK_END)==0); long length=ftell(file); assert(length>0);
    rewind(file);
    uint8_t *bytes=malloc((size_t)length+52); assert(bytes);
    assert(fread(bytes+52,1,(size_t)length,file)==(size_t)length); fclose(file);
    // ID3v2.4 with footer and misleading MP3/ADTS payload must not select a codec.
    memset(bytes,0,52); memcpy(bytes,"ID3",3); bytes[3]=4; bytes[5]=0x10; bytes[9]=32;
    const uint8_t bait[]={0xff,0xfb,0x90,0,0xff,0xf1,0x4c,0x80,1,0x9f,0xfc};
    memcpy(bytes+10,bait,sizeof(bait));
    const size_t chunks[]={1,7,2048};
    // Fixtures may already have an ID3 prefix. Compute the expected audio start
    // independently using the specified synchsafe tag size, never the probe.
    size_t original_skip=0;
    while ((size_t)length-original_skip>=10 && memcmp(bytes+52+original_skip,"ID3",3)==0) {
        const uint8_t *p=bytes+52+original_skip;
        size_t count=10+((size_t)p[6]<<21)+((size_t)p[7]<<14)+((size_t)p[8]<<7)+p[9];
        if (p[3]==4 && (p[5]&0x10)) count+=10;
        assert(count<=(size_t)length-original_skip); original_skip+=count;
    }
    corpus_expected=bytes+52+original_skip; corpus_size=(size_t)length-original_skip;
    for (unsigned tag=0;tag<2;++tag) for(size_t c=0;c<sizeof(chunks)/sizeof(chunks[0]);++c) {
        stream_probe_t probe={0}; native_codec_t codec=NATIVE_CODEC_AUTO; bool first=true;
        captured_size=0; const uint8_t *input=bytes+(tag?0:52);
        size_t size=(size_t)length+(tag?52:0);
        for(size_t offset=0;offset<size;) {
            size_t chunk=size-offset; if(chunk>chunks[c])chunk=chunks[c];
            assert(send_stream_audio(42,&codec,input+offset,chunk,&first,&probe)); offset+=chunk;
        }
        assert(!first && codec==expected && captured_codec==expected && captured_size==corpus_size);
    }
    printf("Corpus passed: codec=%u input=%ld audio=%zu cases=6\n",(unsigned)expected,length,corpus_size);
    corpus_expected=NULL; free(bytes);
}

int main(int argc, char **argv) {
    const uint8_t mp3[] = {0xff,0xfb,0x90,0x00,1,2,3,4,5,6,7,8};
    const uint8_t aac[] = {0xff,0xf1,0x4c,0x80,0x01,0x9f,0xfc,1,2,3,4,5};
    const uint8_t flac[] = {'f','L','a','C',0,0,0,34,1,2,3,4};
    const uint8_t ogg[] = {'O','g','g','S',0,2,0,0,0,0,0,0};
    replay(mp3,sizeof(mp3),0,NATIVE_CODEC_MP3);
    replay(aac,sizeof(aac),0,NATIVE_CODEC_AAC);
    replay(flac,sizeof(flac),0,NATIVE_CODEC_FLAC);
    replay(ogg,sizeof(ogg),0,NATIVE_CODEC_OGG);
    // A complete signature after junk must be recognized without waiting for
    // payload or unrelated trailing bytes, even when the read ends here.
    const uint8_t *headers[] = {mp3, aac, flac, ogg};
    const size_t header_sizes[] = {4, 7, 8, 5};
    const native_codec_t codecs[] = {NATIVE_CODEC_MP3, NATIVE_CODEC_AAC,
                                    NATIVE_CODEC_FLAC, NATIVE_CODEC_OGG};
    for (size_t kind=0; kind<4; ++kind) {
        for (size_t junk=1; junk<=24; ++junk) {
            uint8_t prefix_only[32]={0};
            memcpy(prefix_only+junk,headers[kind],header_sizes[kind]);
            replay(prefix_only,junk+header_sizes[kind],junk,codecs[kind]);
            // The same input one byte short must still be unresolved.
            stream_probe_t partial={0}; size_t count=0;
            assert(stream_probe_feed(&partial,prefix_only,
                   junk+header_sizes[kind]-1,&count)==STREAM_PROBE_MORE);
        }
        const uint8_t overlapping[][4]={{0,0xff,0xff,0xff},{'f','L','f','L'},
                                      {'O','g','O','g'},{'I','D','I','D'}};
        for (size_t prefix=0; prefix<4; ++prefix) {
            uint8_t joined[12]; memcpy(joined,overlapping[prefix],4);
            memcpy(joined+4,headers[kind],header_sizes[kind]);
            replay(joined,4+header_sizes[kind],4,codecs[kind]);
        }
    }
    uint8_t tagged_header[15]={0,'I','D','3',4,0,0,0,0,0,0};
    memcpy(tagged_header+11,mp3,4);
    replay(tagged_header,sizeof(tagged_header),11,NATIVE_CODEC_MP3);
    for (size_t junk=1; junk<=24; ++junk) {
        uint8_t prefixed[36]={0};
        memcpy(prefixed+junk,aac,sizeof(aac));
        replay(prefixed,junk+sizeof(aac),junk,NATIVE_CODEC_AAC);
        memcpy(prefixed+junk,mp3,sizeof(mp3));
        replay(prefixed,junk+sizeof(mp3),junk,NATIVE_CODEC_MP3);
    }
    uint8_t tagged[52] = {'I','D','3',4,0,0x10,0,0,0,20};
    memcpy(tagged+10,mp3,sizeof(mp3)); // False MP3 inside the tag is ignored.
    memcpy(tagged+40,aac,sizeof(aac)); // Header + 20 body + 10 footer.
    replay(tagged,sizeof(tagged),40,NATIVE_CODEC_AAC);
    uint8_t prefix[45] = {0};
    memcpy(prefix+23,tagged,10); prefix[28]=0; prefix[32]=0; // Empty ID3 tag.
    memcpy(prefix+33,flac,sizeof(flac));
    replay(prefix,sizeof(prefix),33,NATIVE_CODEC_FLAC);
    for (unsigned version=2; version<=4; ++version) {
        uint8_t tags[32] = {'I','D','3',2,0,0,0,0,0,0,'I','D','3',3,0,0,0,0,0,0};
        tags[3]=(uint8_t)version;
        memcpy(tags+20,mp3,sizeof(mp3));
        replay(tags,sizeof(tags),20,NATIVE_CODEC_MP3);
    }
    uint8_t bad[12];
    memcpy(bad,aac,sizeof(bad)); bad[2]=0x7c; // Reserved sample-rate index.
    assert(stream_probe_header(bad,7)==STREAM_PROBE_MORE);
    memcpy(bad,aac,sizeof(bad)); bad[4]=0; bad[5]=0; // Impossible frame length.
    assert(stream_probe_header(bad,7)==STREAM_PROBE_MORE);
    memcpy(bad,mp3,sizeof(bad)); bad[2]=0xfc; // Invalid bitrate/sample rate.
    assert(stream_probe_header(bad,4)==STREAM_PROBE_MORE);
    memcpy(bad,mp3,sizeof(bad)); bad[1]=0xeb; // Reserved MPEG version.
    assert(stream_probe_header(bad,4)==STREAM_PROBE_MORE);
    memcpy(bad,mp3,sizeof(bad)); bad[2]=0; // Legal free-format MP3 header.
    assert(stream_probe_header(bad,4)==STREAM_PROBE_MP3);
    uint8_t unknown[5000]={0}; stream_probe_t probe={0}; size_t consumed;
    assert(stream_probe_feed(&probe,unknown,sizeof(unknown),&consumed)==STREAM_PROBE_INVALID);
    assert(consumed<=STREAM_PROBE_SEARCH_BYTES+STREAM_PROBE_HEADER_BYTES);
    size_t again=99;
    assert(stream_probe_feed(&probe,unknown,1,&again)==STREAM_PROBE_INVALID && !again);
    for (unsigned variant=0; variant<3; ++variant) {
        uint8_t id3[10]={'I','D','3',4,0,0,0,0,0,0};
        if (variant==0) id3[6]=0x80; // Not synchsafe.
        if (variant==1) id3[6]=1;    // More than the aggregate tag bound.
        if (variant==2) id3[5]=1;    // Reserved flag.
        probe=(stream_probe_t){0};
        assert(stream_probe_feed(&probe,id3,sizeof(id3),&consumed)==STREAM_PROBE_INVALID);
    }
    probe=(stream_probe_t){0};
    assert(stream_probe_feed(&probe,aac,2,&consumed)==STREAM_PROBE_MORE);
    assert(consumed==2 && probe.used==2); // EOF here is unknown, never MP3.
    assert(strcmp(audio_completion_status(AUDIO_END_FORMAT_UNKNOWN),"unknown audio format")==0);
    native_codec_t codec=NATIVE_CODEC_AUTO; bool first=true;
    probe=(stream_probe_t){0}; reject_output=true; captured_size=0;
    assert(!send_stream_audio(42,&codec,aac,sizeof(aac),&first,&probe));
    assert(first); reject_output=false;
    // Explicit codec selection retains its existing decoder path.
    codec=NATIVE_CODEC_AAC; first=true; captured_size=0; probe=(stream_probe_t){0};
    assert(send_stream_audio(42,&codec,aac,sizeof(aac),&first,&probe));
    assert(captured_size==sizeof(aac) && !probe.used);
    // Deterministic malformed-prefix stress under ASan/UBSan.
    uint32_t random=7;
    for (unsigned iteration=0; iteration<10000; ++iteration) {
        uint8_t bytes[97];
        for (size_t i=0;i<sizeof(bytes);++i) { random=random*1664525U+1013904223U; bytes[i]=(uint8_t)(random>>24); }
        probe=(stream_probe_t){0};
        for (size_t i=0;i<sizeof(bytes);++i) {
            stream_probe_feed(&probe,bytes+i,1,&consumed);
            assert(probe.used<=STREAM_PROBE_HEADER_BYTES && consumed<=1);
        }
    }
    printf("Stream probe/send passed: split headers, exact replay, ID3, bounds, failures; state=%zu bytes\n",sizeof(stream_probe_t));
    assert(argc%2==1);
    for(int i=1;i<argc;i+=2) corpus(argv[i],(native_codec_t)atoi(argv[i+1]));
    return 0;
}

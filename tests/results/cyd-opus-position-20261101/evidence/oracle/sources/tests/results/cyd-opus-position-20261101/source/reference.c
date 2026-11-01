/* Public libopus full-stream reference and exhaustive sample-position check.
 * This is a host diagnostic, not firmware or a numeric-conformance oracle.
 */
#include <assert.h>
#include <inttypes.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct OpusDecoder OpusDecoder;
extern OpusDecoder *opus_decoder_create(int32_t, int, int *);
extern int opus_decode(OpusDecoder *, const unsigned char *, int32_t,
                       int16_t *, int, int);
extern int opus_packet_get_nb_samples(const unsigned char *, int32_t, int32_t);
extern void opus_decoder_destroy(OpusDecoder *);
extern const char *opus_get_version_string(void);

static uint32_t le32(const unsigned char *p) {
    return (uint32_t)p[0]|(uint32_t)p[1]<<8|(uint32_t)p[2]<<16|(uint32_t)p[3]<<24;
}
static uint64_t le64(const unsigned char *p) {
    return (uint64_t)le32(p)|(uint64_t)le32(p+4)<<32;
}
static void read_exact(FILE *f, void *p, size_t n) { assert(fread(p,1,n,f)==n); }
static void write_pcm(const char *path, const int16_t *p, size_t samples) {
    FILE *f=fopen(path,"wb");assert(f);
    assert(fwrite(p,sizeof(*p),samples,f)==samples && !fclose(f));
}
static uint64_t error_sum(const int16_t *vendor, const int16_t *reference,
                          size_t samples) {
    uint64_t sum=0;
    for (size_t i=0;i<samples;++i) {
        int64_t d=(int64_t)vendor[i]-reference[i];
        sum+=(uint64_t)(d*d);
    }
    return sum;
}

int main(int argc,char **argv) {
    assert(argc==5);
    const uint16_t native_endian=1;
    assert(*(const unsigned char *)&native_endian==1 && sizeof(int16_t)==2);
    FILE *f=fopen(argv[1],"rb");assert(f);
    unsigned char header[36];read_exact(f,header,sizeof(header));
    assert(!memcmp(header,"OPPK01\0\0",8));
    uint32_t channels=le32(header+8),preskip=le32(header+12),packets=le32(header+32);
    uint64_t eos=le64(header+16),raw_frames=le64(header+24);
    assert(channels==2 && preskip<eos && eos<=raw_frames && raw_frames<UINT32_MAX);
    assert(raw_frames<=SIZE_MAX/4);
    int16_t *reference=calloc((size_t)raw_frames*channels,sizeof(*reference));assert(reference);
    int error=0;OpusDecoder *decoder=opus_decoder_create(48000,(int)channels,&error);
    assert(decoder && error==0);
    size_t decoded_frames=0;
    for (uint32_t i=0;i<packets;++i) {
        unsigned char length[4];read_exact(f,length,4);uint32_t n=le32(length);
        assert(n && n<=1024*1024);
        unsigned char *packet=malloc(n);assert(packet);read_exact(f,packet,n);
        int expected=opus_packet_get_nb_samples(packet,(int32_t)n,48000);
        assert(expected>0 && expected<=5760 && decoded_frames+(unsigned)expected<=raw_frames);
        int actual=opus_decode(decoder,packet,(int32_t)n,
                              reference+decoded_frames*channels,expected,0);
        assert(actual==expected);decoded_frames+=(unsigned)actual;free(packet);
    }
    assert(fgetc(f)==EOF && !ferror(f) && !fclose(f));
    opus_decoder_destroy(decoder);assert(decoded_frames==raw_frames);
    write_pcm(argv[3],reference,decoded_frames*channels);
    size_t logical_frames=(size_t)(eos-preskip),samples=logical_frames*channels;
    const int16_t *logical=reference+(size_t)preskip*channels;
    write_pcm(argv[4],logical,samples);

    f=fopen(argv[2],"rb");assert(f && !fseek(f,0,SEEK_END));
    long bytes=ftell(f);assert(bytes>0 && bytes%4==0 && !fseek(f,0,SEEK_SET));
    size_t vendor_frames=(size_t)bytes/4;
    assert(vendor_frames==raw_frames && vendor_frames>=logical_frames);
    int16_t *vendor=malloc((size_t)bytes);assert(vendor);read_exact(f,vendor,(size_t)bytes);
    assert(!fclose(f));
    uint64_t best=UINT64_MAX,second=UINT64_MAX;
    size_t best_offset=SIZE_MAX,second_offset=SIZE_MAX,ties=0;
    for (size_t offset=0;offset<=vendor_frames-logical_frames;++offset) {
        uint64_t sum=error_sum(vendor+offset*channels,logical,samples);
        if (sum<best) {
            second=best;second_offset=best_offset;best=sum;best_offset=offset;ties=1;
        } else {
            if (sum==best) ++ties;
            if (sum<second) {second=sum;second_offset=offset;}
        }
    }
    int position_matches=(ties==1 && best_offset==preskip && second>best);
    const int16_t *aligned=vendor+best_offset*channels;
    unsigned peak=0;uint64_t exact=0,within1=0,power=0;int64_t signed_error=0;
    for (size_t i=0;i<samples;++i) {
        int d=(int)aligned[i]-logical[i];unsigned absolute=(unsigned)(d<0?-d:d);
        if (absolute>peak) peak=absolute;
        exact+=(absolute==0);within1+=(absolute<=1);signed_error+=d;
        int64_t v=logical[i];power+=(uint64_t)(v*v);
    }
    uint64_t raw_error=error_sum(vendor,reference,decoded_frames*channels);
    printf("{\"reference\":\"%s\",\"packets\":%u,\"raw_frames\":%zu,"
           "\"logical_frames\":%zu,\"channels\":%u,\"preskip\":%u,"
           "\"eos_granule\":%" PRIu64 ",\"candidate_windows\":%zu,"
           "\"samples_per_candidate\":%zu,\"best_offset\":%zu,\"best_ties\":%zu,"
           "\"best_squared_error\":%" PRIu64 ",\"second_offset\":%zu,"
           "\"second_squared_error\":%" PRIu64 ",\"aligned_max_abs\":%u,"
           "\"aligned_exact_samples\":%" PRIu64 ",\"aligned_within1_samples\":%" PRIu64 ","
           "\"aligned_signed_error\":%" PRId64 ",\"reference_signal_power\":%" PRIu64 ","
           "\"aligned_rmse\":%.12g,\"raw_same_position_squared_error\":%" PRIu64 ","
           "\"unique_sample_position_observed\":%s,\"numeric_conformance_claim\":false}\n",
           opus_get_version_string(),packets,decoded_frames,logical_frames,channels,preskip,eos,
           vendor_frames-logical_frames+1,samples,best_offset,ties,best,second_offset,second,
           peak,exact,within1,signed_error,power,sqrt((double)best/samples),raw_error,
           position_matches?"true":"false");
    free(vendor);free(reference);return position_matches?0:1;
}

/* SDK SHA implementation is outside this host seam. Validate the precise input
 * and use the RFC sample digest; Base64 encoder/decoder below is actual SDK C. */
#define PSA_HASH_OPERATION_INIT 0
#define PSA_ALG_SHA_1 1
#define PSA_SUCCESS 0
typedef int psa_status_t;
typedef int psa_hash_operation_t;
static int psa_hash_setup(psa_hash_operation_t *op,int algorithm) {assert(algorithm==1);*op=1;return 0;}
static int psa_hash_update(psa_hash_operation_t *op,const uint8_t *data,size_t size) {
    static const char expected[]="dGhlIHNhbXBsZSBub25jZQ==258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
    assert(*op==1 && size==sizeof(expected)-1 && !memcmp(data,expected,size));return 0;
}
static int psa_hash_finish(psa_hash_operation_t *op,uint8_t *data,size_t cap,size_t *size) {
    static const uint8_t digest[]={0xb3,0x7a,0x4f,0x2c,0xc0,0x62,0x4f,0x16,0x90,0xf6,0x46,0x06,0xcf,0x38,0x59,0x45,0xb2,0xbe,0xc4,0xea};
    assert(*op==1 && cap>=sizeof(digest));memcpy(data,digest,sizeof(digest));*size=sizeof(digest);return 0;
}
static void psa_hash_abort(psa_hash_operation_t *op) {*op=0;}
#include "sdk-base64.inc"

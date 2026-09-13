/* Diagnostic external-symbol scopes, not an alternative Opus algorithm.
 * Same-TU/internal/inlined calls are NOT intercepted by GNU --wrap: their
 * time remains in their nearest measured parent. Never call it full coverage.
 * ABI/prototypes come from the exact fixed-point headers used by the decoder. */
#include "upstream/celt/config.h"
#include "opus_function_profile.h"
#include "opus_memory.h"
#include "celt.h"
#include "bands.h"
#include "vq.h"
#include "cwrs.h"
#include "mdct.h"
#include "kiss_fft.h"
#include "entdec.h"
#if !defined(FIXED_POINT) || !YORADIO_OPUS_FUNCTION_PROFILE
#error "Function wrappers require fixed-point diagnostic profile"
#endif
#define ABI(N) typedef char check_abi_##N[__builtin_types_compatible_p(__typeof__(&N),__typeof__(&__real_##N)) ? 1 : -1];
#define WRAP(R,N,I,P,A) R __real_##N P; ABI(N) R __wrap_##N P { \
    opus_function_scope_t profile_scope; opus_function_enter(&profile_scope,I); \
    R result = __real_##N A; opus_function_leave(&profile_scope); return result; }
#define WRAPV(N,I,P,A) void __real_##N P; ABI(N) void __wrap_##N P { \
    opus_function_scope_t profile_scope; opus_function_enter(&profile_scope,I); \
    __real_##N A; opus_function_leave(&profile_scope); }
WRAP(int,yoradio_opus_decode_bounded,0,(void *d,const unsigned char *p,int l,int16_t *out,int n),(d,p,l,out,n))
WRAP(int,celt_decode_with_ec,1,(OpusCustomDecoder *s,const unsigned char *p,int l,opus_val16 *out,int n,ec_dec *ec,int accum),(s,p,l,out,n,ec,accum))
WRAPV(quant_all_bands,2,(int enc,const CELTMode *m,int start,int end,celt_norm *x,celt_norm *y,unsigned char *mask,const celt_ener *energy,int *pulses,int shortblocks,int spread,int dual,int intensity,int *tf,opus_int32 bits,opus_int32 balance,ec_ctx *ec,int lm,int bands,opus_uint32 *seed,int complexity,int arch,int disable_inv,celt_norm *norm,int norm_size),(enc,m,start,end,x,y,mask,energy,pulses,shortblocks,spread,dual,intensity,tf,bits,balance,ec,lm,bands,seed,complexity,arch,disable_inv,norm,norm_size))
WRAP(unsigned,alg_unquant,3,(celt_norm *x,int n,int k,int spread,int b,ec_dec *ec,opus_val16 gain),(x,n,k,spread,b,ec,gain))
WRAP(opus_val32,decode_pulses,4,(int *y,int n,int k,ec_dec *ec),(y,n,k,ec))
WRAPV(renormalise_vector,5,(celt_norm *x,int n,opus_val16 gain,int arch),(x,n,gain,arch))
WRAPV(clt_mdct_backward_c,6,(const mdct_lookup *l,kiss_fft_scalar *in,kiss_fft_scalar *out,const opus_val16 *window,int overlap,int shift,int stride,int arch),(l,in,out,window,overlap,shift,stride,arch))
WRAPV(opus_fft_impl,7,(const kiss_fft_state *s,kiss_fft_cpx *out),(s,out))
WRAP(unsigned,ec_decode,8,(ec_dec *s,unsigned ft),(s,ft))
WRAPV(ec_dec_update,9,(ec_dec *s,unsigned fl,unsigned fh,unsigned ft),(s,fl,fh,ft))
WRAP(opus_uint32,ec_dec_uint,10,(ec_dec *s,opus_uint32 ft),(s,ft))
WRAP(int,ec_dec_icdf,11,(ec_dec *s,const unsigned char *icdf,unsigned ftb),(s,icdf,ftb))
WRAP(opus_uint32,ec_dec_bits,12,(ec_dec *s,unsigned bits),(s,bits))
WRAP(int,ec_dec_bit_logp,13,(ec_dec *s,unsigned logp),(s,logp))

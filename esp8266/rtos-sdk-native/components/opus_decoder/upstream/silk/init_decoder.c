/***********************************************************************
Copyright (c) 2006-2011, Skype Limited. All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
- Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
- Neither the name of Internet Society, IETF or IETF Trust, nor the
names of specific contributors, may be used to endorse or promote
products derived from this software without specific prior written
permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
***********************************************************************/

#ifdef __STDC__
#include "config.h"
#endif

#include "main.h"

#ifdef ENABLE_OSCE
#include "osce.h"
#endif

#include "structs.h"
#ifdef YORADIO_OPUS_BOUNDED
#include "opus_memory.h"
#endif

/************************/
/* Reset Decoder State  */
/************************/
opus_int silk_reset_decoder(
    silk_decoder_state          *psDec                          /* I/O  Decoder state pointer                       */
)
{
    /* Clear the entire encoder state, except anything copied */
    silk_memset( &psDec->SILK_DECODER_STATE_RESET_START, 0, sizeof( silk_decoder_state ) - ((char*) &psDec->SILK_DECODER_STATE_RESET_START - (char*)psDec) );
#ifdef YORADIO_OPUS_BOUNDED
    yoradio_opus_clear(psDec->exc_Q14, MAX_FRAME_LENGTH, sizeof(opus_int32));
#endif

    /* Used to deactivate LSF interpolation */
    psDec->first_frame_after_reset = 1;
    psDec->prev_gain_Q16 = 65536;
    psDec->arch = opus_select_arch();

    /* Reset CNG state */
    silk_CNG_Reset( psDec );

    /* Reset PLC state */
    silk_PLC_Reset( psDec );

#ifdef ENABLE_OSCE
    /* Reset OSCE state and method */
    osce_reset(&psDec->osce, OSCE_DEFAULT_METHOD);
#endif

    return 0;
}


/************************/
/* Init Decoder State   */
/************************/
opus_int silk_init_decoder(
    silk_decoder_state          *psDec                          /* I/O  Decoder state pointer                       */
)
{
#ifdef YORADIO_OPUS_BOUNDED
    /* silk_InitDecoder prebinds this pointer; channel reinitialization during
       mono-to-stereo decoding must not allocate or lose the existing region. */
    opus_int32 *exc = psDec->exc_Q14;
#endif
    /* Clear the entire encoder state, except anything copied */
    silk_memset( psDec, 0, sizeof( silk_decoder_state ) );
#ifdef YORADIO_OPUS_BOUNDED
    psDec->exc_Q14 = exc;
#endif

    silk_reset_decoder( psDec );

    return(0);
}


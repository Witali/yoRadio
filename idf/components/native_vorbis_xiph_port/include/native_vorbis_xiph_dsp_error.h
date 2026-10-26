/* Private checked initializer for the source-built decoder.
   The original mdct.h declaration and void wrapper remain unchanged.
   A fresh lookup is zeroed on failure and may be cleared safely. */
#ifndef NATIVE_VORBIS_XIPH_DSP_ERROR_H
#define NATIVE_VORBIS_XIPH_DSP_ERROR_H
#include "mdct.h"
int native_xiph_mdct_init(mdct_lookup *,int);
#endif

#include <stdint.h>
#include "config.h"
#include "mad.h"
#define R8(n) (((n) + 7) & ~7)
/* Sizes are extracted from Xtensa ELF symbols; this code is never executed. */
char size_pointer[sizeof(void *)];
char size_stream[sizeof(struct mad_stream)];
char size_frame[sizeof(struct mad_frame)];
char size_synth[sizeof(struct mad_synth)];
char size_pcm[sizeof(struct mad_pcm)];
char size_arena_1536[1536 + R8(sizeof(struct mad_stream)) + R8(sizeof(struct mad_frame)) + R8(sizeof(struct mad_synth))];

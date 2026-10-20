#pragma once
#include "sdkconfig.h"
#ifdef CONFIG_YORADIO_QEMU_AAC_POINTER_AUDIT
#include "aac_compact_owner.h"
#include "aac_smoothing_history.h"
void aac_pointer_audit_allocate(void *, size_t, aac_compact_owner_t *);
void aac_pointer_audit_free(void *, aac_compact_owner_t *);
void aac_pointer_audit_core(void *, void *, bool);
void aac_pointer_audit_io(const void *, size_t, const void *, size_t);
void aac_pointer_audit_reset(void *);
void aac_pointer_audit_copy(const void *, const void *, size_t);
void aac_pointer_audit_applied(void *,void *,void *,void *,void *,void *,void *,void *,bool);
void aac_pointer_audit_decode_io(void *,void *,void *,void *,void *,void *);
void aac_pointer_audit_ps_bits(void *,void *,bool);
void aac_pointer_audit_frame(void *, void *, void *, void *, bool);
#ifdef AAC_LOW_WORKSPACE
void aac_pointer_audit_low_begin(aac_high_frame_t *, aac_low_workspace_t *);
void aac_pointer_audit_low_end(aac_high_frame_t *);
#endif
void aac_pointer_audit_smoothing(void *, int32_t **[4], aac_smoothing_scratch_t *, unsigned);
void aac_pointer_audit_report(void);
aac_compact_owner_t *aac_compact_owner_audit_context(void);
#define AAC_POINTER_ENVELOPE_ARGS \
    void *frame,int32_t *real,int32_t *imag,int32_t *frequency,int32_t *frequency_count, \
    int32_t *noise_frequency,int noise_bands,int reset,void *alias,int32_t *harmonic_index, \
    int32_t *noise_index,int32_t *previous_harmonics,int32_t *startup,int32_t *limiter_bands, \
    int32_t *gate_mode,int32_t **gain,int32_t **gain_exp,int32_t **noise, \
    int32_t **noise_exp,void *workspace,void *patch,void *sqrt_cache,int real_only
void aac_pointer_audit_envelope(AAC_POINTER_ENVELOPE_ARGS);
#endif

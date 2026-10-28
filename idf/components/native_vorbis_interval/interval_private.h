#pragma once
#include "native_vorbis_interval.h"

native_vorbis_interval_status_t nvi_scope(const native_vorbis_interval_scope_t *scope);
native_vorbis_interval_status_t nvi_point(const native_vorbis_interval_scope_t *scope, const bf_t *value);
void nvi_init(const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value);
void nvi_drop(const native_vorbis_interval_scope_t *scope, native_vorbis_interval_t *value);
native_vorbis_interval_status_t nvi_publish(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, native_vorbis_interval_t *temporary);
native_vorbis_interval_status_t nvi_bf(native_vorbis_bigfloat_status_t status);
bool nvi_zero(const bf_t *value);
native_vorbis_interval_status_t nvi_point_interval(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const bf_t *value);
native_vorbis_interval_status_t nvi_ratio(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, uint64_t numerator, uint64_t denominator);
native_vorbis_interval_status_t nvi_expand(const native_vorbis_interval_scope_t *scope,
    native_vorbis_interval_t *destination, const native_vorbis_interval_t *source, const bf_t *error);

#define NVI_TRY(expression) do { status = (expression); if (status != NATIVE_VORBIS_INTERVAL_OK) goto done; } while (0)
#define NVI_BF(expression) NVI_TRY(nvi_bf(expression))

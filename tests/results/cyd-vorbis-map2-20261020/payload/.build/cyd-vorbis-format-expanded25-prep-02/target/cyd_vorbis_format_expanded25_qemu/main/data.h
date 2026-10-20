#error Root must freeze reviewed raw arrays and contract identity before creating data.h
#pragma once
#include "corpus_case.h"

// Required definitions, with no dummy arrays or success identity supplied:
// CORPUS_CASE_COUNT = 17
// CORPUS_CONTRACT_SHA256 = protocol.load_contract(...)["contract_sha256"]
// CORPUS_EXPECTED_PCM_BYTES = sum of all descriptor expected_pcm_bytes
// static const corpus_case_t corpus_cases[CORPUS_CASE_COUNT] = ...;
// Full 30-byte identification and full 0x05+vorbis-prefixed setup are stored.
// Their first seven bytes are removed only at the public config call boundary.

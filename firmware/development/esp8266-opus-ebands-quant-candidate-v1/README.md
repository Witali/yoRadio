# Experimental raw Opus benchmark, not production

REJECTED: all30 A/B/A runs completed; CPU19278.206833% versus controls
77.863875/77.887833%. Both performance gates fail; do not promote.

2026-09-18. Candidate reuses the accepted signed eBands leaf in
quant_all_bands. Only15 linked bytes change relative to eBands-final.
903216B, CPU160/runtimeQIO40, no RAM/IRAM/stack growth. No audio output.
24 exact host PCM scenarios and linked arithmetic/ABI proofs; physical
A/B/A and final disposition are in
[the experiment](../../../docs/ESP8266_OPUS_ASM_EBANDS_QUANT.md).

SHA256: c24dc62ea1d19063a75f27f4cbd3cdf57d5ce0be3eaccf2166152d92d88ee40e.
Use native OTA only. Do not treat this image as an ordinary radio build.

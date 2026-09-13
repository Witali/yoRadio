# Opus function profile: measured results

Function durations and shares are instrumented, not production estimates. Wrapping very frequent symbols perturbs caller self time and flash cache. No guessed overhead correction. Cross-object calls only.

Cross-object symbol calls only; same-TU/inlined/unwrapped work and bookkeeping remain in parent self time. CPU includes charged ISR; wall includes preemption. No overhead subtraction.

Runs: 10; scored frames: 1200; decoded audio: 24.0 s.

CPU share denominator is measured decoder root time, NOT all available processor time.
Self shares form a partition; inclusive shares overlap. Maxima include measured ISR charges.
Zero calls mean not intercepted on this path, not proof the source function never runs.

| Function | Calls / audio s | Calls / frame | Mean CPU us | Max CPU us | Max wall us | Self CPU % | Inclusive CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|
| yoradio_opus_decode_bounded | 50.00 | 1.000 | 33702.60 | 35749 | 39111 | 12.787 | 100.000 |
| celt_decode_with_ec | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| quant_all_bands | 50.00 | 1.000 | 26029.53 | 27765 | 29898 | 38.000 | 77.233 |
| alg_unquant | 6866.67 | 137.333 | 86.62 | 328 | 1729 | 11.026 | 35.298 |
| decode_pulses | 6866.67 | 137.333 | 59.56 | 211 | 1612 | 16.611 | 24.271 |
| renormalise_vector | 129.17 | 2.583 | 13.79 | 106 | 1050 | 0.106 | 0.106 |
| clt_mdct_backward_c | 79.17 | 1.583 | 1791.15 | 3334 | 5603 | 3.309 | 8.415 |
| opus_fft_impl | 79.17 | 1.583 | 1086.81 | 2054 | 3707 | 5.106 | 5.106 |
| ec_decode | 5491.67 | 109.833 | 5.54 | 97 | 1219 | 1.805 | 1.805 |
| ec_dec_update | 7591.67 | 151.833 | 4.12 | 105 | 1066 | 1.858 | 1.858 |
| ec_dec_uint | 7687.50 | 153.750 | 18.80 | 116 | 1395 | 8.574 | 8.574 |
| ec_dec_icdf | 145.83 | 2.917 | 10.40 | 67 | 1069 | 0.090 | 0.090 |
| ec_dec_bits | 2279.17 | 45.583 | 2.07 | 29 | 1035 | 0.280 | 0.280 |
| ec_dec_bit_logp | 3791.67 | 75.833 | 1.99 | 94 | 1580 | 0.448 | 0.448 |

## Matched control and instrumentation overhead

Sequential trials with Wi-Fi/WebUI on; all observations retained. CPU budget = task time / source-audio duration.

| Fixture | Control CPU median % | Profile CPU median % | Relative overhead % | Control CPU max % | Profile CPU max % |
|---|---:|---:|---:|---:|---:|
| mono-12 | 22.782 | 36.507 | 60.245 | 24.436 | 36.547 |
| mono-24 | 54.689 | 74.261 | 35.787 | 57.293 | 74.311 |
| stereo-64 | 65.555 | 96.690 | 47.495 | 73.470 | 96.806 |
| stereo-128 | 80.683 | 131.280 | 62.711 | 91.486 | 131.399 |
| stereo-192 | 92.876 | 169.046 | 82.011 | 105.613 | 169.170 |

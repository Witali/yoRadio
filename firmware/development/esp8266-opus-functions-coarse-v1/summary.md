# Opus function profile: measured results

Function durations and shares are instrumented, not production estimates. Wrapping very frequent symbols perturbs caller self time and flash cache. No guessed overhead correction. Cross-object calls only.

Cross-object symbol calls only; same-TU/inlined/unwrapped work and bookkeeping remain in parent self time. CPU includes charged ISR; wall includes preemption. No overhead subtraction.

Runs: 10; scored frames: 1200; decoded audio: 24.0 s.

CPU share denominator is measured decoder root time, NOT all available processor time.
Self shares form a partition; inclusive shares overlap. Maxima include measured ISR charges.
Zero calls mean not intercepted on this path, not proof the source function never runs.

| Function | Calls / audio s | Calls / frame | Mean CPU us | Max CPU us | Max wall us | Self CPU % | Inclusive CPU % |
|---|---:|---:|---:|---:|---:|---:|---:|
| yoradio_opus_decode_bounded | 50.00 | 1.000 | 24450.47 | 27004 | 31487 | 16.051 | 100.000 |
| celt_decode_with_ec | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| quant_all_bands | 50.00 | 1.000 | 16500.98 | 18968 | 23351 | 67.487 | 67.487 |
| alg_unquant | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| decode_pulses | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| renormalise_vector | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| clt_mdct_backward_c | 79.17 | 1.583 | 2542.06 | 4634 | 7157 | 9.073 | 16.462 |
| opus_fft_impl | 79.17 | 1.583 | 1140.99 | 2272 | 4795 | 7.389 | 7.389 |
| ec_decode | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| ec_dec_update | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| ec_dec_uint | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| ec_dec_icdf | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| ec_dec_bits | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |
| ec_dec_bit_logp | 0.00 | 0.000 | 0.00 | 0 | 0 | 0.000 | 0.000 |

## Matched control and instrumentation overhead

Sequential trials with Wi-Fi/WebUI on; all observations retained. CPU budget = task time / source-audio duration.

| Fixture | Control CPU median % | Profile CPU median % | Relative overhead % | Control CPU max % | Profile CPU max % |
|---|---:|---:|---:|---:|---:|
| mono-12 | 22.783 | 23.787 | 4.404 | 22.805 | 23.843 |
| mono-24 | 54.710 | 63.242 | 15.595 | 54.748 | 63.258 |
| stereo-64 | 65.559 | 83.887 | 27.956 | 65.600 | 83.972 |
| stereo-128 | 80.714 | 102.303 | 26.747 | 80.780 | 102.348 |
| stereo-192 | 92.819 | 122.777 | 32.275 | 93.012 | 123.160 |

# Combined AAC storage: measured fidelity and estimated persistent bytes

The maxima include synthetic and real inputs. RMS includes all five real
captures, including inactive paths. Instruction costs include test probes.
Every combined numerical run retains the original owner allocation: **0 bytes
of measured heap saving**. Estimates below include the separately verified
lossless layout and the right-channel PS/SBR union, before additional
unpack/cache workspace and allocator rounding.

| Variant | Max PCM error, LSB | +/-3 gate | Real RMS, LSB | Extra QEMU instructions | Estimated SBR owner | Estimated saving |
| --- | ---: | --- | ---: | --- | ---: | ---: |
| 1: all_compatible | 3 | PASS | 0.20243527 | -0.001% to +83.318% | 35,820 B | 19,308 B |
| 2: bulk_qmf_smoothing_ps | 3 | PASS | 0.18834596 | +0.004% to +69.408% | 35,820 B | 19,308 B |
| 3: low_qmf_and_ps | 3 | PASS | 0.18832983 | +0.004% to +63.165% | 42,028 B | 13,100 B |
| 4: qmf_and_smoothing | 3 | PASS | 0.18603697 | +0.004% to +34.152% | 38,992 B | 16,136 B |
| 5: qmf_and_exact_exponents | 3 | PASS | 0.18603697 | +0.004% to +27.774% | 40,912 B | 14,216 B |
| 6: low_qmf_only | 3 | PASS | 0.18601203 | +0.004% to +26.812% | 44,336 B | 10,792 B |
| 7: ps_only | 3 | PASS | 0.07583020 | +0.002% to +53.060% | 49,708 B | 5,420 B |
| 8: exact_traversal | 0 | PASS | 0.00000000 | +0.004% to +9.715% | 49,708 B | 5,420 B |
| 0: binary_bypass | 0 | PASS | 0.00000000 | +0.000% to +0.004% | 49,708 B | 5,420 B |
| 9: all_low_qmf16 | 3 | PASS | 0.31012380 | +0.004% to +82.424% | 34,804 B | 20,324 B |
| 10: all_low_qmf16_ps16 | 3 | PASS | 0.31545975 | +0.004% to +78.828% | 34,540 B | 20,588 B |
| 11: all_shared16 | 10 | FAIL | 0.33005087 | +0.004% to +77.518% | 33,988 B | 21,140 B |
| 12: bulk_shared16 | 3 | PASS | 0.31129985 | +0.004% to +64.372% | 34,380 B | 20,748 B |
| 13: all_bulk16_small18 | 3 | PASS | 0.31546076 | +0.004% to +78.294% | 34,032 B | 21,096 B |

Variants 0 and 8 are numerical controls; their memory column only
shows the independent lossless-layout estimate. They do not allocate it.

## Largest passing complete combination

Variant **13: all_bulk16_small18**: maximum **3 LSB**;
persistent-layout estimate **21,096 B** (**38.27%** of the original SBR owner).

| Logical area | Separate payload saving |
| --- | ---: |
| low_qmf | 8,960 B |
| high_qmf | 2,016 B |
| smoothing_mantissas | 2,240 B |
| smoothing_exponents | 2,560 B |
| ps_delays | 2,156 B |
| hybrid_history | 108 B |
| previous_mix | 128 B |
| hybrid_output | 28 B |
| ps_energy | 84 B |

The rows above overlap in physical memory. Do not add them to the
lossless-layout saving. The persistent model uses the maximum of SBR and PS
space on the right channel and preserves the synthesis suffix.

Passing the retained corpus does not establish a bound for all AAC inputs
or qualify the frame-boundary probes as compact storage for every consumer.

# Four-row smoothing plus PC18 high history

Errors are signed-16 PCM units against the native decoder; instruction costs are QEMU guest instructions.
The previous variant is the retained five-row PC18 experiment. Matching error counts are not a PCM hash comparison.

| Input | Decode peak | Channel RMS | Instructions vs native | Instructions vs previous PC18 | Owner request / block |
| --- | ---: | ---: | ---: | ---: | ---: |
| he44100_stereo | 1 | Not collected | +5.384% | +0.010% | 45932 / 47104 B |
| he48000_stereo | 0 | Not collected | +5.331% | +0.009% | 45932 / 47104 B |
| hev2_44100_stereo | 2 | Not collected | +2.736% | +0.075% | 45932 / 47104 B |
| abba64 | 2 | 0.017279 | +2.684% | +0.046% | 45932 / 47104 B |
| groovesalad16 | 2 | 0.019198 | +4.222% | +0.141% | 45932 / 47104 B |
| groovesalad32 | 0 | 0.000000 | +5.522% | -0.040% | 45932 / 47104 B |
| groovesalad64 | 0 | 0.000000 | +5.177% | +0.007% | 45932 / 47104 B |
| groovesalad128 | 0 | 0.000000 | +0.009% | +0.000% | No SBR owner |

All 81 paired comparisons pass the current 3-LSB gate. Direct FIR tests are bit-exact.
The owner block saves 2048 B versus the previous PC18 owner, 8192 B versus native.
Complex processing needs a 1024-byte temporary payload (1184-byte compiled wrapper frame).
Physical stack, full-radio heap/CPU, public streaming and OTA remain unqualified.

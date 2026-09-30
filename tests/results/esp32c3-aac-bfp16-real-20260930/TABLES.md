# BFP16 error statistics on real AAC radio recordings

All errors are relative to the unmodified Espressif decoder's signed 16-bit PCM.
Three reruns agree exactly; each table counts the audio once, combining L/R.

## 32 subbands per shared exponent

| Recording | Profile / Hz | Samples (L+R) | Max LSB | MAE LSB | RMS LSB | >1 LSB | P99 absolute LSB | Signal/error dB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| groovesalad64 | HE-AAC / 44100 | 2,646,016 | 40 | 0.337537 | 0.773707 | 5.426536% | 2 | 75.27 |
| groovesalad32 | HE-AAC / 44100 | 2,646,016 | 161 | 0.310700 | 1.794243 | 4.241017% | 2 | 67.46 |
| groovesalad16 | HE-AACv2 / 32000 | 1,921,024 | 4 | 0.261795 | 0.587190 | 3.872206% | 2 | 77.62 |
| abba64 | HE-AACv2 / 44100 | 2,646,016 | 8 | 0.356318 | 0.696745 | 5.793238% | 2 | 79.56 |
| groovesalad128 | LC / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |

## 8 subbands per shared exponent

| Recording | Profile / Hz | Samples (L+R) | Max LSB | MAE LSB | RMS LSB | >1 LSB | P99 absolute LSB | Signal/error dB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| groovesalad64 | HE-AAC / 44100 | 2,646,016 | 3 | 0.189418 | 0.497002 | 2.746695% | 2 | 79.11 |
| groovesalad32 | HE-AAC / 44100 | 2,646,016 | 24 | 0.199447 | 0.538470 | 2.931275% | 2 | 77.91 |
| groovesalad16 | HE-AACv2 / 32000 | 1,921,024 | 3 | 0.174172 | 0.475553 | 2.488569% | 2 | 79.46 |
| abba64 | HE-AACv2 / 44100 | 2,646,016 | 3 | 0.210221 | 0.525256 | 3.108220% | 2 | 82.02 |
| groovesalad128 | LC / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |

## 1 subbands per shared exponent

| Recording | Profile / Hz | Samples (L+R) | Max LSB | MAE LSB | RMS LSB | >1 LSB | P99 absolute LSB | Signal/error dB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| groovesalad64 | HE-AAC / 44100 | 2,646,016 | 3 | 0.097992 | 0.354348 | 1.347384% | 2 | 82.05 |
| groovesalad32 | HE-AAC / 44100 | 2,646,016 | 3 | 0.095575 | 0.349735 | 1.308609% | 2 | 81.66 |
| groovesalad16 | HE-AACv2 / 32000 | 1,921,024 | 3 | 0.068054 | 0.294792 | 0.924507% | 1 | 83.61 |
| abba64 | HE-AACv2 / 44100 | 2,646,016 | 3 | 0.100676 | 0.359204 | 1.382531% | 2 | 85.32 |
| groovesalad128 | LC / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |

## Unmodified control

| Recording | Profile / Hz | Samples (L+R) | Max LSB | MAE LSB | RMS LSB | >1 LSB | P99 absolute LSB | Signal/error dB |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| groovesalad64 | HE-AAC / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |
| groovesalad32 | HE-AAC / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |
| groovesalad16 | HE-AACv2 / 32000 | 1,921,024 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |
| abba64 | HE-AACv2 / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |
| groovesalad128 | LC / 44100 | 2,646,016 | 0 | 0.000000 | 0.000000 | 0.000000% | 0 | infinite (identical) |

MAE: mean absolute error. RMS: root mean square error. P99: 99th percentile of absolute error.
Signal/error compares baseline PCM energy with difference energy; it is not an AAC quality score.
Exact histogram bins cover 0-4095 LSB; higher bins have width 4096 and yield percentile bounds.
Error-free runs have zero error energy; their dB ratios are stored as null in JSON.

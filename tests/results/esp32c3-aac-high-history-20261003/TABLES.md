# Persistent high-QMF comparison

PCM errors are signed-16 output units. RMS is the largest per-channel value; synthetic RMS was not collected.
Instruction cost is the largest per-case warm-run median; guards, copy dispatch and statistics are included.

| Storage | Input | Decode peak | Channel RMS | Reset peak | Lifecycle peak | Instructions | Owner request / block | Block saved |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pc18 | synthetic | 2 | — | 1 | 2 | +5.373% | 47980 / 49152 B | 6144 B |
| pc18 | abba64 | 2 | 0.017279 | 1 | 2 | +2.637% | 47980 / 49152 B | 6144 B |
| pc18 | groovesalad16 | 2 | 0.019198 | 1 | 2 | +4.075% | 47980 / 49152 B | 6144 B |
| pc18 | groovesalad32 | 0 | 0.000000 | 1 | 2 | +5.564% | 47980 / 49152 B | 6144 B |
| pc18 | groovesalad64 | 0 | 0.000000 | 1 | 2 | +5.170% | 47980 / 49152 B | 6144 B |
| pc18 | groovesalad128 | 0 | 0.000000 | 1 | 2 | +0.009% | No SBR owner | 0 B |
| pc16 | synthetic | 3 | — | 3 | 3 | +4.770% | 47692 / 49152 B | 6144 B |
| pc16 | abba64 | 2 | 0.022621 | 3 | 3 | +2.455% | 47692 / 49152 B | 6144 B |
| pc16 | groovesalad16 | 2 | 0.025529 | 3 | 3 | +3.747% | 47692 / 49152 B | 6144 B |
| pc16 | groovesalad32 | 3 | 0.048437 | 3 | 3 | +4.958% | 47692 / 49152 B | 6144 B |
| pc16 | groovesalad64 | 3 | 0.050545 | 3 | 3 | +4.604% | 47692 / 49152 B | 6144 B |
| pc16 | groovesalad128 | 0 | 0.000000 | 3 | 3 | +0.009% | No SBR owner | 0 B |

Both formats pass the 3-unit gate on this corpus. Both save the same allocator block space.
AAC-LC does not allocate SBR history. The JSON also retains the profile allocator probe for those control runs.
PC18 retains more accuracy for the next production-adapter experiment. Neither is production-qualified.

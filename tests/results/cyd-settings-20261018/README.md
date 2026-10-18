# CYD normalization HTTP settings

GET `/api/native/settings` retains volume/balance and adds `normalization`,
`normgain`, `normtarget`, `normtime`. POST accepts, for example,
`?normalization=1&normgain=12&normtarget=-6&normtime=6000`.

All recognized controls are validated before any setter runs. Values are plain
decimal; new supported ranges are 0/1, 0..20 dB, -20..0 dBFS and 100..10000 ms.
Existing volume/balance clamping is retained for valid numeric inputs. Known
duplicates, incomplete fields, truncated values and invalid integers return 400.
Common settings setters expose their persistence errors instead of hiding them
behind void output wrappers. Failure returns 500 and the original error code;
earlier fields may already be applied. This is not a multi-setting NVS transaction.

[Actual handler tests](report.json) execute 80 settings requests and all 51
existing stream scenarios under ASan/UBSan with explicit SDK/persistence seams.
They cover readback, range/parse bounds, complete prevalidation, per-setter
failure, and stopping subsequent setters. The 13 existing settings/clock
[source checks](source-checks.log) also pass. DSP golden PCM has its separate
normalizer campaign; physical NVS and audio acceptance remain integration gates.

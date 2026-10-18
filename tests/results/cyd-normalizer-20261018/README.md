# CYD shared normalizer integration

CYD uses the original `AudioNormalizer` algorithm through a portable C adapter.
Its output owner reads persisted normalization settings once per PCM packet,
caches configuration, and processes bounded chunks through a 512-byte static
scratch buffer. Decoder PCM stays read-only, including unaligned input. The
disabled path avoids PCM copying and DSP processing. CYD still mixes to mono;
its PDM, continuous DAC and legacy DAC pins, clocks and DMA configuration remain
target implementations.

Control tasks publish an atomic pending reset request. Only the output task
configures or mutates DSP. Generation discard, EOF, sample-rate and channel
changes reset normalizer history. The continuous DAC configuration also commits
its ready rate only after successful priming, so a failed prime cannot make a
same-rate retry retain the old DSP rate.

[Actual backend tests](normalizer/report.json) pass 239 PDM, 240 continuous DAC
and 239 legacy packets under ASan/UBSan, compared with the original normalizer
processing reference one frame at a time. Coverage includes immutable mmap
input, split-packet identity, mono/stereo/wider layouts, settings cache and
changes, disable/enable, concurrent reset requests, rate/layout/discard/EOF and
failed configure/prime retries. Drivers and the PDM resampler are host seams;
this is not a DMA latency or listening test.

The [disabled gain suite](disabled-gain/report.json) retains all 5,801,300
arithmetic comparisons and 375 output scenarios for each backend. The six
[pipeline lifecycle variants](lifecycle/report.json) and actual shared
[radio controller on both targets](radio/report.json) also pass. The lifecycle
seam checks that real PDM flush/discard paths request DSP reset; the dedicated
normalizer suite checks the DSP implementation itself.

Actual Xtensa resource usage, pinned SDK builds, full lint and physical audio
qualification are separate integration gates. Normalization remains disabled
by default; HTTP controls are integrated in the following settings change.

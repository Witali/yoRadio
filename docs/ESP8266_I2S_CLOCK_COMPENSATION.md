# Diagnostic I2S clock compensation

2026-09-17. Not enabled by default or qualified as a playback fix yet.

The configured PLL clock160MHz and divisors8*13 produce1538461.538 PDM bits/s.
PDM32 therefore consumes48076.923 output samples/s, not48000. Sending one
word per48k PCM sample slowly drains a live input reservoir: approximately
32ms of extra audio per20s. Network stalls remain a separate possible cause.

`-Diagnostic -Pdm32ClockCompensate` tests a causal linear resampler for the
48k input path:624 input samples become625 output samples. One previous PCM
sample, phase and priming flag cost8 static bytes. No allocation, floating
point or decoder changes. GCC originally emitted __divsi3 even for constant
625. The follow-up uses an exact bounded reciprocal:ceil(2^26/625), two
15-bit-split32-bit products and a single quotient correction. An exhaustive
host test checks every numerator0..40893840 against ordinary division.
The largest signed product is65535*624, safely within int32. First sample
is held rather than interpolated from an artificial zero. Stop/init/rate
changes reset interpolation history. Other rates retain the existing path;
this experiment does not claim to correct their clock rate yet.

The Opus decoded PCM remains unchanged. Physical PDM intentionally differs,
because its samples now follow the actual clock. Linear interpolation has
its usual high-frequency response tradeoff; it is not a bit-exact audio
optimization. The modulator itself is unchanged. Host tests compare every
DMA word against an independent absolute-time64-bit interpolation and PDM
oracle, across mono/stereo, gain/normalization, chunk sizes and DMA sizes.
All existing non-experimental rendering tests remain required.

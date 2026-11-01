# Public raw Opus cadence control

Four unchanged complete packet-mode fixtures run through stock public Ogg and
five public raw Opus configurations. Each raw stream owns one persistent
opaque handle, consumes whole complete packets in order, and explicitly uses
48 kHz stereo, ordinary framing (`self_delimited=false`) and no PLC requests.

The aggregate configuration selects the documented duration matching its
packets (120 ms, or 2.5 ms for the ordinary short control); the elementary
configuration selects 2.5 ms. `INVALID` is measured separately as the documented
60 ms output-sizing default. Full-size and initial 12,288-byte aggregate output
buffers distinguish synthesis from resize/retry effects. No undocumented drain
or empty raw packet is inserted. Stock Ogg uses genuine data-bearing EOS and
the public empty terminal drain.

Creator aggregate/elementary float output is byte-identical for these inputs.
Creator integer output on the clipped repeated-frame cases is itself dependent
on decode cadence; this is explicitly not an exact arbitrary-input integer
oracle. Public float peak and hard/soft conversion observations are retained
without a numerical acceptance tolerance. No production workaround or private
codec state is used. This is a diagnostic, not codec conformance acceptance.

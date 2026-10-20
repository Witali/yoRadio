# Floor1 range versus transform size

Read-only standards/source audit, 2026-10-20. Endpoint overflow alone is legal;
the reported FFmpeg setup rejection is an implementation restriction. This
does not certify the complete generated streams or any vendor decoder.

[Vorbis I, Xiph, 2020-07-04](https://xiph.org/vorbis/doc/Vorbis_I_spec.html):
§7.2.2 steps14–16 derive the implicit endpoint from the four-bit rangebits
field, independently of block size. §7.2.3 decodes Y values without adding an
X/block-size restriction. §7.2.4 curve-synthesis steps13–14 explicitly truncate
when the final X exceeds the requested length; steps11–12 extend a shorter
curve. §4.3.6 makes that requested floor length half the current transform
size. Here `N` denotes transform size and `n=N/2` denotes floor length; they
are not interchangeable. Thus X endpoints above current N/2 are supported
by the normative algorithm, including endpoints above the largest N/2.
§7.2.4 also requires an equivalent interpolation algorithm: moving an endpoint
inward before interpolation can change the in-range curve. §1.1.6 permits
only specifically labelled hardware omissions. No floor1 endpoint/block-size
exception is labelled in §7.2.2–7.2.4; it does not authorize dropping these cases.

The exact official [FFmpeg n8.1.1 source](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.1.1/libavcodec/vorbisdec.c)
contains `vorbis_parse_setup_hdr_floors`: after reading rangebits it computes
rangemax, rejects rangemax greater than `blocksize[1]/2`, logs the cited error,
and returns invalid-data before assigning the implicit X endpoint. This is a
global longest-block bound, not a comparison with the selected packet mode.
The tag's [RELEASE](https://github.com/FFmpeg/FFmpeg/blob/n8.1.1/RELEASE)
identifies 8.1.1. The 8.1 doxygen page is corroboration, not the exact-version
source used for this conclusion. No local executable was invoked or certified.

With the supplied floor endpoints128/1024, this guard explains both supplied
diagnostics: S64/L64 compares128 against32; S64/L1024 allows128 then rejects1024
against512. Endpoint16 is below even the minimum legal transform's half-size32,
so the minimal floor fixture avoids this restriction. This arithmetic does
not establish successful decoding or PCM equivalence.

The official [Xiph libvorbis v1.3.7 floor1.c](https://raw.githubusercontent.com/xiph/vorbis/v1.3.7/lib/floor1.c)
corroborates the interpretation: `floor1_unpack` accepts the endpoint derived
from rangebits without a block-size limit, while checking reads, books and
duplicate posts; `floor1_inverse2` passes the selected block's half-size to
`render_line`. That renderer computes the original line slope before limiting
its writes to the requested interval. This is source inspection, not a
libvorbis execution result.

Keep all36 ordered size pairs and the realistic endpoint-overflow cases in
scope. A compact-floor family exercises different coverage and cannot replace
floor truncation coverage. The independent libvorbis execution remains with
root; absent successful reference PCM, a native-FFmpeg refusal supplies no
PCM comparison and must not be converted into a matrix pass. Full setup,
packet, mode/window and output correctness still require their existing gates.

Only static design/inspector inputs were read. The live108 host matrix report
and its transient logs were not read or qualified. No compiler, SDK, QEMU,
reference decoder, Git, device, canonical source or campaign was modified or
run. No Ogg-extension, EOF/reset/OOM or private codec qualification is implied.

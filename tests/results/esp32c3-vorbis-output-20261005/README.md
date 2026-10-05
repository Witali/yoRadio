# Vorbis retry and EOF evidence, 2026-10-05

Original pinned RV32 DSP; no physical board is used by these QEMU cases.
`baseline` and `packet-trace` preserve failures before this repair.
`retry-only` fixes capacity checks but retains the parser EOF defect.
`eof-first` is a preliminary run; `final` is the qualified source snapshot.
`raw-reference` bypasses Ogg streaming and supplies independently extracted
packets to the same original DSP. It establishes all 535 synthesis packets and
528000 frames/channel, matching the fixture final granule without padding.
The old Ogg path missed its final five packets (1088 frames/channel).

All seven final cases pass. Complete PCM matches the raw reference exactly.
FFmpeg 8.1.1 default Vorbis decoding gives the same sample count; max difference
is 2 signed-16 LSB, RMSE 0.70956 LSB. The retained PCM is the direct s16le decode
of tests/fixtures/esp32c3_calibration/vorbis-q10.ogg, with no alignment shift.
Command: ffmpeg -i <fixture> -f s16le -acodec pcm_s16le <output.pcm>.

These cases do not cover every legal granule trim, chained stream or malformed
packet. Build images and source snapshots are kept with each run. QEMU disk
images are excluded because they are reproducible from those files.

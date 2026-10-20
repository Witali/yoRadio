# Checked numeric adapter revision02

Revision01 actual comparison rejected before measuring any case: native FFmpeg
labels its validated two-channel WAV as stereo in framemd5, while Xiph labels
it as 2 channels. Both exact labels are now accepted. WAV channel count2,
rate/format/frame/MD5/byte checks remain mandatory; no other layout is accepted.
All measurement/policy and exact17 process/source/contract gates are unchanged.
Revision01 sources and failed output remain intact. This revision has not yet
measured PCM; root owns its later command and result.

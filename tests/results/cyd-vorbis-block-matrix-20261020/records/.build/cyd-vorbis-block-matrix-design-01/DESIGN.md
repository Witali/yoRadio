# Public raw Vorbis block-pair and transition matrix: design only

The objective is all 36 legal short/long pairs AND SS/SL/LL/LS output transitions
on both CYD/Xtensa and C3/RV32. No missing cell may be skipped or called qualified.
The full generator/validation proposal is below. No candidate construction,
reference decoder, SDK, compiler or target command has been run.

## Standards and public-source findings

[Vorbis I (Xiph, July 2020)](https://xiph.org/vorbis/doc/Vorbis_I_spec.html),
sections 4.2.2,7.2.4,8.6.2 and4.3.8: legal block sizes are powers64..8192,
short<=long; floor1 extends/truncates to requested length; residue endpoints are
clipped; first output is zero, then samples/channel=(previous+current block)/4.
Sections 1.1.3/8.6.2 permit padding and nominal residue end-of-packet; this does not
prove unchanged entropy traversal or useful PCM. Section A.2 defines container
positioning/trimming separately.

Pure public-syntax inspection confirms two floor *type1* configurations, endpoints
128/1024; modes0/1 map to stereo-coupled submaps0/1, each containing both channels.
Their residue2 configs are begin0/end64/partition16 and begin0/end416/partition32.
Thus short-residue capacity fits every legal short size. Long clipping differs:

| long size | pairs | long partitions | construction property before host validation |
|---|---:|---:|---|
| 512..8192 | 30 | 13 | unchanged floor/residue bit traversal; different transforms/windows |
| 64,128,256 | 6 | 2,4,8 | altered residue traversal between passes; require independent evidence |

All36 identification headers are legal. Floor1 rendering permits the changed
lengths. The six difficult bodies are not automatically invalid (padding/nominal
end-of-packet is allowed), but their complete useful decode cannot be inferred.
None of the 36 is newly runtime qualified here, including the easier 30.

## Concrete candidate generator (source proposal, unexecuted)

`matrix_candidates.py --output <fresh-dir> --ffmpeg <pinned.exe> --ffprobe <pinned.exe>`
constructs two 36-case families and writes candidates.json containing exact future
reference argv. It runs no command. It pins the original encoder Ogg/source/audio,
validates CRCs, extracts the public packets, patches identification byte28 (raw
fixture_info byte21), remuxes CRC-correct one-audio-packet-per-page host carriers
and reparses every result.
Rate192000/channels2 and the same setup are preserved. It does not re-encode.

* `identity`: all 68 original audio packets byte-identical. This directly answers
  the header-only question for every pair after independent host validation.
* `transitions`: all 68 donor packets remain in order; insert two copies of the
  original short packet. Donor indices are [0,0,1,2,0,3,...,67]. At new packet3
  clear only its next-window bit; at new packet5 clear only its previous-window
  bit. All other bytes are unchanged. These two public window-header corrections
  match actual neighbors. This family has 70 packets and SS1/SL2/LL65/LS1.

The transition edits deliberately differ from the header-only family; every
change is listed. SS/SL/LL/LS outputs occur at packets1/2/3/4, safely before EOS
container cropping. Priming packet0 still produces zero bytes. For stereo16:

```text
identity:    PCM=[0,S+L]+[2*L]*66; sum=S+133*L; samples/channel=sum/4
transitions: PCM[i>0]=block[i-1]+block[i]; sum=5*S+133*L
```

Transition totals range8832..1130496 bytes; each packet is at most16384 bytes.
The static matrix-plan.json records both families' accounting and pending status.

## Mandatory host gate and accounting

RUNBOOK.md gives exact entry points. Execute both pinned FFmpeg native vorbis and
libvorbis decoders plus packet/frame probe for all 72 candidates with bounded
owned commands and retained tool/source hashes, argv, logs and terminal receipts.
Require correct metadata, all input packets, complete nonzero PCM and active
nonzero SS/SL/LL/LS output in the transition family. No unexplained decoder
error/warning, dropped packet or count deficit qualifies. Same-vendor agreement
alone is insufficient. Parse actual WAV16 rate/channels/bits/sample counts without
-ar/-ac forcing. Native/libvorbis counts and metadata must match; compare aligned
PCM16 with maximum absolute difference<=2 signed16 units and record maximum,
mean/summed difference and differing sample count. Exceeding2 is nonpass until
review; never silently widen the tolerance. Firmware vendor-vs-checked remains
byte-exact. Do not compare PCM hashes across different block pairs.

The original source carriers each have one EOS page holding68 audio packets.
The proposed carriers instead flush each audio packet separately, granule0 for
priming and cumulative sum((previous+current block)//4) thereafter, EOS only on
the last. This gives explicit zero-origin raw positioning. Require actual ffprobe
and WAV sample counts to equal expected_raw_samples; do not merely assume this
page recipe fixes all demux behavior. Keep old singlepage272448/272320 observations
as history, not a new trim formula. Unexplained count differences are nonpass;
never adjust granules to force acceptance. If a host transport discrepancy
persists, a separately reviewed public raw host probe can distinguish it without
starting Ogg target EOF/reset work.

## Difficult six and supplemental minimal fixture

All six clipped-residue pairs remain mandatory in BOTH realistic families. Their
actual native/libvorbis decode, exact counts, nonzero transition outputs and
bounded cross-decoder differences decide validity. A host failure is retained as
an unqualified candidate, not a bridge defect, allowed skip or 30/30 success.
Root has separately assigned a minimal nonzero public floor1/residue1/codebook
fixture for all 36 pairs and neighbor flags. Keep its source/pins/results distinct;
it supplements this realistic corpus and cannot replace its failed/missing cells.
Both public fixture paths preserve the full36/all-transition objective. If donor
short packet0 is silent in a required output, that realistic transition candidate
needs a reviewed active-short donor construction before claiming completion.

## Subsequent raw target qualification

Use the host-qualified transition family for all 36 cases. At rate192000 require
original public vendor full decode first, then fresh original/checked opaque
handles must agree byte-for-byte at the same pair/rate. Preserve every-packet
public metadata lifetime/checks, input consumption,16-byte canaries, exact sizes,
all packet indices and nonzero output for each transition. Vendor unsupported,
panic, timeout or allocation error is nonpass, never an allowed skip. Keep the
existing low-rate/boundary regression and specific public header-error controls;
rate cross-products are not implied by this block matrix.

Parameterize the existing caller's fixed short256/mode accounting using each
case. Native protocol must count all 36 unique pairs, their four transitions and
69 output packets per transition case. Host protocol tests reject missing pairs,
missing/reordered packets/transitions, wrong dimensions/counts/metadata, inexact
PCM, canary failure and incomplete process receipts. Independently run both ABIs
with their correct native core/prefix rules; neither qualifies the other. Call
the outcome public raw block-pair/transition regression for this independently
validated stereo floor1 workload, never general Vorbis conformance.

Only standard-library public-syntax/page-header inspection and arithmetic ran
here. Generator source received syntax inspection only. No previous prep,
canonical file, campaign, deferred Ogg/EOF/reset/ownership/OOM/AAC work or donor
application hook was changed or executed. Input and design hashes are frozen.

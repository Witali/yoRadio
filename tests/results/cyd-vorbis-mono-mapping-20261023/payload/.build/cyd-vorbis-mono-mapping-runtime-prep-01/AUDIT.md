# Mono/mapping21 source and recorded-evidence audit

This review executed no generator, witness, construction test, reference decoder,
SDK, compiler, QEMU, Git or device operation. Only source/text/JSON reads, raw
packet hashes, identification/mode metadata accounting and Python AST parsing
were performed. No recorded WAV/PCM payload was read by the reviewing agent.

The canonical generator is `tests/vorbis_format_corpus/generate_mono_mapping.py`,
SHA256 `c7c494f8b03266a4589a8b141e4b12b008e545f8081a09cf57c9b0965cd14a27`.
It imports the normal pinned minimal helper
`8e3eff3fbe08f24399dd74c5ca449eb7ead0fe0f27e464f6d8314e7fbcaf64f1`.
The actual canonical corpus is `.build/vorbis-mono-mapping-canonical-check-01/`:

- `matrix.json`: `30fad94ec85727030a415f33c544041ed225aae97397b09584a534f7c2636d37`.
- `manifest.json`: `990d5900cfabf9a0027de900f54ad811e857c59944fae2f5f5ff2d4076594d95`.
- 108 manifest entries, including105 full raw/carrier files, all raw hashes checked.
- 21 cases: nine mono and12 stereo;294 packets;464640 expected PCM16 bytes.
- Nine rates:8000,11025,12000,16000,22050,24000,32000,44100,48000.
- Last three stereo48000 cases: coupling, mux/submaps, interleaved residue2.

All105 raw/carrier bytes and the entire matrix match the original
`.build/cyd-vorbis-mono-mapping-prep-01/generated01/` exactly. Construction metadata
also matches. Only the previously declared pure-checks/manifest provenance differs.
All30-byte actual identification packets advertise the correct channels/rate,
short256/long2048 and framing. Actual14 packet-mode/window flags, offset bounds,
both frame-count arrays and per-packet PCM-size arrays agree with independent
overlap arithmetic. Every case has7040 frames; mono14080 bytes, stereo28160.

The committed reproduction record is
`tests/results/vorbis-more-generators-20261020/`:
manifest `c66cefeb56522cdb0b4b466c9823ca02c85d9c9772ed8679aa8944f611cf95ba`.
Its24 retained entries were hash-checked. Its canonical/original mono manifests
match the two actual corpora. It retains generator projections, receipts and full
raw hashes, and explicitly does not duplicate the generated binaries or establish
reference/target qualification. Current generator/minimal-helper/README source
pins match the canonical corpus manifest. No source defect was found in the
finite mono/mapping construction reviewed here.

The unchanged host02 driver SHA
`65a69cdada2c18f72420e348a76c1d5d19da2b4ce9c260a8df6c0e9804767704`
already supports actual channels1/2 dynamically. More importantly, it already
ran all21: `.build/cyd-vorbis-mono-mapping-host-01/report.json`, SHA
`ab80560ca5a1a6d01acdac07508122125bbb7f6597eafb5a94f1a454b31b7abd`.
All42 retained child receipts were checked as actual terminal0, without timeout
or interruption. Recorded metadata reports both decoders accepted all21, all
transition/channel outputs nonzero, and max cross-reference error1 for every case.
The independent recorded qualifier report is
`.build/cyd-vorbis-mono-mapping-qualified-01/qualification.json`, SHA
`c31a87de53327cb0e43215f92339b07fd64c48ba57dbde8778328f298b9f5684`.
It is `DUAL_REFERENCE_QUALIFIED` only for this mono21 campaign, with the existing
predeclared bound2. Its actual wrapper terminal0 is retained. The new runtime
binder will recheck all recorded42 WAV/framemd5 streams and full lengths again;
that future replay was not performed during this source review.

The old target caller37ea/protocol5476 cannot capture mono correctly. They require
channel2 in descriptors/public decoder info, scan PCM with a4-byte stereo stride,
and require both left/right nonzero. The protocol also requires two matrices.
The new separate caller/protocol permit actual1/2 channels, use stride2/4, require
absent mono right counts0, bind actual decoder channels/rate/16bits and preserve
full input consumption, complete PCM, canaries and all four transitions. A single
complete21 matrix preserves original case order without an artificial split.

The meaningful test gap is explicit: canonical `test_books.py` covers book
construction. The mono generator has six useful rejection controls; its historical
`readback02.py` reuses its own `inspect_setup`/`inspect_packet`, and those inspectors
share writer `plan`/`symbol` helpers. This finite source/symbol check is not an
independent Vorbis parser. The existing actual dual-reference qualification is
stronger evidence for these exact21 fixtures. A separate independent construction
reader could improve reusable generator tests later; this prep adds only focused
protocol controls for the mono/stereo assumptions being changed.

The next finite gap is the full21 public raw target capture, then a separately
reviewed numerical comparison. This preparation does not qualify target PCM,
complete Vorbis conformance, radio integration, audio hardware or deferred scopes.

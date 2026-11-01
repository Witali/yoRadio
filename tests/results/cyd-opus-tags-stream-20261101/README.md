# Constant-memory streamed OpusTags: HOST checkpoint

`opus_tags_stream.h` validates required vendor/comment length fields, comment
counts and declared UTF-8 vectors across arbitrary byte, lacing and page splits.
Its verified-page adapter starts from the caller's real held OpusHead event,
commits only accepted page state and never ACKs or resets the caller's page.
Invalid final fields/text leave that held page unACKed and prior state unchanged.
Corrupt CRC pages never reach the validator.

The contract follows [RFC 7845 section 5.2](https://www.rfc-editor.org/rfc/rfc7845.html#section-5.2)
and [RFC 3629 section 4](https://www.rfc-editor.org/rfc/rfc3629.html#section-4).
All declared vectors are validated, including comments beyond 61440 bytes;
the optional permission to ignore those comments is not used. Arbitrary binary
data after the list is accepted. The only header-size policy rejects actual
headers above 125829120 bytes, as expressly permitted by RFC 7845. That exact
size is accepted, including a vendor string filling the legal bound. There is
no whole-comment allocation, metadata display, optional R128 gain application
or tag-name interpretation. This checkpoint qualifies lengths and UTF-8, not
every tag's optional semantic meaning or complete codec/container conformance.

The first actual GCC ASan/UBSan/leak capture passes. Python's strict UTF-8
decoder independently supplies 1308946 vectors: all 1112064 Unicode scalar
values, all single-byte and two-byte sequences, selected three-/four-byte
sequences and 18 explicit boundaries. These are not all possible longer byte
sequences. Each vector is tested as both a declared vendor and comment vector:
2617892 text packets and 2618236 parser schedules. The 32 field controls cover
missing/truncated fields, uint32 boundaries, empty vectors, many comments and
binary tails. Three real streamed size-policy controls test the inclusive
120 MiB bound and the first refused byte. Twenty real verified-page schedules
also pass creator libogg packet/CRC walks with 3398 actual ACKs, including
70000-byte vendor and comment vectors, nil pages and UTF-8 split across lacing.
The measured HOST parser is 32 bytes and verified stream is 56 bytes. No decoder
or native firmware executes in this gate.

Run `python -B tests/verify-opus-tags-playback-host.py --checkpoint tags --require-current`.
The data verifier executes no captured code and reads no omitted vectors,
executable, encoded or PCM payload. Full generated vectors and executables
remain local by hash and size. No prior evidence is overwritten.

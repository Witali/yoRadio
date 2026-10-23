# C3 complete25 numeric source successor02

This source-only successor fixes one pre-runtime issue in numeric prep01:
`c3_platform` decoded the actual macro log without normalizing CRLF, while its
existing line regexes use `$` anchors. The root read the baseline log and reported
1589 LF and 1589 CRLF (actual root observation chunk `e286b5`). That target log and
all PCM remain unread by this preparation.

The **sole functional adapter change** is:

```python
command['stdout_sha256']).decode().replace('\r\n', '\n')
```

`adapter-revision02.diff` contains the complete one-line diff. The raw macro log
is still hash-verified before decoding; only the in-memory regex input changes.
Prep01 is preserved byte-for-byte and is never overwritten.

The base adapter is
`0454f4c7fa2cc52a0bdd3f38899b180afb934356b66f0ade438917d10d052a5f`.
Metrics and policy remain identical at
`a2c600f8e19f3b48baaa12c559e60d0105401cba12362ce0250836c23b319f8f` and
`32ef721fa8a812684e83be296d7b74f90a12414644639f74ea353eef862d3dd6`.
Runner `e00a30172c3b4291f080b2eee937214108adda7b6a03178e2f9833cb44d92034`,
protocol `961b0050f5881e5000116cbf7a598a122407420b0a52da0805d060c7b7e3f7ba`,
caller `8c6aff4bb6d43c6b034db799477653e89fff4c9e65ac0b805d99f257672e9f03`,
contract/model/data, independent old17/new8 reference bindings, and every other
adapter byte are unchanged.

All existing complete25/350packet/623360byte/778event requirements remain. Partial
or NONPASS target captures fail before PCM access. The adapter still requires
actual terminal0 command and direct-tool receipts, retained actual ELF243,
compile JSON and macro context, SDK `9a97f6c54ec638111ce55cd36581b3c192f15207`,
core0/coordinator0, RV32/ILP32/160 MHz/unicore, and the dynamic setup identity
binding between the actual report, frozen candidate, compiled variant and row.
No C3/CYD binary equivalence is assumed.

The optional predeclared project bound remains 2 S16 LSB, default None; it is not
a normative Vorbis tolerance. Full25 results cannot be overridden by the
post-complete25 books16 subgroup. Known failing cases and original dual-reference
NONPASS evidence remain preserved. Numeric, conformance, full G6, radio, and
physical-device qualification are not claimed here.

`prepare_successor.py` assembles only source bytes; `check_source.py` checks ASTs,
the complete one-line byte diff, copied module identities, runtime source pins,
and immutable parent inputs. Neither imports nor executes the prepared adapter,
metrics, policy, protocol, runtime, tests, references, SDK, compiler, or emulator.

After review and a complete actual C3 capture, the root-owned invocation is:

```powershell
& 'C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe' -B -X utf8 .build/c3-vorbis-format-expanded25-numeric-prep-02/compare_capture25.py --repository 'C:/Work/yoRadio/.worktree/esp32-cyd-c3-review' --target '<complete actual C3 full25 directory>' --target-report-sha256 '<reviewed report SHA256>' --target-terminal '<actual direct-tool terminal JSON>' --output '<fresh independent checkout .build output>' --max-abs-error 2
```

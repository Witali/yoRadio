# C3 raw Vorbis format protocol validation

`c3_vorbis_format_protocol.py` is a standalone module based on the reviewed
canonical CYD `fixture_accounting`/`validate_log` algorithm. It directly checks
raw `C3_VORBIS_FORMAT_` lines and core0, as printed by the authoritative public
caller frozen here as `source_main.c`. It does not translate captured C3 logs
into CYD logs or start any process.

`fixture.h` is an exact copy of the caller's fixture, SHA256
`839febe9f12d7bc33e6afd8a9f0b16ee799f12d6c8ecb88188537b7ae8349378`.
The module requires all 68 vendor packets, complete input consumption, exact
public overlap byte counts, 66 full 8192 outputs, public metadata on every
packet including priming, and each paired exact-PCM/canary attestation.

The API keeps the same first four arguments, with two required keyword-only
owned-process facts:

```python
observed = validate_log(raw_log, "baseline", None, fixture_header_text,
                        returncode=actual_returncode, timed_out=actual_timeout_flag)
```

Returncode must be integer0 and timed_out must be explicitly False; missing or
unknown facts are not an implicit success. Failure/panic/timeout captures fail,
even if they contain a complete-looking protocol. Foreign/mixed prefixes,
wrong cores, missing/duplicate/reordered packets or incorrect metadata fail.
The caller still owns input/tool/source binding and the actual process receipt;
this function returns observed protocol counts, not a hardware qualification.

Scopes and expected counts are:

| scope / control | protocol lines | exact pair packets | meaning |
|---|---:|---:|---|
| baseline / None | 285 | 204 | Inherited low-rate header restriction reproduced; acceptance remains false |
| acceptance / None | 421 | 340 | Every legal rate accepted with vendor-exact PCM |
| acceptance / old-guard | 279 | 204 | Exact legal_candidate_open_required after full vendor/ordinary/high-rate prerequisites |

Header rejections require the caller's `header_error=1` attestation after its
public `ESP_AUDIO_ERR_FAIL` and null-handle check; a generic allocation/error
result cannot substitute. A wrong or early control failure cannot qualify.
No C3 target result is inferred from the CYD result or synthetic host tests.

The host suite uses synthetic native C3 protocols and the exact fixture. Eight
methods cover positive scopes, wrong/mixed prefix/core, missing/duplicate/order
and output checks, priming/later zero or wrong metadata, header-error attestation,
wrong/early control failures, explicit process facts and panic/timeout cases.
Only this host suite was executed. No SDK/compiler/QEMU/reference/Git command
or canonical/current-campaign change was performed during this preparation.
Exact argv, source/tool/log hashes and exit status are in host-tests.command.json.

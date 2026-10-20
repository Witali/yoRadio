# CYD static RX: production SDK and complete Clang evidence

This bounded archive retains seven original GCC production qualifications and
six successor Clang frontend/lint qualifications from the exact final successor
closure. The original rejected PDM Clang qualifier remains nonpass history.
The earlier archive-write attempt is separately preserved as a packaging nonpass:
its advertised root reader paths were missing. This archive uses the corrected
canonical packager paths; production qualification remains the same seven/six.
`index.json`, raw reports and both markers specify the actual source/SDK/tool
identities and profile counts; `path-map.json` and `bindings.json` bind retained
text to the original report references. See the retained packager SPEC.md for
selection details, archive-stage observations and qualification limits.

Run the stdlib offline verifier with the independently recorded manifest SHA:

```text
python -B verify.py --manifest-sha256 EXACT_ARCHIVE_MANIFEST_SHA256
```

Optional `--repository PATH` checks explicitly linked repository artifacts.
Without it, prior evidence/firmware payloads remain linked identities. Executable
ELF/object/library/ROM/tool/firmware bytes are intentionally omitted with SHA and
size. Existing app.bin files stay in firmware/development. No SDK, test recipe or
qualifier is replayed, and omitted binaries cannot be reconstructed from this
archive. Hash verification preserves evidence integrity; it is not new physical
acceptance, production Clang equivalence, acoustic quality or peak/free-heap proof.

Production images use GCC/Picolibc. The experimental Clang/Newlib+nano profile
has a separate exact config scope. Physical and deferred codec gates remain open.

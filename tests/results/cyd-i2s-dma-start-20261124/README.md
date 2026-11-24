# ESP32 I2S DMA START regression evidence, 2026-11-24

This package establishes a deterministic register-semantics failure and its START-only fix using real QEMU QTest transactions. It does not establish the cause of the intermittent native continuous-DAC timeout. Native full-app controls are a separate qualification step.

| Control | Existing startup/cancellation cases | New START cases |
|---|---:|---:|
| Exact selected EB88 executable | 6/6 | 0/4 |
| Private retained-object relink | 6/6 | 0/4 |
| Private unchanged recompile/relink | 6/6 | 0/4 |
| Private START-only fix | 6/6 | 4/4 |

The selected baseline SHA256 is `eb88d36f5bea48f547615ee147cf01985f9adf301112e2954ad90b8ca461ed02`. The fixed executable SHA256 is `28068f674d06c4322aa72989756d7dd3734bb0d06c4aa1acf21b919ccb3465f4`.

Each run directory retains its aggregate report, per-case assertions and complete MMIO/clock transactions, and the six-case helper's stdout/stderr. `*-self-contained-qtest` repeats the matched baseline/fixed controls with the helper copied into the private handoff. Reports preserve their original script/executable hashes and commands. Archived historical scripts under `provenance/private-test-sources` explain those exact hashes; use the promoted test directory for future runs.

The baseline incorrectly retains START. Its repeated SDK-style address-only update completes descriptor B before explicit START. With the production-like owner-check-disabled setting, the explicit command consumes B again. With owner checking enabled as a negative control, the explicit command instead raises descriptor error. The fixed image clears stored START after executing the command and passes these checks without timing, EOF, ownership, or driver changes. The hardware basis is [Espressif ESP32 TRM v5.9, section 2.6, printed page 60](https://documentation.espressif.com/ESP32_Technical_Reference_Manual_en.pdf#page=60).

`provenance/input-manifest.json` fingerprints 701 retained/compiler/link inputs. `compiler-dependencies.json` records 420 actual compiler dependency files for each model variant. Compiler tools, compile argv, flat link responses, output hashes, raw/normalized PE comparisons, and successful compiler/linker logs are retained. The unchanged compiled object exactly matches the retained model object. The matched-name unchanged relink matches the selected binary after explicit COFF/export timestamp and PE checksum normalization. The initial differently named relink is retained, including its export-name difference; it is not presented as identical. Historical `summary.json` describes the private experiment before promotion, including its then-frozen HEAD/index.

Executables, object/library/toolchain binaries, caches, firmware, private keys, and full TLS fixtures are absent. Fingerprints of external inputs are provenance records, not embedded build inputs. Recreating the relay requires the matching external QEMU build, toolchain, and recorded objects; the package does not claim to contain a standalone QEMU distribution.

The promoted self-contained entry point and exact retained model/one-line patch are in [the test directory](../../target/cyd_full_app_openeth_qemu/i2s_dma/README.md). Future invocation checks can be added separately without rewriting the preserved original negatives.

## Promoted entry point verification

`promoted-exact-baseline` and `promoted-fixed` preserve fresh checks of the permanent script with no `--legacy` override. The script discovered the bundled six-case helper. The exact baseline still passes the old six and fails all four new cases; the private START-only executable passes all ten. These checks ran without compilation or native full-app tests. `promoted-source-manifest.json` binds the shipped test/model/patch/license files.

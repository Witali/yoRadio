# ESP32 peripheral test selection: source preparation only

Original: `C:/Work/QEMU-ESP32/.worktree/cyd-idf6-compat/tools/test_esp_modules.py`,
SHA-256 `ac6bf67b53508a84a930717103007f5112d784db6a989ff1fd57b14593f17657`.
The original copy is exact; `filter.patch` changes only `main()`. All existing
`test_spi`, `check_sd`, `test_legacy_cyd`, other test bodies and assertions remain
unchanged. The normalized unified diff was reconstructed against the overlay in
memory. No runner was imported or executed, and no external file was changed.

`--soc all` is the default and keeps the existing full check order. Missing
`--c2-rom-dir` produces `parser.error('--c2-rom-dir is required when --soc=all')`
before state-directory creation. The new `--soc esp32` selects only the existing
`esp32_dual_spi` and `legacy_cyd_mmio` checks and hashes only the Xtensa executable.
It performs no C2/C3 image, executable or genuine-ROM access. The report records
`soc` so the filtered success cannot be mistaken for all-SoC coverage.

Future root-owned invocation from the QEMU worktree, after applying/reviewing:

```text
python -B tools/test_esp_modules.py --soc esp32 --qemu-xtensa <new-executable> --state-directory <root-supplied-fresh-workspace-.build-child>
```

The existing runner's two VM scenarios use SPI2/SPI3 LCD/SD MMIO, paused CPUs,
snapshot synthetic media, disabled NIC/display/serial, and loopback QMP/QTest
listeners. Imported `small_tv_vm`, `esp_board`, `small_tv_network`, `small_tv_web`
and `esp_services` define helpers/constants; importing them does not invoke their
seeding functions, create VM processes or enable network services. Their source
hashes are recorded in `inputs.json`.

Actual existing lifecycle limitations require an outer root-owned deadline and
cleanup of that run's owned PID: VM initialization can fail after Popen without
cleanup, and `close()` has no fallback if QMP quit/ACK fails. Dynamically reserved
ports are released before QEMU binds them, and this caller does not use QMP's
optional VM-name identity check. This patch intentionally does not redesign VM.
Use a fresh state directory because existing filenames are overwritten. Run
without `-O` and without `PYTHONOPTIMIZE`, since existing checks use `assert`.
Missing output/report or a failed controller must not be interpreted as success.
These peripheral checks cannot qualify production boot, audio, RF or a board.

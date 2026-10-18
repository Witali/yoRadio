# C3 command generation ordering

The [negative control](before-fix.json) records original production source
hashes. Its [log](before-fix.log) shows the failed semantic assertion: the last
queued command's generation differs from the current generation after a paused
older Play overwrites a newer command. This could discard the selected stream
before connection, rather than simply publish a stale label.

The control mutex now covers each complete Play/Stop/Resume transaction,
including generation/state publication, last URL/codec and queue overwrite.
Resume calls the private locked helper to avoid recursive mutex acquisition.
The benchmark fixture path uses the same ownership boundary.

[The passing report](report.json) and [test log](test.log) cover deterministic
preemption before the state mutex, 2,000 concurrent Play/Stop/Resume operations,
invalid arguments, empty Resume, queue failure and recovery. Actual production
command and state functions run under ASan/UBSan with real host mutexes and a
scripted queue seam. Physical RTOS/Wi-Fi timing remains unqualified.

Existing source/settings contracts pass; the previously found title-race test
also passes. The changed C3 audio module completes targeted clang-tidy with the
same reviewed profile; complete project baselines remain in the
[analysis campaign](../native-lint-20261018/).

The tested-radio production build of source `112c871f` passes. The saved
1,474,480-byte [application](../../../firmware/development/esp32c3-oled-native-command-fix/app.bin)
and [manifest/config](../../../firmware/development/esp32c3-oled-native-command-fix/manifest.json)
have a clean application descriptor and a verified embedded ELF hash.
No flashing or physical acceptance was performed.

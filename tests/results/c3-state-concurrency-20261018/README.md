# C3 metadata generation race

The [new regression](../../run-c3-state-concurrency.py) fails on the original
C3 publication path: preemption after its generation check but before the
state mutex lets the old callback overwrite and then clear the new title.
[The negative control](negative-control.json) records the original source
hashes; its [log](before-fix.log) contains the failed semantic assertion.

The fixed callback passes its generation into the state setter, which compares
identity while holding the state mutex. Stop relies on the existing atomic
state transition's title clear instead of clearing a potentially newer title.

[The passing report](report.json) records source hashes; [the log](test.log)
covers forced preemption at the original race, stale and empty old titles,
20,000 contended updates with actual pthread mutexes, truncation and generation
wrap. ASan/UBSan pass. RTOS scheduling and physical board timing are not modeled.

The C3 tested-radio production build of `793e26c5` passes. Its 1,474,336-byte
[application](../../../firmware/development/esp32c3-oled-native-state-fix/app.bin)
and [manifest/config](../../../firmware/development/esp32c3-oled-native-state-fix/manifest.json)
are saved separately from the previous shared-parser image. The embedded ELF
hash matches the build ELF and its application descriptor has no dirty suffix.
No flashing or physical acceptance was performed.

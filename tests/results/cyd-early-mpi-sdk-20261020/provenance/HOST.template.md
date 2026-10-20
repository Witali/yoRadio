# Reproduction and evidence limits

Root ran the existing `build-production.ps1` exporter against installed SDK
6.0.2, commit `7101770dc6db2667b3c477cc31365dd1acd6db4e`, with no downloads,
Setup or AllowDirty override. Legacy profiles use the pinned SDK5 driver source
at `735507283d5b2f9fb363a1901172dbd9e847945d`. The two original PDM profiles
use the frozen original campaign; the five remaining profiles use exact short
build paths `.build/em-sdk-01/{vc,vl,cp,cc,cl}/build`. The scripts, commands,
installed tool hashes, whole exporter source snapshot and clean HEAD checks are
preserved in the mapped raw evidence.
For selected canonical text only, raw Git blobs and actual compiler-working
bytes are both stored with their hashes. Uniform LF↔CRLF conversion must exactly
reconstruct the working file. This explicit dual representation neither changes
source nor relaxes baseline/evidence/receipt raw-byte checks. A rejected initial
packager-prep raw-equality attempt is retained as history; it ran no SDK/archive.

Both original PDM exporter processes exited zero. Their exact qualified report
SHA is `7c2007b1a33a3dfedde6be0ee13e09b463403d6ffdd9d6506fbe1edbbb29a1f4`.
The remaining five exited zero and were combined only after validating that
unchanged report and its actual image/ELF/log input hashes. The final report SHA
is `@@BACKEND_REPORT_SHA@@`. This archive is generated only after both reports
are complete PASS and all selected input hashes are rechecked.

The baseline `app.bin` and `partition-table.bin` are the only explicit LFS
exceptions to raw Git blob equality. Each standard pointer's OID/size is bound
to the manifest, hydrated file and already-present local object. Raw pointers,
binding metadata and file identities are retained. No object is fetched. The
first failed prepare used strict raw equality before this exact LFS exception;
its source/error metadata is historical, not a successful prepare or SDK run.
It did not save raw stderr; no reconstructed stream is presented as original.

`path-map.json` keys original path plus SHA so frozen historical versions remain
distinct. Stored text is raw or deterministic gzip with both encoded and decoded
hashes. `bindings.json` links original JSON hash locations to retained payloads
or explicit omissions. `current-verification.json` binds every selected file
read and confirms stability after collection. Canonical source snapshots cover
MPI/startup, board/tasks, allocator/reclaim, HTTP and the existing warning's
component declaration. Reading existing profile selectors or build metadata does
not qualify any deferred codec change.

The archive does not duplicate flashable applications, whole ELFs, tool binaries,
ROMs, libraries or objects. Referenced binary artifacts retain SHA/size/role
records; unreferenced replaceable working-build files are outside the selected
archive closure. ELF header/program/data-word metadata and raw nm/disassembly
logs support offline selected-entry checks; omitted original binaries remain
necessary to independently repeat a full linked-binary inspection.

`verify.py` needs only the Python standard library and reads only this directory.
It does not build, invoke SDK tools, contact a device, execute firmware or
establish physical behavior. Earlier isolated target/QEMU tests remain in the
unchanged original MPI archive; minimum-fixture lazy mutex observations must not
be relabelled as the actual full radio's pre-app mutex state. RAM, fragmentation,
timing, pool sizes and task affinity were not retuned or claimed improved.

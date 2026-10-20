# Native OTA component dependency check

Preparation only until the parent authorizes a committed checkpoint. The source
change will query BUILD_COMPONENTS, retain the sibling include fallback only
when native_stream is absent, and use idf_component_optional_requires(PRIVATE
native_stream) after registration. C3 component discovery stays unchanged.
The earlier unconditional PRIV_REQUIRES proposal was not applied or executed;
it would force an extra C3 source archive and was discarded during preparation.

Run fresh component-present and component-absent SDK configurations and compile
only libnative_ota.a for actual CYD SDK 6.0.2 and pinned C3 SDK 6.1. Start from
the verified early-MPI PDM
and C3 AP-timeout sdkconfigs, without the C3 wrapper's RTC rewrites. Do not invoke
setup, download, production export, flashing, serial, or hardware operations.

The CYD present case uses the full actual radio configure. The other three use
an isolated real-SDK project; C3 donor configure would invoke an excluded codec
patcher and must not run. Copy actual main Kconfig definitions without executing
the donor CMake. Report unavailable full-radio configuration symbols explicitly.

Inspect final target LINK_LIBRARIES and INTERFACE_LINK_LIBRARIES (the optional
helper does not amend project_description PRIV_REQUIRES), all three actual compiler rows,
propagated native_stream headers, compiler/SDK/target identities, dependency
headers, object architecture, normalized sdkconfig equivalence, and absence of
the original include-owner warning. Capture every terminal state and failed
attempt. Baseline unrelated SDK notifications are recorded, not attributed to
this change. This is not a full application/runtime/hardware qualification.

Archive compact raw/gzip logs, reports, sources, effective generated metadata,
and identity-only records for tools and libraries. A self-contained offline
verifier must validate all archived bytes and the actual scoped PASS criteria.
Root owns staging, commits, and pushes.

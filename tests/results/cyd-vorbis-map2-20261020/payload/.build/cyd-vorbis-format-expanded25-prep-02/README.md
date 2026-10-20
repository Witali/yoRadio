# Expanded25 test materialization revision02

The first SDK capture failed compilation before QEMU: its data header contained
25 descriptors but still declared CORPUS_CASE_COUNT17 and expected PCM398080.
Its restricted reader mirrored those old constants. Every original source and
failed capture remains unchanged. The decoder candidate itself is unchanged.

Render and recovery now derive both macros from the exact model, and recovery
independently requires declared C capacity == actual descriptor count == model
and raw case counts. Two exact corruptions restore only the old count or PCM
macro. All125 arrays/75 full raw payloads and all descriptor fields remain exact.
The same25 contract/source mapping and existing17+8 reference bindings apply.
Only this successor's data hash and controller data pin change; SDK gates,
caller, protocol and references are unchanged. No target qualification is
claimed by materialization. The known floor0 numerical NONPASS stays open.

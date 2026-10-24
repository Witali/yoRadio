# Floor-presence39 archive verification, 2026-10-24

The [recorded archive](../cyd-vorbis-floor-presence-20261024/CHECKPOINT.md) was
copied byte-for-byte after actual offline replay. Its manifest SHA256 is
`0f95d0c5451290879a088ef4648ebd89cc966622584ebdbb769f2737a08f9cfc`.
All433 archive members and all39 target /78 reference streams remain unchanged.

Actual stage02 replay completed with terminal0 (chunkeb06db). After promotion,
the same verifier completed with terminal0 from a different working directory
(chunk795787), reading only the canonical archive. Both runs reproduced all1212
protocol events,546 packets,971520 PCM bytes and78 full numerical comparisons
under the original2LSB project bound. They execute no decoder, SDK or guest.

The earlier stage01 failed input closure: a variant source and117 original raw
snapshot paths lacked explicit inventory aliases. Stage02 adds the retained
bodies/aliases with exact declared SHA identities. It changes no verifier,
helper, policy, source input or PCM bytes. The original stage01 and rejection
history are retained. A first stage02 attempt then failed on Windows sandbox
private temporary-directory ACLs before numerical replay. The passing runs use
normal user permissions and a checked temporary parent inside the workspace;
all temporary replay files were owned by that run. The source and gates remain
unchanged. Both failed receipts and logs are preserved here.

Independent review verifies all4062 advertised input rows:4058 retained bodies
and4 pre-existing recorded external omissions, with zero unresolved rows.
The source archive has19 unique omitted binary/tool bodies; they are recorded
identities rather than independent live-tool verification. This replay does
not add full dependency closure, QMP lifecycle, production radio, hardware,
performance or complete Vorbis/G6 qualification. See the archive's factual
clarification for the inherited nine-command target controller's actual scope.

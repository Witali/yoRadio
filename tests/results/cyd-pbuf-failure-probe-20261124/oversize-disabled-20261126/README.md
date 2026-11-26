# TCP oversize disabled: rejected option

This bounded experiment is terminal **NONPASS**. It produced no linked
candidate application, Clang qualification, QEMU result or production change.
The pinned SDK requires nonzero `TCP_OVERSIZE` when TCP and the unchanged
`LWIP_NETIF_TX_SINGLE_PBUF=1` are enabled. The actual GCC build reached that
creator constraint in `core/init.c:232-234` and failed.

The public choice exists, but its disabled value is not an admissible isolated
change for this port combination. `PLAN.md` is preserved historical preparation
and includes the earlier, overly broad supported-option assumption; the actual
`CONCLUSION.md`, constraint result and original build output supersede it.
No guard was removed, no SINGLE_PBUF policy was changed and no setting was
widened to manufacture a successful build. Quarter-MSS remains on the same
nonzero/single-pbuf max-length reservation branch and is not the next fix.

The preparation made exactly the intended JSON delta: MSS true->false and
DISABLE false->true. The generated header also changes its existing deprecated
sdkconfig.rename alias. The original header checker rejection and its precise
reviewed continuation are retained. Source aliases and the exact three-line
SDK guard are bound to their original creator-source hashes in source/.

Execution records remain separate: the original configure child exited zero
but its overly narrow header guard stopped the first controller; the reviewed
continuation's GCC child then exited one at the real SDK compatibility guard.
Initial preparation and result-recorder helper rejections are preserved as
well. None of these records is relabeled as passing firmware or runtime.
Synthetic preparation controls remain preparation-only evidence.

The live sdkconfig was rewritten by IDF. Its originally prepared seed is
explicitly reconstructed from the preserved baseline using exactly the two
choice lines; its complete bytes match the original preflight/manifest hash.
This reconstructed file is labeled as such, and the actual generated config,
raw headers, continuation proof and hashes remain separate. JSON and source
records are not edited to hide either checker failure.

The post-build constraint record reports all 61 source pins and 324 protected
inputs rechecked, with source, SDK and prior artifacts unchanged. This package
uses those recorded bindings and verifies selected small inputs; it does not
rehash old binaries, full caches or compiler databases. The source identity is
`f7dee344fb30ce109f2d30a01f0325d353e3b2eb`. Original audio cores/priorities/
stacks, TLS/network budgets and old firmware are not changed by this archive.

Raw verdict/counter bytes are retained. Only personal home components in
public log copies are neutralized; redactions.json records exact original and
published hashes and replacement counts. Large databases, partial objects,
archives, application binaries and private key/certificate bodies stay local.
Recipe copies describe the original isolated experiment and its release;
they are review evidence, not commands to execute from this public directory.
Old SDK/native namespaces are verified and left untouched.

The result rejects this bounded option, not the transfer objective. The next
work is a measured reduction in the status serializer's persistent DRAM, while
retaining full JSON semantics, two clients and the existing protocol budgets.

# TCP oversize disabled: rejected by the pinned SDK combination

The released experiment is terminal **NONPASS**. Reconfigure generated exactly
the intended two boolean changes. Its header additionally changes the generated
deprecated choice alias; that narrow checker correction and the first rejection
are preserved without replacing the original preflight or root release.

The actual firmware build then stopped at the SDK compatibility assertion in
`components/lwip/lwip/src/core/init.c:232–234`:

```c
#if LWIP_TCP && LWIP_NETIF_TX_SINGLE_PBUF && !TCP_OVERSIZE
#error "LWIP_NETIF_TX_SINGLE_PBUF needs TCP_OVERSIZE enabled to create single-pbuf TCP packets"
#endif
```

The original port has TCP enabled and hard-codes SINGLE_PBUF=1. Therefore the
public disabled choice is not an admissible isolated change for this pinned
combination. The earlier preparation's wording that this was a supported first
experiment was too broad: the option exists, but the source compatibility guard
must also be satisfied. The fresh build established that stronger constraint.

No SDK guard was removed, no driver/port policy was changed, and no setting was
widened to produce a green build. Quarter-MSS remains nonzero and still takes
the same unconditional max_length reservation branch; it does not avoid the
observed1512-byte request. A separate change to SINGLE_PBUF would require new
driver/scatter-gather compatibility work and is outside this two-flag release.

The original exec97355 is terminal1 after the header checker; its configure
child21820 exited0. The reviewed continuation exec77406 is terminal1 after the
GCC build child19012 exited1. No coversize26 compiler/build process remains.
No candidate application was linked, and no Clang, linked-image, runtime or
production qualification can honestly be reported for this candidate.

`constraint-result.json` binds the exact source guard, logs, configuration and
preserved failure statuses. All61 source pins and324 protected inputs were
rechecked after the failed build. HEAD/source/index remain f7dee344 and clean;
old caches, fixtures and production files are untouched. Partial fresh objects
and every original log remain local. No QEMU, source edit or publication ran.

Use this result to select another measured DRAM reduction. It is evidence
against this bounded configuration option, not against the goal or the existing
diagnostic findings.

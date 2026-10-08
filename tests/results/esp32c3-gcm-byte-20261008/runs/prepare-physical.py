from pathlib import Path

root=Path('.build/c3-gcm-byte-20261008')
text=Path('.build/c3-staged-dma-profile-20261008/physical.py').read_text()
text=text.replace('.build/c3-staged-dma-profile-20261008/physical',str(root.as_posix())+'/physical')
text=text.replace('rx6-reserve-rxonly-dmaprof/app.bin','rx6-reserve-rxonly-dmaprof-ghash8/app.bin')
text=text.replace('STAGED_DMA_PHYSICAL_COMPLETE','GHASH_PHYSICAL_COMPLETE')
(root/'physical.py').write_text(text)

text=Path('.build/c3-tick-20261008/summarize.py').read_text()
text=text.replace("root = Path('.build/c3-tick-20261008')", "root = Path('.build/c3-gcm-byte-20261008')")
text=text.replace("for tick, base in ((1, Path('.build/c3-staged-dma-profile-20261008/physical')),\n                   (2, root/'tick2/physical'), (5, root/'tick5/physical')):",
                  "for variant, base in (('baseline', Path('.build/c3-staged-dma-profile-20261008/physical')),\n                      ('ghash8', root/'physical')):")
text=text.replace('tick_ms=tick','variant=variant').replace('print(tick,case','print(variant,case')
text=text.replace('complete=len(cases)==6','complete=len(cases)==4')
text=text.replace('Config-only FreeRTOS tick experiment.', 'Exact GHASH implementation experiment; unchanged 1 ms tick.')
text=text.replace("        cases.append(item)", """        stack = {}
        for row in rows:
            m = re.search(r'PERF STACK: name=(\\S+) minimum_free=(\\d+)', row['line'])
            if m:
                stack[m[1]] = min(stack.get(m[1], 1<<30), int(m[2]))
        item['minimum_free_stack_bytes'] = stack
        cases.append(item)""")
(root/'summarize.py').write_text(text)

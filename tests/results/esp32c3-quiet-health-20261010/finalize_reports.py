"""Publish completed qualification counts, preserving original failed gates."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
review = json.loads((ROOT / 'review.json').read_text())
for campaign in review['campaigns'].values():
    restored = campaign['restoration']
    assert restored and all(restored['persistence'].values())
    assert len(restored['states']) == 3
    assert all(not state['audio'] for state in restored['states'])

public = review['campaigns']['physical']['phases']['public']
local = review['campaigns']['physical-local']['phases']['local']
ota = review['campaigns']['physical-local']['phases'].get('ota')
assert public['passed'] == 8 and public['total'] == 10

doc = Path('docs/ESP32C3_QUIET_HEALTH_20261010.md')
text = doc.read_text(encoding='utf-8')
assert '## Completed local and OTA qualification' not in text
text += '\n## Completed local and OTA qualification\n\n'
text += f"The independent local campaign completes **{local['passed']}/{local['total']}** checks.\n"
text += ('The cases cover MP3, FLAC, Vorbis, Opus, AAC-LC, HE-AAC and HE-AACv2\n'
         'files with automatic and explicit codec selection, EOF, AAC transitions,\n'
         'Stop/Play generation, connection drop/stall/error, redirect/jitter,\n'
         'WebSocket format/reconnect, settled recovery and lifetime health.\n\n')
text += '| Phase | Passed / total | Original failures |\n| --- | ---: | --- |\n'
for label, data in (('Public HTTPS', public), ('Local HTTP / lifecycle', local), ('OTA', ota)):
    if data is None:
        text += f'| {label} | Not run | Previous phase failed |\n'
        continue
    failures = '; '.join(c['name'] for c in data['failures']) or 'None'
    text += f"| {label} | {data['passed']} / {data['total']} | {failures} |\n"
text += '\nSettled local observations, in bytes:\n\n'
text += '| Checkpoint | Median free heap | Median largest block | Tasks |\n| --- | ---: | ---: | ---: |\n'
for name, values in local['idle'].items():
    text += f"| {name} | {values['heap']:,.0f} | {values['largest']:,.0f} | {values['tasks']:.0f} |\n"
if local['health']['result'] == 'PASS':
    health = local['health']['evidence']
    text += (f"\nAll {health['samples']:,} local health observations retain the same boot ID,\n"
             f"with {health['allocation_failures']} allocation failures and "
             f"{health['task_watchdog_events']} task-watchdog events.\n"
             f"The sampled minimum current free heap is {health['minimum_heap']:,} B;\n"
             f"minimum largest block is {health['minimum_largest']:,} B. These are\n"
             'sampled current values, not the SDK lifetime low-water mark.\n')
if ota:
    text += ('\nThe OTA suite includes invalid uploads, interrupted/stalled uploads,\n'
             'two accepted application updates and reboot/settings verification.\n'
             'OTA while playing and slow valid uploads are not part of this run.\n')
text += ('\nBoth controllers restore `idf61-listen48-8c1f2d`, verify the exact ELF\n'
         '`76e863160ad21acba7ce86eeaca27f9fb6d58ebf4d3a79ca42ef7b42ae40885b`,\n'
         'confirm settings persistence and record three stopped observations.\n'
         'No serial recovery is used. The candidate remains **not production-qualified**.\n\n'
         'Byte-exact evidence, all failed cases and offline replay instructions:\n'
         '[qualification archive](../tests/results/esp32c3-quiet-health-20261010/README.md).\n')
doc.write_text(text, encoding='utf-8')

todo = Path('docs/ESP32C3_MEMORY_STABILITY_TODO.md')
text = todo.read_text(encoding='utf-8')
anchor = 'Latest [integer-clock cross-codec qualification]'
assert anchor in text and 'quiet production health qualification' not in text
update = ('The [quiet production health qualification](ESP32C3_QUIET_HEALTH_20261010.md)\n'
          f"now records {local['passed']}/{local['total']} local HTTP/lifecycle checks")
if ota:
    update += f" and {ota['passed']}/{ota['total']} OTA checks"
update += ('.\nPublic HTTPS retains two original failed gates (8/10): one 7.029-second\n'
           'paired status/health observation and one HE-AAC minimum largest block\n'
           'of 7,936 B, below the unchanged 8,192 B budget. All five public source\n'
           'formats match independent references; there are no recorded allocation\n'
           'failures or watchdog events in the public campaign. Device timestamps\n'
           'place about 4.9 seconds of the slow response after health snapshot\n'
           'construction; transport attribution remains open. Keep these failures\n'
           'and qualify the remaining exact-image HTTPS, certificate-error and\n'
           'sustained-playback scope before enabling the integrated defaults.\n\n')
todo.write_text(text.replace(anchor, update + anchor, 1), encoding='utf-8')

artifact = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-mpi-health')
path = artifact / 'manifest.json'
manifest = json.loads(path.read_text())
manifest['hardware_tested'] = True
manifest['production_qualified'] = False
manifest['qualification'] = 'Physical public/local qualification; original public failures retained; see evidence report'
manifest['qualification_report'] = 'docs/ESP32C3_QUIET_HEALTH_20261010.md'
manifest['qualification_evidence'] = 'tests/results/esp32c3-quiet-health-20261010'
manifest['qualification_counts'] = {
    name: dict(passed=data['passed'], total=data['total'])
    for name, data in (('public', public), ('local', local), ('ota', ota)) if data
}
manifest['restored_listened_image'] = True
path.write_text(json.dumps(manifest, indent=2) + '\n')
(artifact / '.gitattributes').write_text('sdkconfig -text whitespace=cr-at-eol\n*.json -text whitespace=cr-at-eol\n')
print(json.dumps(manifest['qualification_counts']))

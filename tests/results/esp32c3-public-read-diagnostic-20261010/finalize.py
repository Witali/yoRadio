"""Save bounded diagnostic findings and keep deployment qualification open."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = Path('firmware/development/esp32c3-idf-6.1-r9a97-quiet-read-diag')
ARCHIVE = 'esp32c3-public-read-diagnostic-20261010'
DOC = 'ESP32C3_PUBLIC_READ_DIAGNOSTIC_20261010.md'
review = json.loads((ROOT / 'review.json').read_text())
assert review['review'] == 'PASS' and review['exact_listened_image_restored']
audit = json.loads((ROOT / 'quiet-read-diag/build-audit.json').read_text())
assert audit['result'] == 'PASS'
manifest = json.loads((ART / 'manifest.json').read_text())
assert hashlib.sha256((ART / 'app.bin').read_bytes()).hexdigest() == manifest['image']['sha256']
manifest.update(hardware_tested=True, production_qualified=False,
    qualification='Diagnostic public HTTPS campaign; playback/headroom failures remain open',
    physical_report='docs/' + DOC)
(ART / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
(ROOT / 'firmware-manifest.json').write_bytes((ART / 'manifest.json').read_bytes())

table = ['| Case, 120 s | First stopped status, s | New fatal reads | TLS code | Lost notifications while playing after warmup | Host decoded 125 s | Min free / largest, B |',
         '| --- | ---: | ---: | --- | ---: | --- | ---: |']
for name, d in review['cases'].items():
    stop = f"{d['first_stopped']['seconds']:.2f}" if d['first_stopped'] else 'none'
    code = f"0x{d['last_failure']['tls_code']:04x}" if d['failure_delta'] else 'no new error'
    drops = d['active_pipeline']['output']['completion_queue_drops'] if d['active_pipeline'] else 'unavailable'
    h = d['sampled_health']
    table.append(f"| {name} | {stop} | {d['failure_delta']} | {code} | {drops} | {d['host_decode_completed']} | {h['minimum_heap']:,} / {h['minimum_largest']:,} |")
health = review['health']
text = f'''# Public MP3 / HE-AAC: HTTP/TLS failure diagnostics

## Findings

{chr(10).join(table)}

The numeric failure snapshot identifies `0x7280` as the positive form of
`MBEDTLS_ERR_SSL_CONN_EOF` in this SDK. Our existing TLS adapter maps a nonempty
read returning zero to that error, preserving the distinction between transport
EOF and TLS `close_notify`. The observed system errno 128 is `ENOTCONN` in the
ESP toolchain; it is an accompanying snapshot, not proof of why the peer closed.
`esp_tls_error` 32797 is `ESP_ERR_MBEDTLS_SSL_READ_FAILED`.
The error is not an allocation-failure code. Authenticated partial HTTP bytes
returned before the failure are still passed to the decoder; the connection is
then closed and is never read again.

The host independently decodes the same public URLs with FFmpeg, TLS verification
enabled, to a null output. Host completion demonstrates that a separate client
could decode the source during the observation. It does not prove both clients
used identical connections, packets, DNS destinations, HTTP headers or PCM.
No radio audio or private device settings are saved.

In the repeated MP3 case the host also ends early: 25.887347 seconds of decoded
audio, TLS EOF and a premature-stream/demux I/O error. FFmpeg exits with code 0,
so checking exit status alone would falsely report success; the review additionally
requires at least 124 seconds of decoded audio and a completed progress record.
The first MP3 host control and HE-AAC host control each decode all 125 seconds
without logged errors. Thus an external source/path failure is independently
observed, but this does not prove that every board interruption has that cause.

Pipeline events mainly show phase 7: output is waiting for PCM, decoder for
encoded input, and the stream task is inside HTTP reading. These are call-phase
observations, not scheduler traces. The detailed event ages and overwritten-event
counts are retained in `review.json`; the 16-event ring cannot retain every event.
Output notification losses are not counted as missing audio samples or clicks.
The table excludes periods after the first stopped status. The original full
window, including intentional idle after a failure, remains in `physical/results.json`.

The campaign records {health['allocation_failures']} failed allocations and
{health['task_watchdog_events']} watchdog events in {health['samples']} observations,
with one boot identity. Settled idle recovery: **{review['recovery']['result']}**.
Memory-floor failures remain recorded. Diagnostics change memory layout; these
numbers are not a direct replacement for normal-image qualification.

## Implementation and checks

`CONFIG_YORADIO_PIPELINE_HEALTH_DIAGNOSTIC` remains disabled by default.
It now preserves the last fatal HTTP/TLS read's result, ESP-TLS code, mbedTLS
code, errno, timestamp and sequence in 24 extra static bytes. The total probe
structure is 540 bytes. Capture occurs before close, under an interrupt mask
on the single-core C3, and health serializes a consistent copied snapshot.
Transient retries do not overwrite fatal-error evidence. The timestamp is a
wrapping 32-bit microsecond value; interpret it in bounded observations.

- Actual SDK HTTP reader/parser/TLS adapter harness: 85 cases with diagnostics
  off and 85 with diagnostics on, ASan/UBSan PASS. Fatal retry, partial bytes,
  temporary errors, EOF/framing and errno capture before later API calls are checked.
- Bounded native health JSON: four watchdog/diagnostic combinations, ASan/UBSan PASS.
- Numeric diagnostic validation: five Python tests PASS.
- Build audit: full AAC/FLAC codec arithmetic unchanged in 119 code/constant
  sections across 18 objects; normal public CA bundle preserved.

Compared with the normal one-second-prefill candidate, linked DRAM data grows
by 536 bytes, BSS is unchanged, and IRAM instructions grow by 132 bytes within
the same aligned IRAM allocation. These linked deltas include layout effects;
the new failure record itself is exactly 24 bytes.

## Next action

Compare HTTP and HTTPS at the same MP3 sample rate/bitrate and controlled delivery,
then isolate TCP/TLS delivery delays and per-connection closure. Include a
44.1 kHz MP3 control because the existing high-bitrate local MP3 fixture is 48 kHz.
Investigate contiguous-memory headroom separately without weakening TLS closure
validation or accepting failed reads as clean EOF. Retry/reconnect policy requires
generation/lifetime and unavailable-station-timeout tests before changing it.

This diagnosis narrows the cause; it does not fix playback or qualify production.
The exact listened firmware/settings were restored after the campaign.

App SHA-256: `{manifest['image']['sha256']}`.
ELF SHA-256: `{manifest['image']['app_elf_sha256']}`.

[Frozen evidence](../tests/results/{ARCHIVE}/README.md).
'''
Path('docs', DOC).write_text(text, encoding='utf-8')
(ROOT / 'README.md').write_text(f'''# Public stream read diagnostics

[Report](../../../docs/{DOC}). Diagnostic image; no production pass is claimed.

From the repository root:

```text
python -B tests/results/{ARCHIVE}/review.py
python -B tests/results/{ARCHIVE}/verify_commit.py
```

`review: PASS` means evidence replay/restoration succeeded, not playback acceptance.
`physical/` retains original failures, independent FFmpeg progress, bounded numeric
health and exact restoration. `build-sources/`, `test-sources/`, `host-test-sources/`
and `host-tests/` freeze the inputs and checks. Source/reference hashes identify
the SDK and tools. `index.json` verifies byte-exact files.
Do not run `physical.py` for offline review: it performs app-only OTA.
''', encoding='utf-8')
print('Saved diagnostics report; production qualification remains open')

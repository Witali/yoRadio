"""Generate original deterministic AAC fixtures with FDK AAC's aac-enc example.

Usage: python3 generate.py /path/to/aac-enc
Encoder reference: https://github.com/mstorsjo/fdk-aac/tree/v2.0.3
Only generated audio is checked in; no external recordings are used.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import wave

root = Path(__file__).resolve().parent
encoder = str(Path(sys.argv[1]).resolve())
cases = [
    ("lc-44100-stereo", 44100, 2, 2, 128000),
    ("lc-22050-mono", 22050, 1, 2, 128000),
    ("lc-48000-stereo", 48000, 2, 2, 128000),
    ("he-44100-stereo", 44100, 2, 5, 64000),
    ("he-48000-stereo", 48000, 2, 5, 64000),
    ("hev2-44100-stereo", 44100, 2, 29, 32000),
]
manifest = {"generator": "FDK AAC v2.0.3 aac-enc, original 0.5-second synthetic tones",
            "encoder_commit": "716f4394641d53f0d79c9ddac3fa93b03a49f278", "files": {}}
with tempfile.TemporaryDirectory() as temporary:
    for name, rate, channels, aot, bitrate in cases:
        source = Path(temporary) / (name + ".wav")
        with wave.open(str(source), "wb") as wav:
            wav.setparams((channels, 2, rate, 0, "NONE", "not compressed"))
            pcm = bytearray()
            for frame in range(rate // 2):
                for channel in range(channels):
                    low = 997 if channel == 0 else 1511
                    high = min(12000 + channel * 2000, rate * 0.4)
                    sample = 7000 * math.sin(2 * math.pi * low * frame / rate)
                    sample += 3000 * math.sin(2 * math.pi * high * frame / rate)
                    pcm += struct.pack("<h", round(sample))
            wav.writeframes(pcm)
        output = root / (name + ".aac")
        subprocess.run([encoder, "-t", str(aot), "-r", str(bitrate),
                        str(source), str(output)], check=True)
        data = output.read_bytes()
        manifest["files"][output.name] = {
            "sample_rate": rate, "channels": channels, "audio_object_type": aot,
            "bitrate": bitrate, "size_bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
(root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

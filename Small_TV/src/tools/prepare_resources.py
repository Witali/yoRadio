"""Pack sanitized media at the recovered offsets and generate C resources.

Python standard library only. Never reads private settings or the original dump.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
BASE, END = 0x200000, 0x3e7000


def png_to_bmp(data: bytes) -> bytes:
    """Decode the exported 8-bit RGB/RGBA/gray/palette PNGs without Pillow."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("PNG signature")
    pos, compressed, palette = 8, bytearray(), b""
    while pos < len(data):
        length = struct.unpack_from(">I", data, pos)[0]
        kind, body = data[pos+4:pos+8], data[pos+8:pos+8+length]
        if kind == b"IHDR":
            width, height, depth, color, comp, filtering, interlace = struct.unpack(">IIBBBBB", body)
            if depth != 8 or comp or filtering or interlace or color not in (0, 2, 3, 4, 6):
                raise ValueError("Unsupported PNG")
        elif kind == b"IDAT":
            compressed += body
        elif kind == b"PLTE":
            palette = body
        pos += length + 12
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    raw, rowbytes = zlib.decompress(compressed), width * channels
    if len(raw) != height * (rowbytes + 1):
        raise ValueError("PNG length")
    rows, previous = [], bytearray(rowbytes)
    for y in range(height):
        start = y * (rowbytes + 1)
        mode, row = raw[start], bytearray(raw[start+1:start+1+rowbytes])
        for x in range(rowbytes):
            a, b, c = (row[x-channels] if x >= channels else 0), previous[x], (previous[x-channels] if x >= channels else 0)
            if mode == 1: predictor = a
            elif mode == 2: predictor = b
            elif mode == 3: predictor = (a+b)//2
            elif mode == 4:
                p = a+b-c
                distances = (abs(p-a), abs(p-b), abs(p-c))
                predictor = (a,b,c)[distances.index(min(distances))]
            elif mode == 0: predictor = 0
            else: raise ValueError("PNG filter")
            row[x] = (row[x] + predictor) & 255
        rgb = bytearray()
        for x in range(width):
            pixel = row[x*channels:(x+1)*channels]
            if color == 3: r,g,b = palette[pixel[0]*3:pixel[0]*3+3]
            elif color in (0,4): r = g = b = pixel[0]
            else: r,g,b = pixel[:3]
            rgb += bytes((b,g,r))
        rgb += bytes((-len(rgb)) % 4)
        rows.append(rgb)
        previous = row
    pixels = b"".join(reversed(rows))
    return struct.pack("<2sIHHI", b"BM", 54+len(pixels), 0, 0, 54) + struct.pack("<IiiHHIIiiII", 40,width,height,1,24,0,len(pixels),0,0,0,0) + pixels


def pack_assets(output: Path):
    manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
    packed = bytearray(b"\xff" * (END-BASE))
    records = []
    def put(offset, data, limit):
        if offset < BASE or offset + len(data) > END or len(data) > limit:
            raise ValueError("Asset outside its slot")
        packed[offset-BASE:offset-BASE+len(data)] = data
        records.append({"offset": hex(offset), "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    sizes = []
    for image in manifest["photos"]:
        data = (ASSETS / image["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == image["export_sha256"]
        sizes.append(len(data))
        put(int(image["flash_offset"],16), data, 0x19000)
    for animation in manifest["animations"]:
        container = bytearray(1024)
        container[:3] = b"GIF"
        struct.pack_into("<HH", container, 7, animation["width"], animation["height"])
        for index, frame in enumerate(animation["frames"]):
            data = (ASSETS / frame["file"]).read_bytes()
            assert hashlib.sha256(data).hexdigest() == frame["export_sha256"]
            struct.pack_into("<II", container, 11+8*index, len(data), len(container))
            container += data
        struct.pack_into("<I", container, 3, len(container))
        put(int(animation["flash_offset"],16), container, 0x32000)
    for image in manifest["weather"]:
        data = (ASSETS / image["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == image["export_sha256"]
        put(int(image["flash_offset"],16), png_to_bmp(data), 0x3c00)
    for image in manifest["status"]:
        data = (ASSETS / image["file"]).read_bytes()
        assert hashlib.sha256(data).hexdigest() == image["export_sha256"]
        put(int(image["flash_offset"],16), data, 0x3c00)
    (output / "assets.bin").write_bytes(packed)
    (output / "assets-manifest.json").write_text(json.dumps({"offset":hex(BASE), "size":len(packed), "sha256":hashlib.sha256(packed).hexdigest(), "records":records}, indent=2)+"\n",encoding="utf-8",newline="\n")
    (output / "asset_defaults.h").write_text("#pragma once\n#define DEFAULT_PHOTO_SIZES {"+",".join(map(str,sizes))+"}\n",encoding="utf-8",newline="\n")


def generate_font(output: Path):
    bdf = (ROOT / "third_party/spleen/spleen-6x12.bdf").read_text(encoding="utf-8")
    glyphs = {}
    for block in bdf.split("STARTCHAR ")[1:]:
        lines = block.splitlines()
        code = int(next(line.split()[1] for line in lines if line.startswith("ENCODING ")))
        if 32 <= code < 127:
            bitmap = lines[lines.index("BITMAP")+1:lines.index("ENDCHAR")]
            if len(bitmap) != 12: raise ValueError("Font height")
            glyphs[code] = [int(row,16) for row in bitmap]
    assert len(glyphs) == 95
    text = "/* Spleen 6x12, Copyright Frederic Cambus, BSD-2-Clause. */\n#pragma once\n#include <stdint.h>\nstatic const uint8_t font6x12[95][12] = {\n"
    text += "\n".join("{"+",".join(hex(v) for v in glyphs[code])+"}," for code in range(32,127))
    (output / "font6x12.h").write_text(text+"\n};\n",encoding="utf-8",newline="\n")


def generate_pages(output: Path):
    text = "/* Recovered, sanitized UTF-8 pages. Generated; edit local_site/pages. */\n#include <stddef.h>\n"
    for page in ("setup", "settings", "photo"):
        html = (ROOT.parent / "local_site/pages" / (page+".html")).read_text(encoding="utf-8")
        # Firmware-only usability changes; the archived/local-site pages stay intact.
        html = html.replace("</nav>", ' &middot; <a href="/advanced">Advanced</a></nav>', 1)
        html = html.replace("Show Temperature in Celsius", "Show Temperature in Fahrenheit")
        data = html.encode("utf-8")
        text += "const unsigned char web_"+page+"[] = {\n"
        text += "\n".join(",".join(str(v) for v in data[pos:pos+32])+"," for pos in range(0,len(data),32))
        text += "0};\nconst size_t web_"+page+"_length = "+str(len(data))+";\n"
    (output / "web_pages.c").write_text(text,encoding="utf-8",newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    pack_assets(args.output)
    generate_font(args.output)
    generate_pages(args.output)
    compiled = sorted((ROOT / "app").rglob("*.c")) + sorted((ROOT / "app").rglob("*.h"))
    compiled += sorted((ROOT / "third_party").rglob("*.c")) + sorted((ROOT / "third_party").rglob("*.h"))
    compiled += [ROOT / "CMakeLists.txt", ROOT / "app/CMakeLists.txt", ROOT / "sdkconfig.defaults", ROOT / "partitions.csv"]
    records = [{"file":str(path.relative_to(ROOT)).replace("\\","/"), "sha256":hashlib.sha256(path.read_bytes()).hexdigest()} for path in compiled]
    for name in ("web_pages.c", "font6x12.h", "asset_defaults.h"):
        records.append({"file":"generated/"+name,"sha256":hashlib.sha256((args.output/name).read_bytes()).hexdigest()})
    canonical = json.dumps(records, separators=(",",":"),sort_keys=True).encode("utf-8")
    (args.output/"source-manifest.json").write_text(json.dumps({"aggregate_sha256":hashlib.sha256(canonical).hexdigest(),"files":records},indent=2)+"\n",encoding="utf-8",newline="\n")


if __name__ == "__main__": main()

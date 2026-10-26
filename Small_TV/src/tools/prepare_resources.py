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
from prepare_timezones import generate_timezones

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


def spleen_glyphs():
    """Read the bundled monospace BDF once with explicit size and scalar checks."""
    bdf = (ROOT / "third_party/spleen/spleen-6x12.bdf").read_text(encoding="utf-8")
    glyphs = {}
    for block in bdf.split("STARTCHAR ")[1:]:
        lines = block.splitlines()
        code = int(next(line.split()[1] for line in lines if line.startswith("ENCODING ")))
        if code in glyphs or not 0 <= code <= 0x10ffff or 0xd800 <= code <= 0xdfff:
            raise ValueError("Invalid or duplicate Spleen scalar")
        if 'BBX 6 12 0 -3' not in lines or 'DWIDTH 6 0' not in lines:
            raise ValueError("Unexpected Spleen glyph geometry")
        bitmap = lines[lines.index("BITMAP")+1:lines.index("ENDCHAR")]
        if len(bitmap) != 12: raise ValueError("Font height")
        rows = [int(row,16) for row in bitmap]
        if any(row < 0 or row > 255 or row & 3 for row in rows):
            raise ValueError("Invalid Spleen row")
        glyphs[code] = rows
    return glyphs


def generate_font(output: Path):
    """Keep the existing ASCII Spleen header byte-compatible with prior builds."""
    glyphs = {code:rows for code,rows in spleen_glyphs().items() if 32 <= code < 127}
    assert len(glyphs) == 95
    text = "/* Spleen 6x12, Copyright Frederic Cambus, BSD-2-Clause. */\n#pragma once\n#include <stdint.h>\nstatic const uint8_t font6x12[95][12] = {\n"
    text += "\n".join("{"+",".join(hex(v) for v in glyphs[code])+"}," for code in range(32,127))
    (output / "font6x12.h").write_text(text+"\n};\n",encoding="utf-8",newline="\n")


def generate_unicode_font(output: Path):
    """Scale bundled non-ASCII glyphs to factory text cells, storing LSB-first rows."""
    glyphs = {code:rows for code,rows in spleen_glyphs().items() if code >= 128}
    codes = sorted(glyphs)
    text = ("/* Spleen 6x12, Copyright Frederic Cambus, BSD-2-Clause.\n"
            " * Non-ASCII only: nearest-neighbor scaling; factory ASCII stays unchanged. */\n"
            "#pragma once\n#include <stdint.h>\n"
            f"#define UNICODE_GLYPH_COUNT {len(codes)}\n"
            "static const uint32_t unicode_codepoints[] = {\n"+
            ','.join(str(code) for code in codes)+"\n};\n")
    for height in (16,24,32):
        width, stride = height//2, (height//2+7)//8
        text += f'static const uint8_t unicode_font{height}[UNICODE_GLYPH_COUNT][{height*stride}] = {{\n'
        for code in codes:
            data = bytearray(height*stride)
            for y in range(height):
                for x in range(width):
                    if glyphs[code][y*12//height] & (1 << (7-x*6//width)):
                        data[y*stride+x//8] |= 1 << (x%8)
            text += '{'+','.join(hex(v) for v in data)+'},\n'
        text += '};\n'
    (output/'unicode_bitmaps.h').write_text(text, encoding='utf-8', newline='\n')


def generate_factory_bitmaps(output: Path):
    folder = ROOT / 'resources/factory'
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    header = ('#pragma once\n#include <stdint.h>\n'
              'typedef struct {const uint8_t *data; unsigned width,height,stride,first,count;} factory_font_table_t;\n'
              'typedef struct {const uint8_t *data; unsigned width,height,stride;} factory_symbol_table_t;\n')
    source = '#include "factory_bitmaps.h"\n'
    records = {row['name']: row for row in manifest['tables']}
    for row in manifest['tables']:
        data = (folder / (row['name'] + '.bin')).read_bytes()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Factory bitmap hash mismatch: ' + row['name'])
        source += 'static const uint8_t bitmap_' + row['name'] + '[] = {\n'
        source += '\n'.join(','.join(hex(v) for v in data[i:i+32]) + ',' for i in range(0,len(data),32))
        source += '\n};\n'
    font_names = ['ascii16','ascii24','ascii32','digits40','digits64','digits80']
    header += '#define FACTORY_FONT_COUNT 6\nextern const factory_font_table_t factory_fonts[6];\n'
    source += 'const factory_font_table_t factory_fonts[6] = {\n'
    for name in font_names:
        row = records[name]
        source += '{bitmap_%s,%d,%d,%d,%d,%d},\n' % (name,row['width'],row['height'],row['stride'],row['first'],row['count'])
    source += '};\n'
    header += '#define FACTORY_SYMBOL_COUNT 6\nextern const factory_symbol_table_t factory_symbols[6];\n'
    source += 'const factory_symbol_table_t factory_symbols[6] = {\n'
    units = records['temperature_units']
    for index in range(2):
        source += '{bitmap_temperature_units+%d,24,24,3},\n' % (index*72)
    for name in ['startup_border','startup_cap','simple_plate','digit_plate']:
        row = records[name]
        source += '{bitmap_%s,%d,%d,%d},\n' % (name,row['width'],row['height'],row['stride'])
    source += '};\n'
    (output / 'factory_bitmaps.h').write_text(header,encoding='utf-8',newline='\n')
    (output / 'factory_bitmaps.c').write_text(source,encoding='utf-8',newline='\n')


def generate_pages(output: Path):
    text = "/* Recovered, sanitized UTF-8 pages. Generated; edit local_site/pages. */\n#include <stddef.h>\n"
    for page in ("setup", "settings", "photo"):
        html = (ROOT.parent / "local_site/pages" / (page+".html")).read_text(encoding="utf-8")
        data = html.encode("utf-8")
        text += "const unsigned char web_"+page+"[] = {\n"
        text += "\n".join(",".join(str(v) for v in data[pos:pos+32])+"," for pos in range(0,len(data),32))
        text += "0};\nconst size_t web_"+page+"_length = "+str(len(data))+";\n"
    (output / "web_pages.c").write_text(text,encoding="utf-8",newline="\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument('--jpeg-library-build',type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    pack_assets(args.output)
    generate_font(args.output)
    generate_unicode_font(args.output)
    generate_factory_bitmaps(args.output)
    generate_pages(args.output)
    generate_timezones(args.output)
    library=args.jpeg_library_build
    selection=args.output.parent/'jpeg-library/selection.json'
    if library is None and selection.exists():
        library=Path(json.loads(selection.read_text())['build_directory'])
    jpeg_generated=[]
    if library is not None:
        from jpeg_cache_layout import prepare_cache
        metadata=library/'report.json';archive=library/'library/libjpeg.a'
        if not metadata.exists():metadata=library/'build.json';archive=library/'library/jpeg-static.lib'
        record=json.loads(metadata.read_text())
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=record['library_sha256']:
            raise ValueError('JPEG archive differs from its build record')
        guard,cache,plan,prepared,prepared_manifest=prepare_cache(
            (args.output/'assets.bin').read_bytes(),json.loads((args.output/'assets-manifest.json').read_text()),
            (ROOT/'app/include/board.h').read_text(),(ROOT/'partitions.csv').read_text(),record)
        (args.output/'assets.bin').write_bytes(prepared)
        (args.output/'assets-manifest.json').write_text(json.dumps(prepared_manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
        for name,data in [('jpeg_layout.h',guard),('jpeg_cache_layout.h',cache),
                          ('jpeg-cache-plan.json',json.dumps(plan,indent=2)+'\n')]:
            (args.output/name).write_text(data,encoding='utf-8',newline='\n');jpeg_generated.append(name)
        (args.output/'jpeg-library-build.json').write_bytes(metadata.read_bytes())
        jpeg_generated.append('jpeg-library-build.json')
    compiled = sorted((ROOT / "app").rglob("*.c")) + sorted((ROOT / "app").rglob("*.h"))
    compiled += sorted((ROOT / 'app').rglob('*.cpp'))
    compiled += sorted((ROOT / "third_party").rglob("*.c")) + sorted((ROOT / "third_party").rglob("*.h"))
    for directory in ('codec', 'storage'):
        compiled += sorted((ROOT / directory).glob('*.c')) + sorted((ROOT / directory).glob('*.h'))
    # Include the offline dependency and adapters even while the UI still uses
    # TJpgd. Their separate build report records the actual target archive.
    compiled += sorted(p for p in (ROOT / 'third_party/libjpeg-turbo').rglob('*') if p.is_file())
    compiled += [ROOT / 'tools/build_jpeg_library.py', ROOT / 'tools/prepare_resources.py', ROOT / 'build.ps1']
    compiled += [ROOT / 'tools/verify_wifi_timer_guard.py', ROOT / 'tools/reverse/elf_archive.py', ROOT / 'tools/reverse/rv32_link_match.py']
    compiled += [ROOT / 'tools/verify_nothrow_linkage.py', ROOT / 'tools/reverse/nothrow_linkage.py']
    compiled += [ROOT / "CMakeLists.txt", ROOT / "app/CMakeLists.txt", ROOT / "sdkconfig.defaults", ROOT / "partitions.csv"]
    compiled += [ROOT / "cmake/debug_logging.cmake"]
    compiled += [ROOT / 'cmake/nvs_recovery.cmake', ROOT / 'tools/patch_nvs_page.py']
    compiled += [ROOT / 'tools/verify_nvs_recovery.py', ROOT / 'tools/reverse/nvs_record_linkage.py',
                 ROOT / 'tools/reverse/factory_nvs.py', ROOT / 'tools/reverse/runtime_call_gaps.py',
                 ROOT / 'tools/audit_factory_xrefs.py']
    records = [{"file":str(path.relative_to(ROOT)).replace("\\","/"), "sha256":hashlib.sha256(path.read_bytes()).hexdigest()} for path in compiled]
    for name in ["web_pages.c", "font6x12.h", "unicode_bitmaps.h", "factory_bitmaps.c", "factory_bitmaps.h", "asset_defaults.h", "timezone_data.h",*jpeg_generated]:
        records.append({"file":"generated/"+name,"sha256":hashlib.sha256((args.output/name).read_bytes()).hexdigest()})
    canonical = json.dumps(records, separators=(",",":"),sort_keys=True).encode("utf-8")
    (args.output/"source-manifest.json").write_text(json.dumps({"aggregate_sha256":hashlib.sha256(canonical).hexdigest(),"files":records},indent=2)+"\n",encoding="utf-8",newline="\n")


if __name__ == "__main__": main()

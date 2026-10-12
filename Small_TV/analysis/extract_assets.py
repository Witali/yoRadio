"""Extract and preview the verified Small_TV flash image's visual assets.

JPEG APP/COM metadata is omitted without recompression. BMP assets are
exported as PNG pixels. Animation GIFs are previews at 100 ms per frame;
their timing and palette are not the original container representation.
"""

from __future__ import annotations

import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import struct

from PIL import Image, ImageChops, ImageDraw, ImageFont, __version__ as pillow_version


SOURCE_SHA256 = "5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4"
WEATHER_CODES = [
    "01d", "01n", "02d", "02n", "03d", "03n", "04d", "04n", "09d",
    "09n", "10d", "10n", "11d", "11n", "13d", "13n", "50d", "50n",
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def jpeg(data: bytes) -> tuple[bytes, bytes]:
    """Parse JPEG markers, ignoring embedded metadata thumbnails as boundaries."""
    if data[:2] != b"\xff\xd8":
        raise ValueError("Missing JPEG start")
    chunks = [data[:2]]
    pos = 2
    while pos < len(data):
        start = pos
        if data[pos] != 0xFF:
            raise ValueError("Invalid JPEG marker boundary")
        while pos < len(data) and data[pos] == 0xFF:
            pos += 1
        marker = data[pos]
        pos += 1
        if marker == 0xD9:
            chunks.append(data[start:pos])
            return data[:pos], b"".join(chunks)
        if marker == 0x01 or 0xD0 <= marker <= 0xD7:
            chunks.append(data[start:pos])
            continue
        length = struct.unpack_from(">H", data, pos)[0]
        end = pos + length
        if length < 2 or end > len(data):
            raise ValueError("Invalid JPEG segment length")
        if not (0xE0 <= marker <= 0xEF or marker == 0xFE):
            chunks.append(data[start:end])
        pos = end
        if marker == 0xDA:
            entropy_start = pos
            while True:
                marker_start = data.index(b"\xff", pos)
                pos = marker_start + 1
                while data[pos] == 0xFF:
                    pos += 1
                code = data[pos]
                if code == 0 or 0xD0 <= code <= 0xD7:
                    pos += 1
                    continue
                chunks.append(data[entropy_start:marker_start])
                pos = marker_start
                break
    raise ValueError("Missing JPEG end")


def decoded(data: bytes) -> Image.Image:
    with Image.open(BytesIO(data)) as original:
        original.load()
        rgb = original.convert("RGB")
        return Image.frombytes("RGB", rgb.size, rgb.tobytes())


def write_jpeg(data: bytes, path: Path, offset: int) -> tuple[dict, Image.Image]:
    original, clean = jpeg(data)
    pixels = decoded(original)
    assert ImageChops.difference(pixels, decoded(clean)).getbbox() is None
    with Image.open(BytesIO(clean)) as check:
        assert not check.info and not check.getexif()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(clean)
    return {
        "flash_offset": f"0x{offset:06x}", "source_length": len(original),
        "source_sha256": digest(original), "export_sha256": digest(clean),
        "width": pixels.width, "height": pixels.height,
        "metadata_removed": True, "decoded_pixels_unchanged": True,
    }, pixels


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parents[1]
    parser.add_argument("--dump", type=Path, default=root / "full-flash.bin")
    parser.add_argument("--output", type=Path, default=root / "assets")
    args = parser.parse_args()
    flash = args.dump.read_bytes()
    if len(flash) != 4 * 1024 * 1024 or digest(flash) != SOURCE_SHA256:
        raise ValueError("This extractor requires the verified device snapshot")
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = {"source_sha256": SOURCE_SHA256, "pillow_version": pillow_version,
                "photos": [], "animations": [], "weather": [], "status": []}
    photos, animations, weather, status = [], [], [], []

    for index in range(5):
        offset = 0x200000 + index * 0x19000
        name = f"photos/photo-{index + 1}.jpg"
        item, pixels = write_jpeg(flash[offset:offset + 0x19000], args.output / name, offset)
        item.update(number=index + 1, file=name)
        manifest["photos"].append(item)
        photos.append((f"Photo {index + 1}", pixels))

    for index in range(5):
        base = 0x27D000 + index * 0x32000
        assert flash[base:base + 3] == b"GIF"
        frames, entries = [], []
        for frame in range(127):
            length, offset = struct.unpack_from("<II", flash, base + 11 + frame * 8)
            if length == offset == 0:
                break
            assert offset >= 1024 and length > 0 and offset + length <= 0x32000
            name = f"animations/animation-{index}/frame-{frame:03d}.jpg"
            item, pixels = write_jpeg(flash[base + offset:base + offset + length],
                                      args.output / name, base + offset)
            assert item["source_length"] == length
            item.update(index=frame, file=name)
            entries.append(item)
            frames.append(pixels)
        assert frames
        preview = f"animations/animation-{index}/preview.gif"
        frames[0].save(args.output / preview, save_all=True, append_images=frames[1:],
                       duration=100, loop=0, disposal=2, optimize=False)
        with Image.open(args.output / preview) as check:
            for frame in range(check.n_frames):
                check.seek(frame)
                check.load()
            preview_frame_count = check.n_frames
        manifest["animations"].append({
            "index": index, "flash_offset": f"0x{base:06x}", "frame_count": len(frames),
            "width": frames[0].width, "height": frames[0].height,
            "preview": preview, "preview_frame_count": preview_frame_count,
            "preview_duration_ms_per_source_frame": 100,
            "preview_timing_is_assumed": True, "frames": entries,
        })
        animations.append((f"Animation {index} ({len(frames)} frames)", frames[0]))

    for index, code in enumerate(WEATHER_CODES):
        offset = 0x377000 + index * 0x3C00
        assert flash[offset:offset + 2] == b"BM"
        length = struct.unpack_from("<I", flash, offset + 2)[0]
        assert 54 <= length <= 0x3C00
        source = flash[offset:offset + length]
        pixels = decoded(source)
        name = f"weather/{code}.png"
        path = args.output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        pixels.save(path)
        with Image.open(path) as check:
            assert not check.info and not check.getexif()
            assert ImageChops.difference(pixels, check.convert("RGB")).getbbox() is None
        manifest["weather"].append({
            "code": code, "flash_offset": f"0x{offset:06x}", "file": name,
            "source_format": "BMP", "source_length": length,
            "source_sha256": digest(source), "export_sha256": digest(path.read_bytes()),
            "width": pixels.width, "height": pixels.height,
        })
        weather.append((code, pixels))

    for name, offset in [("temperature", 0x3BA800), ("wind", 0x3BE400),
                         ("yellow-bar", 0x3C2000), ("blue-bar", 0x3C5C00)]:
        filename = f"status/{name}.jpg"
        item, pixels = write_jpeg(flash[offset:offset + 0x3C00],
                                  args.output / filename, offset)
        item.update(name=name, file=filename)
        manifest["status"].append(item)
        status.append((name, pixels))

    # Build an inventory sheet, enlarging small assets with nearest-neighbor sampling.
    sheet = Image.new("RGB", (1250, 940), "#242424")
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("arial.ttf", 17)
    except OSError:
        font = ImageFont.load_default()
    for items, y, columns, cell_width, cell_height in [
        (photos, 0, 5, 250, 280), (animations, 280, 5, 250, 210),
        (weather, 500, 9, 138, 145), (status, 810, 5, 250, 120),
    ]:
        for index, (label, pixels) in enumerate(items):
            x = (index % columns) * cell_width
            top = y + (index // columns) * cell_height
            draw.text((x + 10, top + 8), label, font=font, fill="white")
            factor = min((cell_width - 20) / pixels.width,
                         (cell_height - 45) / pixels.height, 2)
            tile = pixels.resize((round(pixels.width * factor), round(pixels.height * factor)),
                                 Image.Resampling.NEAREST)
            sheet.paste(tile, (x + (cell_width - tile.width) // 2, top + 35))
    sheet.save(args.output / "overview.png")
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                                encoding="utf-8", newline="\n")
    print("Verified and extracted 5 photos, 5 animations (98 JPEG frames), "
          "18 weather icons and 4 status graphics.")


if __name__ == "__main__":
    main()

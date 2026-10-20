#!/usr/bin/env python3
"""Construct a small Vorbis I raw-format supplement; never invoke a decoder.

Stdlib only. All output is create-only in one fresh child directory of this
source directory. The field and CRC checks establish construction accounting,
not independent decoding, audible quality or target acceptance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import struct

HERE = Path(__file__).resolve().parent
SPEC = "https://xiph.org/vorbis/doc/Vorbis_I_spec.html"
OGG_SPEC = "https://xiph.org/ogg/doc/framing.html"
RATE = 192000
CHANNELS = 2
MODES = tuple(0 if c == "S" else 1 for c in "SSLLLSLSSSLLSS")
EXPONENTS = tuple(range(6, 14))


class Bits:
    def __init__(self):
        self.bits = []
        self.fields = []

    def put(self, name, width, value):
        if width < 0 or value < 0 or value >= 1 << width:
            raise ValueError((name, width, value))
        self.fields.append(dict(name=name, offset=len(self.bits), width=width, value=value))
        self.bits.extend((value >> i) & 1 for i in range(width))

    def data(self):
        result = bytearray((len(self.bits) + 7) // 8)
        for i, value in enumerate(self.bits):
            result[i // 8] |= value << (i % 8)
        return bytes(result)

    def report(self):
        data = self.data()
        # Read actual bytes with integer extraction, independently of the writer.
        packed = int.from_bytes(data, "little")
        for field in self.fields:
            actual = (packed >> field["offset"]) & ((1 << field["width"]) - 1)
            if actual != field["value"]:
                raise ValueError("bitfield byte round trip")
        if packed >> len(self.bits):
            raise ValueError("canonical padding must be zero")
        return dict(bytes=len(data), used_bits=len(self.bits),
                    padding_bits=len(data) * 8 - len(self.bits), fields=self.fields)


def prefix(b, packet_type):
    b.put("packet_type", 8, packet_type)
    for i, value in enumerate(b"vorbis"):
        b.put(f"signature[{i}]", 8, value)


def packed_float(integer):
    # Choose mantissa abs(integer), exponent 788. Vorbis is not IEEE-754.
    if not integer or abs(integer) >= 1 << 21:
        raise ValueError("fixture integer outside chosen packed representation")
    return (0x80000000 if integer < 0 else 0) | (788 << 21) | abs(integer)


def unpack_float(word):
    mantissa = word & 0x1fffff
    if word & 0x80000000:
        mantissa = -mantissa
    exponent = ((word & 0x7fe00000) >> 21) - 788
    return Fraction(mantissa) * Fraction(2) ** exponent


def book(b, number, entries, mapped):
    p = f"book[{number}]"
    b.put(p + ".sync", 24, 0x564342)
    b.put(p + ".dimensions", 16, 1)
    b.put(p + ".entries", 24, entries)
    b.put(p + ".ordered", 1, 0)
    b.put(p + ".sparse", 1, 0)
    for i in range(entries):
        b.put(p + f".length_minus_1[{i}]", 5, 0)
    b.put(p + ".lookup_type", 4, int(mapped))
    if mapped:
        b.put(p + ".minimum", 32, packed_float(-1))
        b.put(p + ".delta", 32, packed_float(2))
        b.put(p + ".value_bits_minus_1", 4, 0)
        b.put(p + ".sequence_p", 1, 0)
        for i in range(2):
            b.put(p + f".multiplicand[{i}]", 1, i)


def setup():
    b = Bits()
    prefix(b, 5)
    b.put("codebooks_minus_1", 8, 1)
    book(b, 0, 1, False)  # 20150226 erratum: length1, consume one zero bit.
    book(b, 1, 2, True)   # Complete tree: code0 -> -1, code1 -> +1.
    b.put("time_count_minus_1", 6, 0)
    b.put("time[0].type", 16, 0)
    b.put("floor_count_minus_1", 6, 0)
    b.put("floor[0].type", 16, 1)
    b.put("floor[0].partitions", 5, 0)
    b.put("floor[0].multiplier_minus_1", 2, 0)
    b.put("floor[0].rangebits", 4, 4)
    b.put("residue_count_minus_1", 6, 0)
    b.put("residue[0].type", 16, 1)
    b.put("residue[0].begin", 24, 0)
    b.put("residue[0].end", 24, 16)
    b.put("residue[0].partition_size_minus_1", 24, 15)
    b.put("residue[0].classifications_minus_1", 6, 0)
    b.put("residue[0].classbook", 8, 0)
    b.put("residue[0].cascade_low", 3, 1)
    b.put("residue[0].cascade_high_present", 1, 0)
    b.put("residue[0].stagebook[0][0]", 8, 1)
    b.put("mapping_count_minus_1", 6, 0)
    b.put("mapping[0].type", 16, 0)
    b.put("mapping[0].multiple_submaps", 1, 0)
    b.put("mapping[0].coupling", 1, 0)
    b.put("mapping[0].reserved", 2, 0)
    for field in ("time", "floor", "residue"):
        b.put("mapping[0]." + field, 8, 0)
    b.put("modes_minus_1", 6, 1)
    for mode in range(2):
        b.put(f"mode[{mode}].blockflag", 1, mode)
        b.put(f"mode[{mode}].windowtype", 16, 0)
        b.put(f"mode[{mode}].transformtype", 16, 0)
        b.put(f"mode[{mode}].mapping", 8, 0)
    b.put("framing", 1, 1)
    return b


def identification(short_exp, long_exp):
    b = Bits()
    prefix(b, 1)
    b.put("version", 32, 0)
    b.put("channels", 8, CHANNELS)
    b.put("sample_rate", 32, RATE)
    for name in ("maximum", "nominal", "minimum"):
        b.put("bitrate_" + name, 32, 0)
    b.put("short_exponent", 4, short_exp)
    b.put("long_exponent", 4, long_exp)
    b.put("framing", 1, 1)
    return b


def comment():
    b = Bits()
    prefix(b, 3)
    vendor = b"yoRadio minimal block-format supplement v1"
    b.put("vendor_length", 32, len(vendor))
    for i, value in enumerate(vendor):
        b.put(f"vendor[{i}]", 8, value)
    b.put("comments", 32, 0)
    b.put("framing", 1, 1)
    return b


def sign_code(packet, channel, scalar):
    word = (((packet + 1) * 0x9e3779b9) ^ ((channel + 1) * 0x85ebca6b)
            ^ ((scalar + 1) * 0xc2b2ae35)) & 0xffffffff
    word ^= word >> 16
    word = (word * 0x7feb352d) & 0xffffffff
    word ^= word >> 15
    return word & 1


def audio(packet):
    b = Bits()
    mode = MODES[packet]
    b.put("audio_packet_type", 1, 0)
    b.put("mode", 1, mode)
    if mode:
        b.put("previous_window_flag", 1, MODES[packet - 1] if packet else 0)
        b.put("next_window_flag", 1, MODES[packet + 1] if packet + 1 < len(MODES) else 0)
    # Both floors precede every residue bit (Vorbis 4.3.2 -> 4.3.4).
    for channel in range(CHANNELS):
        b.put(f"floor[{channel}].present", 1, 1)
        b.put(f"floor[{channel}].y0", 8, 255)
        b.put(f"floor[{channel}].y1", 8, 255)
    # One partition/classword per channel. Classwords for BOTH channels first.
    for channel in range(CHANNELS):
        b.put(f"classword[{channel}]", 1, 0)
    for channel in range(CHANNELS):
        codes = [sign_code(packet, channel, i) for i in range(16)]
        if not 0 < sum(codes) < 16:
            raise ValueError("fixture requires both signs in every spectral vector")
        for scalar, code in enumerate(codes):
            b.put(f"residue[{channel}][{scalar}]", 1, code)
    return b


def crc(data):
    value = 0
    for octet in data:
        value ^= octet << 24
        for _ in range(8):
            value = ((value << 1) ^ (0x04c11db7 if value & 0x80000000 else 0)) & 0xffffffff
    return value


def crc_table(data):
    table = [crc(bytes([i])) for i in range(256)]
    value = 0
    for octet in data:
        value = ((value << 8) & 0xffffffff) ^ table[((value >> 24) ^ octet) & 255]
    return value


def page(packet, serial, sequence, granule, flags):
    laces = bytes([255] * (len(packet) // 255) + [len(packet) % 255])
    if len(laces) > 255:
        raise ValueError("bounded fixture page capacity exceeded")
    header = b"OggS" + struct.pack("<BBQIIIB", 0, flags, granule, serial, sequence, 0, len(laces))
    data = bytearray(header + laces + packet)
    struct.pack_into("<I", data, 22, crc(data))
    return bytes(data)


def read_pages(data):
    result = []
    offset = 0
    while offset < len(data):
        if len(data) - offset < 27 or data[offset:offset + 5] != b"OggS\0":
            raise ValueError("page header")
        count = data[offset + 26]
        laces = data[offset + 27:offset + 27 + count]
        length = 27 + count + sum(laces)
        body = data[offset:offset + length]
        if len(laces) != count or len(body) != length or not count or laces[-1] == 255:
            raise ValueError("complete one-packet page required")
        actual = struct.unpack_from("<I", body, 22)[0]
        zeroed = body[:22] + bytes(4) + body[26:]
        if actual != crc_table(zeroed):
            raise ValueError("CRC mismatch")
        version, flags, granule, serial, sequence = struct.unpack_from("<BBQII", body, 4)
        if version or sequence != len(result):
            raise ValueError("version/sequence mismatch")
        result.append(dict(flags=flags, granule=granule, serial=serial,
                           packet=body[27 + count:], crc=f"{actual:08x}"))
        offset += length
    return result


def sha(data):
    return hashlib.sha256(data).hexdigest()


def c_bytes(name, data):
    lines = [f"static const uint8_t {name}[{len(data)}] = {{"]
    for i in range(0, len(data), 12):
        lines.append("    " + ", ".join(f"0x{x:02x}" for x in data[i:i + 12]) + ",")
    return "\n".join(lines + ["};", ""])


def generate(output):
    if output.resolve().parent != HERE or output.exists():
        raise ValueError("output must be a fresh direct child of generator directory")
    minimum, delta = packed_float(-1), packed_float(2)
    if minimum != 0xe2800001 or delta != 0x62800002 or unpack_float(minimum) != -1 or unpack_float(delta) != 2:
        raise ValueError("Vorbis packed float derivation")
    transitions = Counter((MODES[i - 1], MODES[i]) for i in range(1, len(MODES)))
    neighbors = Counter((MODES[i - 1], MODES[i + 1]) for i in range(1, len(MODES) - 1) if MODES[i])
    if set(transitions) != {(0, 0), (0, 1), (1, 0), (1, 1)} or set(neighbors) != set(transitions):
        raise ValueError("all transitions and long neighbor states required")
    sb, cb = setup(), comment()
    packets = [audio(i) for i in range(len(MODES))]
    offsets = [0]
    for packet in packets:
        offsets.append(offsets[-1] + len(packet.data()))
    audio_data = b"".join(p.data() for p in packets)
    payloads = {"setup.bin": sb.data(), "comment.bin": cb.data(), "audio.bin": audio_data}
    bitfields = dict(schema="vorbis-minimal-bitfields-v1", bit_order="LSB first",
                     setup=sb.report(), comment=cb.report(),
                     audio=[p.report() for p in packets], identification={})
    cases = []
    for short_exp in EXPONENTS:
        for long_exp in range(short_exp, 14):
            short, long = 1 << short_exp, 1 << long_exp
            name = f"s{short}-l{long}"
            ib = identification(short_exp, long_exp)
            bitfields["identification"][name] = ib.report()
            sizes = [long if mode else short for mode in MODES]
            frames = [0] + [(sizes[i - 1] + sizes[i]) // 4 for i in range(1, len(MODES))]
            cumulative = []
            total = 0
            for frames_here in frames:
                total += frames_here
                cumulative.append(total)
            serial = 0x4d420000 + len(cases) + 1
            all_packets = [ib.data(), cb.data(), sb.data()] + [p.data() for p in packets]
            granules = [0, 0, 0] + cumulative
            stream = b"".join(page(p, serial, i, granules[i],
                2 if i == 0 else 4 if i == len(all_packets) - 1 else 0)
                for i, p in enumerate(all_packets))
            decoded_pages = read_pages(stream)
            if [p["packet"] for p in decoded_pages] != all_packets or [p["granule"] for p in decoded_pages] != granules:
                raise ValueError("Ogg packet/granule reconstruction mismatch")
            if [p["flags"] for p in decoded_pages] != [2] + [0] * (len(all_packets) - 2) + [4]:
                raise ValueError("Ogg BOS/EOS mismatch")
            payloads[f"cases/{name}/identification.bin"] = ib.data()
            ogg = f"cases/{name}/reference.ogg"
            payloads[ogg] = stream
            cases.append(dict(id=name, ogg=ogg, short=short, long=long, rate=RATE,
                channels=CHANNELS, mode_flags=list(MODES), expected_raw_samples=total,
                expected_s16le_bytes=total * CHANNELS * 2, expected_packet_samples=frames,
                packet_granules=cumulative, page_crc32=[p["crc"] for p in decoded_pages],
                identification_sha256=sha(ib.data()), ogg_sha256=sha(stream)))
    if len(cases) != 36 or any(c["short"] > c["long"] for c in cases):
        raise ValueError("all 36 legal pairs required")
    damaged = bytearray(payloads[cases[0]["ogg"]])
    damaged[-1] ^= 1
    try:
        read_pages(damaged)
    except ValueError as exc:
        if str(exc) != "CRC mismatch":
            raise
    else:
        raise ValueError("CRC tamper control did not reject")
    matrix = dict(schema="vorbis-minimal-block-matrix-v1", status="INDEPENDENT_DECODE_PENDING",
        supplement_not_replacement=True, independent_nonzero_pcm_demonstrated=False,
        packet_count=len(MODES), offsets=offsets, setup="setup.bin", comment="comment.bin",
        audio="audio.bin", audio_sha256=sha(audio_data), cases=cases,
        long_window_flags=[None if not mode else dict(previous=MODES[i - 1], next=MODES[i + 1])
                           for i, mode in enumerate(MODES)],
        transitions={str(k): v for k, v in sorted(transitions.items())},
        long_neighbors={str(k): v for k, v in sorted(neighbors.items())},
        equal_block_note="Mode/flag syntax remains covered when both block lengths coincide; window geometries coincide.")
    header = "// Generated raw-format supplement; independent decoding pending.\n#pragma once\n#include <stdint.h>\n"
    header += "#define MINIMAL_BLOCK_CASES 36\n#define MINIMAL_BLOCK_PACKETS 14\n"
    header += c_bytes("minimal_setup", sb.data()) + c_bytes("minimal_comment", cb.data())
    header += c_bytes("minimal_audio", audio_data)
    header += "static const uint16_t minimal_offsets[15] = {" + ", ".join(map(str, offsets)) + "};\n"
    header += "static const uint8_t minimal_modes[14] = {" + ", ".join(map(str, MODES)) + "};\n"
    header += "typedef struct { uint16_t short_block, long_block; uint32_t total_samples; uint8_t info[30]; uint16_t packet_samples[14]; } minimal_block_case_t;\n"
    header += "static const minimal_block_case_t minimal_cases[36] = {\n"
    for case in cases:
        info = payloads[f"cases/{case['id']}/identification.bin"]
        header += "    {" + f"{case['short']}, {case['long']}, {case['expected_raw_samples']}, "
        header += "{" + ", ".join(f"0x{x:02x}" for x in info) + "}, {"
        header += ", ".join(map(str, case["expected_packet_samples"])) + "}},\n"
    header += "};\n"
    payloads["fixture.h"] = header.encode()
    checks = dict(schema="vorbis-minimal-pure-construction-checks-v1", scope="Generator accounting only",
        packed_float_minimum=dict(hex=f"{minimum:08x}", mantissa=-1, exponent=788, exact_value=-1),
        packed_float_delta=dict(hex=f"{delta:08x}", mantissa=2, exponent=788, exact_value=2),
        codebook_vectors=[-1, 1], cases=36, raw_packets_per_case=14,
        residue_end=16, smallest_vector_size=32, residue_partition_count=1,
        classword_bits_per_packet=2, stagebook_bits_per_packet=32,
        floor_bits_per_packet=34, short_audio_used_bits=70, long_audio_used_bits=72,
        audio_packet_bytes=[len(p.data()) for p in packets],
        actual_bytes_bitfield_roundtrip=True, all_ogg_pages_crc_and_packet_roundtrip=True,
        crc_corruption_control_rejected=True, independent_decode_run=False,
        sdk_compiler_qemu_run=False, nonzero_pcm_observed=False)
    for name, value in (("matrix.json", matrix), ("bitfields.json", bitfields), ("pure-checks.json", checks)):
        payloads[name] = (json.dumps(value, indent=2) + "\n").encode()
    manifest = dict(schema="vorbis-minimal-generator-manifest-v1", generator_sha256=sha(Path(__file__).read_bytes()),
        references=[SPEC, OGG_SPEC], independent_decode_pending=True,
        files=[dict(path=p, bytes=len(d), sha256=sha(d)) for p, d in sorted(payloads.items())])
    payloads["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir()
    for name, data in payloads.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    print(json.dumps(dict(output=str(output), files=len(payloads), cases=len(cases),
        setup_bytes=len(sb.data()), setup_used_bits=len(sb.bits), audio_bytes=len(audio_data),
        manifest_sha256=sha(payloads["manifest.json"]), independent_decode_pending=True)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    generate(parser.parse_args().output)

"""Independent raw-book/Fraction oracle. No parser, codec, consumer or process imports."""
from fractions import Fraction


def need(ok, reason):
    if not ok: raise ValueError(reason)


class Bits:
    def __init__(self, data): self.data, self.position = data, 0
    def read(self, width):
        need(type(width) is int and 0 <= width <= 32 and self.position + width <= len(self.data) * 8, 'bounded raw bits')
        value = sum(((self.data[(self.position + i) // 8] >> ((self.position + i) % 8)) & 1) << i for i in range(width))
        self.position += width
        return value


def number(value):
    """Normative Vorbis packed float as an exact rational; zero has no exponent."""
    mantissa = value & 0x1fffff
    power = ((value >> 21) & 1023) - 788
    sign = -1 if value & 0x80000000 else 1
    return sign * mantissa * (Fraction(2) ** power)


def fixed_fields(value):
    """Independent normalization identity for checking owned parser fields."""
    magnitude = value & 0x1fffff
    if not magnitude: return 0, -9999
    distance = 31 - magnitude.bit_length()
    return (-1 if value & 0x80000000 else 1) * (magnitude << distance), ((value >> 21) & 1023) - 788 - distance


def words(lengths):
    """Assign the least available prefix interval in entry order; no decode-table code."""
    active = [i for i, size in enumerate(lengths) if size]
    need(active and all(type(n) is int and 0 <= n <= 32 for n in lengths), 'valid lengths')
    if len(active) == 1:
        need(lengths[active[0]] == 1, 'public singleton one-bit rule')
        return {active[0]: '0'}
    occupied, out = [], {}
    for index in active:
        width = lengths[index]
        # Intervals use a common 32-bit fraction grid, so lengths may decrease.
        step = 1 << (32 - width)
        cursor = 0
        for first, stop in sorted(occupied):
            if cursor + step <= first: break
            if cursor < stop: cursor = ((stop + step - 1) // step) * step
        need(cursor + step <= 1 << 32, 'prefix tree not overfull')
        occupied.append((cursor, cursor + step))
        out[index] = format(cursor >> (32 - width), '0' + str(width) + 'b')
    need(sum(1 << (32 - lengths[i]) for i in active) == 1 << 32, 'complete non-singleton tree')
    return out


def book(reader):
    first = reader.position
    need(reader.read(24) == 0x564342, 'codebook sync')
    dim, entries = reader.read(16), reader.read(24)
    need(0 < dim <= 16 and 0 < entries <= 64, 'finite declared book geometry')
    lengths = []
    if reader.read(1):
        size = reader.read(5) + 1
        while len(lengths) < entries:
            count = reader.read((entries - len(lengths)).bit_length())
            need(count <= entries - len(lengths) and size <= 32, 'ordered run bounds')
            lengths += [size] * count; size += 1
    else:
        sparse = reader.read(1)
        lengths = [reader.read(5) + 1 if not sparse or reader.read(1) else 0 for _ in range(entries)]
    lookup = reader.read(4)
    need(lookup in (0, 1, 2), 'public lookup type')
    result = dict(first=first, dim=dim, entries=entries, lengths=lengths, lookup=lookup)
    if lookup:
        result['minimum_offset'] = reader.position; result['minimum_packed'] = reader.read(32)
        result['delta_offset'] = reader.position; result['delta_packed'] = reader.read(32)
        result['q_bits'], result['sequence'] = reader.read(4) + 1, reader.read(1)
        quantvals = entries * dim
        if lookup == 1:
            quantvals = 1
            while (quantvals + 1) ** dim <= entries: quantvals += 1
        result['quantvals'] = quantvals
        result['multiplicands'] = [reader.read(result['q_bits']) for _ in range(quantvals)]
    result['end'] = reader.position
    return result


def select(data, index):
    need(data[:7] == b'\x05vorbis', 'complete raw setup header')
    reader = Bits(data); reader.position = 56
    count = reader.read(8) + 1
    need(0 <= index < count, 'existing book index')
    for i in range(index + 1): result = book(reader)
    return result


def patch_zero_fields(data, index, overrides):
    original = select(data, index)
    need(set(overrides) <= {'minimum', 'delta'} and all(type(v) is int and v == 0 for v in overrides.values()), 'zero-only unit field control')
    value, mask, edits = int.from_bytes(data, 'little'), 0, []
    for name in sorted(overrides):
        offset = original[name + '_offset']; field_mask = ((1 << 32) - 1) << offset
        old = (value >> offset) & 0xffffffff
        value &= ~field_mask; mask |= field_mask
        edits.append(dict(field=name, offset=offset, width=32, original=old, replacement=0))
    changed = value.to_bytes(len(data), 'little')
    need(not ((int.from_bytes(changed, 'little') ^ int.from_bytes(data, 'little')) & ~mask), 'only explicit zero float fields may change')
    return changed, edits


def describe(raw, index, points=(0, -8, -24)):
    b = select(raw, index)
    need(b['lookup'] in (1, 2), 'vector book required')
    dim, width = b['dim'], b['q_bits']
    qmin, minp = fixed_fields(b['minimum_packed']); qdel, delp = fixed_fields(b['delta_packed'])
    qdel >>= width; delp += width
    minimum = Fraction(qmin) * Fraction(2) ** minp if qmin else Fraction(0)
    delta = Fraction(qdel) * Fraction(2) ** delp if qdel else Fraction(0)
    need(minimum == number(b['minimum_packed']) and delta == number(b['delta_packed']),
         'selected fixtures retain exact canonical q_del/q_bits scaling')
    need(points and len(set(points)) == len(points) and set(points) <= {0, -8, -24}, 'declared public fixed-point positions')
    active = [i for i, length in enumerate(b['lengths']) if length]
    codes = words(b['lengths'])
    qpack = 0
    if b['lookup'] == 1:
        packed = (width * dim + 8) // 8
        offsets = ((b['quantvals'] - 1).bit_length() * dim + 8) // 8 + (width + 7) // 8
        kind = 1 if packed <= 4 and packed <= offsets else 2
        if kind == 2: qpack = (b['quantvals'] - 1).bit_length()
    else:
        kind = 1 if (width * dim + 8) // 8 <= 4 else 3
        if kind == 3: qpack = ((width + 7) // 8) * dim
    leafwidth = ((width if kind == 1 else qpack) * dim + 8) // 8 if kind in (1, 2) else (len(active) - 1).bit_length() // 8 + 1
    if len(active) == 1: node = 4
    else:
        if leafwidth == 3: leafwidth = 4
        node = max(leafwidth // 2, 1) if (3 * len(active) - 6).bit_length() + 1 <= leafwidth * 4 else leafwidth
    leafwords = 2 if leafwidth > node else 1
    need((node, leafwords) in ((1, 1), (1, 2), (4, 1)), 'finite owned table representations')
    qvalues, probes = [], []
    if kind == 2: qvalues = b['multiplicands'][:]
    for compact, entry in enumerate(active):
        if b['lookup'] == 1:
            digits, original = [], entry
            for _ in range(dim): digits.append(original % b['quantvals']); original //= b['quantvals']
            scalars = [b['multiplicands'][n] for n in digits]
        else:
            digits = []
            scalars = b['multiplicands'][entry * dim:(entry + 1) * dim]
        if kind == 3: qvalues.extend(scalars)
        leaf = sum(v << (width * i) for i, v in enumerate(scalars)) if kind == 1 else \
               sum(v << (qpack * i) for i, v in enumerate(digits)) if kind == 2 else compact
        expected, previous = [], Fraction(0)
        for scalar in scalars:
            need(0 <= scalar * qdel <= (1 << 31) - 1, 'selected scaled signed32 product bound')
            value = minimum + scalar * delta + previous
            expected.append(value)
            previous = value if b['sequence'] else Fraction(0)
        wires = [codes[entry], '1'] if len(active) == 1 else [codes[entry]]
        for code in wires:
            scaled = {}
            for point in points:
                values = [v * (Fraction(2) ** -point) for v in expected]
                need(all(v.denominator == 1 and -(1 << 31) <= v < 1 << 31 for v in values), 'exact signed32 point oracle')
                scaled[str(point)] = [int(v) for v in values]
            probes.append(dict(original=entry, wire=int(code[::-1], 2), bits=len(code), code_msb=code, leaf=leaf,
                wire_scope=('preferred_zero' if code == '0' else 'nonpreferred_one_tolerance_control')
                           if len(active) == 1 else 'canonical_codeword',
                full_standard_or_full_decoder_qualification_claim=False, expected_by_point=scaled))
    storage = 1 if width <= 8 else 2
    qbytes = b''.join(v.to_bytes(storage, 'little') for v in qvalues)
    return dict(raw_book=b, dim=dim, entries=b['entries'], used_entries=len(active), dec_maxlength=max(b['lengths']),
        dec_type=kind, dec_nodeb=node, dec_leafw=leafwords, q_bits=width, q_pack=qpack, q_seq=b['sequence'],
        q_min=qmin, q_minp=minp, q_del=qdel, q_delp=delp, qval_hex=qbytes.hex(),
        table_bytes=(len(active) * 2 + 1) * 4 if node == 4 else len(active) * (leafwords + 1) - 2,
        probes=probes, points=list(points), canonical_scaled_quantization_exact=True,
        zero_minimum=not b['minimum_packed'] & 0x1fffff, zero_delta=not b['delta_packed'] & 0x1fffff)

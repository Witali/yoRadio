"""Independent bounded numeric C-array reader; no compiler or target execution."""
import re


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def readback(text, model):
    numbers = {}
    for name in ('CURVE_CASES', 'CURVE_PACKETS', 'CURVE_CALLS', 'CURVE_BINS'):
        matches = re.findall(r'^#define ' + name + r' ([0-9]+)$', text, re.M)
        need(len(matches) == 1, 'Exact numeric macro: ' + name)
        numbers[name] = int(matches[0])
    need(numbers == dict(CURVE_CASES=6, CURVE_PACKETS=84, CURVE_CALLS=168,
        CURVE_BINS=model['counts']['bins']), 'Complete derived C counts')
    match = re.fullmatch(r'.*?static const int32_t curve_inputs\[CURVE_CALLS\]\[31\] = \{\n(.*?)\n\};\n'
        r'static const uint32_t curve_input_fnv\[CURVE_CALLS\] = \{\n(.*?)\n\};\n', text, re.S)
    need(match is not None, 'Exact bounded C data declarations')
    lines = match[1].splitlines()
    need(len(lines) == 168, 'All168 C descriptors')
    rows = []
    for line in lines:
        need(re.fullmatch(r'  \{-?[0-9]+(?:,-?[0-9]+){30}\},', line) is not None, 'Only31 signed numeric C words')
        row = [int(value) for value in re.findall(r'-?[0-9]+', line)]
        need(all(-(1 << 31) <= x < (1 << 31) for x in row), 'Exact signed32 C domain')
        rows.append(row)
    need(rows == [row['words'] for row in model['calls']], 'All C descriptor/raw field words equal model')
    need(re.fullmatch(r'  [0-9]+u(?:,[0-9]+u){167}', match[2]) is not None, 'All168 numeric C input checksums')
    checksums = [int(x) for x in re.findall(r'[0-9]+', match[2])]
    need(checksums == [row['input_fnv32'] for row in model['calls']], 'Every C checksum equals derived descriptor')
    need(sum(row[3] for row in rows) == model['counts']['bins'] and
         all(row[3] in (32,128,1024) and row[4] in (5,6) and row[5] in (64,128) and row[8] == 24000 for row in rows),
         'All half-block domains and full derived output size')
    return dict(result='BOUNDED_C_ARRAY_READBACK_EQUAL', descriptors=168, words=168*31, bins=numbers['CURVE_BINS'])

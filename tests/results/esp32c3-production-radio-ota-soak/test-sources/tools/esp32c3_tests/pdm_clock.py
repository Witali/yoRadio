"""Decode C3 DAC clock register readback; this is not crystal metrology."""
from fractions import Fraction
import re

FIELDS = ('sclk', 'source', 'integer', 'x', 'y', 'z', 'yn1', 'bdiv', 'osr', 'fp', 'fs')
FIELD_MAX = dict(sclk=2**32-1, source=3, integer=255, x=511, y=511, z=511,
                 yn1=1, bdiv=256, osr=15, fp=1023, fs=1023)
NOMINAL_PCM_HZ = 48000
PDM_BASE_OVERSAMPLING = 64


def parse(line):
    if 'PERF PDM_CLOCK' not in line:
        return None
    marker = 'PERF PDM_CLOCK:'
    if marker not in line or line.count('PERF ') != 1:
        raise ValueError('Damaged clock marker')
    line = re.sub(r'\x1b\[[0-9;]*m', '', line)
    tokens = line.split(marker, 1)[1].strip().split()
    if len(tokens) != len(FIELDS):
        raise ValueError('Incomplete clock fields')
    values = {}
    for name, token in zip(FIELDS, tokens):
        match = re.fullmatch(name+r'=(\d+)', token)
        if not match or int(match[1]) > FIELD_MAX[name]:
            raise ValueError('Invalid clock field '+name)
        values[name] = int(match[1])
    # The experiment is intentionally scoped to the audited fixed-rate DAC.
    if (values['sclk'], values['source'], values['bdiv'], values['osr'], values['fp'], values['fs']) != (
            160000000, 2, 13, 2, 960, 480):
        raise ValueError('Unaudited PCM/DAC clock configuration')
    if values['integer'] < 2:
        raise ValueError('Unsupported integer divider')
    if values['z'] == 0:
        if values['yn1'] != 0:
            raise ValueError('Ambiguous zero fractional divider')
        fractional = Fraction(0)
    else:
        denominator = (values['x']+1)*values['z']+values['y']
        if values['y'] >= values['z'] or values['x'] < 1:
            raise ValueError('Noncanonical fractional divider')
        fractional = Fraction(values['z'], denominator)
        if values['yn1']:
            fractional = 1-fractional
    divider = values['integer']+fractional
    pcm = Fraction(values['sclk'])/(divider*values['bdiv']*values['osr']*PDM_BASE_OVERSAMPLING)
    return dict(registers=values, divider=str(divider), nominal_pcm_hz_fraction=str(pcm),
                nominal_pcm_hz=float(pcm), error_ppm=float((pcm/NOMINAL_PCM_HZ-1)*1000000),
                exact_nominal_48khz=pcm==NOMINAL_PCM_HZ,
                note='Configured register readback; source Hz is nominal, not externally measured.')

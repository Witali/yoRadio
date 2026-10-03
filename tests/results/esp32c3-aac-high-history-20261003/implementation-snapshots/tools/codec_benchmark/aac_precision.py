"""Current AAC precision policy, with explicit historical log interpretation."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
POLICY_FILE = ROOT / 'idf/esp32c3-oled-native/main/aac_pcm_quality.h'


def constant(name):
    matches = re.findall(r'^#define '+name+r' (\d+)$', POLICY_FILE.read_text(), re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('Missing/duplicate PCM policy constant: '+name)
    return int(matches[0])


PRODUCTION_LIMIT = constant('AAC_PCM_PRODUCTION_ERROR_LSB')
DEVELOPMENT_LIMIT = constant('AAC_PCM_DEVELOPMENT_ERROR_LSB')


def log_limits(log, label, *, required=True):
    lines = [line.split(label+'_LIMIT ', 1)[1] for line in log.splitlines() if label+'_LIMIT ' in line]
    if not lines and not required:
        # Early QMF/area probes had no explicit header; their saved policy was 2.
        return dict(development=5, production=2)
    if len(lines) != 1:
        raise ValueError('Missing/duplicate precision limits')
    values = dict(re.findall(r'(\w+)=(\d+)', lines[0]))
    if set(values) != {'development', 'production'}:
        raise ValueError('Malformed precision limits')
    limits = {k: int(v) for k, v in values.items()}
    if limits['production'] not in (2, PRODUCTION_LIMIT) or not 1 <= limits['development'] <= DEVELOPMENT_LIMIT:
        raise ValueError('Unsupported precision limits')
    return limits


def passes(rows, limit):
    return all(max(row['max_l'], row['max_r']) <= limit for row in rows)

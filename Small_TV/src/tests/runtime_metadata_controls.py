"""Reject altered Ghidra ownership, machine instructions, references and completeness claims."""
from copy import deepcopy

from reverse.runtime_metadata import verify


def controls(image, qualification, manifest, recovery, before, after):
    """Change actual checker inputs one at a time, keeping the immutable baseline graph pinned."""
    faults = ('extent', 'body-hash', 'missing-function', 'wrong-owner', 'merged-body', 'missing-instruction',
              'instruction-bytes', 'call-target', 'call-type', 'function-data-alias', 'detached-owner',
              'detached-bytes', 'unrelated-function', 'missing-reference', 'reference-owner', 'program-bytes',
              'existing-instruction', 'instruction-total', 'function-api-count', 'whole-image-claim')
    rejected = []
    for fault in faults:
        m = deepcopy(manifest) if fault in ('extent', 'body-hash') else manifest
        g = deepcopy(after) if fault in ('unrelated-function', 'missing-reference', 'reference-owner') else after
        r = recovery if m is not manifest or g is not after else deepcopy(recovery)
        if fault == 'extent': m['functions'][0]['end'] = '0x403801d6'
        elif fault == 'body-hash': m['functions'][0]['code_sha256'] = '0' * 64
        elif fault == 'missing-function': r['functions'].pop()
        elif fault == 'wrong-owner': r['functions'][0]['after']['name'] = 'guessed_callback'
        elif fault == 'merged-body':
            row = next(row for row in r['functions'] if row['after']['name'] == '__cxa_end_catch')
            row['before']['ranges'][0][1] = '0x420a3e0b'
        elif fault == 'missing-instruction': r['functions'][0]['instructions'].pop()
        elif fault == 'instruction-bytes': r['functions'][0]['instructions'][0]['bytes'] = '0100'
        elif fault in ('call-target', 'call-type'):
            call = next(i for row in r['functions'] for i in row['instructions'] if i['pc'] == '0x40380180')
            call['references'][0]['offset' if fault == 'call-target' else 'type'] = 0x40380566 if fault == 'call-target' else 'UNCONDITIONAL_JUMP'
        elif fault == 'function-data-alias':
            item = next(i for row in r['functions'] for i in row['instructions'] if i['pc'] == '0x420a3f88')
            item['references'][0]['offset'] = 0x40380566
        elif fault == 'detached-owner': r['detached'][0]['owner'] = dict(entry='0x420a3e08', name='guessed_return')
        elif fault == 'detached-bytes': r['detached'][1]['instructions'].pop()
        elif fault == 'unrelated-function': g['functions'][0]['body_bytes'] += 2
        elif fault in ('missing-reference', 'reference-owner'):
            row = next(row for row in g['functions'] if row['entry'] == '0x40380584')
            index = next(i for i, edge in enumerate(row['references']) if edge['from'] == '0x40380180')
            if fault == 'missing-reference': row['references'].pop(index)
            else: row['references'][index]['owner']['entry'] = '0x40380104'
        elif fault == 'program-bytes': r['memory_after']['.iram.vectors'] = '0' * 64
        elif fault == 'existing-instruction': r['instruction_starts_before'].append('0x40380000')
        elif fault == 'instruction-total': r['instruction_count_after'] += 1
        elif fault == 'function-api-count': r['function_count_before'] += 1; r['function_count_after'] += 1
        else: r['whole_image_completeness_proved'] = True
        try:
            verify(image, qualification, m, r, before, g)
        except ValueError:
            rejected.append(fault)
        else:
            raise AssertionError('Altered runtime metadata accepted: ' + fault)
    return dict(passed=True, rejected=rejected)

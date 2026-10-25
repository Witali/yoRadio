"""Validate bounded transient timer metadata and unchanged persistent projects."""
import copy


def validate(recovery, timers, dispatch, before, after, copied, integrity):
    """Bind all 21 owners, instruction deltas and 14 table cells to qualified bodies."""
    expected = {row['start']: row for row in (*timers['functions'], *dispatch['factory']['functions'])}
    assert len(expected) == 21
    assert recovery['program_sha256'] == dispatch['factory']['factory_elf_sha256'] == before['program_sha256'] == after['program_sha256']
    memory = {row['name']: row['sha256'] for row in before['memory_blocks'] if row['initialized']}
    assert recovery['program_bytes_unchanged'] is True and recovery['memory_before'] == recovery['memory_after'] == memory
    assert before['memory_blocks'] == after['memory_blocks']
    assert recovery['whole_image_completeness_proved'] is False
    rows = recovery['functions']
    assert len(rows) == len(expected) and {row['start'] for row in rows} == set(expected)
    functions = {row['entry']: row for row in after['functions'] if row['space'] == 'ram'}
    for row in rows:
        spec = expected[row['start']]
        assert row['name'] == spec['name'] and row['end'] == spec['end']
        assert row['decoded_instructions'] == spec['linked_instruction_starts']
        assert type(row['instructions_in_range_before']) is int and 0 <= row['instructions_in_range_before'] <= row['decoded_instructions']
        assert type(row['created_function']) is bool and row['created_function'] == (not row['before'])
        owner = row['after']
        assert owner['entry'] == row['start'] and owner['name'] == row['name']
        assert owner['ranges'] == [[row['start'], hex(int(row['end'], 0)-1)]]
        assert owner['body_bytes'] == spec['linked_bytes'] == functions[row['start']]['body_bytes']
        assert functions[row['start']]['name'] == row['name']
    added = sum(row['created_function'] for row in rows)
    assert recovery['enumerated_before'] == len(before['functions']) and recovery['enumerated_after'] == len(after['functions'])
    assert recovery['enumerated_after'] - recovery['enumerated_before'] == added
    assert recovery['functions_after'] - recovery['functions_before'] == added
    assert recovery['instruction_count_before'] == before['instruction_count']
    assert recovery['instruction_count_after'] == after['instruction_count']
    instruction_delta = sum(row['decoded_instructions'] - row['instructions_in_range_before'] for row in rows)
    assert after['instruction_count'] - before['instruction_count'] == instruction_delta
    edges = recovery['table_edges']
    entries = dispatch['factory']['table']['entries']
    assert len(edges) == len(entries) == 14
    for actual, entry in zip(edges, entries):
        assert all(actual[key] == entry[key] for key in ('id', 'cell', 'target'))
        assert actual['owner']['entry'] == entry['target'] and actual['owner']['name'] == entry['name']
    assert copied['count'] == len(copied['files']) == 10 and copied['copy_verified'] is True
    assert integrity['passed'] is True and integrity['file_count'] == 10 and len(integrity['projects']) == 2
    assert {row['kind'] for row in integrity['projects']} == {'source', 'copy'}
    for row in integrity['projects']:
        assert row['unchanged'] is True and row['path'] == copied[row['kind']] and row['files'] == copied['files']
    return {'passed': True, 'qualified_bodies': 21, 'created_functions': added, 'renamed_existing_functions': len(rows)-added,
            'added_instructions': instruction_delta, 'table_edges': len(edges), 'persistent_projects_unchanged': True,
            'whole_image_completeness_proved': False}


def rejected_controls(recovery, timers, dispatch, before, after, copied, integrity):
    """Reject altered graph ownership, instruction accounting and persistence claims."""
    rejected = []
    for case in ('missing-owner', 'wrong-body-end', 'wrong-callback-owner', 'missing-table-edge',
                 'changed-program-memory', 'wrong-function-count', 'unbounded-instruction-delta', 'changed-saved-project'):
        row, graph, saved = copy.deepcopy((recovery, after, integrity))
        if case == 'missing-owner': row['functions'].pop()
        elif case == 'wrong-body-end': row['functions'][0]['after']['ranges'][0][1] = row['functions'][0]['end']
        elif case == 'wrong-callback-owner': row['table_edges'][0]['owner']['entry'] = '0x42000020'
        elif case == 'missing-table-edge': row['table_edges'].pop()
        elif case == 'changed-program-memory': row['memory_after'][next(iter(row['memory_after']))] = '0' * 64
        elif case == 'wrong-function-count': row['functions_after'] += 1
        elif case == 'unbounded-instruction-delta':
            row['instruction_count_after'] += 1
            graph['instruction_count'] += 1
        else: saved['projects'][0]['files'][next(iter(saved['projects'][0]['files']))] = '0' * 64
        try:
            validate(row, timers, dispatch, before, graph, copied, saved)
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected.append(case)
        else:
            raise AssertionError('Altered timer recovery accepted: ' + case)
    return rejected

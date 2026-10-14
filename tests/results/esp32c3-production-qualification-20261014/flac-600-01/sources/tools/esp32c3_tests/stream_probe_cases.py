"""Unique fixture identities for repeated stream tests on one firmware boot."""
from common import require


def repeat_specs(specs, repetitions):
    require(type(repetitions) is int and 1 <= repetitions <= 20,
            'Repetitions must be between 1 and 20')
    result = {}
    for iteration in range(1, repetitions + 1):
        for source_name, spec in specs.items():
            name = source_name if iteration == 1 else f'{source_name}--repeat-{iteration}'
            require(name not in result, 'Repeated fixture name collision')
            result[name] = dict(spec, source_name=source_name, iteration=iteration)
    return result


def validate_schedule(report, expected_cases):
    specs = report['fixtures']
    count = report.get('repetitions', 1)
    originals = {name: spec for name, spec in specs.items() if spec.get('iteration', 1) == 1}
    expected = repeat_specs(originals, count)
    names = [case['name'] for case in report['cases']]
    require(len(names) == len(set(names)) == expected_cases and
            names == list(expected) and set(names) == set(specs), 'Case coverage/order differs')
    for name, spec in specs.items():
        source = expected[name]['source_name']
        require(spec.get('source_name', name) == source and
                spec.get('iteration', 1) == expected[name]['iteration'],
                'Repeated fixture identity differs')
        require(all(spec[k] == originals[source][k] for k in ('bytes', 'sha256', 'mime')),
                'Repeated fixture payload differs')
    return {name: spec['source_name'] for name, spec in expected.items()}

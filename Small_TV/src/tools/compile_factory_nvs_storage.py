"""Compile unchanged PageManager/Storage analysis objects with the qualified factory profile."""
import argparse
import json
from pathlib import Path

from compile_factory_nvs_fixture import SDK_REVISION, dependencies, run, sha

SOURCES = ('nvs_pagemanager.cpp', 'nvs_storage.cpp')


def build(sdk, compiler, fixture, output):
    """Reuse canonical compiler options while preserving all existing proof inputs."""
    if output.exists():
        raise ValueError('Preserve existing storage fixture')
    parent = json.loads((fixture/'provenance.json').read_bytes())
    if sha((fixture/'nvs_page.cpp.o').read_bytes()) != parent['object_sha256'] or \
            parent['object_sha256'] != '9ed443fea642655cdfe641e74bce4a26fd69bdefe151c40dee96919888731d0f':
        raise ValueError('Require the qualified factory Page fixture')
    if run(['git', '-C', sdk, 'rev-parse', 'HEAD'], sdk).strip() != SDK_REVISION or \
            run(['git', '-C', sdk, 'status', '--porcelain'], sdk).strip():
        raise ValueError('Require the clean pinned SDK')
    if '14.2.0_20260121' not in run([compiler, '--version'], sdk):
        raise ValueError('Wrong compiler profile')
    config = (fixture/'config/sdkconfig.h').read_bytes()
    if sha(config) != parent['config_sha256']:
        raise ValueError('Factory profile changed')
    output.mkdir(parents=True); (output/'config').mkdir(); (output/'config/sdkconfig.h').write_bytes(config)
    roots = {'sdk': sdk, 'toolchain': compiler.parent.parent, 'fixture': output}
    def canonical(value, expand=False):
        """Keep recorded arguments independent of the local task and SDK directory names."""
        value = str(value)
        for name, path in roots.items():
            token = '${'+name+'}'
            value = value.replace(token, str(path)) if expand else value.replace(str(path), token)
        return value
    template = [canonical(value, True) for value in parent['compile']]; template[0] = str(compiler)
    objects = {}
    for name in SOURCES:
        stem = name.removesuffix('.cpp')
        args = [a.replace('nvs_page.d', stem+'.d').replace('nvs_page.cpp.o', name+'.o')
                 .replace('src/nvs_page.cpp', 'src/'+name).replace('src\\nvs_page.cpp', 'src\\'+name) for a in template]
        args += ['-I'+str(sdk/'components/log/include'), '-I'+str(sdk/'components/soc/esp32c2/include')]
        run(args, output)
        pins = {}
        for path in sorted(set(dependencies(output/(stem+'.d')))):
            owners = [(key, base) for key, base in roots.items() if path.is_relative_to(base)]
            if len(owners) != 1:
                raise ValueError('Unexpected storage dependency root')
            key, base = owners[0]; pins[key+'/'+path.relative_to(base).as_posix()] = sha(path.read_bytes())
        objects[name] = dict(object_sha256=sha((output/(name+'.o')).read_bytes()),
                             compile=[canonical(a) for a in args], dependencies=pins)
    if run(['git', '-C', sdk, 'status', '--porcelain'], sdk).strip():
        raise ValueError('SDK changed during compilation')
    result = dict(passed=True, sdk_revision=SDK_REVISION, config_sha256=sha(config),
                  parent_object_sha256=parent['object_sha256'], sources=objects,
                  production_firmware_built=False, factory_compiler_version_identified=False)
    (output/'provenance.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf8', newline='\n')
    return result


def main():
    """Require explicit inputs and a fresh analysis-only output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('sdk', 'compiler', 'fixture', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    result = build(*(getattr(args, n).resolve() for n in ('sdk', 'compiler', 'fixture', 'output')))
    print(json.dumps({name: row['object_sha256'] for name, row in result['sources'].items()}))


if __name__ == '__main__':
    main()

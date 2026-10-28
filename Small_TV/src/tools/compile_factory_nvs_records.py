"""Compile unchanged NVS Item/HashList sources using the already qualified factory profile."""
import argparse
import json
from pathlib import Path

from compile_factory_nvs_fixture import SDK_REVISION, dependencies, run, sha

SOURCES = ('nvs_types.cpp', 'nvs_item_hash_list.cpp')


def build(sdk, compiler, fixture, output):
    """Preserve the original fixture while recording a separate dependency closure per new object."""
    if output.exists(): raise ValueError('Preserve existing record fixture')
    parent = json.loads((fixture/'provenance.json').read_bytes())
    if parent['object_sha256'] != '9ed443fea642655cdfe641e74bce4a26fd69bdefe151c40dee96919888731d0f' or \
            sha((fixture/'nvs_page.cpp.o').read_bytes()) != parent['object_sha256']:
        raise ValueError('Require the qualified original NVS fixture')
    if run(['git', '-C', sdk, 'rev-parse', 'HEAD'], sdk).strip() != SDK_REVISION or \
            run(['git', '-C', sdk, 'status', '--porcelain'], sdk).strip(): raise ValueError('Require clean pinned SDK')
    if '14.2.0_20260121' not in run([compiler, '--version'], sdk): raise ValueError('Wrong compiler')
    profile = (fixture/'config/sdkconfig.h').read_bytes()
    if sha(profile) != parent['config_sha256']: raise ValueError('Profile changed')
    output.mkdir(parents=True); (output/'config').mkdir(); (output/'config/sdkconfig.h').write_bytes(profile)
    roots = {'sdk': sdk, 'toolchain': compiler.parent.parent, 'fixture': output}
    def expand(value):
        """Keep every original option, resolving only declared local provenance roots."""
        for name, path in roots.items(): value = value.replace('${'+name+'}', str(path))
        return value
    template = [expand(value) for value in parent['compile']]; template[0] = str(compiler)
    reports = {}
    for name in SOURCES:
        stem = name.removesuffix('.cpp')
        args = [value.replace('nvs_page.d', stem+'.d').replace('nvs_page.cpp.o', name+'.o')
                .replace('src/nvs_page.cpp', 'src/'+name).replace('src\\nvs_page.cpp', 'src\\'+name) for value in template]
        args += ['-I'+str(sdk/'components/log/include'), '-I'+str(sdk/'components/soc/esp32c2/include')]
        run(args, output)
        paths = set(dependencies(output/(stem+'.d')))
        pins = {}
        for path in sorted(paths):
            matches = [(key, root) for key, root in roots.items() if path.is_relative_to(root)]
            if len(matches) != 1: raise ValueError('Unexpected record dependency: '+str(path))
            key, root = matches[0]; pins[key+'/'+path.relative_to(root).as_posix()] = sha(path.read_bytes())
        command = list(args)
        for i, value in enumerate(command):
            for key, root in roots.items(): value = value.replace(str(root), '${'+key+'}')
            command[i] = value
        reports[name] = dict(object_sha256=sha((output/(name+'.o')).read_bytes()), dependencies=pins, compile=command)
    if run(['git', '-C', sdk, 'status', '--porcelain'], sdk).strip(): raise ValueError('SDK changed during compilation')
    report = dict(passed=True, sdk_revision=SDK_REVISION, parent_object_sha256=parent['object_sha256'],
                  config_sha256=sha(profile), sources=reports, production_firmware_built=False,
                  factory_compiler_version_identified=False)
    (output/'provenance.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8', newline='\n')
    return report


def main():
    """Require explicit pinned inputs and a fresh task-local output directory."""
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('sdk', 'compiler', 'fixture', 'output'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    report = build(*(getattr(args, n).resolve() for n in ('sdk', 'compiler', 'fixture', 'output')))
    print(json.dumps({name: row['object_sha256'] for name, row in report['sources'].items()}))


if __name__ == '__main__': main()

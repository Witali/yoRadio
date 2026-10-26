"""Materialize a declared resource port beside an unchanged Xiph copy.

Every before fragment must match exactly once. No compiler, SDK, network,
external patch executable or other subprocess is invoked.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

BASE_SHA = '897096caf216de0e161f4fd833037863f8e2dc3da0531e34b851503f932f4b14'

def need(ok, reason):
    if not ok:
        raise ValueError(reason)

def sha(body):
    return hashlib.sha256(body).hexdigest()

def relative(name):
    path = PurePosixPath(name)
    need(name == path.as_posix() and path.parts and not path.is_absolute()
         and '..' not in path.parts and ':' not in name and '\\' not in name,
         'contained canonical relative path')
    return name

def checked_tree(root, manifest_name, expected_sha, schema):
    raw = (root / manifest_name).read_bytes()
    need(expected_sha is None or sha(raw) == expected_sha, 'pinned manifest identity')
    manifest = json.loads(raw)
    need(manifest['schema'] == schema and isinstance(manifest['files'], dict), 'manifest schema')
    files = {relative(name): digest for name, digest in manifest['files'].items()}
    need(manifest_name not in files, 'manifest excludes itself')
    need(all(len(d) == 64 and set(d) <= set('0123456789abcdef') for d in files.values()), 'file hashes')
    paths = list(root.rglob('*'))
    need(not any(p.is_symlink() for p in paths), 'regular source tree')
    need({p.relative_to(root).as_posix() for p in paths if p.is_file()}
         == set(files) | {manifest_name}, 'exact complete file inventory')
    bodies = {name: (root / name).read_bytes() for name in files}
    need(all(sha(bodies[name]) == digest for name, digest in files.items()), 'every source file hash')
    bodies[manifest_name] = raw
    return manifest, bodies

def materialize(upstream, port, output):
    upstream, port, output = upstream.resolve(), port.resolve(), output.resolve()
    need(upstream != port and not output.is_relative_to(upstream) and not output.is_relative_to(port)
         and not upstream.is_relative_to(output) and not port.is_relative_to(output), 'source/output separation')
    baseline, original = checked_tree(upstream, 'component-manifest.json', BASE_SHA, 'native-vorbis-xiph-source-v1')
    adaptation, edits = checked_tree(port, 'port-manifest.json', None, 'native-vorbis-xiph-resource-port-v1')
    need(adaptation['base_manifest_sha256'] == BASE_SHA, 'same unchanged release baseline')
    changes = json.loads(edits['edits.json'])
    need(changes['schema'] == 'native-vorbis-xiph-exact-edits-v1'
         and len(changes['edits']) == 33, 'thirty-three exact reviewed edits')
    modified, applied = {}, []
    for change in changes['edits']:
        source = relative(change['source'])
        before_name, after_name = relative(change['before']), relative(change['after'])
        need(source in baseline['compile_sources'], 'only a declared compiled source can change')
        before, after = edits[before_name], edits[after_name]
        need(before and after and before != after, 'explicit nonempty source deviation')
        body = modified.get(source, original[source])
        need(body.count(before) == 1, 'one exact original fragment: ' + before_name)
        modified[source] = body.replace(before, after, 1)
        applied.append(dict(source=source, before=before_name, after=after_name,
                            before_sha256=sha(before), after_sha256=sha(after)))
    need(set(modified) == {'upstream/libvorbis/lib/block.c', 'upstream/libvorbis/lib/sharedbook.c',
                           'upstream/libogg/src/bitwise.c', 'upstream/libvorbis/lib/codebook.c',
                           'upstream/libvorbis/lib/floor0.c', 'upstream/libvorbis/lib/floor1.c',
                           'upstream/libvorbis/lib/res0.c', 'upstream/libvorbis/lib/mapping0.c',
                           'upstream/libvorbis/lib/info.c', 'upstream/libvorbis/lib/mdct.c',
                           'upstream/libvorbis/lib/synthesis.c'},
         'only the eleven reviewed translation units change')
    generated = {'base/' + name: body for name, body in original.items()}
    generated.update({'ported/' + PurePosixPath(name).name: body for name, body in modified.items()})
    generated['ported/native_vorbis_xiph_header_error.h'] = edits['include/native_vorbis_xiph_header_error.h']
    generated['ported/native_vorbis_xiph_dsp_error.h'] = edits['include/native_vorbis_xiph_dsp_error.h']
    generated['ported/native_vorbis_xiph_comment_error.h'] = edits['include/native_vorbis_xiph_comment_error.h']
    generated['ported/native_vorbis_xiph_packet_error.h'] = edits['include/native_vorbis_xiph_packet_error.h']
    units = [dict(original=name, compiled=('ported/' + PurePosixPath(name).name
              if name in modified else 'base/' + name)) for name in baseline['compile_sources']]
    record = dict(schema='native-vorbis-xiph-generated-port-v1', base_manifest_sha256=BASE_SHA,
                  port_manifest_sha256=sha(edits['port-manifest.json']), edits=applied,
                  compiled_units=units, files={name: sha(body) for name, body in sorted(generated.items())})
    generated['PORTING.json'] = (json.dumps(record, indent=2, sort_keys=True) + '\n').encode()
    # Reconfiguration can reuse only an identical complete generated tree.
    if output.exists():
        paths = list(output.rglob('*'))
        need(not any(p.is_symlink() for p in paths), 'regular existing generated tree')
        existing = {p.relative_to(output).as_posix(): p.read_bytes() for p in paths if p.is_file()}
        need(existing == generated, 'generated output differs; use a fresh build directory')
    else:
        output.mkdir(parents=True)
        for name, body in sorted(generated.items()):
            path = output / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
    return record

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('upstream', 'port', 'output'):
        parser.add_argument('--' + name, required=True, type=Path)
    args = parser.parse_args()
    result = materialize(args.upstream, args.port, args.output)
    print(json.dumps(dict(prepared=True, base_manifest_sha256=BASE_SHA,
                         port_manifest_sha256=result['port_manifest_sha256'],
                         compiled_units=len(result['compiled_units']), edits=len(result['edits']))))

if __name__ == '__main__':
    main()

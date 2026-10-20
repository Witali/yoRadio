"""Offline CYD production build and verified development firmware export.

Only development destinations are writable. No command deploys firmware or
invokes setup. The exporter can also qualify an existing clean build directly.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile


PROJECT = Path('idf/esp32-cyd2usb-native')
PROJECT_NAME = 'yoradio_cyd2usb_native'
IDF_VERSION = 'v6.0.2'
BACKENDS = {
    'pdm': 'YORADIO_NATIVE_AUDIO_OUTPUT_PDM',
    'continuous': 'YORADIO_NATIVE_AUDIO_OUTPUT_DAC',
    'legacy': 'YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC',
}
SOURCE_EXCLUSIONS = ('firmware/development/', 'tests/results/')


class ValidationError(RuntimeError):
    """A build cannot be identified as the requested production artifact."""


def require(condition, message):
    if not condition:
        raise ValidationError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def file_sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args])


def source_snapshot(root):
    commit = git(root, 'rev-parse', 'HEAD').decode().strip()
    changed = {os.fsdecode(n) for n in git(root, 'diff', '--name-only', 'HEAD', '-z').split(b'\0') if n}
    untracked = [os.fsdecode(n) for n in git(root, 'ls-files', '--others', '--exclude-standard', '-z').split(b'\0') if n]
    included = lambda name: not any(name.startswith(prefix) for prefix in SOURCE_EXCLUSIONS)
    untracked = sorted(name for name in untracked if included(name))
    entries = {}
    for entry in git(root, 'ls-files', '--stage', '-z').split(b'\0'):
        if entry:
            metadata, raw_name = entry.split(b'\t', 1)
            mode, blob, stage = metadata.split()
            name = os.fsdecode(raw_name)
            if included(name):
                require(stage == b'0', 'Resolve source merge conflicts before a production build.')
                entries[name] = (mode, blob)
    for name in untracked:
        entries[name] = (b'untracked', b'')
    digest = hashlib.sha256()
    for name in sorted(entries):
        mode, blob = entries[name]
        path = root / name
        digest.update(os.fsencode(name) + b'\0' + mode + b'\0')
        if name not in changed and name not in untracked:
            # Git already identifies clean contents. Do not reread gigabytes of
            # immutable firmware/history merely to qualify an incremental build.
            digest.update(b'git-blob\0' + blob)
        elif path.is_symlink():
            digest.update(b'symlink\0' + os.fsencode(os.readlink(path)))
        elif path.is_file():
            digest.update(bytes.fromhex(file_sha256(path)))
        else:
            digest.update(b'missing\0')
    return {'commit': commit, 'dirty': bool(changed),
            'source_dirty': any(included(name) for name in changed),
            'untracked': untracked, 'excluded_paths': list(SOURCE_EXCLUSIONS),
            'content_sha256': digest.hexdigest()}


def check_source(snapshot, allow_dirty):
    require(allow_dirty or not (snapshot.get('source_dirty', snapshot['dirty']) or snapshot['untracked']),
            'Commit source before a production build/export, or explicitly select --allow-dirty.')


def resolve_relative(path, base):
    path = Path(path)
    return (path if path.is_absolute() else base / path).resolve()


def destination(root, variant, explicit=None):
    require(bool(re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9._-]{0,95}', variant)),
            'Variant must be a simple directory name (at most 96 characters).')
    development = root / 'firmware/development'
    require(development.resolve() == development,
            'firmware/development must not redirect to another directory.')
    out = resolve_relative(explicit, root) if explicit else (development / variant).resolve()
    require(out != development and out.is_relative_to(development),
            'Firmware output must be inside firmware/development; versioned releases are immutable.')
    require(not out.is_symlink(), 'A firmware output directory must not be a symlink.')
    return out


def parse_sdkconfig(text):
    values = {}
    for line in text.splitlines():
        unset = re.fullmatch(r'# CONFIG_([A-Z0-9_]+) is not set', line)
        setting = re.fullmatch(r'CONFIG_([A-Z0-9_]+)=(.*)', line)
        if unset:
            key, value = unset[1], False
        elif setting:
            key, raw = setting.groups()
            if raw in ('y', 'n'):
                value = raw == 'y'
            elif raw.startswith('"'):
                value = json.loads(raw)
            else:
                value = int(raw, 16 if raw.lower().startswith('0x') else 10)
        else:
            continue
        require(key not in values, f'Duplicate sdkconfig key: {key}')
        values[key] = value
    return values


def build_file(build, name):
    path = resolve_relative(name, build)
    require(path.is_relative_to(build), f'Build artifact escapes its build directory: {name}')
    require(path.is_file(), f'Missing build artifact: {path}')
    return path


def c_string(data):
    return data.split(b'\0', 1)[0].decode('utf-8')


def image_descriptor(image):
    require(len(image) >= 288 and image[0] == 0xE9, 'Not an ESP application image.')
    require(struct.unpack_from('<H', image, 12)[0] == 0, 'Image chip ID is not ESP32.')
    require(1 <= image[1] <= 16, 'Invalid image segment count.')
    position, checksum = 24, 0xEF
    for segment in range(image[1]):
        require(position + 8 <= len(image), 'Truncated image segment header.')
        size = struct.unpack_from('<I', image, position + 4)[0]
        position += 8
        require(size > 0 and position + size <= len(image), 'Truncated image segment payload.')
        if segment == 0:
            require(size >= 256 and struct.unpack_from('<I', image, position)[0] == 0xABCD5432,
                    'First image segment has no ESP application descriptor.')
        for value in image[position:position + size]:
            checksum ^= value
        position += size
    checksum_position = ((position + 1 + 15) // 16) * 16 - 1
    require(checksum_position < len(image) and image[checksum_position] == checksum,
            'Image segment checksum mismatch.')
    end = checksum_position + 1
    require(image[23] == 1, 'Production image must include its SHA256 image checksum.')
    require(len(image) == end + 32 and hashlib.sha256(image[:end]).digest() == image[end:],
            'Image SHA256 checksum mismatch or unexpected trailing bytes.')
    descriptor = image[32:288]
    return {'version': c_string(descriptor[16:48]), 'project_name': c_string(descriptor[48:80]),
            'idf_version': c_string(descriptor[112:144]), 'elf_sha256': descriptor[144:176].hex()}


def partition_slots(data, flash_bytes):
    require(len(data) >= 32 and len(data) % 32 == 0, 'Invalid generated partition table size.')
    slots, ranges, md5_seen = {}, [], False
    for offset in range(0, len(data), 32):
        entry = data[offset:offset + 32]
        magic = struct.unpack_from('<H', entry)[0]
        if magic == 0xFFFF:
            break
        if magic == 0xEBEB:
            require(not md5_seen and hashlib.md5(data[:offset]).digest() == entry[16:],
                    'Partition table MD5 mismatch.')
            md5_seen = True
            continue
        require(not md5_seen and magic == 0x50AA, 'Invalid generated partition table entry.')
        _, kind, subtype, address, size, label, _ = struct.unpack('<HBBII16sI', entry)
        require(size > 0 and address >= 0x9000 and address + size <= flash_bytes,
                'Partition exceeds configured ESP32 flash bounds.')
        require(all(address + size <= start or address >= end for start, end in ranges),
                'Overlapping partitions in generated table.')
        ranges.append((address, address + size))
        if kind == 0 and subtype in (0x10, 0x11):
            require(subtype not in slots, 'Duplicate OTA application partition.')
            slots[subtype] = {'name': c_string(label), 'offset': address, 'bytes': size}
    require(md5_seen and set(slots) == {0x10, 0x11},
            'Expected a checked partition table with both ota_0 and ota_1 slots.')
    return [slots[0x10], slots[0x11]]


def qualify(root, build, dependencies, backend, snapshot, expected_config=None):
    description_path = build_file(build, 'project_description.json')
    desc = json.loads(description_path.read_text(encoding='utf-8'))
    require(desc.get('target') == 'esp32', 'Build target is not ESP32.')
    require(desc.get('project_name') == PROJECT_NAME, 'Unexpected IDF project name.')
    require(desc.get('git_revision') == IDF_VERSION, f'CYD requires pinned IDF {IDF_VERSION}.')
    require(resolve_relative(desc['project_path'], build) == (root / PROJECT).resolve(),
            'Build belongs to another project/worktree.')
    require(resolve_relative(desc['build_dir'], build) == build, 'Build directory identity mismatch.')
    require(resolve_relative(desc['idf_path'], build) == (dependencies / IDF_VERSION).resolve(),
            'Build used another ESP-IDF dependency root.')
    compiler = Path(desc.get('c_compiler', ''))
    require('xtensa-esp32-elf-gcc' in compiler.name.lower(), 'Production compiler is not ESP32 Xtensa GCC.')
    require(compiler.resolve().is_relative_to((dependencies / 'tools-v6.0.2').resolve()),
            'Compiler did not come from pinned CYD tools-v6.0.2.')
    require(compiler.is_file(), 'The recorded production compiler is missing.')

    config_path = resolve_relative(desc['config_file'], build)
    if expected_config is not None:
        require(config_path == expected_config.resolve(), 'Build used a different sdkconfig than requested.')
    config_text = config_path.read_bytes()
    config = json.loads(build_file(build, 'config/sdkconfig.json').read_text(encoding='utf-8'))
    current_text = config_text.decode('utf-8').split('# Deprecated options for backward compatibility', 1)[0]
    parsed = parse_sdkconfig(current_text)
    # IDF appends compatibility aliases to the text file but intentionally omits
    # them from generated JSON. Every generated (current) symbol must match.
    require(set(parsed) == set(config) and
            all(type(parsed[key]) is type(value) and parsed[key] == value
                for key, value in config.items()),
            'Generated sdkconfig JSON does not match the actual sdkconfig text.')
    require(config.get('IDF_TARGET') == 'esp32' and config.get('IDF_TARGET_ARCH') == 'xtensa',
            'sdkconfig is not for ESP32 Xtensa.')
    require(config.get(BACKENDS[backend]) is True and
            all(config.get(key) is not True for name, key in BACKENDS.items() if name != backend),
            f'sdkconfig selected another audio backend; requested {backend}.')
    require(type(config.get('LWIP_SNTP_MAX_SERVERS')) is int and
            config['LWIP_SNTP_MAX_SERVERS'] >= 2,
            'CYD time settings require CONFIG_LWIP_SNTP_MAX_SERVERS >= 2.')
    flash = re.fullmatch(r'(\d+)MB', str(config.get('ESPTOOLPY_FLASHSIZE', '')))
    require(flash is not None, 'Missing configured flash size.')
    flash_bytes = int(flash[1]) * 1024 * 1024
    require(flash_bytes == 4 * 1024 * 1024, 'CYD production hardware profile expects 4 MiB flash.')

    image_path, elf_path = build_file(build, desc['app_bin']), build_file(build, desc['app_elf'])
    image, elf = image_path.read_bytes(), elf_path.read_bytes()
    require(len(elf) >= 52 and elf[:6] == b'\x7fELF\x01\x01' and
            struct.unpack_from('<H', elf, 18)[0] == 94, 'Application ELF is not 32-bit little-endian Xtensa.')
    app = image_descriptor(image)
    require(app['project_name'] == PROJECT_NAME, 'Image application descriptor names another project.')
    require(app['version'] == desc['project_version'], 'Image version differs from CMake project description.')
    require(snapshot['commit'][:8] in app['version'], 'Image version does not identify current source commit.')
    require(app['version'].endswith('-dirty') == snapshot['dirty'],
            'Image dirty marker does not match the source snapshot.')
    require(app['idf_version'] == IDF_VERSION, 'Image application descriptor used another ESP-IDF version.')
    require(app['elf_sha256'] == sha256(elf), 'Image embedded ELF SHA256 does not match the actual ELF.')
    partition_path = build_file(build, 'partition_table/partition-table.bin')
    slots = partition_slots(partition_path.read_bytes(), flash_bytes)
    require(all(len(image) <= slot['bytes'] for slot in slots), 'Application image exceeds an OTA slot.')
    flash_args = json.loads(build_file(build, 'flasher_args.json').read_text(encoding='utf-8'))
    require(flash_args.get('extra_esptool_args', {}).get('chip') == 'esp32', 'Flash recipe selects another chip.')
    require(int(flash_args['app']['offset'], 0) == slots[0]['offset'] and
            resolve_relative(flash_args['app']['file'], build) == image_path,
            'Flash recipe application does not match ota_0/image.')
    return {'image': image_path, 'elf': elf_path, 'config': config_path,
            'config_json': build / 'config/sdkconfig.json', 'partitions': partition_path,
            'description': description_path, 'flash_args': build / 'flasher_args.json',
            'details': {'target': 'esp32', 'backend': backend, 'idf_version': IDF_VERSION,
                        'app_version': app['version'], 'app_bytes': len(image),
                        'app_sha256': sha256(image), 'elf_sha256': sha256(elf),
                        'sdkconfig_sha256': sha256(config_text),
                        'sdkconfig_json_sha256': file_sha256(build / 'config/sdkconfig.json'),
                        'partition_table_sha256': file_sha256(partition_path),
                        'project_description_sha256': file_sha256(description_path),
                        'flasher_args_sha256': file_sha256(build / 'flasher_args.json'),
                        'ota_slots': slots, 'flash_bytes': flash_bytes,
                        'compiler': str(compiler), 'compiler_sha256': file_sha256(compiler),
                        'build_directory': str(build)}}


def archive_failure(out, build, error, snapshot):
    """Keep a successful but unqualified build away from the hand-off app.bin."""
    candidate = build / f'{PROJECT_NAME}.bin'
    if not candidate.is_file():
        return
    failure = out / 'failed-validation' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    failure.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(candidate, failure / 'unverified-app.bin')
    write_json(failure / 'validation-failure.json', {
        'build_check': 'FAILED', 'physical_tested': False, 'error': str(error),
        'source': snapshot, 'app_sha256': file_sha256(candidate), 'build_directory': str(build),
    })


def export(root, build, dependencies, backend, variant, out, snapshot, **options):
    # Validate before touching an existing development hand-off. Failed candidates
    # get an explicitly unverified archive rather than replacing its app.bin.
    require(out == destination(root, variant, out), 'Invalid development destination.')
    try:
        return _export(root, build, dependencies, backend, variant, out, snapshot, **options)
    except (OSError, ValueError, KeyError, ValidationError) as error:
        try:
            archive_failure(out, build, error, snapshot)
        except OSError as archive_error:
            print(f'Could not archive unverified candidate: {archive_error}', file=sys.stderr)
        raise


def _export(root, build, dependencies, backend, variant, out, snapshot, *, expected_config=None,
            evidence=(), build_logs=(), command=None, sdkconfig_seed=None):
    after_build = source_snapshot(root)
    # Actual Git dirty state can change when another backend's output is saved.
    # It is retained for descriptor provenance, but is not itself source content.
    require({key: value for key, value in after_build.items() if key != 'dirty'} ==
            {key: value for key, value in snapshot.items() if key != 'dirty'},
            'Source changed during the build/export.')
    if sdkconfig_seed and sdkconfig_seed['mode'] == 'copied-cyd-full-config':
        seed_path = Path(sdkconfig_seed['source_path'])
        require(seed_path.is_file() and file_sha256(seed_path) == sdkconfig_seed['source_sha256'],
                'CYD sdkconfig seed changed during the build (including ignored/generated seeds).')
    qualified = qualify(root, build, dependencies, backend, snapshot, expected_config)
    refs = []
    for reference in evidence:
        path = resolve_relative(reference, root)
        require(path.is_file(), f'Missing evidence file: {path}')
        refs.append({'path': str(path), 'sha256': file_sha256(path)})
    logs = [Path(p).resolve() for p in build_logs]
    require(all(path.is_file() for path in logs), 'A requested build log is missing.')
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.production-export-', dir=out) as temporary:
        stage = Path(temporary)
        copies = {'app.bin': qualified['image'], 'sdkconfig': qualified['config'],
                  'sdkconfig.json': qualified['config_json'], 'partition-table.bin': qualified['partitions'],
                  'project_description.json': qualified['description'], 'flasher_args.json': qualified['flash_args']}
        for name, path in copies.items():
            shutil.copyfile(path, stage / name)
        for name, field in [('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256'),
                            ('sdkconfig.json', 'sdkconfig_json_sha256'), ('partition-table.bin', 'partition_table_sha256'),
                            ('project_description.json', 'project_description_sha256'),
                            ('flasher_args.json', 'flasher_args_sha256')]:
            require(file_sha256(stage / name) == qualified['details'][field],
                    f'Build artifact changed during archival: {name}')
        log_entries = []
        for index, path in enumerate(logs):
            name = f'build-{index + 1}.log'
            shutil.copyfile(path, stage / name)
            log_entries.append({'file': name, 'original_path': str(path), 'sha256': file_sha256(stage / name)})
        manifest = dict(qualified['details'], variant=variant, source_commit=snapshot['commit'],
                        source_dirty=snapshot.get('source_dirty', snapshot['dirty']),
                        source_git_dirty=snapshot['dirty'], source_untracked=snapshot['untracked'],
                        source_git_dirty_after_build=after_build['dirty'],
                        source_excluded_paths=snapshot.get('excluded_paths', list(SOURCE_EXCLUSIONS)),
                        source_content_sha256=snapshot['content_sha256'], build_check='PASS',
                        physical_tested=False, created_utc=datetime.now(timezone.utc).isoformat(),
                        evidence=refs, build_logs=log_entries, build_command=command)
        manifest['sdkconfig_seed'] = sdkconfig_seed
        write_json(stage / 'manifest.json', manifest)
        # A manifest is the completion marker. An interrupted replacement must
        # never leave an older PASS manifest beside a newer application image.
        (out / 'manifest.json').unlink(missing_ok=True)
        for file in stage.iterdir():
            if file.name != 'manifest.json':
                os.replace(file, out / file.name)
        os.replace(stage / 'manifest.json', out / 'manifest.json')
    print(json.dumps(manifest, indent=2))
    return manifest


def preflight(dependencies, backend):
    required = [dependencies / 'v6.0.2/tools/idf.py', dependencies / 'v6.0.2/export.ps1',
                dependencies / 'v6.0.2/tools/cmake/version.cmake',
                dependencies / 'python-3.12.10/tools/python.exe', dependencies / 'tools-v6.0.2/idf-env.json',
                dependencies / 'esp-adf-libs/esp_audio_codec/CMakeLists.txt',
                dependencies / 'esp-adf-libs/esp_audio_codec/lib/esp32/libesp_audio_codec.a']
    if backend == 'legacy':
        required.append(dependencies / 'v5.5.4/components/driver/deprecated/i2s_legacy.c')
    require(all(path.is_file() for path in required),
            'Offline dependencies are incomplete; this wrapper will not invoke setup.ps1. Missing: ' +
            ', '.join(str(path) for path in required if not path.is_file()))
    version = required[2].read_text(encoding='utf-8')
    require(all(re.search(rf'set\(IDF_VERSION_{key}\s+{value}\)', version) for key, value in
                [('MAJOR', 6), ('MINOR', 0), ('PATCH', 2)]), 'Installed CYD ESP-IDF version is not 6.0.2.')


def build_command(root, dependencies, build, config, backend, powershell):
    return [str(powershell), '-NoProfile', '-NonInteractive', '-File', str(root / PROJECT / 'build.ps1'),
            '-DependencyRoot', str(dependencies), '-BuildDirectory', str(build),
            '-Sdkconfig', str(config), '-AudioBackend', backend]


def seed_configuration(root, config, backend):
    project = root / PROJECT
    defaults = [project / 'sdkconfig.defaults']
    if backend != 'pdm':
        defaults.append(project / ('sdkconfig.dac.defaults' if backend == 'continuous' else 'sdkconfig.legacy-dac.defaults'))
    require(all(path.is_file() for path in defaults), 'CYD sdkconfig defaults are missing.')
    result = {'defaults': [{'path': str(path), 'sha256': file_sha256(path)} for path in defaults]}
    if config.is_file():
        return dict(result, mode='existing-isolated-config', source_path=str(config), source_sha256=file_sha256(config))
    seed = project / {'pdm': 'sdkconfig', 'continuous': 'sdkconfig.dac', 'legacy': 'sdkconfig.legacy-dac'}[backend]
    if not seed.is_file():
        return dict(result, mode='cyd-defaults', source_path=None, source_sha256=None)
    contents = seed.read_bytes()
    selected = parse_sdkconfig(contents.decode('utf-8').split('# Deprecated options for backward compatibility', 1)[0])
    require(selected.get('IDF_TARGET') == 'esp32', 'Full sdkconfig seed is not a CYD ESP32 configuration.')
    require(selected.get(BACKENDS[backend]) is True and
            all(selected.get(key) is not True for name, key in BACKENDS.items() if name != backend),
            'Full CYD sdkconfig seed selects a different audio backend.')
    config.parent.mkdir(parents=True, exist_ok=True)
    # Read and copy one byte sequence: an ignored/generated seed is still an
    # identified build input and is checked again before final publication.
    with config.open('xb') as output:
        output.write(contents)
    return dict(result, mode='copied-cyd-full-config', source_path=str(seed), source_sha256=sha256(contents))


def apply_time_capacity(config):
    """Upgrade only an isolated build config to support both desired servers."""
    if not config.is_file():
        return {'minimum_servers': 2, 'mode': 'cyd-defaults', 'changed': False}
    original = config.read_bytes()
    text = original.decode('utf-8')
    current = parse_sdkconfig(text.split('# Deprecated options for backward compatibility', 1)[0]).get('LWIP_SNTP_MAX_SERVERS')
    require(current is None or (type(current) is int and current >= 1),
            'Invalid CONFIG_LWIP_SNTP_MAX_SERVERS in isolated build configuration.')
    result = {'minimum_servers': 2, 'previous': current, 'changed': current is None or current < 2}
    if not result['changed']:
        return result
    newline = '\r\n' if b'\r\n' in original else '\n'
    pattern = r'(?m)^(?:CONFIG_LWIP_SNTP_MAX_SERVERS=[^\r\n]*|# CONFIG_LWIP_SNTP_MAX_SERVERS is not set)\r?$'
    replacement = 'CONFIG_LWIP_SNTP_MAX_SERVERS=2'
    if re.search(pattern, text):
        text = re.sub(pattern, replacement + ('\r' if newline == '\r\n' else ''), text)
    else:
        # Put a new current option before IDF's compatibility-only tail.
        marker = '# Deprecated options for backward compatibility'
        at = text.find(marker)
        prefix, tail = (text[:at], text[at:]) if at >= 0 else (text, '')
        text = prefix + ('' if not prefix or prefix.endswith('\n') else newline) + replacement + newline + tail
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=config.parent, prefix='.time-config-', delete=False) as output:
            temporary = Path(output.name)
            output.write(text.encode('utf-8'))
        os.replace(temporary, config)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return result


def build_production(root, dependencies, build, config, backend, variant, out, powershell, *,
                     allow_dirty=False, evidence=()):
    preflight(dependencies, backend)
    require(Path(powershell).is_file(), 'PowerShell executable does not exist.')
    require(not config.exists() or config.is_file(), 'sdkconfig path is not a regular file.')
    # Avoid mutating tracked baseline configurations or importing C3 defaults.
    require(config.resolve().is_relative_to(build.resolve()),
            'Production sdkconfig must be inside its isolated build directory.')
    require(build not in (root, root / PROJECT, root / PROJECT / 'main'),
            'Use an isolated production build directory rather than a source directory.')
    cache = (build / 'CMakeCache.txt').read_text(encoding='utf-8', errors='replace') if (build / 'CMakeCache.txt').is_file() else ''
    require(not re.search(r'(?mi)^(?:IDF_TOOLCHAIN|CMAKE_(?:C|CXX)_COMPILER)(?::[^=]*)?=.*clang', cache),
            'Use a fresh GCC build directory; this directory contains a Clang configuration.')
    snapshot = source_snapshot(root)
    check_source(snapshot, allow_dirty)
    log_dir = root / '.build/production-wrapper' / variant / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    log_dir.mkdir(parents=True, exist_ok=False)
    command = build_command(root, dependencies, build, config, backend, powershell)
    write_json(log_dir / 'source.json', snapshot)
    write_json(log_dir / 'command.json', command)
    config_seed = seed_configuration(root, config, backend)
    config_seed['time_capacity'] = apply_time_capacity(config)
    write_json(log_dir / 'sdkconfig-seed.json', config_seed)
    stdout_path, stderr_path = log_dir / 'stdout.log', log_dir / 'stderr.log'
    environment = os.environ.copy()
    environment['IDF_TOOLCHAIN'] = 'gcc'
    environment['IDF_COMPONENT_MANAGER'] = '0'
    print(f'Building {backend}; logs: {log_dir}', flush=True)
    # An exit in build.ps1 or export.ps1 exits only this child. Argument vectors
    # preserve spaces and shell metacharacters without constructing shell code.
    with stdout_path.open('wb') as stdout, stderr_path.open('wb') as stderr:
        result = subprocess.run(command, cwd=root, env=environment, stdout=stdout, stderr=stderr, check=False)
    require(result.returncode == 0,
            f'CYD build failed with exit {result.returncode}; see {stdout_path} and {stderr_path}.')
    return export(root, build, dependencies, backend, variant, out, snapshot, expected_config=config,
                  evidence=evidence, build_logs=(stdout_path, stderr_path), command=command,
                  sdkconfig_seed=config_seed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'export'))
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--dependency-root', type=Path, required=True)
    parser.add_argument('--backend', choices=BACKENDS, default='pdm')
    parser.add_argument('--build-dir', type=Path)
    parser.add_argument('--sdkconfig', type=Path)
    parser.add_argument('--variant')
    parser.add_argument('--output-directory', type=Path)
    parser.add_argument('--powershell', type=Path)
    parser.add_argument('--allow-dirty', action='store_true')
    parser.add_argument('--evidence', action='append', default=[])
    parser.add_argument('--build-log', action='append', type=Path, default=[])
    args = parser.parse_args(argv)
    root, dependencies = args.repository.resolve(), args.dependency_root.resolve()
    variant = args.variant or f'esp32-cyd2usb-native-production-{args.backend}'
    build = resolve_relative(args.build_dir or f'build-production-{args.backend}', root / PROJECT)
    config = resolve_relative(args.sdkconfig, root / PROJECT) if args.sdkconfig else build / 'sdkconfig'
    out = destination(root, variant, args.output_directory)
    if args.command == 'build':
        require(args.powershell is not None, 'The build command needs --powershell (PowerShell 7 executable).')
        build_production(root, dependencies, build, config, args.backend, variant, out, args.powershell,
                         allow_dirty=args.allow_dirty, evidence=args.evidence)
    else:
        snapshot = source_snapshot(root)
        check_source(snapshot, args.allow_dirty)
        export(root, build, dependencies, args.backend, variant, out, snapshot,
               expected_config=config if args.sdkconfig else None,
               evidence=args.evidence, build_logs=args.build_log)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, ValidationError) as error:
        print(f'CYD production error: {error}', file=sys.stderr)
        sys.exit(1)

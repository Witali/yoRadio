"""Qualify deterministic ESP32 image/config/ELF fixtures and production orchestration.

This exercises the real exporter and a real child-process exit, with only Git
identity and the external IDF builder replaced. It never builds or flashes IDF.
"""
import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/export_cyd_production.py'
SPEC = importlib.util.spec_from_file_location('cyd_production', TOOL)
production = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(production)
OUTPUT = ROOT / '.build/production-wrapper-tests'
COMMIT = '0123456789abcdef0123456789abcdef01234567'


class Fixture:
    def __init__(self, root):
        self.root = root
        self.project = root / production.PROJECT
        self.build = self.project / 'build with spaces'
        self.dependencies = root / 'installed dependencies'
        self.out = root / 'firmware/development/test-pdm'
        self.config = self.build / 'sdkconfig'
        self.snapshot = {'commit': COMMIT, 'dirty': False, 'untracked': [], 'content_sha256': 'a' * 64}
        self.build.mkdir(parents=True)
        (self.build / 'config').mkdir()
        (self.build / 'partition_table').mkdir()
        self.compiler = self.dependencies / 'tools-v6.0.2/tools/xtensa-esp-elf/test/bin/xtensa-esp32-elf-gcc.exe'
        files = {
            'v6.0.2/tools/idf.py': '# installed fixture only\n',
            'v6.0.2/export.ps1': '# installed fixture only\n',
            'v6.0.2/tools/cmake/version.cmake': 'set(IDF_VERSION_MAJOR 6)\nset(IDF_VERSION_MINOR 0)\nset(IDF_VERSION_PATCH 2)\n',
            'python-3.12.10/tools/python.exe': 'fixture',
            'tools-v6.0.2/idf-env.json': '{}',
            'esp-adf-libs/esp_audio_codec/CMakeLists.txt': '# fixture',
            'esp-adf-libs/esp_audio_codec/lib/esp32/libesp_audio_codec.a': 'fixture',
            'v5.5.4/components/driver/deprecated/i2s_legacy.c': '/* fixture */',
        }
        for relative, content in files.items():
            path = self.dependencies / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')
        self.compiler.parent.mkdir(parents=True, exist_ok=True)
        self.compiler.write_bytes(b'fixture compiler identity')
        self.elf = bytearray(52)
        self.elf[:6] = b'\x7fELF\x01\x01'
        struct.pack_into('<H', self.elf, 18, 94)
        self.elf_path = self.build / f'{production.PROJECT_NAME}.elf'
        self.elf_path.write_bytes(self.elf)
        self.image_path = self.build / f'{production.PROJECT_NAME}.bin'
        self.description = {
            'target': 'esp32', 'project_name': production.PROJECT_NAME,
            'project_version': f'v0.1-g{COMMIT[:8]}', 'git_revision': 'v6.0.2',
            'project_path': str(self.project), 'build_dir': str(self.build),
            'idf_path': str(self.dependencies / 'v6.0.2'), 'c_compiler': str(self.compiler),
            'config_file': str(self.config), 'app_bin': self.image_path.name, 'app_elf': self.elf_path.name,
        }
        self.settings = {'IDF_TARGET': 'esp32', 'IDF_TARGET_ARCH': 'xtensa', 'ESPTOOLPY_FLASHSIZE': '4MB'}
        self.backend('pdm')
        (self.project / 'sdkconfig.defaults').write_bytes(self.config.read_bytes())
        (self.project / 'sdkconfig.dac.defaults').write_text('CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_DAC=y\n')
        (self.project / 'sdkconfig.legacy-dac.defaults').write_text('CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_LEGACY_DAC=y\n')
        self.write_description()
        self.write_image()
        self.write_partitions()
        production.write_json(self.build / 'flasher_args.json', {
            'extra_esptool_args': {'chip': 'esp32'},
            'app': {'offset': '0x10000', 'file': self.image_path.name},
        })

    def backend(self, backend):
        self.settings.update({key: name == backend for name, key in production.BACKENDS.items()})
        self.write_config()

    def write_config(self):
        lines = []
        for key, value in self.settings.items():
            if value is False:
                lines.append(f'# CONFIG_{key} is not set')
            else:
                lines.append(f'CONFIG_{key}=' + ('y' if value is True else json.dumps(value)))
        # Real IDF text includes compatibility aliases omitted from JSON.
        lines += ['# Deprecated options for backward compatibility', 'CONFIG_DEPRECATED_COMPAT_ALIAS=y']
        self.config.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        production.write_json(self.build / 'config/sdkconfig.json', self.settings)

    def write_description(self):
        production.write_json(self.build / 'project_description.json', self.description)

    def write_image(self, *, payload_size=512, chip=0, version=None, elf_hash=None, idf_version='v6.0.2'):
        header = bytearray(24)
        header[0:2] = bytes([0xE9, 1])
        struct.pack_into('<H', header, 12, chip)
        header[23] = 1
        payload = bytearray(payload_size)
        struct.pack_into('<I', payload, 0, 0xABCD5432)
        for offset, value in ((16, version or self.description['project_version']),
                              (48, production.PROJECT_NAME), (112, idf_version)):
            encoded = value.encode('utf-8')
            payload[offset:offset + len(encoded)] = encoded
        payload[144:176] = elf_hash or hashlib.sha256(self.elf_path.read_bytes()).digest()
        image = header + struct.pack('<II', 0x3F400020, len(payload)) + payload
        checksum = 0xEF
        for value in payload:
            checksum ^= value
        image.extend(bytes((-(len(image) + 1)) % 16))
        image.append(checksum)
        image.extend(hashlib.sha256(image).digest())
        self.image_path.write_bytes(image)

    def write_partitions(self, sizes=(0x1B0000, 0x1B0000), second_address=0x1C0000):
        data = bytearray()
        for subtype, address, size, name in ((0x10, 0x10000, sizes[0], b'app0'),
                                              (0x11, second_address, sizes[1], b'app1')):
            data.extend(struct.pack('<HBBII16sI', 0x50AA, 0, subtype, address, size, name, 0))
        data.extend(b'\xeb\xeb' + b'\xff' * 14 + hashlib.md5(data).digest())
        data.extend(b'\xff' * 32)
        (self.build / 'partition_table/partition-table.bin').write_bytes(data)

    def qualify(self, backend='pdm'):
        return production.qualify(self.root, self.build, self.dependencies, backend,
                                  self.snapshot, expected_config=self.config)

    def export(self, **kwargs):
        with patch.object(production, 'source_snapshot', return_value=self.snapshot), contextlib.redirect_stdout(io.StringIO()):
            return production.export(self.root, self.build, self.dependencies, 'pdm', 'test-pdm',
                                     self.out, self.snapshot, expected_config=self.config, **kwargs)


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='case-', dir=OUTPUT)
        self.addCleanup(self.temporary.cleanup)
        self.fixture = Fixture(Path(self.temporary.name))

    def reject(self, message, backend='pdm'):
        with self.assertRaisesRegex(production.ValidationError, message):
            self.fixture.qualify(backend)

    def test_all_three_backend_profiles_accept_only_their_own_selection(self):
        for selected in production.BACKENDS:
            self.fixture.backend(selected)
            self.assertEqual(self.fixture.qualify(selected)['details']['backend'], selected)
            for requested in production.BACKENDS:
                if requested != selected:
                    self.reject('another audio backend', requested)

    def test_archive_has_verified_hashes_source_config_and_both_ota_limits(self):
        evidence = self.fixture.root / 'evidence.txt'
        evidence.write_text('Host-only fixture evidence; physical testing pending.', encoding='utf-8')
        log = self.fixture.root / 'builder.log'
        log.write_text('fixture child complete\n', encoding='utf-8')
        manifest = self.fixture.export(evidence=[evidence], build_logs=[log])
        for name, field in [('app.bin', 'app_sha256'), ('sdkconfig', 'sdkconfig_sha256'),
                            ('sdkconfig.json', 'sdkconfig_json_sha256'), ('partition-table.bin', 'partition_table_sha256')]:
            self.assertEqual(production.file_sha256(self.fixture.out / name), manifest[field])
        self.assertEqual(manifest['source_commit'], COMMIT)
        self.assertFalse(manifest['source_dirty'])
        self.assertFalse(manifest['physical_tested'])
        self.assertEqual(manifest['build_check'], 'PASS')
        self.assertEqual([slot['bytes'] for slot in manifest['ota_slots']], [0x1B0000, 0x1B0000])
        self.assertEqual((self.fixture.out / 'build-1.log').read_bytes(), log.read_bytes())

    def test_failure_keeps_existing_handoff_and_archives_candidate_as_unverified(self):
        old = self.fixture.export()
        old_app = (self.fixture.out / 'app.bin').read_bytes()
        self.fixture.write_image(chip=5)
        with self.assertRaisesRegex(production.ValidationError, 'chip ID'):
            self.fixture.export()
        self.assertEqual((self.fixture.out / 'app.bin').read_bytes(), old_app)
        self.assertEqual(json.loads((self.fixture.out / 'manifest.json').read_text()), old)
        failures = list((self.fixture.out / 'failed-validation').glob('*/validation-failure.json'))
        self.assertEqual(len(failures), 1)
        self.assertEqual(json.loads(failures[0].read_text())['build_check'], 'FAILED')
        self.assertTrue((failures[0].parent / 'unverified-app.bin').is_file())

    def test_changed_artifact_between_qualification_and_copy_cannot_publish_pass(self):
        original_copy = shutil.copyfile

        def mutate_on_copy(source, target, *args, **kwargs):
            result = original_copy(source, target, *args, **kwargs)
            if Path(target).name == 'app.bin':
                with Path(target).open('ab') as changed:
                    changed.write(b'changed during copy')
            return result

        with patch.object(production.shutil, 'copyfile', side_effect=mutate_on_copy):
            with self.assertRaisesRegex(production.ValidationError, 'changed during archival'):
                self.fixture.export()
        self.assertFalse((self.fixture.out / 'manifest.json').exists())

    def test_build_target_c3_is_rejected(self):
        self.fixture.description['target'] = 'esp32c3'
        self.fixture.write_description()
        self.reject('target is not ESP32')

    def test_image_chip_c3_is_rejected_even_when_description_says_esp32(self):
        self.fixture.write_image(chip=5)
        self.reject('chip ID')

    def test_wrong_idf_description_and_image_are_rejected(self):
        self.fixture.description['git_revision'] = 'v6.1'
        self.fixture.write_description()
        self.reject('pinned IDF')
        self.fixture.description['git_revision'] = 'v6.0.2'
        self.fixture.write_description()
        self.fixture.write_image(idf_version='v6.1')
        self.reject('another ESP-IDF')

    def test_wrong_worktree_or_dependency_root_is_rejected(self):
        self.fixture.description['project_path'] = str(self.fixture.root / 'another checkout')
        self.fixture.write_description()
        self.reject('another project/worktree')
        self.fixture.description['project_path'] = str(self.fixture.project)
        self.fixture.description['idf_path'] = str(self.fixture.dependencies / 'v6.1')
        self.fixture.write_description()
        self.reject('another ESP-IDF dependency root')

    def test_config_target_or_json_disagreement_is_rejected(self):
        self.fixture.settings['IDF_TARGET'] = 'esp32c3'
        self.fixture.write_config()
        self.reject('not for ESP32 Xtensa')
        self.fixture.settings['IDF_TARGET'] = 'esp32'
        self.fixture.write_config()
        self.fixture.config.write_text(self.fixture.config.read_text().replace('CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM=y',
                                                                             '# CONFIG_YORADIO_NATIVE_AUDIO_OUTPUT_PDM is not set'))
        self.reject('does not match')

    def test_two_audio_backends_are_rejected(self):
        self.fixture.settings[production.BACKENDS['legacy']] = True
        self.fixture.write_config()
        self.reject('another audio backend')

    def test_current_config_symbol_missing_from_generated_json_is_rejected(self):
        self.fixture.config.write_text('CONFIG_NEW_FEATURE=y\n' + self.fixture.config.read_text())
        self.reject('does not match')

    def test_requested_sdkconfig_identity_is_checked(self):
        other = self.fixture.build / 'other-sdkconfig'
        other.write_bytes(self.fixture.config.read_bytes())
        self.fixture.description['config_file'] = str(other)
        self.fixture.write_description()
        self.reject('different sdkconfig')

    def test_bad_elf_architecture_or_embedded_digest_is_rejected(self):
        self.fixture.elf_path.write_bytes(self.fixture.elf_path.read_bytes() + b'new ELF')
        self.reject('embedded ELF SHA256')
        self.fixture.write_image()
        bad = bytearray(self.fixture.elf_path.read_bytes())
        struct.pack_into('<H', bad, 18, 243)  # RISC-V, rather than Xtensa.
        self.fixture.elf_path.write_bytes(bad)
        self.fixture.write_image()
        self.reject('not 32-bit little-endian Xtensa')

    def test_image_checksum_and_sha_corruption_are_rejected(self):
        bad = bytearray(self.fixture.image_path.read_bytes())
        bad[400] ^= 1
        self.fixture.image_path.write_bytes(bad)
        self.reject('segment checksum')
        self.fixture.write_image()
        bad = bytearray(self.fixture.image_path.read_bytes())
        bad[-1] ^= 1
        self.fixture.image_path.write_bytes(bad)
        self.reject('SHA256 checksum')

    def test_version_must_match_both_description_and_current_commit(self):
        self.fixture.write_image(version='v0.1-gdeadbeef')
        self.reject('version differs')
        self.fixture.description['project_version'] = 'v0.1-gdeadbeef'
        self.fixture.write_description()
        self.reject('current source commit')

    def test_dirty_marker_is_verified_and_explicit_dirty_snapshot_is_recordable(self):
        self.fixture.snapshot['dirty'] = True
        self.reject('dirty marker')
        with self.assertRaisesRegex(production.ValidationError, 'Commit source'):
            production.check_source(self.fixture.snapshot, False)
        production.check_source(self.fixture.snapshot, True)
        self.fixture.description['project_version'] += '-dirty'
        self.fixture.write_description()
        self.fixture.write_image()
        self.assertTrue(self.fixture.export()['source_dirty'])

    def test_untracked_source_requires_explicit_dirty_permission(self):
        snapshot = dict(self.fixture.snapshot, untracked=['main/new_file.c'])
        with self.assertRaisesRegex(production.ValidationError, 'Commit source'):
            production.check_source(snapshot, False)
        production.check_source(snapshot, True)

    def source_git_fixture(self):
        names = ['idf/esp32-cyd2usb-native/main/app.c', 'idf/components/shared/helper.c',
                 'data/index.html', 'firmware/v1.0/immutable-release.bin',
                 'firmware/development/old/app.bin', 'tests/results/old/report.json']
        for name in names:
            path = self.fixture.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('fixture source ' + name, encoding='utf-8')
        entries = b''.join(b'100644 ' + hashlib.sha1(name.encode()).hexdigest().encode() +
                           b' 0\t' + name.encode() + b'\0' for name in names)
        changed, extra_source = set(), set()

        def git_fixture(root, *arguments):
            if arguments == ('rev-parse', 'HEAD'):
                return COMMIT.encode() + b'\n'
            if arguments == ('diff', '--name-only', 'HEAD', '-z'):
                return b''.join(name.encode() + b'\0' for name in sorted(changed))
            if arguments == ('ls-files', '--stage', '-z'):
                return entries
            if arguments == ('ls-files', '--others', '--exclude-standard', '-z'):
                generated = {str(path.relative_to(root)).replace('\\', '/')
                             for prefix in production.SOURCE_EXCLUSIONS
                             for path in (root / prefix).rglob('*') if path.is_file()}
                return b''.join(name.encode() + b'\0' for name in sorted((generated - set(names)) | extra_source))
            raise AssertionError(arguments)

        return patch.object(production, 'git', side_effect=git_fixture), changed, extra_source

    def test_sequential_generated_exports_preserve_source_identity_and_allow_the_next_build(self):
        git_fixture, changed, _ = self.source_git_fixture()
        with git_fixture, contextlib.redirect_stdout(io.StringIO()):
            before = production.source_snapshot(self.fixture.root)
            production.export(self.fixture.root, self.fixture.build, self.fixture.dependencies, 'pdm', 'test-pdm',
                              self.fixture.out, before, expected_config=self.fixture.config)
            (self.fixture.root / 'tests/results/new').mkdir(parents=True)
            (self.fixture.root / 'tests/results/new/report.json').write_text('{"status":"PASS"}')
            changed.update(['firmware/development/old/app.bin', 'tests/results/old/report.json'])
            after = production.source_snapshot(self.fixture.root)
            self.assertEqual(before['content_sha256'], after['content_sha256'])
            self.assertFalse(after['source_dirty'])
            self.assertTrue(after['dirty'])  # Actual Git/descriptor state remains visible.
            self.assertEqual(after['untracked'], [])
            production.check_source(after, False)
            self.fixture.description['project_version'] += '-dirty'
            self.fixture.write_description()
            self.fixture.write_image()
            manifest = production.export(self.fixture.root, self.fixture.build, self.fixture.dependencies, 'pdm',
                                         'second-profile', self.fixture.out.parent / 'second-profile', after,
                                         expected_config=self.fixture.config)
            self.assertFalse(manifest['source_dirty'])
            self.assertTrue(manifest['source_git_dirty'])
            self.assertEqual(manifest['source_excluded_paths'], list(production.SOURCE_EXCLUSIONS))

    def test_changed_and_new_application_component_and_web_sources_remain_detected(self):
        git_fixture, changed, extra_source = self.source_git_fixture()
        with git_fixture:
            baseline = production.source_snapshot(self.fixture.root)
            for name in ['idf/esp32-cyd2usb-native/main/app.c', 'idf/components/shared/helper.c', 'data/index.html']:
                with self.subTest(changed=name):
                    changed.add(name)
                    path = self.fixture.root / name
                    path.write_text(path.read_text() + ' changed')
                    snapshot = production.source_snapshot(self.fixture.root)
                    self.assertNotEqual(snapshot['content_sha256'], baseline['content_sha256'])
                    with self.assertRaisesRegex(production.ValidationError, 'Commit source'):
                        production.check_source(snapshot, False)
                    changed.clear()
            for name in ['idf/esp32-cyd2usb-native/main/new.c', 'idf/components/shared/new.c', 'data/new.html']:
                with self.subTest(untracked=name):
                    (self.fixture.root / name).write_text('new source')
                    extra_source.add(name)
                    snapshot = production.source_snapshot(self.fixture.root)
                    self.assertIn(name, snapshot['untracked'])
                    with self.assertRaisesRegex(production.ValidationError, 'Commit source'):
                        production.check_source(snapshot, False)
                    extra_source.clear()

    def test_clean_immutable_firmware_uses_git_identity_without_reading_binary_contents(self):
        git_fixture, _, _ = self.source_git_fixture()
        with git_fixture, patch.object(production, 'file_sha256', side_effect=AssertionError('Unexpected working-file read')):
            snapshot = production.source_snapshot(self.fixture.root)
        self.assertFalse(snapshot['source_dirty'])

    def test_source_change_during_build_never_gets_pass_manifest(self):
        changed = dict(self.fixture.snapshot, content_sha256='b' * 64)
        with patch.object(production, 'source_snapshot', return_value=changed):
            with self.assertRaisesRegex(production.ValidationError, 'Source changed'):
                production.export(self.fixture.root, self.fixture.build, self.fixture.dependencies, 'pdm',
                                  'test-pdm', self.fixture.out, self.fixture.snapshot)
        self.assertFalse((self.fixture.out / 'manifest.json').exists())

    def test_smaller_second_ota_slot_is_enforced(self):
        self.fixture.write_partitions(sizes=(0x1B0000, 256))
        self.reject('exceeds an OTA slot')

    def test_overlapping_and_corrupted_partition_tables_are_rejected(self):
        self.fixture.write_partitions(second_address=0x20000)
        self.reject('Overlapping partitions')
        self.fixture.write_partitions()
        path = self.fixture.build / 'partition_table/partition-table.bin'
        bad = bytearray(path.read_bytes())
        bad[90] ^= 1
        path.write_bytes(bad)
        self.reject('Partition table MD5')

    def test_flash_recipe_wrong_app_offset_is_rejected(self):
        path = self.fixture.build / 'flasher_args.json'
        recipe = json.loads(path.read_text())
        recipe['app']['offset'] = '0x1c0000'
        production.write_json(path, recipe)
        self.reject('Flash recipe application')

    def test_clang_or_unpinned_compiler_is_rejected(self):
        self.fixture.description['c_compiler'] = str(self.fixture.compiler.with_name('clang.exe'))
        self.fixture.write_description()
        self.reject('not ESP32 Xtensa GCC')
        self.fixture.description['c_compiler'] = str(self.fixture.root / self.fixture.compiler.name)
        self.fixture.write_description()
        self.reject('pinned CYD tools')

    def test_versioned_release_and_parent_destinations_are_protected(self):
        for path in ('firmware/v1.0/test', 'firmware/development', 'firmware/development/../v1.0/test'):
            with self.assertRaisesRegex(production.ValidationError, 'inside firmware/development'):
                production.destination(self.fixture.root, 'test', path)
        for variant in ('../release', '.', 'test/path'):
            with self.assertRaises(production.ValidationError):
                production.destination(self.fixture.root, variant)

    def test_artifact_path_escape_is_rejected(self):
        self.fixture.description['app_bin'] = '../outside.bin'
        self.fixture.write_description()
        self.reject('escapes its build directory')

    def test_development_symlink_cannot_redirect_archive_to_a_release(self):
        release = self.fixture.root / 'firmware/v1.0'
        release.mkdir(parents=True)
        try:
            (release.parent / 'development').symlink_to(release, target_is_directory=True)
        except OSError:
            self.skipTest('Creating directory symlinks is unavailable on this host.')
        with self.assertRaisesRegex(production.ValidationError, 'must not redirect'):
            production.destination(self.fixture.root, 'test')

    def test_missing_dependency_preflight_never_starts_a_builder(self):
        (self.fixture.dependencies / 'v6.0.2/tools/idf.py').unlink()
        with patch.object(production.subprocess, 'run') as runner:
            with self.assertRaisesRegex(production.ValidationError, 'will not invoke setup'):
                production.build_production(self.fixture.root, self.fixture.dependencies, self.fixture.build,
                                            self.fixture.config, 'pdm', 'test-pdm', self.fixture.out, Path(sys.executable))
        runner.assert_not_called()

    def test_legacy_requires_its_own_installed_driver(self):
        (self.fixture.dependencies / 'v5.5.4/components/driver/deprecated/i2s_legacy.c').unlink()
        production.preflight(self.fixture.dependencies, 'pdm')
        with self.assertRaisesRegex(production.ValidationError, 'i2s_legacy.c'):
            production.preflight(self.fixture.dependencies, 'legacy')

    def test_each_cyd_full_profile_seeds_missing_config_without_losing_tuning(self):
        profiles = {'pdm': 'sdkconfig', 'continuous': 'sdkconfig.dac', 'legacy': 'sdkconfig.legacy-dac'}
        for backend, name in profiles.items():
            with self.subTest(backend=backend):
                self.fixture.backend(backend)
                contents = self.fixture.config.read_bytes() + b'CONFIG_BOARD_SPECIFIC_TUNING=217\n'
                seed = self.fixture.project / name
                seed.write_bytes(contents)
                self.fixture.config.unlink()
                result = production.seed_configuration(self.fixture.root, self.fixture.config, backend)
                self.assertEqual(result['mode'], 'copied-cyd-full-config')
                self.assertEqual(self.fixture.config.read_bytes(), contents)
                self.assertEqual(result['source_sha256'], hashlib.sha256(contents).hexdigest())
                self.assertEqual(result['source_path'], str(seed))
                self.assertEqual(seed.read_bytes(), contents)

    def test_existing_isolated_sdkconfig_is_never_replaced_by_a_full_profile(self):
        original = self.fixture.config.read_bytes()
        (self.fixture.project / 'sdkconfig').write_bytes(b'CONFIG_DO_NOT_IMPORT_THIS=999\n')
        result = production.seed_configuration(self.fixture.root, self.fixture.config, 'pdm')
        self.assertEqual(result['mode'], 'existing-isolated-config')
        self.assertEqual(self.fixture.config.read_bytes(), original)

    def test_clean_clone_without_full_config_uses_only_cyd_backend_defaults(self):
        self.fixture.config.unlink()
        result = production.seed_configuration(self.fixture.root, self.fixture.config, 'continuous')
        self.assertEqual(result['mode'], 'cyd-defaults')
        self.assertFalse(self.fixture.config.exists())
        self.assertEqual([Path(item['path']).name for item in result['defaults']],
                         ['sdkconfig.defaults', 'sdkconfig.dac.defaults'])

    def test_c3_or_wrong_backend_full_config_cannot_be_imported_as_a_cyd_seed(self):
        self.fixture.settings['IDF_TARGET'] = 'esp32c3'
        self.fixture.write_config()
        seed = self.fixture.project / 'sdkconfig'
        seed.write_bytes(self.fixture.config.read_bytes())
        self.fixture.config.unlink()
        with self.assertRaisesRegex(production.ValidationError, 'not a CYD ESP32'):
            production.seed_configuration(self.fixture.root, self.fixture.config, 'pdm')
        self.fixture.settings['IDF_TARGET'] = 'esp32'
        self.fixture.backend('legacy')
        seed.write_bytes(self.fixture.config.read_bytes())
        self.fixture.config.unlink()
        with self.assertRaisesRegex(production.ValidationError, 'different audio backend'):
            production.seed_configuration(self.fixture.root, self.fixture.config, 'pdm')

    def test_ignored_full_seed_changed_during_build_is_rejected(self):
        seed = self.fixture.project / 'sdkconfig'
        seed.write_bytes(self.fixture.config.read_bytes())
        self.fixture.config.unlink()
        provenance = production.seed_configuration(self.fixture.root, self.fixture.config, 'pdm')
        seed.write_bytes(seed.read_bytes() + b'# changed ignored seed\n')
        with self.assertRaisesRegex(production.ValidationError, 'seed changed during the build'):
            self.fixture.export(sdkconfig_seed=provenance)
        self.assertFalse((self.fixture.out / 'manifest.json').exists())

    def child(self, exit_code):
        script = self.fixture.root / 'child with spaces.py'
        script.write_text('import sys\nprint("child build completed")\nprint(sys.argv[1])\nsys.exit(' + str(exit_code) + ')\n',
                          encoding='utf-8')
        command = [sys.executable, str(script), 'literal path ; $() with spaces']
        with patch.object(production, 'source_snapshot', return_value=self.fixture.snapshot), \
                patch.object(production, 'build_command', return_value=command), contextlib.redirect_stdout(io.StringIO()):
            return production.build_production(self.fixture.root, self.fixture.dependencies, self.fixture.build,
                                               self.fixture.config, 'pdm', 'test-pdm', self.fixture.out, Path(sys.executable))

    def test_child_exit_zero_still_runs_real_export_and_archives_its_logs(self):
        manifest = self.child(0)
        log = self.fixture.out / manifest['build_logs'][0]['file']
        self.assertIn('literal path ; $() with spaces', log.read_text())
        self.assertEqual(manifest['build_check'], 'PASS')

    def test_nonzero_child_exit_cannot_publish_a_previous_image(self):
        with self.assertRaisesRegex(production.ValidationError, 'exit 7'):
            self.child(7)
        self.assertFalse((self.fixture.out / 'app.bin').exists())

    def test_isolated_configs_cannot_mutate_tracked_baseline(self):
        with self.assertRaisesRegex(production.ValidationError, 'inside its isolated build directory'):
            production.build_production(self.fixture.root, self.fixture.dependencies, self.fixture.build,
                                        self.fixture.project / 'sdkconfig', 'pdm', 'test-pdm',
                                        self.fixture.out, Path(sys.executable))

    def test_powershell_frontend_forwards_options_without_shell_interpretation(self):
        powershell = shutil.which('pwsh')
        dependencies = next((ancestor / '.idf' for ancestor in [ROOT, *ROOT.parents]
                             if (ancestor / '.idf/python-3.12.10/tools/python.exe').is_file()), None)
        if not powershell or dependencies is None or os.name != 'nt':
            self.skipTest('PowerShell 7 and installed Windows bootstrap Python are required for this frontend test.')
        self.fixture.project.mkdir(exist_ok=True)
        frontend = self.fixture.project / 'build-production.ps1'
        shutil.copyfile(ROOT / production.PROJECT / 'build-production.ps1', frontend)
        tools = self.fixture.root / 'tools'
        tools.mkdir()
        capture = self.fixture.root / 'forwarded.json'
        (tools / TOOL.name).write_text(
            'import json,pathlib,sys\npathlib.Path(__file__).resolve().parents[1].joinpath("forwarded.json").write_text(json.dumps(sys.argv[1:]))\n',
            encoding='utf-8')
        result = subprocess.run([powershell, '-NoProfile', '-NonInteractive', '-File', str(frontend),
                                 '-DependencyRoot', str(dependencies), '-AudioBackend', 'legacy',
                                 '-BuildDirectory', 'space ; $() directory', '-Sdkconfig', 'space config',
                                 '-Variant', 'test-variant', '-FirmwareOutputDirectory', 'firmware/development/test',
                                 '-Evidence', 'evidence with spaces.md', '-AllowDirty'],
                                cwd=self.fixture.root, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        forwarded = json.loads(capture.read_text())
        self.assertEqual(forwarded[0], 'build')
        for flag, value in [('--backend', 'legacy'), ('--build-dir', 'space ; $() directory'),
                            ('--sdkconfig', 'space config'), ('--variant', 'test-variant'),
                            ('--output-directory', 'firmware/development/test'),
                            ('--evidence', 'evidence with spaces.md')]:
            self.assertEqual(forwarded[forwarded.index(flag) + 1], value)
        self.assertIn('--allow-dirty', forwarded)


def main():
    global OUTPUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    OUTPUT = args.output.resolve()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProductionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    report = {'status': 'PASS' if result.wasSuccessful() else 'FAIL', 'tests': result.testsRun,
              'failures': len(result.failures), 'errors': len(result.errors),
              'skipped': [{'test': str(test), 'reason': reason} for test, reason in result.skipped],
              'source_sha256': {str(path.relative_to(ROOT)): production.file_sha256(path)
                                for path in [TOOL, ROOT / 'idf/esp32-cyd2usb-native/build-production.ps1', Path(__file__)]},
              'scope': 'Deterministic host image/ELF/config fixtures and actual subprocess exit; no SDK build or hardware.'}
    production.write_json(OUTPUT / 'report.json', report)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())

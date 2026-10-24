"""Real CMake phase guards and component recipes; no SDK/compiler/codec runs.

Valid component cases use an exact five-path SHA256 allowlist and target-command
stubs. These test configuration behavior, not actual SDK/archive file identity.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / 'tests/target/vorbis_floor1_positions_qemu/main/CMakeLists.txt'
DEFAULT_CMAKE = Path('C:/Work/yoRadio/.idf/tools-v6.0.2/tools/cmake/4.0.3/bin/cmake.exe')
BINDING_ERROR = 'Explicit known FLOOR1_BINDING_CONTROL is required'
RESET_MODE_ERROR = 'Known FLOOR1_RESET_MODE on/off is required when defined'
OPEN_OOM_MODE_ERROR = 'Known FLOOR1_OPEN_OOM_MODE on/off is required when defined'
EXPECTED_CASES = frozenset((
    'early-undefined', 'early-registered', 'early-unknown', 'unknown-dispatch',
    'unknown-binding', 'renderer-off', 'direct-control', 'old-placement-control',
    'early-reset-undefined', 'early-reset-registered', 'early-reset-unknown',
    'unknown-reset', 'empty-reset', 'reset-renderer-off', 'reset-direct',
    'reset-open-control', 'reset-decode-control', 'component-legacy-undefined',
    'component-reset-off', 'component-reset-esp32', 'component-reset-esp32c3',
    'component-legacy-open-control',
    'early-open-oom-undefined', 'early-open-oom-registered', 'early-open-oom-unknown',
    'unknown-open-oom', 'empty-open-oom', 'open-oom-renderer-off', 'open-oom-direct',
    'open-oom-open-control', 'open-oom-decode-control', 'open-oom-reset-on',
    'component-open-oom-esp32', 'component-open-oom-esp32c3', 'component-open-oom-off',
    'component-reset-open-oom-off', 'component-open-oom-default-reset'))


def identity(path):
    data = path.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


class RegisteredCMake(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.output.mkdir(parents=True, exist_ok=False)
        cls.inputs = {str(p): identity(p) for p in (SUBJECT, Path(__file__).resolve(), cls.cmake, Path(sys.executable).resolve())}
        cls.source = SUBJECT.read_bytes()
        cls.frozen = cls.output / 'component.cmake'
        cls.frozen.write_bytes(cls.source)
        # Move exactly the current binding guard, preserving all other raw bytes.
        newline = b'\r\n' if b'\r\n' in cls.source else b'\n'
        block = newline.join(line.encode() for line in (
            'set(binding_controls "none" "register-open" "register-decode")',
            'if(NOT FLOOR1_BINDING_CONTROL IN_LIST binding_controls)',
            '    message(FATAL_ERROR "' + BINDING_ERROR + '")', 'endif()', ''))
        early = b'if(CMAKE_BUILD_EARLY_EXPANSION)' + newline
        if cls.source.count(block) != 1 or cls.source.count(early) != 1:
            raise AssertionError('Expected exact phase guard for the frozen negative control')
        cls.control = cls.output / 'binding-before-early.cmake'
        cls.control.write_bytes(cls.source.replace(block, b'', 1).replace(early, block + early, 1))
        cls.report = dict(passed=False, configure_only=True, compiler_invoked=False,
            sdk_export_invoked=False, runtime_invoked=False, inputs=cls.inputs,
            frozen_source=identity(cls.frozen), negative_control=identity(cls.control),
            negative_control_change='move only binding-control guard before early return',
            expected_cases=sorted(EXPECTED_CASES), actual_archive_identity_qualified=False,
            component_recipe_note='Five-path SHA256 allowlist and target stubs; no SDK/archive filesystem access.',
            commands=[])
        cls.save()

    @classmethod
    def save(cls):
        (cls.output / 'report.json').write_text(json.dumps(cls.report, indent=2) + '\n', encoding='utf-8')

    def component_stubs(self, directory, target, dispatch, binding, renderer, reset, open_oom):
        """Allow only subject-owned configuration calls; never read an SDK/archive."""
        self.assertIn(target, ('esp32', 'esp32c3'))
        variant = (directory / 'mock-variant').as_posix()
        codec = (directory / 'mock-codec').as_posix()
        sources = [variant + '/vorbis_repair/' + part + '.c' for part in ('setup', 'output')]
        pins = dict(setup='1'*64, output='2'*64, abi='3'*64, floor='4'*64)
        codec_sha = ('92ba997358f50994d41422438c78bf2d7ee86dc1efc265f5356a66e221ae2e58' if target == 'esp32'
                     else '311caa814095b098e476b28e46d55623ef70c26b0d73d69ba5832e154ec8d909')
        allowed = [(sources[0], pins['setup']), (sources[1], pins['output']),
                   (variant+'/vorbis_repair_abi.h', pins['abi']),
                   (variant+'/vorbis_repair/floor1_render.h', pins['floor']),
                   (codec+'/lib/'+target+'/libesp_audio_codec.a', codec_sha)]
        lines = ['set(COMPONENT_LIB fixture_component)', 'set(IDF_TARGET '+target+')',
            'set(CONFIG_IDF_TARGET_ESP32 '+('ON)' if target == 'esp32' else 'OFF)'),
            'set(CONFIG_IDF_TARGET_ESP32C3 '+('ON)' if target == 'esp32c3' else 'OFF)'),
            'set(IDF_VERSION_MAJOR 6)', 'set(IDF_VERSION_MINOR '+('0)' if target == 'esp32' else '1)'),
            'set(IDF_VERSION_PATCH '+('2)' if target == 'esp32' else '0)'),
            'set(ENV{VORBIS_FLOOR1_MAIN} "'+variant+'")',
            'set(ENV{YORADIO_AUDIO_CODEC_COMPONENT} "'+codec+'")',
            'set_property(GLOBAL PROPERTY HASH_CALLS "")',
            'set_property(GLOBAL PROPERTY SOURCE_CALLS 0)',
            'set_property(GLOBAL PROPERTY LINK_OPTIONS "")',
            'set_property(GLOBAL PROPERTY DEFINITION_CALLS 0)',
            'set_property(GLOBAL PROPERTY COMPILE_DEFINITIONS "")']
        lines += ['set(FLOOR1_'+part+'_SHA256 '+pin+')' for part,pin in pins.items()]
        lines += ['function(file)',
            '  if(NOT ARGC EQUAL 3 OR NOT "${ARGV0}" STREQUAL "SHA256")',
            '    message(FATAL_ERROR "UNEXPECTED_FILE_COMMAND")', '  endif()']
        for index, (path, pin) in enumerate(allowed):
            lines += [('  if' if index == 0 else '  elseif')+'("${ARGV1}" STREQUAL "'+path+'")',
                      '    set(value "'+pin+'")']
        lines += ['  else()', '    message(FATAL_ERROR "UNEXPECTED_HASH_PATH:${ARGV1}")', '  endif()',
            '  set_property(GLOBAL APPEND PROPERTY HASH_CALLS "${ARGV1}")',
            '  set(${ARGV2} "${value}" PARENT_SCOPE)', 'endfunction()',
            'function(target_sources)',
            '  if(NOT "${ARGV0}" STREQUAL "fixture_component" OR NOT "${ARGV1}" STREQUAL "PRIVATE" OR',
            '     NOT ARGC EQUAL 4 OR NOT "${ARGV2}" STREQUAL "'+sources[0]+'" OR',
            '     NOT "${ARGV3}" STREQUAL "'+sources[1]+'")',
            '    message(FATAL_ERROR "UNEXPECTED_TARGET_SOURCES")', '  endif()',
            '  get_property(count GLOBAL PROPERTY SOURCE_CALLS)',
            '  math(EXPR count "${count}+1")', '  set_property(GLOBAL PROPERTY SOURCE_CALLS "${count}")',
            'endfunction()', 'function(target_link_options)',
            '  if(NOT "${ARGV0}" STREQUAL "fixture_component" OR NOT "${ARGV1}" STREQUAL "INTERFACE")',
            '    message(FATAL_ERROR "UNEXPECTED_LINK_SCOPE")', '  endif()',
            '  set(options ${ARGN})', '  list(REMOVE_AT options 0 1)',
            '  set_property(GLOBAL APPEND PROPERTY LINK_OPTIONS ${options})', 'endfunction()',
            'function(target_compile_definitions)',
            '  if(NOT ARGC EQUAL 3 OR NOT "${ARGV0}" STREQUAL "fixture_component" OR',
            '     NOT "${ARGV1}" STREQUAL "PRIVATE" OR',
            '     (NOT "${ARGV2}" STREQUAL "VORBIS_RESET_CYCLES=1" AND NOT "${ARGV2}" STREQUAL "VORBIS_OPEN_OOM=1"))',
            '    message(FATAL_ERROR "UNEXPECTED_FIXTURE_DEFINITION")', '  endif()',
            '  get_property(count GLOBAL PROPERTY DEFINITION_CALLS)',
            '  math(EXPR count "${count}+1")', '  set_property(GLOBAL PROPERTY DEFINITION_CALLS "${count}")',
            '  set_property(GLOBAL APPEND PROPERTY COMPILE_DEFINITIONS "${ARGV2}")',
            'endfunction()']
        links = ['-Wl,--wrap=esp_vorbis_dec_open', '-Wl,--wrap=esp_vorbis_dec_decode']
        if renderer == 'on': links.append('-Wl,--wrap=floor1_inverse2')
        if dispatch == 'registered' and binding != 'register-open':
            links.append('-Wl,--wrap=esp_vorbis_dec_register')
        if open_oom == 'on':
            links += ['-Wl,--wrap=media_lib_module_calloc', '-Wl,--wrap=media_lib_free']
        definitions = []
        if reset == 'on': definitions.append('VORBIS_RESET_CYCLES=1')
        if open_oom == 'on': definitions.append('VORBIS_OPEN_OOM=1')
        checks = ['get_property(hashes GLOBAL PROPERTY HASH_CALLS)',
            'if(NOT "${hashes}" STREQUAL "'+';'.join(path for path,pin in allowed)+'")',
            '  message(FATAL_ERROR "Wrong ordered source/archive hash calls")', 'endif()',
            'get_property(sources GLOBAL PROPERTY SOURCE_CALLS)', 'if(NOT sources EQUAL 1)',
            '  message(FATAL_ERROR "Wrong source registration count")', 'endif()',
            'get_property(links GLOBAL PROPERTY LINK_OPTIONS)',
            'if(NOT "${links}" STREQUAL "'+';'.join(links)+'")',
            '  message(FATAL_ERROR "Wrong complete wrapper link recipe: ${links}")', 'endif()',
            'get_property(definitions GLOBAL PROPERTY DEFINITION_CALLS)',
            'if(NOT definitions EQUAL '+str(len(definitions))+')',
            '  message(FATAL_ERROR "Wrong private fixture compile definition count")', 'endif()',
            'get_property(actual_definitions GLOBAL PROPERTY COMPILE_DEFINITIONS)',
            'if(NOT "${actual_definitions}" STREQUAL "'+';'.join(definitions)+'")',
            '  message(FATAL_ERROR "Wrong complete private fixture compile definitions")', 'endif()',
            'message(STATUS "REGISTRY_CMAKE_COMPONENT_RECIPE target='+target+' reset='+str(reset or 'undefined')+'")']
        return lines, checks

    def run_cmake(self, name, *, early=False, dispatch=None, binding=None, renderer=None, reset=None, open_oom=None,
                  expected=None, source='main.c', control=False, undefined=False, component_target=None):
        directory = self.output / name
        directory.mkdir()
        lines = ['cmake_minimum_required(VERSION 3.20)',
            'set(CMAKE_BUILD_EARLY_EXPANSION ' + ('ON)' if early else 'OFF)'),
            'set_property(GLOBAL PROPERTY REGISTER_CALLS 0)',
            'function(idf_component_register)',
            '  get_property(count GLOBAL PROPERTY REGISTER_CALLS)',
            '  math(EXPR count "${count}+1")',
            '  set_property(GLOBAL PROPERTY REGISTER_CALLS "${count}")',
            '  cmake_parse_arguments(ARG "" "" "SRCS;INCLUDE_DIRS;REQUIRES" ${ARGN})',
            '  if(NOT "${ARG_SRCS}" STREQUAL "' + source + '")',
            '    message(FATAL_ERROR "Unexpected discovery source: ${ARG_SRCS}")',
            '  endif()',
            '  message(STATUS "REGISTRY_CMAKE_IDF_REGISTER source=${ARG_SRCS}")',
            'endfunction()']
        component_checks = []
        if component_target is not None:
            self.assertFalse(early or expected or control)
            component_lines, component_checks = self.component_stubs(directory, component_target, dispatch, binding, renderer, reset, open_oom)
            lines += component_lines
        else:
            # Any SDK/archive access or target mutation before a guard is an error.
            for command in ('file','target_sources','target_link_options','target_compile_definitions'):
                lines += ['function('+command+')', '  message(FATAL_ERROR "UNEXPECTED_'+command.upper()+'")', 'endfunction()']
        if undefined:
            lines += ['foreach(option FLOOR1_DISPATCH_MODE FLOOR1_BINDING_CONTROL FLOOR1_RENDER_MODE FLOOR1_RESET_MODE FLOOR1_OPEN_OOM_MODE)',
                '  if(DEFINED ${option})', '    message(FATAL_ERROR "Unexpected inherited option ${option}")',
                '  endif()', 'endforeach()', 'message(STATUS "REGISTRY_CMAKE_OPTIONS_UNDEFINED")']
        for key, value in (('FLOOR1_DISPATCH_MODE', dispatch), ('FLOOR1_BINDING_CONTROL', binding),
                           ('FLOOR1_RENDER_MODE', renderer), ('FLOOR1_RESET_MODE', reset), ('FLOOR1_OPEN_OOM_MODE', open_oom)):
            if value is not None:
                lines.append('set(' + key + ' "' + value + '")')
        helper = self.control if control else self.frozen
        lines += ['include("' + helper.as_posix() + '")',
            'get_property(count GLOBAL PROPERTY REGISTER_CALLS)', 'if(NOT count EQUAL 1)',
            '  message(FATAL_ERROR "idf_component_register was not invoked exactly once")', 'endif()']
        lines += component_checks + ['message(STATUS "REGISTRY_CMAKE_EARLY_COMPLETE")']
        script = directory / 'case.cmake'
        script.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        argv = [str(self.cmake), '-P', str(script)]
        record = dict(name=name, argv=argv, cwd=str(directory), script=identity(script),
            helper=helper.name, expected_error=expected, returncode=None, timed_out=False,
            interrupted=False, passed=False, component_target=component_target,
            archive_hashes_stubbed=component_target is not None, reset_mode=reset, open_oom_mode=open_oom)
        started = time.monotonic()
        try:
            with (directory / 'stdout.log').open('wb') as stdout, (directory / 'stderr.log').open('wb') as stderr:
                try:
                    completed = subprocess.run(argv, cwd=directory, stdin=subprocess.DEVNULL,
                        stdout=stdout, stderr=stderr, timeout=15, check=False,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                    record['returncode'] = completed.returncode
                except subprocess.TimeoutExpired:
                    record['timed_out'] = True
                    raise
                except BaseException:
                    record['interrupted'] = True
                    raise
            text = (directory / 'stdout.log').read_text(encoding='utf-8', errors='strict') + (directory / 'stderr.log').read_text(encoding='utf-8', errors='strict')
            normalized = ' '.join(text.split())
            self.assertEqual(record['returncode'], 1 if expected else 0, text)
            self.assertEqual(text.count('REGISTRY_CMAKE_IDF_REGISTER source=' + source), 1, text)
            self.assertNotIn('UNEXPECTED_', text)
            self.assertNotIn('Select the ESP32 or ESP32-C3 standalone raw test', text)
            self.assertNotIn('Wrong pinned SDK', text)
            if expected:
                self.assertEqual(normalized.count(expected), 1, text)
                self.assertNotIn('REGISTRY_CMAKE_EARLY_COMPLETE', text)
            else:
                self.assertEqual(text.count('REGISTRY_CMAKE_EARLY_COMPLETE'), 1, text)
            if undefined:
                self.assertIn('REGISTRY_CMAKE_OPTIONS_UNDEFINED', text)
            if component_target is not None:
                self.assertEqual(text.count('REGISTRY_CMAKE_COMPONENT_RECIPE target='+component_target+
                    ' reset='+str(reset or 'undefined')), 1, text)
            record['passed'] = True
        finally:
            record['elapsed_seconds'] = time.monotonic() - started
            for stream in ('stdout', 'stderr'):
                path = directory / (stream + '.log')
                if path.is_file(): record[stream] = identity(path)
            self.report['commands'].append(record)
            self.save()

    def test_early_discovery_without_cache_options(self):
        self.run_cmake('early-undefined', early=True, undefined=True)

    def test_early_discovery_registered_source(self):
        self.run_cmake('early-registered', early=True, dispatch='registered', binding='none',
            renderer='on', source='registered.c')

    def test_early_discovery_does_not_validate_partial_options(self):
        self.run_cmake('early-unknown', early=True, dispatch='unknown', binding='unknown', renderer='unknown')

    def test_normal_unknown_dispatch_rejected_before_sdk(self):
        self.run_cmake('unknown-dispatch', dispatch='unknown', binding='none', renderer='off',
            expected='Explicit FLOOR1_DISPATCH_MODE direct/registered is required')

    def test_normal_unknown_binding_rejected_before_sdk(self):
        self.run_cmake('unknown-binding', dispatch='direct', binding='unknown', renderer='off', expected=BINDING_ERROR)

    def test_registered_renderer_off_rejected_before_sdk(self):
        self.run_cmake('renderer-off', dispatch='registered', binding='none', renderer='off',
            source='registered.c', expected='Registered dispatch requires the renderer')

    def test_direct_binding_control_rejected_before_sdk(self):
        self.run_cmake('direct-control', dispatch='direct', binding='register-open', renderer='off',
            expected='Binding controls require registered dispatch')

    def test_old_guard_placement_control_reproduces_exact_failure(self):
        self.run_cmake('old-placement-control', early=True, undefined=True, control=True, expected=BINDING_ERROR)

    def test_early_reset_discovery_without_other_cache_options(self):
        self.run_cmake('early-reset-undefined', early=True, reset='on', undefined=True)

    def test_early_reset_discovery_registered_source(self):
        self.run_cmake('early-reset-registered', early=True, dispatch='registered', binding='none',
            renderer='on', reset='on', source='registered.c')

    def test_early_reset_discovery_does_not_validate_unknown_mode(self):
        self.run_cmake('early-reset-unknown', early=True, reset='unknown')

    def test_unknown_reset_mode_rejected_before_sdk(self):
        self.run_cmake('unknown-reset', dispatch='registered', binding='none', renderer='on',
            reset='unknown', source='registered.c', expected=RESET_MODE_ERROR)

    def test_empty_reset_mode_rejected_before_sdk(self):
        self.run_cmake('empty-reset', dispatch='registered', binding='none', renderer='on',
            reset='', source='registered.c', expected=RESET_MODE_ERROR)

    def test_reset_requires_renderer_before_sdk(self):
        self.run_cmake('reset-renderer-off', dispatch='registered', binding='none', renderer='off',
            reset='on', source='registered.c', expected='Reset cycles require the renderer')

    def test_reset_requires_registered_dispatch_before_sdk(self):
        self.run_cmake('reset-direct', dispatch='direct', binding='none', renderer='on',
            reset='on', source='render.c', expected='Reset cycles require registered dispatch')

    def test_reset_rejects_open_binding_control_before_sdk(self):
        self.run_cmake('reset-open-control', dispatch='registered', binding='register-open', renderer='on',
            reset='on', source='registered.c', expected='Reset cycles require no binding control')

    def test_reset_rejects_decode_binding_control_before_sdk(self):
        self.run_cmake('reset-decode-control', dispatch='registered', binding='register-decode', renderer='on',
            reset='on', source='registered.c', expected='Reset cycles require no binding control')

    def test_normal_legacy_undefined_reset_component_recipe(self):
        self.run_cmake('component-legacy-undefined', dispatch='direct', binding='none', renderer='off',
            component_target='esp32')

    def test_normal_reset_off_registered_component_recipe(self):
        self.run_cmake('component-reset-off', dispatch='registered', binding='none', renderer='on', reset='off',
            source='registered.c', component_target='esp32')

    def test_normal_esp32_reset_component_recipe(self):
        self.run_cmake('component-reset-esp32', dispatch='registered', binding='none', renderer='on', reset='on',
            source='registered.c', component_target='esp32')

    def test_normal_esp32c3_reset_component_recipe(self):
        self.run_cmake('component-reset-esp32c3', dispatch='registered', binding='none', renderer='on', reset='on',
            source='registered.c', component_target='esp32c3')

    def test_normal_legacy_open_control_reset_off_component_recipe(self):
        self.run_cmake('component-legacy-open-control', dispatch='registered', binding='register-open',
            renderer='on', reset='off', source='registered.c', component_target='esp32')

    def test_early_open_oom_discovery_without_other_cache_options(self):
        self.run_cmake('early-open-oom-undefined', early=True, open_oom='on', undefined=True)

    def test_early_open_oom_discovery_registered_source(self):
        self.run_cmake('early-open-oom-registered', early=True, dispatch='registered', binding='none',
            renderer='on', reset='off', open_oom='on', source='registered.c')

    def test_early_open_oom_discovery_does_not_validate_unknown_mode(self):
        self.run_cmake('early-open-oom-unknown', early=True, open_oom='unknown')

    def test_unknown_open_oom_mode_rejected_before_sdk(self):
        self.run_cmake('unknown-open-oom', dispatch='registered', binding='none', renderer='on',
            reset='off', open_oom='unknown', source='registered.c', expected=OPEN_OOM_MODE_ERROR)

    def test_empty_open_oom_mode_rejected_before_sdk(self):
        self.run_cmake('empty-open-oom', dispatch='registered', binding='none', renderer='on',
            reset='off', open_oom='', source='registered.c', expected=OPEN_OOM_MODE_ERROR)

    def test_open_oom_requires_renderer_before_sdk(self):
        self.run_cmake('open-oom-renderer-off', dispatch='registered', binding='none', renderer='off',
            reset='off', open_oom='on', source='registered.c', expected='Open allocation failures require the renderer')

    def test_open_oom_requires_registered_dispatch_before_sdk(self):
        self.run_cmake('open-oom-direct', dispatch='direct', binding='none', renderer='on', reset='off',
            open_oom='on', source='render.c', expected='Open allocation failures require registered dispatch')

    def test_open_oom_rejects_open_binding_control_before_sdk(self):
        self.run_cmake('open-oom-open-control', dispatch='registered', binding='register-open', renderer='on',
            reset='off', open_oom='on', source='registered.c', expected='Open allocation failures require no binding control')

    def test_open_oom_rejects_decode_binding_control_before_sdk(self):
        self.run_cmake('open-oom-decode-control', dispatch='registered', binding='register-decode', renderer='on',
            reset='off', open_oom='on', source='registered.c', expected='Open allocation failures require no binding control')

    def test_open_oom_rejects_reset_cycles_before_sdk(self):
        self.run_cmake('open-oom-reset-on', dispatch='registered', binding='none', renderer='on', reset='on',
            open_oom='on', source='registered.c', expected='Open allocation failures require reset cycles off')

    def test_normal_esp32_open_oom_component_recipe(self):
        self.run_cmake('component-open-oom-esp32', dispatch='registered', binding='none', renderer='on',
            reset='off', open_oom='on', source='registered.c', component_target='esp32')

    def test_normal_esp32c3_open_oom_component_recipe(self):
        self.run_cmake('component-open-oom-esp32c3', dispatch='registered', binding='none', renderer='on',
            reset='off', open_oom='on', source='registered.c', component_target='esp32c3')

    def test_normal_open_oom_off_registered_component_recipe(self):
        self.run_cmake('component-open-oom-off', dispatch='registered', binding='none', renderer='on',
            reset='off', open_oom='off', source='registered.c', component_target='esp32')

    def test_normal_open_oom_off_preserves_reset_component_recipe(self):
        self.run_cmake('component-reset-open-oom-off', dispatch='registered', binding='none', renderer='on',
            reset='on', open_oom='off', source='registered.c', component_target='esp32')

    def test_normal_open_oom_uses_default_off_reset_component_recipe(self):
        self.run_cmake('component-open-oom-default-reset', dispatch='registered', binding='none', renderer='on',
            open_oom='on', source='registered.c', component_target='esp32')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cmake', type=Path, default=DEFAULT_CMAKE)
    parser.add_argument('--output', type=Path, default=ROOT / '.build/vorbis-registered-cmake-host-01')
    args, unittest_args = parser.parse_known_args()
    RegisteredCMake.cmake = args.cmake.resolve(strict=True)
    RegisteredCMake.output = args.output.resolve()
    build_root = (ROOT / '.build').resolve()
    if RegisteredCMake.output == build_root or not RegisteredCMake.output.is_relative_to(build_root) or RegisteredCMake.output.exists():
        parser.error('Output must be a fresh directory under this worktree .build')
    outcome = unittest.main(argv=[sys.argv[0], *unittest_args], exit=False)
    if not hasattr(RegisteredCMake, 'report'):
        return 1
    report = RegisteredCMake.report
    report['inputs_unchanged'] = all(identity(Path(p)) == pin for p, pin in RegisteredCMake.inputs.items())
    report['frozen_copies_unchanged'] = identity(RegisteredCMake.frozen) == report['frozen_source'] and identity(RegisteredCMake.control) == report['negative_control']
    report['tests_run'] = outcome.result.testsRun
    report['passed'] = outcome.result.wasSuccessful() and outcome.result.testsRun == len(EXPECTED_CASES) and len(report['commands']) == len(EXPECTED_CASES) and {c['name'] for c in report['commands']} == EXPECTED_CASES and all(c['passed'] for c in report['commands']) and report['inputs_unchanged'] and report['frozen_copies_unchanged']
    RegisteredCMake.save()
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

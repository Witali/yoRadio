"""Real CMake script-mode phase guards; no SDK, compiler, codec or target runs."""
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
            negative_control_change='move only binding-control guard before early return', commands=[])
        cls.save()

    @classmethod
    def save(cls):
        (cls.output / 'report.json').write_text(json.dumps(cls.report, indent=2) + '\n', encoding='utf-8')

    def run_cmake(self, name, *, early=False, dispatch=None, binding=None, renderer=None,
                  expected=None, source='main.c', control=False, undefined=False):
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
            'endfunction()',
            # Any SDK/archive file access or target modification is an error here.
            'function(file)', '  message(FATAL_ERROR "UNEXPECTED_SDK_ARCHIVE_FILE_ACCESS")', 'endfunction()',
            'function(target_sources)', '  message(FATAL_ERROR "UNEXPECTED_TARGET_SOURCES")', 'endfunction()',
            'function(target_link_options)', '  message(FATAL_ERROR "UNEXPECTED_TARGET_LINK_OPTIONS")', 'endfunction()']
        if undefined:
            lines += ['foreach(option FLOOR1_DISPATCH_MODE FLOOR1_BINDING_CONTROL FLOOR1_RENDER_MODE)',
                '  if(DEFINED ${option})', '    message(FATAL_ERROR "Unexpected inherited option ${option}")',
                '  endif()', 'endforeach()', 'message(STATUS "REGISTRY_CMAKE_OPTIONS_UNDEFINED")']
        for key, value in (('FLOOR1_DISPATCH_MODE', dispatch), ('FLOOR1_BINDING_CONTROL', binding),
                           ('FLOOR1_RENDER_MODE', renderer)):
            if value is not None:
                lines.append('set(' + key + ' "' + value + '")')
        helper = self.control if control else self.frozen
        lines += ['include("' + helper.as_posix() + '")',
            'get_property(count GLOBAL PROPERTY REGISTER_CALLS)', 'if(NOT count EQUAL 1)',
            '  message(FATAL_ERROR "idf_component_register was not invoked exactly once")', 'endif()',
            'message(STATUS "REGISTRY_CMAKE_EARLY_COMPLETE")']
        script = directory / 'case.cmake'
        script.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        argv = [str(self.cmake), '-P', str(script)]
        record = dict(name=name, argv=argv, cwd=str(directory), script=identity(script),
            helper=helper.name, expected_error=expected, returncode=None, timed_out=False,
            interrupted=False, passed=False)
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
    report['passed'] = outcome.result.wasSuccessful() and outcome.result.testsRun == 8 and len(report['commands']) == 8 and all(c['passed'] for c in report['commands']) and report['inputs_unchanged'] and report['frozen_copies_unchanged']
    RegisteredCMake.save()
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())

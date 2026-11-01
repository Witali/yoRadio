"""Check the actual CYD AAC-Plus Kconfig dependency/default with installed Kconfiglib.

Only the required codec/target symbols are provided by this host-only wrapper.
Other external SDK symbols remain unavailable; their original warnings are saved.
The native diagnostic separately executes the production configuration header.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import kconfiglib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'idf/esp32-cyd2usb-native/main/Kconfig.projbuild'


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    out = args.output.resolve()
    assert out.is_relative_to(ROOT / '.build') and not out.exists()
    out.mkdir(parents=True)
    originals = [SOURCE, Path(__file__).resolve()]
    frozen = {}
    for path in originals:
        body = path.read_bytes()
        snapshot = out / path.name
        snapshot.write_bytes(body)
        frozen[path.relative_to(ROOT).as_posix()] = dict(snapshot=snapshot.name, sha256=sha(body), bytes=len(body))
    report_path = out / 'report.json'
    report = dict(passed=False, sources=frozen, cases=[], native_decoder_executed=False,
                  kconfiglib_module_sha256=sha(Path(kconfiglib.__file__).read_bytes()))

    def save():
        report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')

    save()
    try:
        wrapper = out / 'Kconfig'
        wrapper.write_text('mainmenu "CYD public AAC configuration test"\n'
                           'config IDF_TARGET\n    string\n    default "esp32"\n'
                           'config YORADIO_AAC_DECODER_ESPRESSIF\n    bool "Vendor AAC"\n'
                           'config YORADIO_AAC_DECODER_HELIX\n    bool "Helix AAC"\n'
                           'source "' + (out / SOURCE.name).as_posix() + '"\n', encoding='utf-8')
        kconf = kconfiglib.Kconfig(str(wrapper), warn_to_stderr=False)
        vendor = kconf.syms['YORADIO_AAC_DECODER_ESPRESSIF']
        plus = kconf.syms['YORADIO_AAC_PLUS']
        core = sys.modules[type(plus).__module__]
        report['kconfiglib_core_sha256'] = sha(Path(core.__file__).read_bytes())
        assert plus.type == core.BOOL

        def check(name, expected, visibility):
            assert plus.str_value == expected and plus.visibility == visibility
            report['cases'].append(dict(name=name, vendor=vendor.str_value, actual=plus.str_value,
                                        visibility=plus.visibility, passed=True))

        vendor.set_value(2)
        check('vendor-default-full-AAC', 'y', 2)
        plus.set_value(0)
        check('explicit-core-only-preference', 'n', 2)
        plus.unset_value()
        check('restore-default-full-AAC', 'y', 2)
        vendor.set_value(0)
        check('vendor-disabled', 'n', 0)
        plus.set_value(2)
        check('forced-plus-cannot-ignore-dependency', 'n', 0)
        kconf.syms['YORADIO_AAC_DECODER_HELIX'].set_value(2)
        check('Helix-has-no-vendor-plus-option', 'n', 0)
        vendor.set_value(2)
        check('restore-vendor-and-requested-plus', 'y', 2)
        plus.set_value(0)
        check('vendor-explicit-off-remains-off', 'n', 2)
        (out / 'kconfig-warnings.log').write_text('\n'.join(kconf.warnings) + '\n', encoding='utf-8')
        report['unprovided_external_symbol_warnings'] = len(kconf.warnings)
        for path in originals:
            pin = frozen[path.relative_to(ROOT).as_posix()]
            assert sha(path.read_bytes()) == pin['sha256'] == sha((out / pin['snapshot']).read_bytes())
        report['passed'] = report['all_source_bindings_current'] = True
    except Exception as error:
        report['failure'] = dict(type=type(error).__name__, reason=str(error))
    finally:
        save()
    print(json.dumps(dict(passed=report['passed'], cases=len(report['cases']),
                         capture=out.relative_to(ROOT).as_posix(), failure=report.get('failure'))))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    sys.dont_write_bytecode = True
    raise SystemExit(main())

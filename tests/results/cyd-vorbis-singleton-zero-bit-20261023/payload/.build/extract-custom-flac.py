from pathlib import Path
import hashlib

root=Path(__file__).resolve().parents[1]
old=root/'idf/esp32c3-oled-native/components/custom_flac'
new=root/'idf/components/custom_flac'
assert not new.exists()
new.mkdir()
for name in ['custom_flac_adapter.cpp','custom_flac_adapter.h']:
    data=(old/name).read_bytes()
    if name.endswith('.cpp'):
        assert hashlib.sha256(data).hexdigest()=='ffa4f71d2e0387e369ad5da1f5fa268557d6fc50cd56738cb65affaaafbd7a26'
    (new/name).write_bytes(data)
    (old/name).write_text(('' if name.endswith('.cpp') else '#pragma once\n')+
        '// Compatibility entry point; both native targets use the shared implementation.\n'+
        '#include "../../../components/custom_flac/'+name+'"\n')
cmake=(old/'CMakeLists.txt').read_text()
cmake=cmake.replace('set(YORADIO_FLAC_DIR','set(YORADIO_FLAC_COMPONENT_DIR "${CMAKE_CURRENT_LIST_DIR}")\nset(YORADIO_FLAC_DIR',1)
cmake=cmake.replace('/../../../../yoRadio/','/../../../yoRadio/')
cmake=cmake.replace('    "custom_flac_adapter.cpp"','    "${YORADIO_FLAC_COMPONENT_DIR}/custom_flac_adapter.cpp"')
cmake=cmake.replace('    "."','    "${YORADIO_FLAC_COMPONENT_DIR}"')
(new/'CMakeLists.txt').write_text(cmake)
(old/'CMakeLists.txt').write_text('# Keep the historical C3 component identity and include paths.\ninclude("${CMAKE_CURRENT_LIST_DIR}/../../../components/custom_flac/CMakeLists.txt")\n')
for name in ['tests/run-c3-maintenance.py','tests/run-esp32c3-stream-format.py',
             'tools/codec_benchmark/verify_vorbis_repair_build.py']:
    path=root/name
    value=path.read_text()
    assert 'idf/esp32c3-oled-native/components/custom_flac' in value
    path.write_text(value.replace('idf/esp32c3-oled-native/components/custom_flac','idf/components/custom_flac'))
path=root/'tests/run-flac-stream-eof.py'
value=path.read_text().replace("ADAPTER = 'idf/esp32c3-oled-native/components/custom_flac'", "ADAPTER = 'idf/components/custom_flac'\nLEGACY_ADAPTER = 'idf/esp32c3-oled-native/components/custom_flac'")
needle="    baseline = subprocess.check_output(['git', 'show', args.baseline_revision+':'+ADAPTER+'/custom_flac_adapter.cpp'], cwd=ROOT)"
assert needle in value
value=value.replace(needle,"    baseline_path = ADAPTER + '/custom_flac_adapter.cpp'\n    if subprocess.run(['git','cat-file','-e',args.baseline_revision+':'+baseline_path], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:\n        baseline_path = LEGACY_ADAPTER + '/custom_flac_adapter.cpp'\n    baseline = subprocess.check_output(['git', 'show', args.baseline_revision+':'+baseline_path], cwd=ROOT)")
value=value.replace("    report['baseline_revision'] =", "    report['baseline_adapter_path'] = baseline_path\n    report['baseline_revision'] =")
path.write_text(value)
path=root/'tools/codec_benchmark/run_flac_depths.py'
value=path.read_text()
needle="    adapter='idf/esp32c3-oled-native/components/custom_flac/'"
assert needle in value
value=value.replace(needle,"    adapter='idf/components/custom_flac/'\n    if args.revision and subprocess.run(['git','cat-file','-e',args.revision+':'+adapter+'custom_flac_adapter.cpp'], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode:\n        adapter='idf/esp32c3-oled-native/components/custom_flac/'")
path.write_text(value)
path=root/'tests/esp32c3-native-idf.test.js'
value=path.read_text()
value=value.replace('  const cmake = read("components", "custom_flac", "CMakeLists.txt");\n  const adapter = read("components", "custom_flac", "custom_flac_adapter.cpp");',
    '  const shim = read("components", "custom_flac", "CMakeLists.txt");\n  const shared = (...parts) => fs.readFileSync(path.join(root, "idf", "components", "custom_flac", ...parts), "utf8");\n  const cmake = shared("CMakeLists.txt");\n  const adapter = shared("custom_flac_adapter.cpp");\n  assert.match(shim, /include\\(.*components\\/custom_flac\\/CMakeLists\\.txt/);')
path.write_text(value)
path=root/'tests/codec-benchmark.test.js'
value=path.read_text()
value=value.replace("'idf', 'esp32c3-oled-native', 'components',", "'idf', 'components',")
path.write_text(value)
print('Shared adapter and header preserve production bytes; C3 shims and current runners use canonical paths.')

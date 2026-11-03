"""Prepare one future Xtensa syntax command; never run a compiler/SDK/QEMU."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
TARGET=ROOT/'tests/target/cyd_flac_ordinary_task_qemu/project/main/main.cpp'


def pin(path):
    data=path.read_bytes(); return dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())


def windows_argv(command):
    shell=ctypes.WinDLL('shell32',use_last_error=True); kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    shell.CommandLineToArgvW.argtypes=[wintypes.LPCWSTR,ctypes.POINTER(ctypes.c_int)]; shell.CommandLineToArgvW.restype=ctypes.POINTER(wintypes.LPWSTR)
    kernel.LocalFree.argtypes=[wintypes.HLOCAL]; kernel.LocalFree.restype=wintypes.HLOCAL
    count=ctypes.c_int(); pointer=shell.CommandLineToArgvW(command,ctypes.byref(count)); assert pointer
    try: return [pointer[index] for index in range(count.value)]
    finally: kernel.LocalFree(ctypes.cast(pointer,wintypes.HLOCAL))


def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--recipe',type=Path,required=True); parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(); recipe=args.recipe.resolve(); out=args.output.resolve()
    assert sys.platform=='win32' and recipe.is_relative_to(ROOT/'.build') and out.is_relative_to(ROOT/'.build') and not out.exists()
    database=recipe/'build/compile_commands.json'; rows=json.loads(database.read_bytes())
    selected=[row for row in rows if Path(row['file']).name=='main.cpp' and '/project/main/' in row['file'].replace('\\','/')]
    assert len(selected)==1; row=selected[0]; argv=windows_argv(row['command']); compiler=Path(argv[0]); assert compiler.is_file()
    out.mkdir(parents=True); (out/'tmp').mkdir(); (out/'sources').mkdir(); (out/'config').mkdir(); (out/'response').mkdir()
    snapshots={}
    def snapshot(source,destination):
        data=source.read_bytes(); destination.parent.mkdir(parents=True,exist_ok=True); destination.write_bytes(data)
        snapshots[str(source.resolve())]=dict(snapshot=destination.relative_to(out).as_posix(),**pin(source))
    snapshot(TARGET,out/'sources/main.cpp'); snapshot(Path(__file__).resolve(),out/'sources/prepare_syntax.py')
    snapshot(TARGET.parent/'CMakeLists.txt',out/'sources/diagnostic-main-CMakeLists.txt')
    snapshot(database,out/'sources/recipe-compile-commands.json')
    original_config=recipe/'build/config/sdkconfig.h'; snapshot(original_config,out/'sources/recipe-sdkconfig.h')
    # This derived syntax-only header is NOT a newly generated native sdkconfig.
    # The actual future native campaign must independently qualify its resolved
    # config against the controller's production-policy provenance.
    policy=dict(CONFIG_ESP_TASK_WDT_EN=1,CONFIG_ESP_TASK_WDT_INIT=1,CONFIG_ESP_TASK_WDT_TIMEOUT_S=5,
        CONFIG_ESP_TASK_WDT_PANIC=None,CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU0=1,CONFIG_ESP_TASK_WDT_CHECK_IDLE_TASK_CPU1=1,
        CONFIG_ESP_INT_WDT=1,CONFIG_ESP_INT_WDT_TIMEOUT_MS=300,CONFIG_ESP_INT_WDT_CHECK_CPU1=1,
        CONFIG_HEAP_POISONING_DISABLED=1,CONFIG_HEAP_POISONING_LIGHT=None,CONFIG_HEAP_POISONING_COMPREHENSIVE=None,
        CONFIG_YORADIO_NATIVE_DIAGNOSTICS=None,CONFIG_YORADIO_OGG_TIMELINE=1,CONFIG_YORADIO_AAC_PLUS=1,
        CONFIG_YORADIO_AAC_DECODER_ESPRESSIF=1,CONFIG_YORADIO_FLAC_DECODER_CUSTOM=1,CONFIG_YORADIO_FLAC_DECODER_ESPRESSIF=None)
    text=original_config.read_text()
    for key,value in policy.items():
        text=re.sub(r'^#define '+key+r'\b[^\n]*\n','',text,flags=re.M)
        text+='\n#undef '+key+'\n'+('' if value is None else '#define '+key+' '+str(value)+'\n')
    (out/'config/sdkconfig.h').write_text(text,encoding='utf-8')
    old_repository=recipe/'sources/repository'; old_vendor=recipe/'sources/vendor/esp_audio_codec'; repository=ROOT.parent.parent
    vendor=repository/'.idf/esp-adf-libs/esp_audio_codec'
    command=[str(compiler)]; cursor=1
    while cursor<len(argv):
        value=argv[cursor]
        if value in ('-o','-MF','-MT','-MQ'): cursor+=2; continue
        if value in ('-c','-MD','-MMD','-MP','-fstack-usage'): cursor+=1; continue
        if not value.startswith(('-','@')) and Path(value).resolve()==Path(row['file']).resolve(): value=str(out/'sources/main.cpp')
        elif value.startswith('-I'):
            path=Path(value[2:]).resolve()
            if path==recipe/'build/config': path=out/'config'
            elif path==Path(row['file']).resolve().parent: path=out/'sources'
            elif path.is_relative_to(old_repository): path=ROOT/path.relative_to(old_repository)
            elif path.is_relative_to(old_vendor): path=vendor/path.relative_to(old_vendor)
            value='-I'+str(path)
        elif value.startswith('@'):
            response=Path(value[1:]); target=out/'response'/response.name; snapshot(response,target); value='@'+str(target)
        command.append(value); cursor+=1
    command+=['-I'+str(ROOT/'idf/components/custom_flac'),'-I'+str(ROOT/'yoRadio/src/audioI2S/flac_decoder'),
              '-I'+str(ROOT/'idf/components/custom_codec_support'),'-I'+str(ROOT/'yoRadio/src/audioI2S'),
              '-DFLAC_OUTPUT_FRAMES=512','-DFLAC_SEGMENTED_WORKSPACE=1',
              '-fsyntax-only','-fdiagnostics-color=never','-MMD','-MF',str(out/'main.d'),'-MT',str(out/'main.syntax')]
    assert '-c' not in command and '-o' not in command and str(out/'sources/main.cpp') in command
    metadata={}
    closure=json.loads((recipe/'actual-compiler-closure.json').read_bytes())
    for unit in closure['translation_units']:
        if Path(unit['file']).name!='main.cpp': continue
        for name in unit.get('actual_dependency_paths',[]):
            path=Path(name).resolve()
            if path.is_relative_to(old_repository): path=ROOT/path.relative_to(old_repository)
            elif path.is_relative_to(old_vendor): path=vendor/path.relative_to(old_vendor)
            if path.is_file(): metadata[str(path)]=pin(path)
    for path in (ROOT/'idf/esp32-cyd2usb-native/main').glob('*.h'):
        metadata[str(path.resolve())]=pin(path)
    metadata[str(ROOT/'idf/components/custom_flac/custom_flac_adapter.h')]=pin(ROOT/'idf/components/custom_flac/custom_flac_adapter.h')
    for path in (ROOT/'idf/components/custom_codec_support/Arduino.h',ROOT/'idf/components/custom_codec_support/CMakeLists.txt'):
        metadata[str(path)]=pin(path)
    plan=dict(prepared=True,compiler_started=False,SDK_started=False,QEMU_started=False,
        syntax_only=True,final_native_configuration_qualified=False,command=command,cwd=row['directory'],
        environment=dict(TMP=str(out/'tmp'),TEMP=str(out/'tmp')),compiler=dict(path=str(compiler),**pin(compiler)),
        snapshots=snapshots,derived_syntax_config=dict(**pin(out/'config/sdkconfig.h'),policy=policy),
        metadata_not_new_compiler_observed_closure=metadata,recipe_closure=pin(recipe/'actual-compiler-closure.json'),
        planned_dependency_output=str(out/'main.d'),old_recipe_outputs_modified=False)
    (out/'syntax-plan.json').write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(prepared=True,compiler_started=False,SDK_started=False,QEMU_started=False,
                         bound_metadata_files=len(metadata),syntax_plan=str(out/'syntax-plan.json')),indent=2))


if __name__=='__main__': main()

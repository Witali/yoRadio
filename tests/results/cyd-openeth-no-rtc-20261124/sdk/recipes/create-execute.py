from common import *

text=(ROOT/'.build/copeneth24/execute.py').read_text()
start=text.index('def guard('); end=text.index('def main():')
text=text[:start]+text[end:]
text=text.replace('import time\n','import time\nfrom common import SOURCE, guard\n')
text=text.replace("preflight=load(BASE/'preflight.json'); release=load(BASE/'release.json')", "preflight=load(BASE/'preflight.json')")
text=text.replace("source_commit=release['source_commit']",'source_commit=SOURCE')
text=text.replace("preflight['source_project_reference']","'b65437a1bc59c9d269ce7bece597efddc70cea58'")
text=text.replace('guard(preflight,row,release)','guard(preflight,row)')
text=text.replace("load(directory/'baseline/sdkconfig.json')","load(ROOT/row['rtc_on']/'compiled/config/sdkconfig.json')")
text=text.replace("for item in row['objects']: same(item)","for item in row['objects']:\n            assert pin(ROOT/item['path'])==item['identity']")
start=text.index("        assert pin(Path(row['driver_entry']['file']))")
end=text.index("        invocation('gcc-reconfigure'",start)
text=text[:start]+"        report['rtc_access_probe_enabled']=True; write(status,report)\n"+text[end:]
text=text.replace("        assert not (cache/row['driver_entry']['output']).exists(),'Driver was not explicitly invalidated'\n",'')
text=text.replace("        clang=directory/'clang'; clang.mkdir(); shutil.copyfile(directory/'sdkconfig',clang/'sdkconfig')", "        clang=BASE/'clang-shared'; clang.mkdir(exist_ok=True); shutil.copyfile(directory/'sdkconfig',clang/'sdkconfig')")
needle="        call('qualify',[sdk_python,'-B',BASE/'qualify.py',backend])"
replacement="""        for name in ('sdkconfig','config/sdkconfig.json','config/sdkconfig.h','compile_commands.json'):
            output=compiled/'clang'/name; output.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(clang/name,output)
        call('qualify',[sdk_python,'-B',BASE/'qualify.py',backend])"""
assert needle in text; text=text.replace(needle,replacement)
text=text.replace('Requires a separately root-created release.json.','Authorized RTC-off build; fixed source and preserved-input guards apply.')
text=text.replace('Preparation of this file is not authorization to configure or compile.','Root authorized compilation after bounded preflight; retain the 2 GiB space guard.')
assert 'release' not in text.replace('released','').replace('release.json','')
(BASE/'execute.py').write_text(text,encoding='utf-8',newline='\n')
print('Prepared RTC-off execute recipe; not executed.')

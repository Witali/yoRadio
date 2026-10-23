from pathlib import Path
import difflib
import importlib.util
import subprocess

root=Path(__file__).resolve().parents[1]
path='idf/esp32c3-oled-native/main/web_upload.c'
spec=importlib.util.spec_from_file_location('extract',root/'tests/run-web-warning-regressions.py')
helpers=importlib.util.module_from_spec(spec);spec.loader.exec_module(helpers)
old=subprocess.check_output(['git','show','HEAD:'+path],cwd=root).decode()
current=(root/path).read_text()
before=helpers.function(old,'receive_form')
after=helpers.function(current,'receive_form')
assert old.count(before)==1 and before!=after
desired=old.replace(before,after)
patch=''.join(difflib.unified_diff(old.splitlines(True),desired.splitlines(True),fromfile='a/'+path,tofile='b/'+path)).encode()
(root/'.build/multipart-receiver-staged.patch').write_bytes(patch)
subprocess.run(['git','apply','--cached','--check','--whitespace=error'],input=patch,cwd=root,check=True)
subprocess.run(['git','apply','--cached','--whitespace=error'],input=patch,cwd=root,check=True)

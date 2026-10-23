from pathlib import Path
import difflib
import subprocess

root=Path(__file__).resolve().parents[1]
desired={}
path='idf/esp32-cyd2usb-native/main/CMakeLists.txt'
old=subprocess.check_output(['git','show','HEAD:'+path],cwd=root).decode()
needle='  PRIV_REQUIRES esp-tls)\n'
assert old.count(needle)==1
desired[path]=old.replace(needle,needle+'\ninclude("${CMAKE_CURRENT_LIST_DIR}/compat/httpd_rfc6455/enable.cmake")\nnative_enable_httpd_rfc6455()\n')
path='idf/esp32c3-oled-native/main/CMakeLists.txt'
old=subprocess.check_output(['git','show','HEAD:'+path],cwd=root).decode()
needle='\nyoradio_aac_profile()\n'
assert old.count(needle)==1
desired[path]=old.replace(needle,'\ninclude("${CMAKE_CURRENT_LIST_DIR}/../../esp32-cyd2usb-native/main/compat/httpd_rfc6455/enable.cmake")\nnative_enable_httpd_rfc6455()\n'+needle)
path='idf/esp32c3-oled-native/CMakeLists.txt'
current=(root/path).read_text()
needle='  "${CMAKE_CURRENT_LIST_DIR}/../components/native_web_transport"\n'
assert current.count(needle)==1
desired[path]=current.replace(needle,'')
patch=''
for path,target in desired.items():
    old=subprocess.check_output(['git','show','HEAD:'+path],cwd=root).decode()
    patch+=''.join(difflib.unified_diff(old.splitlines(True),target.splitlines(True),fromfile='a/'+path,tofile='b/'+path))
data=patch.encode()
(root/'.build/httpd-overlay-staged.patch').write_bytes(data)
subprocess.run(['git','apply','--cached','--check','--whitespace=error'],input=data,cwd=root,check=True)
subprocess.run(['git','apply','--cached','--whitespace=error'],input=data,cwd=root,check=True)

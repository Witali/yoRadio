import subprocess

path = 'idf/esp32-cyd2usb-native/main/CMakeLists.txt'
old = subprocess.check_output(['git', 'show', 'HEAD:' + path])
anchor = b'    native_stream\n'
assert old.count(anchor) == 1
updated = old.replace(anchor, anchor + b'    native_web_transport\n')
blob = subprocess.check_output(['git', 'hash-object', '-w', '--stdin'], input=updated).decode().strip()
subprocess.run(['git', 'update-index', '--cacheinfo', '100644', blob, path], check=True)

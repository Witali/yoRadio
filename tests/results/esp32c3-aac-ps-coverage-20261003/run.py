from pathlib import Path
import subprocess,time
root=Path.cwd();out=root/'.build/ps-dispatch-investigation'
elf=root/'idf/esp32c3-oled-native/build-qemu-aac-pointer-audit/yoradio_esp32c3_oled_native.elf'
flash=root/'.build/aac-pointer-audit-captures/groovesalad16/flash.bin'
def wsl(p):return '/mnt/c/'+str(p)[3:].replace('\\','/')
command=['wsl.exe','--exec','/mnt/c/Work/yoRadio/.worktree/esp32c3-stream-format/.build/qemu-cache-host/qemu-system-riscv32','-M','esp32c3,audiodev=audio0','-nographic','-no-reboot','-snapshot','-icount','shift=0,align=off,sleep=off','-audiodev',f'wav,id=audio0,path={wsl(out/"audio.wav")},out.frequency=48000','-L','/mnt/c/Work/QEMU-ESP32/share/qemu','-drive',f'file={wsl(flash)},if=mtd,format=raw','-S','-gdb','tcp::1237']
gdb='C:/Work/yoRadio/.idf/tools-v6.0.2/tools/riscv32-esp-elf-gdb/17.1_20260402/riscv32-esp-elf-gdb/bin/riscv32-esp-elf-gdb-no-python.exe'
with (out/'qemu.log').open('w') as qlog,(out/'gdb.log').open('w') as glog:
 q=subprocess.Popen(command,stdout=qlog,stderr=subprocess.STDOUT)
 try:
  time.sleep(1)
  subprocess.run([gdb,'-q','--batch',str(elf),'-x',str(out/'trace.gdb')],stdout=glog,stderr=subprocess.STDOUT,check=True,timeout=180)
  q.wait(timeout=30)
 finally:
  if q.poll() is None:q.terminate();q.wait(timeout=10)

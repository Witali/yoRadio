"""Own one qualified, isolated R06 guest; no guest starts without --execute.

Raw flash, keys, UART, packet capture and debugger logs stay in OS-private temp.
The caller must own any debugger/peer children and stop them before this guest.
"""
import argparse
import contextlib
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import tempfile
import time

BASE=Path(__file__).resolve().parent
ROOT=BASE.parents[1]
LAUNCHER=ROOT/'.build/cws-close26/launch-rfc-target.py'
API=runpy.run_path(str(LAUNCHER),run_name='pressure_host_released_launcher')
require=API['require'];pin=API['pin'];write=API['write'];load=API['load']
DUMP_FAILURE=re.compile(r'network dump write error\s*-\s*stopping dump',re.I)


class Guest:
    def __init__(self, options, prepared):
        self.options=options
        self.q,self.config,self.flash,self.parts,self.helper,self.client,self.binding,self.inputs=prepared
        self.child=None
        self.private=None
        self.health=None
        self.endpoint=None
        self.started=None
        self.report=dict(state='NOT_STARTED',source_commit=API['SOURCE'],checkout_commit=API['CHECKOUT'],
            backend='continuous',transport=options.transport,physical_tested=False,
            qualified_image=self.q['image'],qualified_elf=self.q['elf'],qualified_config=self.q['config'],
            original_memory_gate=pin(options.memory_gate),base_launcher=pin(LAUNCHER),host=pin(Path(__file__)),
            firmware_or_config_modified=False,guest_observer=False,pressure_proved=False)

    def save(self):
        if self.started is not None:
            self.report['elapsed_seconds']=round(time.monotonic()-self.started,3)
        write(self.options.output/'host.json',self.report)

    def check(self):
        require(self.child is not None and self.child.poll() is None,'owned-guest-exited')
        require((self.private/'qemu-uart.log').stat().st_size<=4*1024*1024,'uart-capture-bound')
        capture=self.private/'wire.pcap'
        if capture.exists():
            require(capture.stat().st_size<=4*1024*1024,'pcap-capture-bound')
        else:
            require(time.monotonic()-self.started<10,'pcap-not-created')
        uart=(self.private/'qemu-uart.log').read_text(errors='replace')
        require(not self.helper['FATAL'].search(uart),'guest-fatal-marker')
        require(not DUMP_FAILURE.search(uart),'passive-capture-write-error')
        return uart

    def __enter__(self):
        self.started=time.monotonic()
        parent=API['external'](self.options.private_parent or Path(tempfile.gettempdir()))
        require(parent.is_dir(),'external-private-parent-required')
        self.private=Path(tempfile.mkdtemp(prefix='yoradio-r06-',dir=parent)).resolve()
        require(self.private.parent==parent,'private-owner-mismatch')
        self.options.output.mkdir(parents=True,exist_ok=False)
        self.report.update(state='STARTING',private_run_basename=self.private.name,
            private_material_outside_repository=True,private_material_retained=True)
        try:
            if self.options.transport=='wss':
                nvs,tls=API['provision'](self.options,self.private)
                self.flash[0x9000:0xe000]=nvs
                self.binding['certificate_sha256']=tls['certificate_sha256']
                self.report['tls_offline']=tls
            self.flash_hash=hashlib.sha256(self.flash).hexdigest()
            self.flash_path=self.private/'flash.bin'
            self.flash_path.write_bytes(self.flash)
            self.web_port=self.helper['local_port']()
            self.gdb_port=self.helper['local_port']()
            require(self.web_port!=self.gdb_port,'distinct-listeners-required')
            command=[str(self.options.qemu.resolve()),'-global','driver=ssi.esp32.spi,property=input-delay-ns,value=25',
                '-audiodev','none,id=quiet','-M','esp32,st7789=on,audiodev=quiet,dac-rate=48000',
                '-smp','2','-L',str(self.options.rom.resolve()),'-display','none','-monitor','none',
                '-serial','stdio','-no-reboot','-snapshot','-gdb','tcp:127.0.0.1:'+str(self.gdb_port),
                '-nic','user,model=open_eth,restrict=on,id=r06net,hostfwd=tcp:127.0.0.1:'+str(self.web_port)+
                '-:'+('443'if self.options.transport=='wss'else'80'),
                '-object','filter-dump,id=r06wire,netdev=r06net,file='+str(self.private/'wire.pcap').replace(',',',,')+',maxlen=160',
                '-drive','file='+str(self.flash_path).replace(',',',,')+',if=mtd,format=raw']
            write(self.private/'actual-command.json',command)
            self.report.update(binding=self.binding,host_loopback_port=self.web_port,gdb_loopback_port=self.gdb_port,
                passive_capture=dict(max_packet_bytes=160,max_file_bytes=4*1024*1024,netdev='r06net'),
                debugger_attached=False)
            self.log=(self.private/'qemu-uart.log').open('xb')
            self.child=subprocess.Popen(command,cwd=self.private,stdin=subprocess.DEVNULL,stdout=self.log,
                stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
            self.report['qemu_pid']=self.child.pid
            self.save()
            self.endpoint=self.client['Endpoint'](self.options.transport+'://localhost:'+str(self.web_port)+'/ws',
                self.options.ca,self.binding.get('certificate_sha256'))
            self.health=self.client['Health'](self.endpoint)
            until=time.monotonic()+API['BOOT_SECONDS']
            while time.monotonic()<until:
                uart=self.check()
                if 'CYD_OPENETH_READY'in uart and ('Native HTTPS server started'if self.options.transport=='wss'else'Native HTTP server started')in uart:
                    try:
                        health=self.health.read()
                        status=self.health.read('/api/native/status')
                    except (OSError,http.client.HTTPException,self.client['CheckFailure']):
                        self.health.close();time.sleep(.2);continue
                    require(health['allocation_failures']==0 and status['audio']is False,'clean-idle-boot-required')
                    require((self.private/'wire.pcap').is_file() and (self.private/'wire.pcap').stat().st_size>=24,'passive-capture-not-ready')
                    self.report.update(state='READY',initial_health=self.client['health_summary'](health),
                        initial_status={key:status.get(key)for key in ('audio','generation','format')})
                    self.health.close()
                    self.save()
                    return self
                time.sleep(.2)
            raise API['Reject']('guest-boot-deadline')
        except BaseException:
            self.__exit__(*__import__('sys').exc_info())
            raise

    def __exit__(self,kind,error,traceback):
        if self.health is not None:
            with contextlib.suppress(Exception):self.health.close()
        if self.endpoint is not None:
            with contextlib.suppress(Exception):self.endpoint.abort_owned()
        try:
            API['terminate_owned'](self.child)
        finally:
            if hasattr(self,'log'):self.log.close()
            self.report['owned_guest_stopped']=self.child is None or self.child.poll()is not None
            self.report['capture_stopped']=self.child is not None and self.child.poll()is not None and (self.private/'wire.pcap').is_file()
            self.report['qemu_exit_code']=None if self.child is None else self.child.returncode
            checks=('owned_guest_stopped','all_input_pins_still_match','host_and_launcher_pins_still_match',
                'checkout_commit_still_matches','flash_unchanged','fatal_markers_absent','capture_write_errors_absent','capture_stopped')
            try:
                self.report['all_input_pins_still_match']=all(pin(path)==identity for path,identity in self.inputs.items())
                self.report['host_and_launcher_pins_still_match']=(pin(Path(__file__))==self.report['host'] and
                    pin(LAUNCHER)==self.report['base_launcher'])
                self.report['checkout_commit_still_matches']=API['git']('rev-parse','HEAD')==API['CHECKOUT']
                self.report['flash_unchanged']=hasattr(self,'flash_path') and pin(self.flash_path)['sha256']==self.flash_hash
                uart_path=self.private/'qemu-uart.log'
                uart=uart_path.read_text(errors='replace')if uart_path.is_file()else''
                self.report['fatal_markers_absent']=uart_path.is_file() and not self.helper['FATAL'].search(uart)
                self.report['capture_write_errors_absent']=uart_path.is_file() and not DUMP_FAILURE.search(uart)
            except Exception as final_error:
                self.report.update(state='TERMINAL_NONPASS',final_check_category=type(final_error).__name__)
            if not all(self.report.get(key)is True for key in checks):
                self.report.update(state='TERMINAL_NONPASS',category='final-owner-input-or-capture-check-failed')
            if kind is not None:self.report.update(state='TERMINAL_NONPASS',category=type(error).__name__)
            if self.options.output.exists():self.save()
        return False


def main():
    parser=argparse.ArgumentParser(add_help=False)
    parser.add_argument('--mode',choices=('boot',),default='boot')
    known,rest=parser.parse_known_args()
    options=API['options'](rest)
    prepared=API['preflight'](options)
    if not options.execute:
        print(json.dumps(dict(state='PREFLIGHT_PASS',mode=known.mode,guest_started=False)))
        return
    with Guest(options,prepared)as guest:
        guest.report.update(state='BOOT_PROBE_PASS',pressure_proved=False,
            scope='Pinned guest boot with accepted passive netdev filter and debugger listener; no pressure or debugger witness claimed')
        guest.save()
    require(guest.report['owned_guest_stopped']and guest.report['all_input_pins_still_match']and guest.report['host_and_launcher_pins_still_match']and
        guest.report['checkout_commit_still_matches']and guest.report.get('flash_unchanged'),'final-owner-or-input-check-failed')
    print(json.dumps(dict(state=guest.report['state'],guest_stopped=True,pressure_proved=False)))


if __name__=='__main__':
    try:main()
    except Exception as error:
        print(json.dumps(dict(state='TERMINAL_NONPASS',category=type(error).__name__)))
        raise SystemExit(1)

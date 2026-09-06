"""Bounded UART TX log capture; never send application commands on GPIO3."""
import argparse
import time
import serial

p = argparse.ArgumentParser()
p.add_argument('--port', default='COM8')
p.add_argument('--seconds', type=float, default=55)
p.add_argument('--reset', action='store_true')
a = p.parse_args()
with serial.Serial(port=None, baudrate=115200, timeout=.2) as uart:
    uart.port = a.port
    uart.dtr = False
    uart.rts = False
    uart.open()
    if a.reset:
        uart.rts = True
        time.sleep(.15)
        uart.rts = False
    until = time.monotonic() + a.seconds
    while time.monotonic() < until:
        data = uart.read(4096)
        if data:
            print(data.decode('utf-8', errors='replace'), end='', flush=True)

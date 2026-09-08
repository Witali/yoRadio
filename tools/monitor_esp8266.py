"""Bounded UART TX log capture; never send application commands on GPIO3."""
import argparse
import sys
import time
from pathlib import Path
import serial

# The boot ROM uses a different baud rate; malformed bytes must not crash a
# Windows console configured with a legacy code page during log capture.
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = argparse.ArgumentParser()
p.add_argument('--port', default='COM8')
p.add_argument('--seconds', type=float, default=55)
p.add_argument('--reset', action='store_true')
p.add_argument('--reconnect', action='store_true', help='Retry a disconnected USB adapter without resetting the board')
p.add_argument('--stop-file', help='Exit gracefully when this marker file exists')
a = p.parse_args()
until = time.monotonic() + a.seconds
reset_pending = a.reset

def running():
    return time.monotonic() < until and not (a.stop_file and Path(a.stop_file).exists())

while running():
    try:
        with serial.Serial(port=None, baudrate=115200, timeout=.2) as uart:
            uart.port = a.port
            uart.dtr = False
            uart.rts = False
            uart.open()
            print(f'monitor: connected {a.port}; reset={reset_pending}', flush=True)
            if reset_pending:
                uart.rts = True
                time.sleep(.15)
                uart.rts = False
                reset_pending = False
            while running():
                data = uart.read(4096)
                if data:
                    print(data.decode('utf-8', errors='replace'), end='', flush=True)
        break
    except (serial.SerialException, OSError) as error:
        if not a.reconnect:
            raise
        print(f'\nmonitor: adapter disconnected; retry without reset: {error}', flush=True)
        if running():
            time.sleep(.5)

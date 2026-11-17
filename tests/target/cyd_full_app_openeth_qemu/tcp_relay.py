"""Connect one QEMU guestfwd command to the loopback TLS fixture."""
import os
import socket
import sys
import threading


def copy_to_peer(peer):
    try:
        while data := os.read(sys.stdin.fileno(), 32768):
            peer.sendall(data)
    except OSError:
        pass
    try:
        peer.shutdown(socket.SHUT_WR)
    except OSError:
        pass


def main():
    with socket.create_connection(('127.0.0.1', int(sys.argv[1]))) as peer:
        peer.settimeout(None)
        threading.Thread(target=copy_to_peer, args=(peer,), daemon=True).start()
        try:
            while data := peer.recv(32768):
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
        except OSError:
            pass


if __name__ == '__main__':
    main()

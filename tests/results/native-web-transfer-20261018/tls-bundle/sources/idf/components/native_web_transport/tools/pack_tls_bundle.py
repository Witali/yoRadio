"""Create a private NTLS bundle or NVS CSV outside the source repository.

This does not contact a device, erase/write NVS, generate an identity, or install
trust. The native provisioning API repeats certificate/key validation on device.
"""
import argparse
import os
from pathlib import Path
import ssl
import struct

CERT_MAX = 8192
KEY_MAX = 4096


def repository_roots():
    return tuple(p for p in Path(__file__).resolve().parents if (p / '.git').exists())


def check_secret_destination(path, roots=None):
    destination = Path(path).resolve()
    for root in repository_roots() if roots is None else roots:
        if destination.is_relative_to(Path(root).resolve()):
            raise ValueError('Secret output must be outside the source repository')
    return destination


def read_bounded(path, maximum):
    with Path(path).open('rb') as stream:
        data = stream.read(maximum + 1)
    if not data or len(data) > maximum or b'\0' in data:
        raise ValueError('PEM input is empty, oversized, or contains NUL bytes')
    return data


def build_bundle(certificate=b'', key=b'', maintenance=False):
    if maintenance:
        if certificate or key:
            raise ValueError('Maintenance mode does not contain credentials')
    elif (not certificate or not key or len(certificate) > CERT_MAX or
          len(key) > KEY_MAX or b'\0' in certificate or b'\0' in key):
        raise ValueError('Invalid certificate/key lengths or embedded NUL')
    return struct.pack('<4sHHII', b'NTLS', 1, 0 if maintenance else 1,
                       len(certificate), len(key)) + certificate + key


def encode_output(bundle, nvs_csv=False):
    if not nvs_csv:
        return bundle
    return ('key,type,encoding,value\nweb_tls,namespace,,\n'
            'bundle,data,hex2bin,' + bundle.hex() + '\n').encode('ascii')


def write_secret(path, data):
    destination = check_secret_destination(path)
    # Exclusive creation avoids overwriting another identity or following a
    # final-component symlink. The containing directory must be user-private;
    # Windows ACLs remain the user's policy (0600 applies on POSIX systems).
    descriptor = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(data)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path)
    parser.add_argument('--key', type=Path)
    parser.add_argument('--maintenance', action='store_true')
    parser.add_argument('--format', choices=('ntls', 'nvs-csv'), default='ntls')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.maintenance and (args.certificate or args.key):
        parser.error('Maintenance mode cannot include certificate/key inputs')
    if not args.maintenance and (not args.certificate or not args.key):
        parser.error('TLS mode requires certificate and key inputs')
    try:
        check_secret_destination(args.output)
        certificate = key = b''
        if not args.maintenance:
            certificate = read_bounded(args.certificate, CERT_MAX)
            key = read_bounded(args.key, KEY_MAX)
            # Empty password callback avoids an interactive encrypted-key prompt.
            # Reject credentials unsupported by this local validator; the board
            # independently checks its pinned mbedTLS parser and key pairing.
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(args.certificate, args.key, password=lambda: b'')
        bundle = build_bundle(certificate, key, args.maintenance)
        write_secret(args.output, encode_output(bundle, args.format == 'nvs-csv'))
    except (OSError, ValueError, ssl.SSLError):
        parser.exit(1, 'Credential packing failed; check inputs, limits, pairing, '
                       'and a new private output path outside the repository.\n')
    print('Private provisioning output created. No device was modified.')


if __name__ == '__main__':
    main()

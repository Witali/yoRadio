"""Generate an ephemeral CA and server certificate for local TLS record tests.

Keep keys and generated overlays in ignored .build storage. Trust the CA only
in dedicated laboratory firmware, never in production or the operating system.
"""
from datetime import datetime, timedelta, timezone
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID


def generate(host, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    now = datetime.now(timezone.utc)
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'YoRadio ephemeral record-test CA')])
    server_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, host)])
    ca = (x509.CertificateBuilder().subject_name(ca_name).issuer_name(ca_name)
          .public_key(ca_key.public_key()).serial_number(x509.random_serial_number())
          .not_valid_before(now-timedelta(minutes=5)).not_valid_after(now+timedelta(days=2))
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .add_extension(x509.KeyUsage(False, False, False, False, False, True, True, False, False), critical=True)
          .sign(ca_key, hashes.SHA256()))
    try:
        san = x509.IPAddress(ipaddress.ip_address(host))
    except ValueError:
        san = x509.DNSName(host)
    server = (x509.CertificateBuilder().subject_name(server_name).issuer_name(ca_name)
              .public_key(server_key.public_key()).serial_number(x509.random_serial_number())
              .not_valid_before(now-timedelta(minutes=5)).not_valid_after(now+timedelta(days=2))
              .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
              .add_extension(x509.SubjectAlternativeName([san]), critical=False)
              .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
              .add_extension(x509.KeyUsage(True, False, True, False, False, False, False, False, False), critical=True)
              .sign(ca_key, hashes.SHA256()))
    for name, value in (('ca.pem', ca), ('server.pem', server)):
        (output/name).write_bytes(value.public_bytes(serialization.Encoding.PEM))
    (output/'server.key').write_bytes(server_key.private_bytes(serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    # The CA signing key is deliberately not persisted; no more leaves needed.
    return dict(ca=output/'ca.pem', cert=output/'server.pem', key=output/'server.key')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    generate(args.host, args.output)
    print('Created local record-test CA, leaf certificate and private server key.')

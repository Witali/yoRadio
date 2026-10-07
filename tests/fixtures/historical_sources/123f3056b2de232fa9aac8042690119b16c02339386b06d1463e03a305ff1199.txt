"""Create an untrusted localhost/IP certificate for TLS rejection tests only.

Do not install this CA into a production firmware or the operating system.
Write into an ignored .build directory; private keys must not be committed.
"""
import argparse
from datetime import datetime, timedelta, timezone
import ipaddress
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
    name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,args.host)])
    try:
        san=x509.IPAddress(ipaddress.ip_address(args.host))
    except ValueError:
        san=x509.DNSName(args.host)
    now=datetime.now(timezone.utc)
    cert=(x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
          .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=1))
          .not_valid_after(now+timedelta(days=2)).add_extension(x509.SubjectAlternativeName([san]),critical=False)
          .sign(key,hashes.SHA256()))
    for filename,data in [('cert.pem',cert.public_bytes(serialization.Encoding.PEM)),
                          ('key.pem',key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))]:
        # Never silently replace a key/certificate already used by another test.
        with (args.output/filename).open('xb') as stream:
            stream.write(data)
    print('Created untrusted test certificate and private key in the selected directory.')


if __name__ == '__main__':
    main()

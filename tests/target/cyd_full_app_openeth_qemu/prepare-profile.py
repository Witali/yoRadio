"""Make an OpenETH sdkconfig from a built CYD production sdkconfig."""
import argparse
from datetime import datetime, timedelta, timezone
import ipaddress
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]


def write_local_ca(output, address='10.0.2.100'):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

    now = datetime.now(timezone.utc)

    def name(text):
        return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, text)])

    def certificate(subject, issuer, key):
        return (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
                .public_key(key.public_key()).serial_number(x509.random_serial_number())
                .not_valid_before(now - timedelta(hours=1)).not_valid_after(now + timedelta(days=1)))

    ca_name = name('CYD OpenETH local diagnostic CA')
    ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    ca = (certificate(ca_name, ca_name, ca_key)
          .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
          .sign(ca_key, hashes.SHA256()))
    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    server = (certificate(name(address), ca_name, server_key)
              .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
              .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(address))]), critical=False)
              .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
              .sign(ca_key, hashes.SHA256()))
    (output / 'ca.pem').write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    (output / 'server.pem').write_bytes(server.public_bytes(serialization.Encoding.PEM))
    (output / 'server-key.pem').write_bytes(server_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdkconfig', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    tls = parser.add_mutually_exclusive_group()
    tls.add_argument('--tls-diagnostics', action='store_true', help='Use a 30 s task watchdog, telemetry and a disposable local CA')
    tls.add_argument('--tls-production-policy', action='store_true',
                     help='Add a disposable CA while retaining quiet production watchdog and instrumentation settings')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT / '.build') or output == ROOT / '.build':
        raise ValueError('Use a fresh profile directory under the project .build')
    seed = args.sdkconfig.read_text()
    if not re.search(r'^CONFIG_IDF_TARGET="esp32"$', seed, re.M):
        raise ValueError('Expected a classic ESP32 production sdkconfig')
    if args.tls_production_policy and re.search(r'^CONFIG_YORADIO_NATIVE_DIAGNOSTICS=y$', seed, re.M):
        raise ValueError('Production-policy TLS requires a quiet source sdkconfig')
    output.mkdir(parents=True)
    values = {'ETH_USE_OPENETH': 'y', 'ETH_USE_ESP32_EMAC': 'n'}
    if args.tls_diagnostics or args.tls_production_policy:
        write_local_ca(output)
        values.update(MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE='y',
                      MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH=f'"{(output / "ca.pem").as_posix()}"')
    if args.tls_diagnostics:
        values.update(ESP_TASK_WDT_TIMEOUT_S='30', YORADIO_NATIVE_DIAGNOSTICS='y')
    for key, value in values.items():
        seed = re.sub(rf'(?m)^(?:CONFIG_{key}=.*|# CONFIG_{key} is not set)\n?', '', seed)
        seed += f'\nCONFIG_{key}={value}\n'
    (output / 'sdkconfig').write_text(seed, encoding='utf-8', newline='\n')


if __name__ == '__main__':
    main()

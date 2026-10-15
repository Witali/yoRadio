"""Prepare isolated TLS-record diagnostic; never install trust into the OS."""
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib, ipaddress, json
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID

base=Path('.build/c3-confirm-tls-lab-20261015')
trust=base/'trust';trust.mkdir()
now=datetime.now(timezone.utc)
issuer=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'YoRadio local TLS test 20261015')])
ca_key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
ca=(x509.CertificateBuilder().subject_name(issuer).issuer_name(issuer).public_key(ca_key.public_key())
    .serial_number(x509.random_serial_number()).not_valid_before(now-timedelta(minutes=5))
    .not_valid_after(now+timedelta(days=2)).add_extension(x509.BasicConstraints(ca=True,path_length=0),critical=True)
    .sign(ca_key,hashes.SHA256()))
key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
leaf=(x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'192.168.100.253')]))
    .issuer_name(issuer).public_key(key.public_key()).serial_number(x509.random_serial_number())
    .not_valid_before(now-timedelta(minutes=5)).not_valid_after(now+timedelta(days=2))
    .add_extension(x509.BasicConstraints(ca=False,path_length=None),critical=True)
    .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address('192.168.100.253'))]),critical=False)
    .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]),critical=False)
    .sign(ca_key,hashes.SHA256()))
for name,data in [('ca.pem',ca.public_bytes(serialization.Encoding.PEM)),
                  ('server.pem',leaf.public_bytes(serialization.Encoding.PEM)),
                  ('server.key',key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))]:
    with (trust/name).open('xb') as f:f.write(data)
# No CA private key is saved. The server key stays in this ignored directory.
meta=dict(ca_sha256=hashlib.sha256((trust/'ca.pem').read_bytes()).hexdigest(),
          server_certificate_sha256=hashlib.sha256((trust/'server.pem').read_bytes()).hexdigest(),
          not_after=leaf.not_valid_after_utc.isoformat(),host='192.168.100.253')
(base/'trust-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
old=Path('.build/c3-confirm-probe-20261014')
build=(old/'build.ps1').read_text().replace('build-confirm-probe-20261014','build-confirm-tls-lab-20261015')
build=build.replace('esp32c3-idf61-confirm-probe','esp32c3-idf61-confirm-tls-lab')
build=build.replace('esp32c3-idf61-continuous-confirm/sdkconfig','esp32c3-idf61-confirm-probe/sdkconfig')
build=build.replace("@('YORADIO_PIPELINE_HEALTH_DIAGNOSTIC')","@('MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE')")
build=build.replace('[IO.File]::WriteAllText',
    "$config = [regex]::Replace($config, '(?m)^CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH=.*\\r?\\n?', '')\n"
    "$config += 'CONFIG_MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE_PATH=\""+(trust/'ca.pem').resolve().as_posix()+"\"' + \"`n\"\n"
    '[IO.File]::WriteAllText',1)
build=build.replace('idf61-cprobe-20261014','idf61-ctls-20261015')
(base/'build.ps1').write_text(build)
package=(old/'package.py').read_text().replace('build-confirm-probe-20261014','build-confirm-tls-lab-20261015')
package=package.replace('c3-confirm-probe-20261014','c3-confirm-tls-lab-20261015').replace('esp32c3-idf61-confirm-probe','esp32c3-idf61-confirm-tls-lab')
package=package.replace("'YORADIO_PIPELINE_PROFILE',\n    'MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE'", "'YORADIO_PIPELINE_PROFILE'")
package=package.replace("enabled = (", "enabled = ('MBEDTLS_CUSTOM_CERTIFICATE_BUNDLE', 'MBEDTLS_CERTIFICATE_BUNDLE_DEFAULT_FULL', ",1)
package=package.replace('idf61-cprobe-20261014','idf61-ctls-20261015')
package=package.replace('laboratory_ca=False',"laboratory_ca=True, laboratory_only=True, extra_trust_ca_sha256=sha(OUT/'trust/ca.pem')")
package=package.replace('Diagnostic-only build/link', 'Local-CA diagnostic-only build/link')
(base/'package.py').write_text(package)
print(json.dumps(meta))

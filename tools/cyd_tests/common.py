"""Strict CYD artifact identity and transport; no installation or reboot API."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from tools import export_cyd_production as production
from tools.esp32c3_tests.common import Board, Failure, Report, fixtures, require

OUTPUT_NAMES = {'pdm': 'I2S PDM', 'continuous': 'internal DAC',
                'legacy': 'legacy I2S/DAC x16'}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Artifact:
    app: Path
    backend: str
    hashes: dict
    elf_sha256: str
    diagnostics: bool
    evidence: dict

    def current(self):
        require(all(digest(path.read_bytes()) == value for path, value in self.hashes.items()),
                'Local acceptance artifact changed')


def load_artifact(app, backend):
    """Validate complete ESP image bytes and the exact exported profile offline."""
    require(backend in OUTPUT_NAMES, 'Unknown CYD backend')
    app = Path(app).resolve()
    config, manifest_path = app.with_name('sdkconfig'), app.with_name('manifest.json')
    raw, config_raw, manifest_raw = app.read_bytes(), config.read_bytes(), manifest_path.read_bytes()
    description = production.image_descriptor(raw)  # chip, segments, checksum and complete SHA
    require(description['project_name'] == production.PROJECT_NAME, 'Wrong CYD image project')
    require(description['idf_version'] == production.IDF_VERSION, 'Unexpected CYD image SDK')
    manifest = json.loads(manifest_raw)
    require(type(manifest) is dict and manifest.get('build_check') == 'PASS' and
            manifest.get('target') == 'esp32' and manifest.get('backend') == backend and
            manifest.get('idf_version') == production.IDF_VERSION, 'Wrong exported CYD profile')
    require(manifest.get('app_sha256') == digest(raw) and
            manifest.get('sdkconfig_sha256') == digest(config_raw) and
            manifest.get('elf_sha256') == description['elf_sha256'] and
            manifest.get('app_version') == description['version'] and
            type(manifest.get('app_bytes')) is int and manifest['app_bytes'] == len(raw),
            'Image/config/manifest identity mismatch')
    config_values = production.parse_sdkconfig(config_raw.decode('utf-8'))
    require(config_values.get('IDF_TARGET') == 'esp32' and
            config_values.get('FREERTOS_UNICORE') is False and
            config_values.get(production.BACKENDS[backend]) is True and
            all(config_values.get(key) is not True for name, key in production.BACKENDS.items()
                if name != backend), 'Configuration does not select the CYD two-core/backend profile')
    hashes = {app: digest(raw), config: digest(config_raw), manifest_path: digest(manifest_raw)}
    evidence = dict(target='esp32', project=production.PROJECT_NAME, backend=backend,
                    app_sha256=digest(raw), sdkconfig_sha256=digest(config_raw),
                    manifest_sha256=digest(manifest_raw), elf_sha256=description['elf_sha256'],
                    app_version=description['version'], idf_version=description['idf_version'])
    return Artifact(app, backend, hashes, description['elf_sha256'],
                    config_values.get('YORADIO_NATIVE_DIAGNOSTICS') is True, evidence)


def status_fields(raw):
    require(type(raw) is dict and raw.get('firmware') == 'esp-idf-native', 'Wrong CYD status schema')
    for key in ('audio', 'connecting', 'format_is_pcm', 'channels_are_core'):
        require(type(raw.get(key)) is bool, 'Invalid CYD status flag: ' + key)
    require(raw.get('network') in ('starting', 'client', 'ap', 'error') and
            type(raw.get('format')) is str and len(raw['format']) <= 160 and
            type(raw.get('codec')) is str and raw['codec'] in ('', 'auto', 'AAC', 'MP3', 'FLAC', 'OGG'),
            'Invalid CYD status format/network')
    fields = ('generation', 'bitrate', 'sample_rate_hz', 'channels', 'bits_per_sample',
              'pcm_sample_rate_hz', 'pcm_channels')
    require(all(type(raw.get(k)) is int and 0 <= raw[k] <= 0xffffffff for k in fields),
            'Missing or invalid CYD numeric status')
    result = {key: raw[key] for key in ('firmware', 'network', 'audio', 'connecting', 'format',
                                      'format_is_pcm', 'channels_are_core', 'codec', *fields)}
    result['sample_rate'] = result.pop('sample_rate_hz')
    result['pcm_sample_rate'] = result.pop('pcm_sample_rate_hz')
    return result  # Station names, titles and arbitrary extra fields never enter reports.


class CydBoard(Board):
    """Only playback writes are allowed, each rechecking local and live identity."""
    def __init__(self, origin, artifact, *, transport=None):
        parsed = urlsplit(origin)
        require(parsed.scheme in ('http', 'https') and parsed.hostname and
                not parsed.username and not parsed.password and not parsed.query and
                not parsed.fragment and parsed.path in ('', '/'), 'Expected a plain board origin')
        super().__init__(origin)
        self.artifact, self.transport, self.bound = artifact, transport, False

    def _read(self, path, data=None, timeout=5, *, headers=None):
        if self.transport:
            return self.transport(path, data=data, timeout=timeout, headers=headers)
        return super().request(path, data, timeout, headers=headers)

    def check_identity(self):
        self.artifact.current()
        info = json.loads(self._read('/api/native/ota'))
        require(type(info) is dict and info.get('app_elf_sha256') == self.artifact.elf_sha256 and
                info.get('version') == self.artifact.evidence['app_version'] and
                info.get('partition') in ('app0', 'app1') and
                all(type(info.get(k)) is int and info[k] > 0 for k in ('max_size', 'max_body_size')),
                'Live CYD image identity mismatch')
        capabilities = json.loads(self._read('/api/native/capabilities'))
        require(type(capabilities) is dict and type(capabilities.get('schema')) is int and
                capabilities['schema'] == 1 and capabilities.get('firmware') == 'esp32-cyd2usb-native' and
                capabilities.get('audio_output') == OUTPUT_NAMES[self.artifact.backend],
                'Live CYD backend/capabilities mismatch')
        return {key: info[key] for key in ('app_elf_sha256', 'version', 'partition', 'max_size', 'max_body_size')}

    def authorize(self):
        info = self.check_identity()
        self.bound = True
        return info

    def request(self, path, data=None, timeout=5, *, headers=None):
        if data is not None:
            require(self.bound, 'CYD identity must be bound before playback writes')
            require(path == '/api/native/stop' or
                    re.fullmatch(r'/api/native/play\?codec=(auto|mp3|aac|flac|ogg|opus|vorbis)', path),
                    'This controller permits only playback writes')
            self.check_identity()
        else:
            require(path in ('/api/native/ota', '/api/native/capabilities', '/api/native/status',
                             '/api/native/health', '/api/native/settings', '/api/native/time',
                             '/api/native/network-settings', '/api/native/radio',
                             '/api/native/wifi', '/data/playlist.csv'), 'Unsupported CYD read')
        return self._read(path, data, timeout, headers=headers)

    def status(self):
        return status_fields(self.json('/api/native/status'))

    def settings(self):
        # In-memory equality only. No C3 display commands, station names or passwords.
        fields = {'settings': ('volume', 'balance', 'normalization', 'normgain', 'normtarget', 'normtime'),
                  'time': ('utc_offset_minutes', 'sync_interval_minutes', 'server1', 'server2'),
                  'network-settings': ('hostname', 'ap_timeout_minutes'),
                  'radio': ('smartstart',)}
        result = {}
        for route, keys in fields.items():
            value = self.json('/api/native/' + route)
            require(type(value) is dict and all(key in value for key in keys), 'Missing CYD settings snapshot')
            result[route] = {key: value[key] for key in keys}
        return result

    def reboot(self):
        raise Failure('Playback acceptance has no reboot or deployment operation')


def cyd_fixtures(extra_manifest=None):
    values = fixtures(extra_manifest)
    for spec in values.values():
        if spec['codec'] == 'aac':
            # CYD public decoder reports PCM, not a nominal HE/PS profile tag.
            # Full fixture PCM rate/channels remain mandatory; encoded bytes stay exact.
            spec['label'] = 'AAC PCM'
    return values

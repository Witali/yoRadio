"""Recover the firmware's three HTML documents and apply local-browser fixes."""

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SHA256 = "5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4"
PAGES = {"setup": 0x26EDC, "settings": 0x2963B, "photo": 0x32E6E}


def recover() -> None:
    """Preserve original documents and regenerate browser copies with audited fixes."""
    flash = (ROOT.parent / "full-flash.bin").read_bytes()
    if hashlib.sha256(flash).hexdigest() != SHA256:
        raise ValueError("Unexpected flash snapshot")
    manifest = {"source_sha256": SHA256, "encoding": "GB18030 to UTF-8", "pages": []}
    for name, offset in PAGES.items():
        c_string = flash[offset:flash.index(b"\0", offset)]
        end = c_string.lower().rfind(b"</html>") + len(b"</html>")
        if end < 7:
            raise ValueError("Missing HTML document end")
        raw = c_string[:end]
        (ROOT / "source").mkdir(exist_ok=True)
        (ROOT / "source" / f"{name}.html").write_bytes(raw)
        page = raw.decode("gb18030").replace("\r\n", "\n")
        if name == "settings":
            # Raw-sector flags are part of the factory API: 1 selects Fahrenheit
            # and km/h, despite the opposite captions in the original HTML.
            # The browser-time flag is stored only; no timestamp is ever sent.
            fixes = {
                'Show Temperature in Celsius': 'Show Temperature in Fahrenheit',
                '1=Celsius': '1=Fahrenheit',
                'Mile display:': 'Wind speed in km/h:',
                'Sync phone or PC time:': 'Browser time sync (unavailable):',
                '<input type="checkbox" id="temp-unit-switch">':
                    '<input type="checkbox" id="temp-unit-switch" aria-label="Show temperature in Fahrenheit" disabled>',
                '<input type="checkbox" id="hour-format-switch">':
                    '<input type="checkbox" id="hour-format-switch" aria-label="12-hour clock" disabled>',
                '<input type="checkbox" id="mile-display-switch">':
                    '<input type="checkbox" id="mile-display-switch" aria-label="Wind speed in km/h" disabled>',
                '<input type="checkbox" id="time-sync-switch">':
                    '<input type="checkbox" id="time-sync-switch" aria-label="Browser time sync" disabled '
                    'title="Time is synchronized automatically over Wi-Fi.">',
            }
            for original, corrected in fixes.items():
                if page.count(original) != 1:
                    raise ValueError(f'Missing or ambiguous factory settings control: {original}')
                page = page.replace(original, corrected, 1)
            # The firmware accepts 0..100%; the original 2..99 slider silently
            # clamps the saved default 100% to 99 before the user touches it.
            page = page.replace("min='2' max='99'", "min='0' max='100'")
            # Loading errors must not invent checked defaults and accidentally
            # overwrite other saved flags when one switch is changed.
            start = page.index('function initSwitches() {')
            end = page.index('// 发送开关状态到ESP8266', start)
            page = page[:start] + '''function initSwitches() {
                    // Read actual flags before permitting a combined settings write.
                    const controls = ['temp-unit-switch', 'hour-format-switch', 'mile-display-switch'];
                    const status = document.getElementById('switch-status');
                    controls.forEach(id => document.getElementById(id).disabled = true);
                    status.textContent = 'Loading clock settings…';
                    fetch('/getsettings')
                        .then(response => {
                            if (!response.ok) throw new Error('Cannot load clock settings');
                            return response.json();
                        })
                        .then(data => {
                            if (!data || !['tempUnit', 'hourFormat', 'mileDisplay', 'timeSync'].every(
                                key => data[key] === 0 || data[key] === 1)) {
                                throw new Error('Invalid clock settings');
                            }
                            document.getElementById('temp-unit-switch').checked = data.tempUnit === 1;
                            document.getElementById('hour-format-switch').checked = data.hourFormat === 1;
                            document.getElementById('mile-display-switch').checked = data.mileDisplay === 1;
                            document.getElementById('time-sync-switch').checked = data.timeSync === 1;
                            controls.forEach(id => document.getElementById(id).disabled = false);
                            status.textContent = '';
                        })
                        .catch(error => {
                            console.error('Error loading clock settings:', error);
                            status.textContent = 'Clock settings could not be loaded. Reload to retry.';
                        });
                }

                ''' + page[end:]
            page = page.replace('<!-- 时间格式选择 -->',
                                '<p id="switch-status" role="status" aria-live="polite"></p>\n'
                                '                <!-- 时间格式选择 -->', 1)
            page = page.replace("function refreshList() {",
                                "function refreshList() {\n"
                                "            if (!document.getElementById('wifi_list')) return;", 1)
            # These controls are commented out in the factory settings page.
            # Do not occupy HTTP sessions or scan/disconnect Wi-Fi for absent UI.
            for endpoint, control in [('GetNightStartTime', 'starttime'),
                                      ('GetNightStopTime', 'stoptime')]:
                page = page.replace(f"fetch('/{endpoint}')",
                                    f"if (!document.getElementById('{control}')) return;\n"
                                    f"                    fetch('/{endpoint}')", 1)
            # This initializer is at script scope, unlike the two DOM callbacks
            # above; short-circuit its promise chain instead of returning.
            page = page.replace("fetch('/get_night_brightness')",
                                "NightbrightnessSlider && fetch('/get_night_brightness')", 1)
            page = page.replace("const select = document.getElementById('wifi_list');",
                                "const select = document.getElementById('wifi_list');\n"
                                "                    if (!select) return;")
            for variable in ["StartTimeSelect", "StopTimeSelect", "NightbrightnessSlider"]:
                page = page.replace(f"{variable}.value =", f"if ({variable}) {variable}.value =")
            for target in ["NightbrightnessSlider", "counter",
                           "document.getElementById('wifiscanForm')",
                           "document.getElementById('advancedSettingsForm')"]:
                page = page.replace(f"{target}.addEventListener", f"{target}?.addEventListener")
        if name == "setup":
            page = page.replace("function handleResponse(response)", "function readResponse(response)")
            page = page.replace(".then(handleResponse)", ".then(readResponse).then(handleResponse)")
        if name == "photo":
            # Keep the factory bytes in source/; working pages allow the user
            # to select a source square instead of always taking the center.
            crop_ui = (ROOT / 'photo_crop.html').read_text(encoding='utf-8')
            crop_script = (ROOT / 'photo_crop.js').read_text(encoding='utf-8')
            page = page.replace('<script>', crop_ui + '\n<script>', 1)
            start = page.index('        function resizeAndCropImage(file) {')
            start = page.rfind('        /**', 0, start)
            end = page.index('        async function handleFileUpload', start)
            if start < 0:
                raise ValueError('Missing factory image processing block')
            page = page[:start] + crop_script + '\n\n' + page[end:]
            # Keep the factory protocol while pacing writes by actual ACKs,
            # without a sleep after success or after the last failed attempt.
            start = page.index('        async function uploadImageInChunks(file, fileNumber) {')
            start = page.rfind('        /**', 0, start)
            end = page.index('        // 分块下载图片', start)
            if start < 0:
                raise ValueError('Missing factory upload block')
            upload_script = (ROOT / 'photo_upload.js').read_text(encoding='utf-8')
            page = page[:start] + upload_script + '\n\n' + page[end:]
            # Browser Canvas encoders may insert ICC APP2 even after EXIF was
            # removed by drawing pixels. Strip all APP/COM before device upload.
            cleaner = (ROOT / 'jpeg_metadata.js').read_text(encoding='utf-8')
            page = page.replace('<script>', '<script>\n' + cleaner, 1)
            original = 'const processedFile = new File([processedBlob],'
            if page.count(original) != 1:
                raise ValueError('Missing or ambiguous processed Canvas upload')
            page = page.replace(original,
                'const cleanBlob = await stripCanvasJpegMetadata(processedBlob);\n'
                '                const processedFile = new File([cleanBlob],', 1)
            page = page.replace('URL.createObjectURL(processedBlob)', 'URL.createObjectURL(cleanBlob)')
            page = page.replace('$${', '${')
            page = page.replace("console.error('Upload process error:', error);",
                "if (error.name !== 'AbortError') console.error('Upload process error:', error);")
            page = page.replace("showStatus(`Error: ${error.message}`, 'error');",
                "showStatus(error.name === 'AbortError' ? 'Upload cancelled' : `Error: ${error.message}`,\n"
                "                    error.name === 'AbortError' ? 'info' : 'error');", 1)
            page = page.replace("type === 'success' ? 'status-success' : 'status-error'",
                "type === 'success' ? 'status-success' : type === 'error' ? 'status-error' : ''", 1)
        page = page.replace("window.location.href = 'about:blank'", "window.location.href = '/'")
        nav = ('\n<nav aria-label="Pages" style="text-align:center;padding:10px;'
               'font:14px Arial,sans-serif;margin-bottom:12px">'
               '<a href="/settings">Clock Settings</a> &middot; '
               '<a href="/photo">Photos</a> &middot; '
               '<a href="/setup">Wi-Fi Setup</a></nav>\n')
        page = page.replace("<body>", "<body>" + nav, 1)
        (ROOT / "pages").mkdir(exist_ok=True)
        page = "\n".join(line.rstrip() for line in page.splitlines()).rstrip() + "\n"
        rendered = page.encode("utf-8")
        (ROOT / "pages" / f"{name}.html").write_bytes(rendered)
        manifest["pages"].append({
            "name": name, "flash_offset": f"0x{offset:06x}",
            "original_document_bytes": len(raw), "c_string_bytes": len(c_string),
            "ignored_trailing_bytes_hex": c_string[end:].hex(),
            "original_sha256": hashlib.sha256(raw).hexdigest(),
            "local_page_sha256": hashlib.sha256(rendered).hexdigest(),
        })
    (ROOT / "pages-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n",
                                             encoding="utf-8", newline="\n")
    print("Recovered setup, settings and photo pages from the verified dump.")


if __name__ == "__main__":
    recover()

"""Recover the firmware's three HTML documents and apply local-browser fixes."""

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
SHA256 = "5321a6b9016a8fc8335958193b4ab182e0d9ea85cfc3363063f120080c1844f4"
PAGES = {"setup": 0x26EDC, "settings": 0x2963B, "photo": 0x32E6E}


def recover() -> None:
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

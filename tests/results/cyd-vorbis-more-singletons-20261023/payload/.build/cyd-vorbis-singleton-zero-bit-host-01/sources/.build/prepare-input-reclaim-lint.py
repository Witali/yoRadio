from pathlib import Path

root=Path.cwd()
old=root/'.build/run-output-telemetry-lint-configure.ps1'
body=old.read_text().replace('output-telemetry','input-reclaim')
needle='$seed = [IO.File]::ReadAllText((Join-Path (Get-Location) "$project/build-c3-transfer/sdkconfig"))'
assert body.count(needle)==1
body=body.replace(needle,needle+'\n$seed = [regex]::Replace($seed, "(?m)^(?:# )?CONFIG_YORADIO_TLS_INPUT_RECLAIM[^\\r\\n]*(?:\\r?\\n)?", "")\n$seed += "`nCONFIG_YORADIO_TLS_INPUT_RECLAIM=y`n"')
(root/'.build/run-input-reclaim-lint-configure.ps1').write_text(body)
body=(root/'.build/run-output-telemetry-lint.py').read_text().replace('output-telemetry','input-reclaim')
needle="        assert config['ESP_DEFAULT_CPU_FREQ_MHZ'] == 240"
assert body.count(needle)==1
body=body.replace(needle,needle+"\n        assert config['YORADIO_TLS_INPUT_RECLAIM']")
needle="    paths.update(p for p in (ROOT / 'tools').glob('patch_*.py') if p.is_file())"
assert body.count(needle)==1
body=body.replace(needle,needle+"\n    paths.update(p for p in (ROOT / project / 'main/compat').rglob('*.cmake') if p.is_file())")
(root/'.build/run-input-reclaim-lint.py').write_text(body)

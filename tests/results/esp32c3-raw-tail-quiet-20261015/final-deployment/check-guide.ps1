$ErrorActionPreference = 'Stop'
$guide = [IO.File]::ReadAllText((Join-Path $PWD 'docs/ESP32C3_BEGINNERS_GUIDE.md'))
$blocks = [regex]::Matches($guide, '(?s)```powershell\r?\n(.*?)```')
foreach ($block in $blocks) {
    $parseTokens = $null; $parseErrors = $null
    [void][Management.Automation.Language.Parser]::ParseInput($block.Groups[1].Value, [ref]$parseTokens, [ref]$parseErrors)
    if ($parseErrors.Count) { throw ($parseErrors | Out-String) }
}
$variant = 'esp32c3-idf61-raw-tail-quiet'
$firmware = Join-Path $PWD "firmware/development/$variant"
$installFiles = Join-Path $PWD 'firmware/development/esp32c3-oled-native-installation'
$selection = [regex]::Match($guide, '(?s)(\$bootloader = Join-Path.*?)(?=\r?\n& \$flashPython)')
if (-not $selection.Success) { throw 'Boot-file selection block missing' }
& ([scriptblock]::Create($selection.Groups[1].Value))
Write-Output "PowerShell syntax: $($blocks.Count) blocks PASS; current variant file hashes PASS"

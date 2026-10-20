[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$reclaimGitCount = if ($env:GIT_CONFIG_COUNT) { [int]$env:GIT_CONFIG_COUNT } else { 0 }
Set-Item -Path "Env:GIT_CONFIG_KEY_$reclaimGitCount" -Value 'core.longpaths'
Set-Item -Path "Env:GIT_CONFIG_VALUE_$reclaimGitCount" -Value 'true'
$env:GIT_CONFIG_COUNT = ($reclaimGitCount + 1).ToString()
& C:/Work/yoRadio/.idf/python-3.12.10/tools/python.exe -B -X utf8 .build/input-reclaim-production-preflight.py
if ($LASTEXITCODE -ne 0) { throw 'Seven-profile production preflight failed' }
$reclaimProfiles = Get-Content -LiteralPath '.build/input-reclaim-production-profiles.json' -Raw | ConvertFrom-Json
foreach ($profile in $reclaimProfiles) {
    $evidence = @('tests/results/cyd-input-reclaim-20261020/README.md',
                  'tests/results/cyd-http-request-buffer-20261020/README.md')
    if ($profile.custom_flac) { $evidence += 'tests/results/cyd-flac-runtime-20261019/README.md' }
    Write-Output "Building $($profile.variant)"
    & ./idf/esp32-cyd2usb-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf `
        -BuildDirectory $profile.build_directory -Sdkconfig $profile.sdkconfig `
        -AudioBackend $profile.backend -Variant $profile.variant -Evidence $evidence
    if ($LASTEXITCODE -ne 0) { throw "Production export failed: $($profile.variant)" }
}

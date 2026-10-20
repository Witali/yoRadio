param(
    [ValidateSet('c3','pdm','continuous','legacy','custom-pdm')][string]$Backend,
    [switch]$Child
)
$ErrorActionPreference='Stop'
if ($Child) {
    $env:PYTHONUTF8='1'
    $powerGitConfigCount=if($env:GIT_CONFIG_COUNT){[int]$env:GIT_CONFIG_COUNT}else{0}
    Set-Item -Path "Env:GIT_CONFIG_KEY_$powerGitConfigCount" -Value 'core.longpaths'
    Set-Item -Path "Env:GIT_CONFIG_VALUE_$powerGitConfigCount" -Value 'true'
    $env:GIT_CONFIG_COUNT=($powerGitConfigCount+1).ToString()
    if ($Backend -eq 'c3') {
        & ./idf/esp32c3-oled-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf -TestedRadioProfile -BuildDirectory build-c3-transfer -Sdkconfig build-c3-transfer/sdkconfig -FirmwareOutputDirectory firmware/development/esp32c3-oled-native-network-power
    } elseif ($Backend -eq 'custom-pdm') {
        $powerCustomBuild=[IO.Path]::GetFullPath((Join-Path (Get-Location) '.build/cyd-flac-runtime-sdk-custom'))
        & ./idf/esp32-cyd2usb-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $powerCustomBuild -Sdkconfig "$powerCustomBuild/sdkconfig" -AudioBackend pdm -Variant 'esp32-cyd2usb-native-network-power-custom-flac-pdm' -Evidence @('tests/results/network-power-transfer-20261019/README.md','tests/results/cyd-flac-runtime-20261019/README.md')
    } else {
        $powerBuildDirectory=switch($Backend){'pdm'{'build-c3-transfer'} 'continuous'{'build-c3-transfer-dac'} 'legacy'{'build-c3-transfer-legacy'}}
        & ./idf/esp32-cyd2usb-native/build-production.ps1 -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $powerBuildDirectory -Sdkconfig "$powerBuildDirectory/sdkconfig" -AudioBackend $Backend -Variant "esp32-cyd2usb-native-network-power-$Backend" -Evidence @('tests/results/network-power-transfer-20261019/README.md')
    }
    exit $LASTEXITCODE
}
$powerLogBase=Join-Path (Get-Location) ".build/power-production-$Backend"
$powerArguments=@('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Backend',$Backend)
$powerProcess=Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $powerArguments -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$powerLogBase.out.log" -RedirectStandardError "$powerLogBase.err.log"
if ($powerProcess.ExitCode -ne 0) {
    Get-Content -LiteralPath "$powerLogBase.out.log" -Tail 15
    Get-Content -LiteralPath "$powerLogBase.err.log" -Tail 12
    exit $powerProcess.ExitCode
}
Get-Content -LiteralPath "$powerLogBase.out.log" -Tail 7
exit 0

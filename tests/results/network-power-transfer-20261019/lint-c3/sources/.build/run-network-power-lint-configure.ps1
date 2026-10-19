param([ValidateSet('cyd','c3')][string]$Board, [switch]$Child)
$ErrorActionPreference = 'Stop'
$project = if ($Board -eq 'cyd') { 'idf/esp32-cyd2usb-native' } else { 'idf/esp32c3-oled-native' }
$build = 'build-lint-network-power-final02'
if ($Child) {
    & "$project/build.ps1" -DependencyRoot C:/Work/yoRadio/.idf -BuildDirectory $build -Sdkconfig "$build/sdkconfig" -IdfArguments @('-D','IDF_TOOLCHAIN=clang','reconfigure')
    exit $LASTEXITCODE
}
$directory = Join-Path (Get-Location) "$project/$build"
if (Test-Path -LiteralPath $directory) { throw "Preserve earlier configure: $directory" }
New-Item -ItemType Directory -Path $directory | Out-Null
$seed = [IO.File]::ReadAllText((Join-Path (Get-Location) "$project/build-c3-transfer/sdkconfig"))
[IO.File]::WriteAllText((Join-Path $directory 'sdkconfig'), $seed, [Text.UTF8Encoding]::new($false))
$base = Join-Path (Get-Location) ".build/network-power-lint-configure-$Board-02"
$childArgs = @('-NoLogo','-NoProfile','-NonInteractive','-File',$PSCommandPath,'-Child','-Board',$Board)
$job = Start-Process -FilePath (Get-Command pwsh).Source -ArgumentList $childArgs -WindowStyle Hidden -Wait -PassThru -RedirectStandardOutput "$base.out.log" -RedirectStandardError "$base.err.log"
if ($job.ExitCode -ne 0) {
    Get-Content -LiteralPath "$base.out.log" -Tail 18
    Get-Content -LiteralPath "$base.err.log" -Tail 18
    exit $job.ExitCode
}
Get-Content -LiteralPath "$base.out.log" -Tail 6
exit 0

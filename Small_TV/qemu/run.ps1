[CmdletBinding()]
param(
    [ValidateSet('prepare','start','test','status','stop','reset','screenshot')][string]$Action='start',
    [ValidateSet('original','reconstructed')][string]$Firmware='reconstructed',
    [string]$QemuRoot='C:\Work\QEMU-ESP32',
    [string]$QemuExecutable,
    [string]$StateDirectory,
    [ValidateSet('clock','setup','offline')][string]$Network='clock',
    [ValidateSet('sdl','none')][string]$Display='sdl',
    [ValidateRange(-1,65535)][int]$HttpBasePort=0,
    [ValidateRange(0,65535)][int]$ServicePort=0,
    [string[]]$ServiceUrl=@(),
    [ValidateRange(5,3600)][int]$TestSeconds=30,
    [ValidateRange(0,65535)][int]$GdbPort=0,
    [string]$ScreenshotPath,
    [switch]$Persistent,
    [switch]$Paused
)
$ErrorActionPreference='Stop'
$repository=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
if(!$StateDirectory){$StateDirectory=Join-Path $repository ".build\small-tv-vm\$Network-$Firmware"}
$launcher=Join-Path $QemuRoot 'run-small-tv-esp32c2.ps1'
if(!(Test-Path -LiteralPath $launcher)){throw "QEMU launcher not found: $launcher"}
$parameters=@{
    Action=$Action; Firmware=$Firmware; YoRadioRepository=$repository;
    HardwareProfile=(Join-Path $PSScriptRoot 'profiles\small-tv-c2.json');
    StateDirectory=[IO.Path]::GetFullPath($StateDirectory); Network=$Network; Display=$Display;
    HttpBasePort=$HttpBasePort; ServicePort=$ServicePort; ServiceUrl=$ServiceUrl;
    TestSeconds=$TestSeconds; GdbPort=$GdbPort; Persistent=$Persistent; Paused=$Paused
}
if($QemuExecutable){$parameters.QemuExecutable=[IO.Path]::GetFullPath($QemuExecutable)}
if($ScreenshotPath){$parameters.ScreenshotPath=[IO.Path]::GetFullPath($ScreenshotPath)}
& $launcher @parameters

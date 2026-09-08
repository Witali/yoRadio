param(
    [ValidateSet('127.0.0.1','192.168.100.253')][string]$Address='192.168.100.253',
    [ValidateRange(1024,65535)][int]$Port=8765,
    [ValidateRange(50,1000)][int]$SampleMs=100
)
$ErrorActionPreference='Stop'
$taskRoot=(Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Add-Type -Path (Join-Path $PSScriptRoot 'NetworkTcpSource.cs')
[NetworkTcpSource]::Run($taskRoot,$Address,$Port,$SampleMs)

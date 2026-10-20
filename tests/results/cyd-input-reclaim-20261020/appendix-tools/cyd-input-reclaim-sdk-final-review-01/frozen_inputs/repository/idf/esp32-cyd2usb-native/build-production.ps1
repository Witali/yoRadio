[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)]
    [string]$DependencyRoot,
    [ValidateSet('pdm', 'continuous', 'legacy')]
    [string]$AudioBackend = 'pdm',
    [string]$BuildDirectory = '',
    [string]$Sdkconfig = '',
    [string]$Variant = '',
    [string]$FirmwareOutputDirectory = '',
    [string[]]$Evidence = @(),
    [switch]$AllowDirty
)

$ErrorActionPreference = 'Stop'
if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw 'Production builds require PowerShell 7, as does the existing native build script.'
}
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$dependencies = [IO.Path]::GetFullPath($DependencyRoot)
$python = Join-Path $dependencies 'python-3.12.10/tools/python.exe'
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Installed bootstrap Python was not found: $python. This wrapper never downloads dependencies."
}
$arguments = @(
    (Join-Path $repository 'tools/export_cyd_production.py'), 'build',
    '--repository', $repository, '--dependency-root', $dependencies,
    '--powershell', (Get-Process -Id $PID).Path, '--backend', $AudioBackend
)
foreach ($entry in @(
    @('--build-dir', $BuildDirectory), @('--sdkconfig', $Sdkconfig),
    @('--variant', $Variant), @('--output-directory', $FirmwareOutputDirectory)
)) {
    if (-not [string]::IsNullOrWhiteSpace($entry[1])) { $arguments += $entry }
}
foreach ($reference in $Evidence) { $arguments += @('--evidence', $reference) }
if ($AllowDirty) { $arguments += '--allow-dirty' }

# Python starts build.ps1 in a separate PowerShell process. An exit in IDF's
# environment scripts cannot terminate this wrapper before the archive step.
& $python @arguments
if ($LASTEXITCODE -ne 0) { throw "Production build/export failed (exit $LASTEXITCODE)." }

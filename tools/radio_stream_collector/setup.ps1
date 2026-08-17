[CmdletBinding()]
param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"
$toolRoot = $PSScriptRoot
$repositoryRoot = [IO.Path]::GetFullPath((Join-Path $toolRoot "..\.."))
$venvRoot = Join-Path $repositoryRoot ".build\radio-stream-collector-venv"
$venvPython = Join-Path $venvRoot "Scripts\python.exe"
$requirements = Join-Path $toolRoot "requirements-radio-streams.txt"
$collector = Join-Path $toolRoot "radio_stream_collector.py"

function Resolve-PythonExecutable {
    param([Parameter(Mandatory)][string]$RequestedCommand)

    $candidates = @()
    $requested = Get-Command $RequestedCommand -CommandType Application -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($requested) {
        $candidates += $requested.Source
    }

    $managedPythonRoot = Join-Path ([Environment]::GetFolderPath("LocalApplicationData")) "Python"
    if (Test-Path -LiteralPath $managedPythonRoot -PathType Container) {
        $candidates += Get-ChildItem -LiteralPath $managedPythonRoot -Directory -Filter "pythoncore-*" |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName "python.exe" } |
            Where-Object { Test-Path -LiteralPath $_ -PathType Leaf }
    }

    foreach ($candidate in $candidates | Select-Object -Unique) {
        & $candidate --version *> $null
        if ($LASTEXITCODE -eq 0) {
            return $candidate
        }
    }
    throw "Python 3 was not found. Install Python or pass its executable with -Python."
}

if (-not (Test-Path -LiteralPath $requirements -PathType Leaf)) {
    throw "Requirements file is missing: $requirements"
}

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    $pythonExe = Resolve-PythonExecutable -RequestedCommand $Python
    Write-Host "Creating radio collector environment in $venvRoot"
    & $pythonExe -m venv $venvRoot
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create the radio collector Python environment"
    }
}

& $venvPython -m pip install --disable-pip-version-check -r $requirements
if ($LASTEXITCODE -ne 0) {
    throw "Radio collector dependency installation failed with exit code $LASTEXITCODE"
}

& $venvPython $collector --self-test
if ($LASTEXITCODE -ne 0) {
    throw "Radio collector self-test failed with exit code $LASTEXITCODE"
}

Write-Host "Radio collector tools are ready."
Write-Host "Run: & '$venvPython' '$collector' --verify -v"

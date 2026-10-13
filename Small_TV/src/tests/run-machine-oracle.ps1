[CmdletBinding()]
param(
    [switch]$InstallDependencies,
    [switch]$Quick,
    [string]$PythonPath,
    [string]$OutputDirectory
)
$ErrorActionPreference = "Stop"
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\..\.."))
if (!$PythonPath) {
    $PythonPath = Join-Path $repo ".idf\tools-v6.1\python_env\idf6.1_py3.12_env\Scripts\python.exe"
}
if (!(Test-Path -LiteralPath $PythonPath)) {
    throw "Pass -PythonPath pointing to Python 3.12 or newer."
}
$dependencies = Join-Path $repo ".build\small-tv-parity\oracle-deps"
if ($InstallDependencies) {
    & $PythonPath -m pip install --only-binary=:all: --no-deps --target $dependencies `
        -r (Join-Path $PSScriptRoot "oracle-requirements.txt")
    if ($LASTEXITCODE) { throw "Oracle dependency installation failed." }
}
$prepare = Join-Path $repo "Small_TV\analysis\prepare_analysis.py"
& $PythonPath $prepare --output (Join-Path $repo ".build\small-tv-reverse")
if ($LASTEXITCODE) { throw "Factory image validation failed." }
if (!(Test-Path -LiteralPath (Join-Path $repo ".build\small-tv-esp32c2\small_tv_reconstructed.elf"))) {
    throw "Build the current C application with Small_TV/src/build.ps1 first."
}
$arguments = @()
if (!$Quick) { $arguments += "--extended" }
if ($OutputDirectory) { $arguments += @("--output", $OutputDirectory) }
& $PythonPath (Join-Path $PSScriptRoot "machine_oracle.py") @arguments
if ($LASTEXITCODE) { throw "Renderer machine verification failed." }

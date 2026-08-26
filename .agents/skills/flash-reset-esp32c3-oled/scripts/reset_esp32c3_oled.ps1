[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidatePattern('^COM[0-9]+$')]
    [string]$Port,

    [ValidateSet('Watchdog', 'Rts')]
    [string]$Method = 'Watchdog',

    [string]$PythonPath,

    [uri]$VerifyUrl,

    [ValidateRange(3, 120)]
    [int]$VerifyTimeoutSeconds = 25,

    [ValidateRange(100, 2000)]
    [int]$ResetMilliseconds = 200
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Get-NativeUsbDevice {
    param([string]$SerialPort)

    $portPattern = '\(' + [regex]::Escape($SerialPort) + '\)'
    $devices = @(
        Get-CimInstance Win32_PnPEntity |
            Where-Object {
                $_.Name -match $portPattern -and
                $_.PNPDeviceID -match '^USB\\VID_303A&PID_1001'
            }
    )

    if ($devices.Count -eq 0) {
        throw "$SerialPort is not an ESP32-C3 native USB Serial/JTAG device (VID_303A, PID_1001)."
    }
    if ($devices.Count -gt 1) {
        throw "More than one ESP32-C3 native USB device claims $SerialPort."
    }

    return $devices[0]
}

function Find-EsptoolPython {
    param([string]$RequestedPath)

    $candidates = [System.Collections.Generic.List[string]]::new()
    if ($RequestedPath) {
        $candidates.Add($RequestedPath)
    }
    if ($env:IDF_PYTHON_ENV_PATH) {
        $candidates.Add((Join-Path $env:IDF_PYTHON_ENV_PATH 'Scripts\python.exe'))
    }

    $repositoryRoot = [System.IO.Path]::GetFullPath(
        (Join-Path $PSScriptRoot '..\..\..\..')
    )
    $bundledPattern = Join-Path $repositoryRoot '.idf\tools-v*\python_env\idf*_env\Scripts\python.exe'
    foreach ($candidate in @(Get-ChildItem -Path $bundledPattern -File -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -ExpandProperty FullName)) {
        $candidates.Add($candidate)
    }

    $systemPython = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($systemPython) {
        $candidates.Add($systemPython.Source)
    }

    foreach ($candidate in @($candidates | Select-Object -Unique)) {
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            continue
        }

        $null = @(& $candidate -m esptool version 2>&1)
        if ($LASTEXITCODE -eq 0) {
            return $candidate
        }
    }

    throw 'Could not find a Python environment containing esptool. Run the ESP32-C3 setup script or pass -PythonPath.'
}

function Invoke-RtsReset {
    param(
        [string]$SerialPort,
        [int]$DurationMilliseconds
    )

    $serial = [System.IO.Ports.SerialPort]::new()
    $serial.PortName = $SerialPort
    $serial.BaudRate = 115200
    $serial.DataBits = 8
    $serial.Parity = [System.IO.Ports.Parity]::None
    $serial.StopBits = [System.IO.Ports.StopBits]::One
    $serial.Handshake = [System.IO.Ports.Handshake]::None
    $serial.DtrEnable = $false
    $serial.RtsEnable = $false

    try {
        try {
            $serial.Open()
        } catch {
            throw "Cannot open $SerialPort. Close its serial monitor or uploader and retry. $($_.Exception.Message)"
        }

        $serial.DtrEnable = $false
        $serial.RtsEnable = $true
        Start-Sleep -Milliseconds $DurationMilliseconds
        $serial.RtsEnable = $false
    } finally {
        if ($serial.IsOpen) {
            $serial.DtrEnable = $false
            $serial.RtsEnable = $false
            $serial.Close()
        }
        $serial.Dispose()
    }
}

function Wait-NativeUsbPort {
    param(
        [string]$SerialPort,
        [int]$TimeoutSeconds
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    do {
        try {
            $null = Get-NativeUsbDevice -SerialPort $SerialPort
            return
        } catch {
            Start-Sleep -Milliseconds 250
        }
    } while ([DateTime]::UtcNow -lt $deadline)

    throw "$SerialPort did not return within $TimeoutSeconds seconds after reset."
}

function Wait-WebUi {
    param(
        [uri]$Url,
        [int]$TimeoutSeconds
    )

    $deadline = [DateTime]::UtcNow.AddSeconds($TimeoutSeconds)
    $lastError = $null
    do {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 3 -UseBasicParsing
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300) {
                return $response.StatusCode
            }
            $lastError = "HTTP $($response.StatusCode)"
        } catch {
            $lastError = $_.Exception.Message
        }
        Start-Sleep -Milliseconds 500
    } while ([DateTime]::UtcNow -lt $deadline)

    throw "The USB reset completed, but $Url did not return HTTP 2xx within $TimeoutSeconds seconds. Last error: $lastError"
}

$device = Get-NativeUsbDevice -SerialPort $Port
$description = "$Method reset of $($device.PNPDeviceID)"
if (-not $PSCmdlet.ShouldProcess($Port, $description)) {
    return
}

if ($Method -eq 'Rts') {
    Invoke-RtsReset -SerialPort $Port -DurationMilliseconds $ResetMilliseconds
    Write-Host "$Port RTS reset completed."
} else {
    $python = Find-EsptoolPython -RequestedPath $PythonPath
    $arguments = @(
        '-m', 'esptool',
        '--chip', 'esp32c3',
        '-p', $Port,
        '--before', 'usb-reset',
        '--after', 'watchdog-reset',
        'run'
    )

    $output = @(& $python @arguments 2>&1)
    $exitCode = $LASTEXITCODE
    $output | ForEach-Object { Write-Host $_ }
    $outputText = $output -join [Environment]::NewLine
    $watchdogRequested = $outputText -match 'Hard resetting with a watchdog'

    if ($exitCode -ne 0 -and -not $watchdogRequested) {
        throw "esptool failed before issuing the watchdog reset (exit code $exitCode)."
    }
    if ($exitCode -ne 0) {
        Write-Warning 'The USB device disappeared during watchdog reset; this is expected when the reset marker was printed.'
    }

    Start-Sleep -Milliseconds 500
    Wait-NativeUsbPort -SerialPort $Port -TimeoutSeconds 10
    Write-Host "$Port watchdog reset completed."
}

if ($VerifyUrl) {
    $statusCode = Wait-WebUi -Url $VerifyUrl -TimeoutSeconds $VerifyTimeoutSeconds
    Write-Host "Application verified: $VerifyUrl returned HTTP $statusCode."
} else {
    Write-Warning 'USB reset was issued, but application startup was not independently verified. Pass -VerifyUrl when the WebUI address is known.'
}

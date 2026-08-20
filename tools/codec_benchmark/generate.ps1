[CmdletBinding()]
param(
    [string]$OutputDirectory = "",
    [string]$FfmpegPath = "",
    [ValidateRange(5, 30)]
    [int]$DurationSeconds = 11
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot "..\.."))
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $repository ".build\codec-benchmark"
}
$OutputDirectory = [IO.Path]::GetFullPath($OutputDirectory)

if ([string]::IsNullOrWhiteSpace($FfmpegPath)) {
    $ffmpeg = Get-Command ffmpeg.exe -CommandType Application `
        -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($ffmpeg) { $FfmpegPath = $ffmpeg.Source }
}
if (-not (Test-Path -LiteralPath $FfmpegPath -PathType Leaf)) {
    throw "ffmpeg.exe was not found; pass its path with -FfmpegPath"
}

New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$source = Join-Path $OutputDirectory "source-48k-stereo.wav"
$filter = @(
    "anoisesrc=color=white:amplitude=0.34:sample_rate=48000:duration=${DurationSeconds}:seed=12345[nl]"
    "anoisesrc=color=pink:amplitude=0.34:sample_rate=48000:duration=${DurationSeconds}:seed=67890[nr]"
    "sine=frequency=997:sample_rate=48000:duration=${DurationSeconds}:beep_factor=2[tl]"
    "sine=frequency=1601:sample_rate=48000:duration=${DurationSeconds}:beep_factor=2[tr]"
    "[nl][tl]amix=inputs=2:weights='0.72 0.28':normalize=0[left]"
    "[nr][tr]amix=inputs=2:weights='0.72 0.28':normalize=0[right]"
    "[left][right]amerge=inputs=2,alimiter=limit=0.95[out]"
) -join ";"

& $FfmpegPath -y -hide_banner -loglevel warning `
    -filter_complex $filter -map "[out]" -ar 48000 -ac 2 `
    -c:a pcm_s16le $source
if ($LASTEXITCODE -ne 0) { throw "Failed to generate benchmark source" }

$fixtures = @(
    @{
        Name = "mp3-320.mp3"; Codec = "mp3"; TargetKbps = 320
        Arguments = @("-c:a", "libmp3lame", "-b:a", "320k", "-write_xing", "0")
    }
    @{
        Name = "aac-lc-320.aac"; Codec = "aac"; TargetKbps = 320
        Arguments = @("-c:a", "aac", "-profile:a", "aac_low", "-b:a", "320k", "-f", "adts")
    }
    @{
        Name = "flac-level8.flac"; Codec = "flac"; TargetKbps = 0
        Arguments = @("-c:a", "flac", "-compression_level", "8")
    }
    @{
        Name = "vorbis-q10.ogg"; Codec = "ogg"; TargetKbps = 0
        Arguments = @("-c:a", "libvorbis", "-q:a", "10", "-f", "ogg")
    }
    @{
        Name = "opus-510.ogg"; Codec = "ogg"; TargetKbps = 510
        Arguments = @("-c:a", "libopus", "-b:a", "510k", "-vbr", "off",
                      "-application", "audio", "-frame_duration", "20", "-f", "ogg")
    }
)

$manifest = foreach ($fixture in $fixtures) {
    $destination = Join-Path $OutputDirectory $fixture.Name
    $arguments = @("-y", "-hide_banner", "-loglevel", "warning", "-i", $source,
                   "-map", "0:a:0") + $fixture.Arguments + @($destination)
    & $FfmpegPath @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to encode $($fixture.Name)"
    }
    $bytes = (Get-Item -LiteralPath $destination).Length
    [pscustomobject]@{
        Name = $fixture.Name
        Codec = $fixture.Codec
        TargetKbps = $fixture.TargetKbps
        Bytes = $bytes
        AverageKbps = [math]::Round(($bytes * 8) / ($DurationSeconds * 1000), 1)
        DurationSeconds = $DurationSeconds
    }
}

$manifest | Export-Csv -NoTypeInformation -Encoding utf8 `
    (Join-Path $OutputDirectory "manifest.csv")
$manifest | Format-Table -AutoSize

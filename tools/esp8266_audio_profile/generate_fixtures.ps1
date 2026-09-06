param(
    [string]$FfmpegPath = "ffmpeg",
    [string]$OutputDirectory = ".build/esp8266-audio-profile/fixtures",
    [int]$DurationSeconds = 45
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

$left = "anoisesrc=color=white:amplitude=0.2:sample_rate=48000:duration=$($DurationSeconds):seed=8266"
$right = "anoisesrc=color=white:amplitude=0.2:sample_rate=48000:duration=$($DurationSeconds):seed=8267"
$join = "[0:a][1:a]join=inputs=2:channel_layout=stereo[a]"

foreach ($bitrate in 32, 128, 320) {
    $output = Join-Path $OutputDirectory "mp3-$bitrate.mp3"
    & $FfmpegPath -hide_banner -loglevel error -y -f lavfi -i $left -f lavfi -i $right -filter_complex $join -map "[a]" -ar 48000 -c:a libmp3lame -b:a "$($bitrate)k" -write_xing 0 -id3v2_version 0 $output
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $output" }
}

foreach ($bitrate in 48, 128, 320) {
    $output = Join-Path $OutputDirectory "aac-$bitrate.aac"
    & $FfmpegPath -hide_banner -loglevel error -y -f lavfi -i $left -f lavfi -i $right -filter_complex $join -map "[a]" -ar 48000 -c:a aac -b:a "$($bitrate)k" -f adts $output
    if ($LASTEXITCODE -ne 0) { throw "ffmpeg failed for $output" }
}
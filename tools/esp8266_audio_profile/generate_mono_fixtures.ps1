param([string]$FfmpegPath = 'ffmpeg')
$ErrorActionPreference = 'Stop'
$fixtureDir = Join-Path $PSScriptRoot '../../tests/fixtures/helix_mono'
New-Item -ItemType Directory -Path $fixtureDir -Force | Out-Null
# Own deterministic tones: correlated stereo with a nonzero difference and
# an envelope that exercises short/start/stop transform windows.
$signal = 'aevalsrc=0.15*sin(2*PI*440*t)*(0.2+0.8*gt(mod(t\,0.08)\,0.03))|0.13*sin(2*PI*440*t)*(0.2+0.8*gt(mod(t\,0.08)\,0.03))+0.02*sin(2*PI*997*t):s=48000:d=0.4'
foreach ($case in @(@('mpeg1',48000,128,2), @('mpeg2',22050,64,2), @('mpeg25',11025,32,2), @('mono',24000,32,1))) {
    $output = Join-Path $fixtureDir ($case[0] + '.mp3')
    & $FfmpegPath -hide_banner -loglevel error -y -f lavfi -i $signal -ar $case[1] -ac $case[3] -c:a libmp3lame -b:a "$($case[2])k" -joint_stereo 1 -write_xing 0 -id3v2_version 0 $output
    if ($LASTEXITCODE -ne 0) { throw "MP3 fixture generation failed: $output" }
}

$ErrorActionPreference = 'Stop'
# Deterministic gated tones exercise transient short windows and transitions.
foreach ($aacCase in @(@('mono-22050', 22050, 'mono', '48k'), @('stereo-44100', 44100, 'stereo', '192k'))) {
    $aacExpr = '0.7*sin(2*PI*997*t)*lt(mod(t,0.125),0.025)'
    if ($aacCase[2] -eq 'stereo') { $aacExpr += '|0.6*sin(2*PI*1571*t)*lt(mod(t+0.04,0.19),0.03)' }
    & ffmpeg -hide_banner -loglevel error -y -f lavfi -i "aevalsrc='${aacExpr}':s=$($aacCase[1]):d=1:c=$($aacCase[2])" -c:a aac -profile:a aac_low -b:a $aacCase[3] -f adts (Join-Path $PSScriptRoot "$($aacCase[0]).aac")
    if ($LASTEXITCODE) { throw 'AAC fixture generation failed' }
}

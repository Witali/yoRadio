[CmdletBinding()]
param(
    [string]$BdfPath = "",
    [string]$OutputPath = "",
    [string]$NativeOutputPath = ""
)

$ErrorActionPreference = "Stop"
$repository = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
if (-not $BdfPath) {
    $BdfPath = Join-Path $PSScriptRoot "fonts\spleen-6x12.bdf"
}
if (-not $OutputPath) {
    $OutputPath = Join-Path $repository `
        "yoRadio\src\displays\fonts\C3Terminal12.h"
}
if (-not $NativeOutputPath) {
    $NativeOutputPath = Join-Path $repository `
        "idf\esp32c3-oled-native\main\font6x12.h"
}
if (-not (Test-Path -LiteralPath $BdfPath -PathType Leaf)) {
    throw "Spleen 6x12 BDF was not found at $BdfPath"
}

[Text.Encoding]::RegisterProvider([Text.CodePagesEncodingProvider]::Instance)
$cp437 = [Text.Encoding]::GetEncoding(437)

# Preserve yoRadio's control/icons and any legacy byte glyph for which Spleen
# has no corresponding Unicode character.
$legacySource = Get-Content -LiteralPath (Join-Path $repository `
    "yoRadio\fonts\glcdfont.c") -Raw
$legacy = [regex]::Matches($legacySource, '0x[0-9A-Fa-f]{2}') |
    ForEach-Object { [Convert]::ToByte($_.Value.Substring(2), 16) }
if ($legacy.Count -lt 1280) {
    throw "The existing 256-character 5x7 font could not be parsed"
}

$bdfLines = Get-Content -LiteralPath $BdfPath
$fontAscentLine = $bdfLines | Where-Object { $_ -match '^FONT_ASCENT ' } |
    Select-Object -First 1
if (-not $fontAscentLine) { throw "BDF FONT_ASCENT is missing" }
$fontAscent = [int]($fontAscentLine -replace '^FONT_ASCENT ', '')
$records = @{}
for ($lineIndex = 0; $lineIndex -lt $bdfLines.Count; $lineIndex++) {
    if ($bdfLines[$lineIndex] -notmatch '^STARTCHAR ') { continue }
    $encoding = -1
    $width = 0
    $height = 0
    $xOffset = 0
    $yOffset = 0
    $rows = [Collections.Generic.List[string]]::new()
    for ($lineIndex++;
         $lineIndex -lt $bdfLines.Count -and $bdfLines[$lineIndex] -ne 'ENDCHAR';
         $lineIndex++) {
        if ($bdfLines[$lineIndex] -match '^ENCODING (-?\d+)$') {
            $encoding = [int]$Matches[1]
        } elseif ($bdfLines[$lineIndex] -match
                  '^BBX (\d+) (\d+) (-?\d+) (-?\d+)$') {
            $width = [int]$Matches[1]
            $height = [int]$Matches[2]
            $xOffset = [int]$Matches[3]
            $yOffset = [int]$Matches[4]
        } elseif ($bdfLines[$lineIndex] -eq 'BITMAP') {
            for ($row = 0; $row -lt $height; $row++) {
                $rows.Add($bdfLines[++$lineIndex])
            }
        }
    }
    if ($encoding -ge 0) {
        $records[$encoding] = [pscustomobject]@{
            Width = $width
            Height = $height
            X = $xOffset
            Y = $yOffset
            Rows = $rows
        }
    }
}

$cellWidth = 6
$cellHeight = 12
$pixels = New-Object 'bool[,]' $cellWidth, $cellHeight
$bitmapBytes = [Collections.Generic.List[byte]]::new()
$glyphLines = [Collections.Generic.List[string]]::new()

function Clear-Glyph {
    for ($y = 0; $y -lt $cellHeight; $y++) {
        for ($x = 0; $x -lt $cellWidth; $x++) {
            $pixels[$x, $y] = $false
        }
    }
}

function Set-LegacyGlyph([int]$Code) {
    Clear-Glyph
    for ($y = 0; $y -lt $cellHeight; $y++) {
        $sourceY = [Math]::Min(6, [Math]::Floor($y * 7 / $cellHeight))
        for ($x = 0; $x -lt $cellWidth; $x++) {
            $sourceX = [Math]::Min(4, [Math]::Floor($x * 5 / $cellWidth))
            $column = $legacy[$Code * 5 + $sourceX]
            $pixels[$x, $y] = ($column -band (1 -shl $sourceY)) -ne 0
        }
    }
}

function Get-UnicodeForByte([int]$Code) {
    if ($Code -eq 0xA8) { return 0x0401 }
    if ($Code -eq 0xB8) { return 0x0451 }
    if ($Code -ge 0xC0) { return 0x0410 + $Code - 0xC0 }
    return [int][char]$cp437.GetString([byte[]]@([byte]$Code))
}

function Set-BdfGlyph([int]$Code) {
    $unicode = Get-UnicodeForByte $Code
    $record = $records[$unicode]
    if ($null -eq $record) { return $false }
    Clear-Glyph
    $top = $fontAscent - ($record.Height + $record.Y)
    for ($sourceY = 0; $sourceY -lt $record.Height; $sourceY++) {
        $targetY = $top + $sourceY
        if ($targetY -lt 0 -or $targetY -ge $cellHeight) { continue }
        $raw = [Convert]::ToUInt32($record.Rows[$sourceY], 16)
        $storedWidth = [Math]::Ceiling($record.Width / 8) * 8
        for ($sourceX = 0; $sourceX -lt $record.Width; $sourceX++) {
            $targetX = $record.X + $sourceX
            if ($targetX -lt 0 -or $targetX -ge $cellWidth) { continue }
            $mask = [uint32]1 -shl ($storedWidth - 1 - $sourceX)
            $pixels[$targetX, $targetY] = ($raw -band $mask) -ne 0
        }
    }
    return $true
}

function Set-ReplacementGlyph {
    Clear-Glyph
    for ($y = 0; $y -lt $cellHeight; $y++) {
        for ($x = 0; $x -lt $cellWidth; $x++) {
            $border = ($y -le 10) -and `
                ($x -eq 0 -or $x -eq 5 -or $y -eq 0 -or $y -eq 10)
            $question = ($y -eq 2 -and $x -ge 2 -and $x -le 3) -or `
                ($y -eq 3 -and $x -eq 4) -or `
                (($y -eq 4 -or $y -eq 5 -or $y -eq 7) -and $x -eq 3)
            $pixels[$x, $y] = $border -or $question
        }
    }
}

for ($code = 0; $code -le 255; $code++) {
    if ($code -eq 0x7F) {
        Set-ReplacementGlyph
    } elseif ($code -lt 0x20 -or -not (Set-BdfGlyph $code)) {
        Set-LegacyGlyph $code
    }

    $offset = $bitmapBytes.Count
    $packed = 0
    $mask = 0x80
    for ($y = 0; $y -lt $cellHeight; $y++) {
        for ($x = 0; $x -lt $cellWidth; $x++) {
            if ($pixels[$x, $y]) { $packed = $packed -bor $mask }
            $mask = $mask -shr 1
            if ($mask -eq 0) {
                $bitmapBytes.Add([byte]$packed)
                $packed = 0
                $mask = 0x80
            }
        }
    }
    if ($mask -ne 0x80) { $bitmapBytes.Add([byte]$packed) }
    $glyphLines.Add((
        "  {{ {0,5}, 6, 12, 6, 0, -9 }}, // 0x{1:X2}" -f $offset, $code))
}

$licenseComment = @(
    "// Generated by tools/Generate-Esp32C3OledFont.ps1 from Spleen 6x12.",
    "// Spleen is Copyright (c) 2018-2026, Frederic Cambus, BSD-2-Clause:",
    "// tools/fonts/Spleen-LICENSE",
    "// Fixed 6x12 cells cover the same 256 byte values as yoRadio's 5x7 font."
)

$lines = [Collections.Generic.List[string]]::new()
$lines.Add("#ifndef C3_TERMINAL_12_H")
$lines.Add("#define C3_TERMINAL_12_H")
$lines.Add("")
foreach ($comment in $licenseComment) { $lines.Add($comment) }
$lines.Add("const uint8_t C3Terminal12Bitmaps[] PROGMEM = {")
for ($index = 0; $index -lt $bitmapBytes.Count; $index += 12) {
    $last = [Math]::Min($index + 11, $bitmapBytes.Count - 1)
    $chunk = for ($item = $index; $item -le $last; $item++) {
        '0x{0:X2}' -f $bitmapBytes[$item]
    }
    $lines.Add("  " + ($chunk -join ", ") + ",")
}
$lines.Add("};")
$lines.Add("")
$lines.Add("const GFXglyph C3Terminal12Glyphs[] PROGMEM = {")
foreach ($glyph in $glyphLines) { $lines.Add($glyph) }
$lines.Add("};")
$lines.Add("")
$lines.Add("const GFXfont C3Terminal12 PROGMEM = {")
$lines.Add("  (uint8_t *)C3Terminal12Bitmaps,")
$lines.Add("  (GFXglyph *)C3Terminal12Glyphs,")
$lines.Add("  0x00, 0xFF, 13")
$lines.Add("};")
$lines.Add("")
$lines.Add("#endif")
[IO.File]::WriteAllLines([IO.Path]::GetFullPath($OutputPath), $lines,
    [Text.UTF8Encoding]::new($false))

$nativeLines = [Collections.Generic.List[string]]::new()
$nativeLines.Add("#pragma once")
$nativeLines.Add("")
$nativeLines.Add("#include <stdint.h>")
$nativeLines.Add("")
foreach ($comment in $licenseComment) { $nativeLines.Add($comment) }
$nativeLines.Add("static const uint8_t font6x12[$($bitmapBytes.Count)] = {")
for ($index = 0; $index -lt $bitmapBytes.Count; $index += 12) {
    $last = [Math]::Min($index + 11, $bitmapBytes.Count - 1)
    $chunk = for ($item = $index; $item -le $last; $item++) {
        '0x{0:X2}' -f $bitmapBytes[$item]
    }
    $nativeLines.Add("    " + ($chunk -join ", ") + ",")
}
$nativeLines.Add("};")
$nativeLines.Add("")
$nativeLines.Add("static const uint32_t font6x12_unicode_80_bf[64] = {")
for ($code = 0x80; $code -le 0xBF; $code += 8) {
    $values = for ($item = $code; $item -lt $code + 8; $item++) {
        '0x{0:X4}' -f (Get-UnicodeForByte $item)
    }
    $nativeLines.Add("    " + ($values -join ", ") + ",")
}
$nativeLines.Add("};")
[IO.File]::WriteAllLines([IO.Path]::GetFullPath($NativeOutputPath),
    $nativeLines, [Text.UTF8Encoding]::new($false))

Write-Host "Generated both C3 fonts ($($bitmapBytes.Count) bitmap bytes, 256 glyphs)"

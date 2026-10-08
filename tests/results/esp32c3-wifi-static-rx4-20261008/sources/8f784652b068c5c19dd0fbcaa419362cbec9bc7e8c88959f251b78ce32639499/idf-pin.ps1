# Keep toolchain series separate from the exact SDK source revision.
function Get-YoRadioIdfPin {
    param([Parameter(Mandatory)][string]$Project)
    $version = (Get-Content -LiteralPath (Join-Path $Project 'idf-version.txt') -Raw).Trim()
    if ($version -notmatch '^v\d+\.\d+(?:\.\d+)?$') { throw 'Invalid pinned ESP-IDF version' }
    $revisionFile = Join-Path $Project 'idf-revision.txt'
    $revision = $version
    $directory = $version
    if (Test-Path -LiteralPath $revisionFile) {
        $revision = (Get-Content -LiteralPath $revisionFile -Raw).Trim()
        if ($revision -notmatch '^[0-9a-f]{40}$') { throw 'ESP-IDF revision must be a full lowercase commit hash' }
        $directory += '-' + $revision.Substring(0, 12)
    }
    return [pscustomobject]@{ Version = $version; Revision = $revision; Directory = $directory }
}

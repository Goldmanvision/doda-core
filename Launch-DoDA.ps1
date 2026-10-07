[CmdletBinding()]
param(
    [ValidatePattern('^\d{1,2}$')]
    [string] $Map,

    [ValidateSet('UZDoom', 'GZDoom')]
    [string] $Engine,

    [string] $IwadPath = 'C:\Dev\uzdoom_src\freedoom2.wad',

    [switch] $Wait
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# DoDA Launcher Configuration
# ---------------------------------------------------------------------------

$UZDoomPath = 'C:\Dev\uzdoom_src\uzdoom-build\uzdoom.exe'
$GZDoomPath = 'C:\Dev\gzdoom-4-14-2-windows\gzdoom.exe'

# This launcher must remain in the doda-core root.
$projectRoot = $PSScriptRoot
$projectName = Split-Path -Path $projectRoot -Leaf

if ($projectName -ne 'doda-core') {
    throw @"
This launcher must be saved in the doda-core project root.

Current script location:
$projectRoot

Expected location:
C:\Dev\uzdoom_src\doda-core\Launch-DoDA.ps1
"@
}

$mapsDirectory = Join-Path $projectRoot 'MAPS'

if (-not (Test-Path -LiteralPath $mapsDirectory -PathType Container)) {
    throw "DoDA maps directory was not found: $mapsDirectory"
}

$mapFiles = Get-ChildItem `
    -Path $mapsDirectory `
    -Filter 'MAP*.wad' `
    -File |
    ForEach-Object {
        if ($_.BaseName -match '^MAP(\d{2})$') {
            [PSCustomObject]@{
                Number = [int] $Matches[1]
                Name = $_.BaseName
                Path = $_.FullName
            }
        }
    } |
    Sort-Object Number

if (-not $mapFiles) {
    throw "No MAP##.wad files were found under: $mapsDirectory"
}

$availableMapNumbers = @($mapFiles.Number)

# ---------------------------------------------------------------------------
# Engine Selection
# ---------------------------------------------------------------------------

if (-not $Engine) {
    Write-Host ''
    Write-Host 'Choose Doom engine:' -ForegroundColor Cyan
    Write-Host '  1  UZDoom  - DoDA development build / custom native bridge'
    Write-Host '  2  GZDoom  - faster startup compatibility test'
    Write-Host ''

    $engineChoice = Read-Host 'Engine choice (1 or U = UZDoom; 2 or G = GZDoom; Enter = UZDoom)'

    switch ($engineChoice.Trim().ToUpperInvariant()) {
        ''  { $Engine = 'UZDoom' }
        '1' { $Engine = 'UZDoom' }
        'U' { $Engine = 'UZDoom' }
        'UZDOOM' { $Engine = 'UZDoom' }
        '2' { $Engine = 'GZDoom' }
        'G' { $Engine = 'GZDoom' }
        'GZDOOM' { $Engine = 'GZDoom' }

        default {
            throw @"
Invalid engine selection: $engineChoice

Use:
  1 or U for UZDoom
  2 or G for GZDoom
"@
        }
    }
}

switch ($Engine) {
    'UZDoom' {
        $enginePath = $UZDoomPath
        $engineLabel = 'UZDoom'
    }

    'GZDoom' {
        $enginePath = $GZDoomPath
        $engineLabel = 'GZDoom'
    }

    default {
        throw "Unsupported engine value: $Engine"
    }
}

if (-not (Test-Path -LiteralPath $enginePath -PathType Leaf)) {
    throw @"
The configured $engineLabel executable was not found:

$enginePath

Update the corresponding `$UZDoomPath or `$GZDoomPath value
near the top of Launch-DoDA.ps1.
"@
}

if (-not (Test-Path -LiteralPath $IwadPath -PathType Leaf)) {
    throw @"
The configured IWAD was not found:

$IwadPath

Update the default `$IwadPath value in Launch-DoDA.ps1,
or launch with -IwadPath 'C:\path\to\your-iwad.wad'.
"@
}

# ---------------------------------------------------------------------------
# Map Selection
# ---------------------------------------------------------------------------

if (-not $Map) {
    Write-Host ''
    Write-Host 'Available DoDA maps:' -ForegroundColor Cyan

    foreach ($mapInfo in $mapFiles) {
        Write-Host ("  {0,2}  {1}" -f $mapInfo.Number, $mapInfo.Name)
    }

    Write-Host ''
    $Map = Read-Host 'Choose map number (01, 1, 02, 2, etc.; Enter = 01)'
}

if ([string]::IsNullOrWhiteSpace($Map)) {
    $Map = '01'
}

$mapNumber = 0

if (-not [int]::TryParse($Map, [ref] $mapNumber)) {
    throw "Map selection '$Map' is not valid. Use 01, 1, 02, 2, and so on."
}

if ($mapNumber -notin $availableMapNumbers) {
    $availableText = (
        $availableMapNumbers |
        ForEach-Object { $_.ToString('00') }
    ) -join ', '

    throw @"
MAP$($mapNumber.ToString('00')) is not available.

Available maps:
$availableText
"@
}

$mapName = 'MAP{0:D2}' -f $mapNumber

# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

$arguments = @(
    '-iwad', $IwadPath,
    '-file', $projectRoot,
    '+map', $mapName
)

Write-Host ''
Write-Host 'Launching DoDA...' -ForegroundColor Green
Write-Host "Engine:  $engineLabel" -ForegroundColor Green
Write-Host "EXE:     $enginePath" -ForegroundColor DarkGray
Write-Host "IWAD:    $IwadPath" -ForegroundColor DarkGray
Write-Host "Project: $projectRoot" -ForegroundColor DarkGray
Write-Host "Map:     $mapName" -ForegroundColor Green

if ($engineLabel -eq 'GZDoom') {
    Write-Host ''
    Write-Host 'GZDoom test note:' -ForegroundColor Yellow
    Write-Host 'Confirm MAP01 loads and FOIMS-X opens without native DoDA API errors.' `
        -ForegroundColor Yellow
}

Write-Host ''

$startParameters = @{
    FilePath = $enginePath
    ArgumentList = $arguments
    WorkingDirectory = $projectRoot
}

if ($Wait) {
    $startParameters.Wait = $true
}

Start-Process @startParameters
<#
.SYNOPSIS
    Clones (or updates) the Compass Hill repository and optionally opens the walkthrough.

.DESCRIPTION
    - Checks for Git and offers to install it with winget if it's missing.
    - Clones into a folder OUTSIDE OneDrive (default: %USERPROFILE%\Projects\Compass_Hill),
      or pulls the latest changes if a copy is already there.
    - With -Serve, starts a local web server for the walkthrough and opens it
      in your browser.

    Why not Documents? When OneDrive backs up Documents ("Known Folder Move"),
    Documents really lives in OneDrive\Documents. OneDrive then syncs the .git
    folder file by file, locks files while Git writes them, can turn files into
    online-only placeholders, and creates "-PCNAME" conflict copies. Those break
    Git repositories. So the script refuses OneDrive folders unless you pass
    -AllowOneDrive, and offers to move an existing clone out of OneDrive.

    The repository is private. The first clone opens a GitHub sign-in window
    (Git Credential Manager, which comes with Git for Windows).

.EXAMPLE
    .\Get-CompassHill.ps1
    Clones to C:\Users\<you>\Projects\Compass_Hill.

.EXAMPLE
    .\Get-CompassHill.ps1 -Path D:\Projects\Compass_Hill -Serve
    Clones to D:\Projects\Compass_Hill, then opens the walkthrough.
#>
[CmdletBinding()]
param(
    [string]$Path = (Join-Path $env:USERPROFILE 'Projects\Compass_Hill'),
    [string]$Branch = 'claude/epic-bell-08fxwr',
    [switch]$Serve,
    [int]$Port = 8000,
    [switch]$AllowOneDrive
)

$ErrorActionPreference = 'Stop'
$RepoUrl = 'https://github.com/matthewdrobinette-source/Compass_Hill.git'
$SafeDefault = Join-Path $env:USERPROFILE 'Projects\Compass_Hill'

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }

# --- OneDrive detection -----------------------------------------------------
function Get-OneDriveRoots {
    $roots = @($env:OneDrive, $env:OneDriveConsumer, $env:OneDriveCommercial)
    # Business accounts can have several roots; they're listed in the registry
    $key = 'HKCU:\Software\Microsoft\OneDrive\Accounts'
    if (Test-Path $key) {
        Get-ChildItem $key -ErrorAction SilentlyContinue | ForEach-Object {
            $roots += (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).UserFolder
        }
    }
    $roots | Where-Object { $_ } | ForEach-Object { $_.TrimEnd('\') } | Sort-Object -Unique
}

function Resolve-FullPath([string]$p) {
    $full = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($p))
    # Follow junctions/symlinks on the deepest existing ancestor (e.g. a redirected Documents)
    $probe = $full
    while ($probe -and -not (Test-Path -LiteralPath $probe)) { $probe = Split-Path $probe -Parent }
    if ($probe) {
        $item = Get-Item -LiteralPath $probe -Force
        if ($item.LinkType -and $item.Target) {
            $target = @($item.Target)[0]
            $full = $target.TrimEnd('\') + $full.Substring($probe.TrimEnd('\').Length)
        }
    }
    return $full
}

function Test-InOneDrive([string]$p) {
    $full = Resolve-FullPath $p
    foreach ($root in Get-OneDriveRoots) {
        if ($full.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase) -or
            $full.Equals($root, [StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    # Fallback: any path segment named OneDrive or "OneDrive - <Org>"
    return [bool]($full -match '\\OneDrive( - [^\\]+)?(\\|$)')
}

$Path = Resolve-FullPath $Path
$docs = [Environment]::GetFolderPath('MyDocuments')
if (Test-InOneDrive $docs) {
    Write-Host "Note: your Documents folder is synced by OneDrive ($docs), so the clone goes elsewhere."
}

if ((Test-InOneDrive $Path) -and -not $AllowOneDrive) {
    Write-Warn "$Path is inside OneDrive. OneDrive sync corrupts Git repositories."
    $answer = Read-Host "Clone to $SafeDefault instead? (Y/N)"
    if ($answer -notmatch '^[Yy]') {
        throw 'Stopped. Pick a folder outside OneDrive with -Path, or pass -AllowOneDrive to override.'
    }
    $Path = $SafeDefault
}

# --- 1. Git ---------------------------------------------------------------
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Warn 'Git is not installed.'
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        $answer = Read-Host 'Install Git for Windows now with winget? (Y/N)'
        if ($answer -match '^[Yy]') {
            winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
            # make the new git visible in this session
            $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                        [Environment]::GetEnvironmentVariable('Path', 'User')
        }
    }
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'Git is required. Install it from https://git-scm.com/download/win, then run this script again.'
    }
}

# --- 2. An old copy in OneDrive\Documents? Offer to move it out -------------
$oldCopy = Join-Path $docs 'Compass_Hill'
if ((Test-Path (Join-Path $oldCopy '.git')) -and (Test-InOneDrive $oldCopy) -and
    -not $oldCopy.Equals($Path, [StringComparison]::OrdinalIgnoreCase)) {
    Write-Warn "Found an existing copy in OneDrive: $oldCopy"
    if (-not (Test-Path $Path)) {
        $answer = Read-Host "Move it to $Path? OneDrive will then remove it from the cloud copy too. (Y/N)"
        if ($answer -match '^[Yy]') {
            New-Item -ItemType Directory -Force -Path (Split-Path $Path -Parent) | Out-Null
            Write-Step "Moving $oldCopy to $Path"
            Move-Item -LiteralPath $oldCopy -Destination $Path
            Write-Warn 'Checking the moved copy for OneDrive damage...'
            git -C $Path fsck --no-progress 2>&1 | Select-Object -First 5 | ForEach-Object { Write-Host "   $_" }
        }
    }
}

# --- 3. Clone or update -----------------------------------------------------
# core.longpaths avoids errors on deep paths; autocrlf=false keeps the model files byte-exact
$gitOpts = @('-c', 'core.longpaths=true', '-c', 'core.autocrlf=false')

if (Test-Path (Join-Path $Path '.git')) {
    Write-Step "Updating existing copy in $Path"
    git -C $Path config core.longpaths true
    git -C $Path fetch origin $Branch
    git -C $Path checkout $Branch
    git -C $Path pull --ff-only origin $Branch
}
else {
    if ((Test-Path $Path) -and (Get-ChildItem $Path -Force | Select-Object -First 1)) {
        throw "$Path exists and isn't empty. Pick another folder with -Path."
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $Path -Parent) | Out-Null
    Write-Step "Cloning $RepoUrl ($Branch) into $Path"
    git @gitOpts clone --branch $Branch $RepoUrl $Path
    git -C $Path config core.longpaths true
    git -C $Path config core.autocrlf false
}
if ($LASTEXITCODE -ne 0) { throw "Git failed (exit code $LASTEXITCODE)." }

Write-Step 'Done. Contents:'
Get-ChildItem $Path | Where-Object { $_.Name -notlike '.*' } | Format-Table Name, Length -AutoSize

Write-Host ''
Write-Host "Your copy: $Path"
Write-Host '  Compass_Hill_Master_Plan.pdf   the plan'
Write-Host '  blender\CompassHill.blend      open in Blender 4.2 or later'
Write-Host '  renders\                       Cycles stills'
Write-Host '  walkthrough\                   interactive walkthrough (run this script with -Serve)'
Write-Host ''
Write-Host 'Tip: to reach it from Documents, make a shortcut instead of moving the folder there.'

if (-not $Serve) {
    Write-Host ''
    Write-Host "To walk the estate: .\Get-CompassHill.ps1 -Path `"$Path`" -Serve"
    return
}

# --- 4. Serve the walkthrough ------------------------------------------------
$site = Join-Path $Path 'walkthrough'
$url = "http://localhost:$Port/"

# Prefer the py launcher; "python" may be the Microsoft Store placeholder
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = @('py', '-3') }
elseif ((Get-Command python -ErrorAction SilentlyContinue) -and ((& python --version 2>&1) -match 'Python 3')) { $py = @('python') }
if ($py) {
    Write-Step "Serving $site at $url with Python (press Ctrl+C to stop)"
    Start-Process $url
    $pyArgs = @($py | Select-Object -Skip 1) + @('-m', 'http.server', "$Port", '--directory', $site)
    & $py[0] @pyArgs
    return
}

Write-Step "Serving $site at $url (press Ctrl+C to stop)"
$types = @{
    '.html' = 'text/html; charset=utf-8'; '.js' = 'application/javascript'; '.css' = 'text/css'
    '.glb' = 'model/gltf-binary'; '.wasm' = 'application/wasm'; '.json' = 'application/json'
    '.png' = 'image/png'; '.jpg' = 'image/jpeg'
}
$listener = [System.Net.HttpListener]::new()
$listener.Prefixes.Add($url)
$listener.Start()
Start-Process $url
try {
    while ($listener.IsListening) {
        $ctx = $listener.GetContext()
        $rel = [Uri]::UnescapeDataString($ctx.Request.Url.AbsolutePath.TrimStart('/'))
        if ([string]::IsNullOrEmpty($rel)) { $rel = 'index.html' }
        $file = [IO.Path]::GetFullPath((Join-Path $site $rel))
        if ($file.StartsWith($site, [StringComparison]::OrdinalIgnoreCase) -and (Test-Path $file -PathType Leaf)) {
            $bytes = [IO.File]::ReadAllBytes($file)
            $ext = [IO.Path]::GetExtension($file).ToLower()
            $ctx.Response.ContentType = $(if ($types[$ext]) { $types[$ext] } else { 'application/octet-stream' })
            $ctx.Response.ContentLength64 = $bytes.Length
            $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
        }
        else { $ctx.Response.StatusCode = 404 }
        $ctx.Response.Close()
    }
}
finally { $listener.Stop() }

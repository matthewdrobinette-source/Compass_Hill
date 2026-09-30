<#
.SYNOPSIS
    Gets a local copy of the public Compass Hill repository and optionally opens the walkthrough.

.DESCRIPTION
    - With Git installed: clones the repository, or pulls the latest changes
      if a copy is already there. No sign-in is needed; the repository is public.
    - Without Git (or with -NoGit): downloads the branch as a ZIP and unpacks it.
      Run the script again to refresh the copy.
    - Keeps the copy OUTSIDE OneDrive (default: %USERPROFILE%\Projects\Compass_Hill).
      When OneDrive backs up Documents, Documents really lives in OneDrive\Documents;
      OneDrive syncing a .git folder, making files online-only and creating
      "-PCNAME" conflict copies corrupts repositories. OneDrive folders are refused
      unless you pass -AllowOneDrive.
    - With -Serve, starts a local web server for the walkthrough and opens it in
      your browser (Python if you have it, otherwise a built-in PowerShell server).

.EXAMPLE
    .\Get-CompassHill.ps1
    Copies the repository to C:\Users\<you>\Projects\Compass_Hill.

.EXAMPLE
    .\Get-CompassHill.ps1 -Serve
    Gets or updates the copy, then opens the walkthrough at http://localhost:8000/.

.EXAMPLE
    .\Get-CompassHill.ps1 -Path D:\Projects\Compass_Hill -NoGit
    Downloads the ZIP into D:\Projects\Compass_Hill without using Git.
#>
[CmdletBinding()]
param(
    [string]$Path = (Join-Path $env:USERPROFILE 'Projects\Compass_Hill'),
    [string]$Branch = 'claude/epic-bell-08fxwr',
    [switch]$Serve,
    [int]$Port = 8000,
    [switch]$NoGit,
    [switch]$AllowOneDrive
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'   # makes Invoke-WebRequest much faster in Windows PowerShell 5.1
$Owner = 'matthewdrobinette-source'
$Repo = 'Compass_Hill'
$RepoUrl = "https://github.com/$Owner/$Repo.git"
$ZipUrl = "https://github.com/$Owner/$Repo/archive/refs/heads/$Branch.zip"
$SafeDefault = Join-Path $env:USERPROFILE 'Projects\Compass_Hill'
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Warn($msg) { Write-Host $msg -ForegroundColor Yellow }

# --- OneDrive detection -----------------------------------------------------
function Get-OneDriveRoots {
    $roots = @($env:OneDrive, $env:OneDriveConsumer, $env:OneDriveCommercial)
    $key = 'HKCU:\Software\Microsoft\OneDrive\Accounts'   # work/school accounts can add more roots
    if (Test-Path $key) {
        Get-ChildItem $key -ErrorAction SilentlyContinue | ForEach-Object {
            $roots += (Get-ItemProperty $_.PSPath -ErrorAction SilentlyContinue).UserFolder
        }
    }
    $roots | Where-Object { $_ } | ForEach-Object { $_.TrimEnd('\') } | Sort-Object -Unique
}

function Resolve-FullPath([string]$p) {
    $full = [IO.Path]::GetFullPath([Environment]::ExpandEnvironmentVariables($p))
    # follow a junction/symlink on the deepest existing folder (e.g. a redirected Documents)
    $probe = $full
    while ($probe -and -not (Test-Path -LiteralPath $probe)) { $probe = Split-Path $probe -Parent }
    if ($probe) {
        $item = Get-Item -LiteralPath $probe -Force
        if ($item.LinkType -and $item.Target) {
            $full = (@($item.Target)[0]).TrimEnd('\') + $full.Substring($probe.TrimEnd('\').Length)
        }
    }
    return $full
}

function Test-InOneDrive([string]$p) {
    $full = Resolve-FullPath $p
    foreach ($root in Get-OneDriveRoots) {
        if ($full.Equals($root, [StringComparison]::OrdinalIgnoreCase) -or
            $full.StartsWith($root + '\', [StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return [bool]($full -match '\\OneDrive( - [^\\]+)?(\\|$)')
}

$Path = Resolve-FullPath $Path
$docs = [Environment]::GetFolderPath('MyDocuments')
if (Test-InOneDrive $docs) {
    Write-Host "Note: your Documents folder is synced by OneDrive ($docs), so the copy goes elsewhere."
}
if ((Test-InOneDrive $Path) -and -not $AllowOneDrive) {
    Write-Warn "$Path is inside OneDrive, which corrupts Git repositories."
    $answer = Read-Host "Use $SafeDefault instead? (Y/N)"
    if ($answer -notmatch '^[Yy]') {
        throw 'Stopped. Pick a folder outside OneDrive with -Path, or pass -AllowOneDrive to override.'
    }
    $Path = $SafeDefault
}

# An older copy in OneDrive\Documents? Offer to move it out.
$oldCopy = Join-Path $docs 'Compass_Hill'
if ((Test-Path $oldCopy) -and (Test-InOneDrive $oldCopy) -and -not (Test-Path $Path) -and
    -not $oldCopy.Equals($Path, [StringComparison]::OrdinalIgnoreCase)) {
    Write-Warn "Found an older copy in OneDrive: $oldCopy"
    $answer = Read-Host "Move it to $Path? (OneDrive also removes it from the cloud.) (Y/N)"
    if ($answer -match '^[Yy]') {
        New-Item -ItemType Directory -Force -Path (Split-Path $Path -Parent) | Out-Null
        Write-Step "Moving $oldCopy to $Path"
        Move-Item -LiteralPath $oldCopy -Destination $Path
    }
}

# --- Get the files -------------------------------------------------------------
$haveGit = [bool](Get-Command git -ErrorAction SilentlyContinue)
$isClone = Test-Path (Join-Path $Path '.git')

if ($haveGit -and -not $NoGit) {
    if ($isClone) {
        Write-Step "Updating the copy in $Path"
        git -C $Path config core.longpaths true
        git -C $Path fetch origin $Branch
        if ($LASTEXITCODE -eq 0) { git -C $Path checkout $Branch }
        if ($LASTEXITCODE -eq 0) { git -C $Path pull --ff-only origin $Branch }
    }
    else {
        if ((Test-Path $Path) -and (Get-ChildItem $Path -Force | Select-Object -First 1)) {
            throw "$Path exists and isn't empty. Pick another folder with -Path, or add -NoGit to refresh a ZIP copy."
        }
        New-Item -ItemType Directory -Force -Path (Split-Path $Path -Parent) | Out-Null
        Write-Step "Cloning $RepoUrl ($Branch) into $Path"
        git -c core.longpaths=true -c core.autocrlf=false clone --branch $Branch $RepoUrl $Path
        if ($LASTEXITCODE -eq 0) {
            git -C $Path config core.longpaths true
            git -C $Path config core.autocrlf false
        }
    }
    if ($LASTEXITCODE -ne 0) { throw "Git failed (exit code $LASTEXITCODE)." }
}
else {
    if (-not $haveGit -and -not $NoGit) {
        Write-Host 'Git is not installed, so this downloads a ZIP instead.'
        Write-Host 'To get updates with Git later: winget install --id Git.Git -e, then run this script again'
        Write-Host '(point -Path at a new folder, since a ZIP copy is not a Git clone).'
    }
    if ($isClone) { throw "$Path is a Git clone. Update it with Git, or pick another folder for the ZIP copy." }
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("CompassHill-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $tmp | Out-Null
    try {
        $zip = Join-Path $tmp 'repo.zip'
        Write-Step "Downloading $ZipUrl (about 70 MB)"
        Invoke-WebRequest -Uri $ZipUrl -OutFile $zip -UseBasicParsing
        Write-Step 'Unpacking'
        Expand-Archive -LiteralPath $zip -DestinationPath $tmp -Force
        $top = Get-ChildItem $tmp -Directory | Select-Object -First 1   # Compass_Hill-claude-epic-bell-08fxwr
        New-Item -ItemType Directory -Force -Path $Path | Out-Null
        Write-Step "Copying into $Path"
        Copy-Item -Path (Join-Path $top.FullName '*') -Destination $Path -Recurse -Force
    }
    finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

Write-Step 'Done.'
Get-ChildItem $Path | Where-Object { $_.Name -notlike '.*' } | Format-Table Name, Length -AutoSize
Write-Host "Your copy: $Path"
Write-Host '  Compass_Hill_Master_Plan.pdf   the plan'
Write-Host '  blender\CompassHill.blend      open in Blender 4.2 or later'
Write-Host '  renders\                       Cycles stills'
Write-Host '  walkthrough\                   interactive walkthrough (run this script with -Serve)'
Write-Host 'Tip: to reach it from Documents, make a shortcut there instead of moving the folder.'

if (-not $Serve) {
    Write-Host ''
    Write-Host "To walk the estate: .\Get-CompassHill.ps1 -Path `"$Path`" -Serve"
    return
}

# --- Serve the walkthrough --------------------------------------------------------
$site = Join-Path $Path 'walkthrough'
$url = "http://localhost:$Port/"

# Prefer the py launcher; a bare "python" may be the Microsoft Store placeholder
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

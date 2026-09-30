<#
.SYNOPSIS
    Clones (or updates) the Compass Hill repository and optionally opens the walkthrough.

.DESCRIPTION
    - Checks for Git and offers to install it with winget if it's missing.
    - Clones the repository into the target folder, or pulls the latest
      changes if it's already there.
    - With -Serve, starts a local web server for the walkthrough and opens
      it in your browser. It uses Python if you have it; otherwise a small
      built-in PowerShell server.

    The repository is private. The first clone opens a GitHub sign-in window
    (Git Credential Manager, which comes with Git for Windows).

.EXAMPLE
    .\Get-CompassHill.ps1
    Clones to Documents\Compass_Hill.

.EXAMPLE
    .\Get-CompassHill.ps1 -Path D:\Projects\Compass_Hill -Serve
    Clones to D:\Projects\Compass_Hill, then opens the walkthrough.
#>
[CmdletBinding()]
param(
    [string]$Path = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Compass_Hill'),
    [string]$Branch = 'claude/epic-bell-08fxwr',
    [switch]$Serve,
    [int]$Port = 8000
)

$ErrorActionPreference = 'Stop'
$RepoUrl = 'https://github.com/matthewdrobinette-source/Compass_Hill.git'

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }

# --- 1. Git ---------------------------------------------------------------
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host 'Git is not installed.' -ForegroundColor Yellow
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

# --- 2. Clone or update -----------------------------------------------------

if (Test-Path (Join-Path $Path '.git')) {
    Write-Step "Updating existing copy in $Path"
    git -C $Path fetch origin $Branch
    git -C $Path checkout $Branch
    git -C $Path pull --ff-only origin $Branch
}
else {
    if ((Test-Path $Path) -and (Get-ChildItem $Path -Force | Select-Object -First 1)) {
        throw "$Path exists and isn't empty. Pick another folder with -Path."
    }
    Write-Step "Cloning $RepoUrl ($Branch) into $Path"
    git clone --branch $Branch $RepoUrl $Path
}

Write-Step 'Done. Contents:'
Get-ChildItem $Path | Where-Object { $_.Name -notlike '.*' } | Format-Table Name, Length -AutoSize

Write-Host ''
Write-Host 'What''s where:'
Write-Host '  Compass_Hill_Master_Plan.pdf   the plan'
Write-Host '  blender\CompassHill.blend      open in Blender 4.2 or later'
Write-Host '  renders\                       Cycles stills'
Write-Host '  walkthrough\                   interactive walkthrough (run this script with -Serve)'

if (-not $Serve) {
    Write-Host ''
    Write-Host "To walk the estate: .\Get-CompassHill.ps1 -Path `"$Path`" -Serve"
    return
}

# --- 3. Serve the walkthrough ------------------------------------------------
$site = Join-Path $Path 'walkthrough'
$url = "http://localhost:$Port/"
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python -and ((& python --version 2>&1) -match 'Python 3')) {
    Write-Step "Serving $site at $url with Python (close the window or press Ctrl+C to stop)"
    Start-Process $url
    & python -m http.server $Port --directory $site
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

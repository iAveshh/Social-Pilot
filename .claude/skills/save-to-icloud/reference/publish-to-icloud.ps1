<#
.SYNOPSIS
  Copy a finished reel and its covers into iCloud Drive, and verify the copy.

.DESCRIPTION
  Writes only into <Root>\<Slug>\. It never enumerates, reads or modifies
  anything else in iCloud Drive -- that folder holds the user's personal
  documents and is not ours to walk.

  Copying a file into the iCloud folder is NOT the same as it reaching iCloud.
  The sync client has to be running to upload it. This script reports what it
  actually observed: files staged, hashes verified, and whether the client was
  running at the time. It never claims an upload it cannot see.

.EXAMPLE
  .\publish-to-icloud.ps1 -Slug glm-flash-open-reel
  .\publish-to-icloud.ps1 -Slug glm-flash-open-reel -Caption (Get-Content cap.txt -Raw)
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$Slug,

  # Repo root; defaults to two levels above this script's skill folder.
  [string]$RepoRoot = 'D:\Github Forks\Social-Pilot',

  # Destination root: the account's own folder, one subfolder per project.
  # Point at "$env:USERPROFILE\Pictures\iCloud Photos" only if iCloud Photos is
  # actually configured to sync that folder.
  [string]$Root = "$env:USERPROFILE\iCloudDrive\optimalgradient\reels",

  # Optional caption + hashtags, written beside the video so it is on the phone
  # when posting. Posting itself happens outside this repo.
  [string]$Caption = ''
)

$ErrorActionPreference = 'Stop'

$proj = Join-Path $RepoRoot ("projects\" + $Slug)
if (-not (Test-Path $proj)) { throw "No such project: $proj" }

$renders = Join-Path $proj 'renders'
if (-not (Test-Path $renders)) { throw "No renders directory: $renders" }

# What we ship. The video is required; a missing cover is a hard stop, because
# shipping a reel without one is the thing the pipeline exists to prevent.
$plan = @(
  @{ From = 'final.mp4';          To = "$Slug.mp4";             Required = $true  },
  @{ From = 'thumbnail.png';      To = "$Slug-cover.png";       Required = $true  },
  @{ From = 'thumbnail.4x5.png';  To = "$Slug-cover-4x5.png";   Required = $false },
  @{ From = 'thumbnail.1x1.png';  To = "$Slug-cover-1x1.png";   Required = $false }
)

$missing = @()
foreach ($p in $plan) {
  if ($p.Required -and -not (Test-Path (Join-Path $renders $p.From))) { $missing += $p.From }
}
if ($missing.Count -gt 0) {
  throw ("Cannot publish, missing required file(s): " + ($missing -join ', ') +
         ". Render the reel and its cover first.")
}

$dest = Join-Path $Root $Slug
$freshTree = -not (Test-Path $dest)
New-Item -ItemType Directory -Force -Path $dest | Out-Null

# Exclusion is INHERITED. One excluded folder anywhere between the sync root and
# our files condemns the whole subtree, and the files inside still report a
# plausible-looking "Sync pending" forever. So check every level, not just the
# leaf -- an excluded intermediate is exactly what was missed the first time.
function Get-Avail {
  param([string]$Path)
  try {
    $shell = New-Object -ComObject Shell.Application
    $ns = $shell.NameSpace((Split-Path $Path -Parent))
    $item = $ns.ParseName((Split-Path $Path -Leaf))
    if ($null -eq $item) { return 'unknown' }
    return $ns.GetDetailsOf($item, 312)
  } catch { return 'unknown' }
}

$syncRoot = Join-Path $env:USERPROFILE 'iCloudDrive'
$chain = @()
if ($dest.StartsWith($syncRoot, [StringComparison]::OrdinalIgnoreCase)) {
  $cur = $dest
  while ($cur.Length -gt $syncRoot.Length) {
    $chain = @([pscustomobject]@{ path = $cur.Substring($syncRoot.Length).TrimStart('\')
                                  availability = (Get-Avail $cur) }) + $chain
    $cur = Split-Path $cur -Parent
  }
}
$badParent = @($chain | Where-Object { $_.availability -match 'Excluded' })
if ($badParent.Count -gt 0) {
  throw ("Folder '" + $badParent[0].path + "' is Excluded (not synced). " +
         "Everything beneath it is condemned and will never upload. Delete that " +
         "folder, let iCloud claim the recreated one, then re-run.")
}

# THE TRAP: files copied into a folder iCloud has not yet claimed are marked
# "Excluded (not synced)" and never upload. They sit on disk looking perfect --
# right size, right hash, no error anywhere -- while the phone shows nothing.
# The sync engine claims new directories within a few seconds, so when we just
# created the tree, wait for the claim (a reparse point) before writing into it.
if ($freshTree) {
  $deadline = (Get-Date).AddSeconds(45)
  while ((Get-Date) -lt $deadline) {
    $claimed = ((Get-Item -LiteralPath $dest -Force).Attributes -band
                [IO.FileAttributes]::ReparsePoint) -ne 0
    if ($claimed) { break }
    Start-Sleep -Milliseconds 1500
  }
}

$copied = @()
$skipped = @()
foreach ($p in $plan) {
  $src = Join-Path $renders $p.From
  if (-not (Test-Path $src)) { $skipped += $p.From; continue }

  $dst = Join-Path $dest $p.To
  Copy-Item -LiteralPath $src -Destination $dst -Force

  # Verify rather than trust. A truncated copy into a cloud-backed folder is
  # silent, and the whole point of this step is that the file left the machine.
  $hs = (Get-FileHash -LiteralPath $src -Algorithm SHA256).Hash
  $hd = (Get-FileHash -LiteralPath $dst -Algorithm SHA256).Hash
  if ($hs -ne $hd) { throw "Copy verification FAILED for $($p.To) - hashes differ." }

  $copied += [pscustomobject]@{
    name     = $p.To
    bytes    = (Get-Item -LiteralPath $dst).Length
    sha256   = $hd.Substring(0, 16)
    verified = $true
  }
}

# Ask the shell what Explorer's "Availability status" column says. This is the
# only reading that distinguishes "will upload" from "silently excluded" -- file
# attributes and hashes look identical in both cases.
function Get-Availability {
  param([string]$Dir, [string]$Name)
  try {
    $shell = New-Object -ComObject Shell.Application
    $ns = $shell.NameSpace($Dir)
    $item = $ns.ParseName($Name)
    if ($null -eq $item) { return 'unknown' }
    return $ns.GetDetailsOf($item, 312)   # 312 = Availability status
  } catch { return 'unknown' }
}

if ($Caption.Trim().Length -gt 0) {
  $capPath = Join-Path $dest "$Slug-caption.txt"
  # UTF-8 *without* a BOM. PS 5.1's `-Encoding utf8` writes one, and it rides
  # along as an invisible leading character when the caption is pasted.
  [System.IO.File]::WriteAllText(
    $capPath, $Caption, (New-Object System.Text.UTF8Encoding($false)))
  $copied += [pscustomobject]@{
    name = "$Slug-caption.txt"; bytes = (Get-Item -LiteralPath $capPath).Length
    sha256 = ''; verified = $true
  }
}

# Is the sync client actually running? If not, these files are staged on disk
# and will upload whenever iCloud next starts - say exactly that.
$proc = @(Get-Process -ErrorAction SilentlyContinue |
          Where-Object { $_.ProcessName -like '*iCloud*' })
$clientRunning = $proc.Count -gt 0

$installed = $null -ne (Get-AppxPackage -Name '*iCloud*' -ErrorAction SilentlyContinue)

# Give the engine a moment to claim what we just wrote, then read the truth.
Start-Sleep -Seconds 5
foreach ($c in $copied) {
  Add-Member -InputObject $c -NotePropertyName availability `
             -NotePropertyValue (Get-Availability -Dir $dest -Name $c.name) -Force
}
$excluded = @($copied | Where-Object { $_.availability -match 'Excluded' })

$syncState = if ($excluded.Count -gt 0) {
  'EXCLUDED_will_not_upload'
} elseif ($clientRunning) {
  'client_running_upload_expected'
} elseif ($installed) {
  'staged_locally_client_not_running'
} else {
  'staged_locally_client_not_installed'
}

[pscustomobject]@{
  destination     = $dest
  files           = $copied
  skipped         = $skipped
  excluded_count  = $excluded.Count
  client_running  = $clientRunning
  client_installed= $installed
  sync_state      = $syncState
  note            = switch ($syncState) {
    'EXCLUDED_will_not_upload' { 'FAILED TO SYNC: iCloud marked these files "Excluded (not synced)" - they are on disk but will NEVER upload. Delete the files (keep the folders, which iCloud has now claimed) and re-run; copying into an already-claimed folder fixes it.' }
    'client_running_upload_expected'      { 'iCloud is running; upload should follow shortly. Confirm on the device before relying on it.' }
    'staged_locally_client_not_running'   { 'Files are on disk in the iCloud folder but iCloud is NOT running - nothing has uploaded yet. Start iCloud for Windows to sync.' }
    'staged_locally_client_not_installed' { 'iCloud for Windows was not detected. Files are staged at the path above only.' }
  }
} | ConvertTo-Json -Depth 5

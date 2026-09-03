#Requires -Version 5.1

param(
    [string[]]$SearchRoots = @(
        "$env:ProgramFiles\Jellyfin",
        "${env:ProgramFiles(x86)}\Jellyfin",
        "$env:ProgramData\Jellyfin"
    )
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "Jellyfin Animated Splash Installer"
Write-Host "================================="
Write-Host ""

# -------------------------------------------------------------------------
# Open file picker
# -------------------------------------------------------------------------

Add-Type -AssemblyName System.Windows.Forms

$FileDialog = New-Object System.Windows.Forms.OpenFileDialog
$FileDialog.Title = "Select Jellyfin animated startup logo"
$FileDialog.Filter = "WebP Images (*.webp)|*.webp|Image Files (*.webp;*.png;*.gif)|*.webp;*.png;*.gif|All Files (*.*)|*.*"
$FileDialog.FilterIndex = 1
$FileDialog.Multiselect = $false
$FileDialog.CheckFileExists = $true
$FileDialog.CheckPathExists = $true

$Result = $FileDialog.ShowDialog()

if ($Result -ne [System.Windows.Forms.DialogResult]::OK) {
    Write-Host "No file selected. Exiting."
    exit 0
}

$LogoFile = $FileDialog.FileName
$TargetFileName = [System.IO.Path]::GetFileName($LogoFile)

Write-Host "[+] Selected splash image:"
Write-Host "    $LogoFile"
Write-Host ""

Write-Host "[+] Target filename:"
Write-Host "    $TargetFileName"
Write-Host ""

# -------------------------------------------------------------------------
# Validate source logo
# -------------------------------------------------------------------------

$LogoFile = [System.IO.Path]::GetFullPath($LogoFile)

if (-not (Test-Path -LiteralPath $LogoFile -PathType Leaf)) {
    throw "Selected logo file does not exist: $LogoFile"
}

# -------------------------------------------------------------------------
# Find valid Jellyfin search roots
# -------------------------------------------------------------------------

$ValidRoots = @(
    $SearchRoots |
        Where-Object {
            $_ -and (Test-Path -LiteralPath $_ -PathType Container)
        } |
        Select-Object -Unique
)

if (-not $ValidRoots) {
    throw "Could not find a Jellyfin installation in any configured search root."
}

Write-Host "[+] Searching Jellyfin installation paths..."

foreach ($Root in $ValidRoots) {
    Write-Host "    $Root"
}

Write-Host ""

# -------------------------------------------------------------------------
# Find HTML/CSS files containing .splashLogo
#
# This intentionally searches recursively instead of relying on a fixed
# Jellyfin file path.
# -------------------------------------------------------------------------

$CandidateFiles = foreach ($Root in $ValidRoots) {

    Get-ChildItem `
        -LiteralPath $Root `
        -Recurse `
        -File `
        -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in @(".html", ".htm", ".css")
    } |
    ForEach-Object {

        $File = $_

        try {
            $Content = [System.IO.File]::ReadAllText($File.FullName)

            if ($Content -match '\.splashLogo') {

                [PSCustomObject]@{
                    File    = $File
                    Content = $Content
                }
            }
        }
        catch {
            # Ignore unreadable files.
        }
    }
}

if (-not $CandidateFiles) {
    throw "No Jellyfin HTML/CSS file containing '.splashLogo' was found."
}

Write-Host "[+] Found splash styling in:"

foreach ($Candidate in $CandidateFiles) {
    Write-Host "    $($Candidate.File.FullName)"
}

Write-Host ""

# -------------------------------------------------------------------------
# Regex for splashLogo blocks containing background-image
#
# Examples supported:
#
# .splashLogo {
#     background-image: url(assets/img/banner-light.png);
# }
#
# .splashLogo{background-image:url("assets/img/banner-light.png")}
#
# .splashLogo{background-image:url('assets/img/banner-light.png')}
#
# -------------------------------------------------------------------------

$SplashBlockPattern = '(?is)(\.splashLogo\s*\{[^{}]*?background-image\s*:\s*url\(\s*["'']?)([^)"'']+)(["'']?\s*\)[^{}]*?\})'

$ChangesMade = 0
$FilesChanged = @()

foreach ($Candidate in $CandidateFiles) {

    $FilePath = $Candidate.File.FullName
    $Content  = $Candidate.Content

    Write-Host ""
    Write-Host "[+] Inspecting:"
    Write-Host "    $FilePath"

    $Matches = [regex]::Matches(
        $Content,
        $SplashBlockPattern
    )

    if ($Matches.Count -eq 0) {

        Write-Host "    [!] .splashLogo exists, but no background-image URL was found."
        continue
    }

    Write-Host "    [+] Found $($Matches.Count) splash image reference(s)."

    # ---------------------------------------------------------------------
    # Determine where Jellyfin currently stores the referenced splash asset
    # ---------------------------------------------------------------------

    $ExistingReference = $Matches[0].Groups[2].Value.Trim()

    Write-Host "    [+] Existing splash reference:"
    Write-Host "        $ExistingReference"

    # Ignore externally hosted or embedded images because they do not reveal
    # a reliable local asset directory.
    $IsRemoteReference =
        $ExistingReference -match '^(https?:)?//' -or
        $ExistingReference -match '^data:'

    if ($IsRemoteReference) {

        Write-Host "    [!] Existing splash image is remote or embedded."
        Write-Host "    [!] Cannot reliably determine a local Jellyfin asset path."
        continue
    }

    # Strip query string and hash fragments if Jellyfin ever adds cache
    # busting to the asset URL.
    $CleanReference = $ExistingReference -replace '[?#].*$', ''

    # Normalize web-style slashes to Windows filesystem separators.
    $CleanReference = $CleanReference.Replace(
        '/',
        [System.IO.Path]::DirectorySeparatorChar
    )

    $ContainingDirectory = Split-Path -Parent $FilePath

    # A leading slash in HTML/CSS normally refers to the web root rather
    # than the Windows filesystem root.
    if ($CleanReference.StartsWith(
        [System.IO.Path]::DirectorySeparatorChar
    )) {

        $CleanReference = $CleanReference.TrimStart(
            [System.IO.Path]::DirectorySeparatorChar
        )
    }

    # Resolve the referenced asset path relative to the HTML/CSS file.
    $ExistingAssetPath = Join-Path `
        $ContainingDirectory `
        $CleanReference

    try {
        $ExistingAssetPath = [System.IO.Path]::GetFullPath(
            $ExistingAssetPath
        )
    }
    catch {

        Write-Host "    [!] Could not resolve the existing Jellyfin asset path."
        continue
    }

    $AssetDirectory = Split-Path -Parent $ExistingAssetPath

    Write-Host "    [+] Resolved Jellyfin asset directory:"
    Write-Host "        $AssetDirectory"

    if (-not (Test-Path -LiteralPath $AssetDirectory -PathType Container)) {

        Write-Host "    [!] Resolved asset directory does not exist."
        Write-Host "    [!] Skipping this file."
        continue
    }

    # ---------------------------------------------------------------------
    # Copy selected animation into Jellyfin's existing asset directory
    # ---------------------------------------------------------------------

    $DestinationLogo = Join-Path `
        $AssetDirectory `
        $TargetFileName

    try {

        Copy-Item `
            -LiteralPath $LogoFile `
            -Destination $DestinationLogo `
            -Force

        Write-Host "    [+] Installed splash image:"
        Write-Host "        $DestinationLogo"
    }
    catch {

        Write-Host "    [!] Failed to copy splash image."
        Write-Host "        $($_.Exception.Message)"
        continue
    }

    # ---------------------------------------------------------------------
    # Build replacement URL
    #
    # Preserve Jellyfin's existing directory structure and replace only
    # the filename.
    # ---------------------------------------------------------------------

    $ReferenceDirectory = ""

    $LastForwardSlash = $ExistingReference.LastIndexOf('/')
    $LastBackSlash    = $ExistingReference.LastIndexOf('\')

    $LastSlash = [Math]::Max(
        $LastForwardSlash,
        $LastBackSlash
    )

    if ($LastSlash -ge 0) {

        $ReferenceDirectory = $ExistingReference.Substring(
            0,
            $LastSlash + 1
        )
    }

    $NewReference = "$ReferenceDirectory$TargetFileName"

    Write-Host "    [+] New splash reference:"
    Write-Host "        $NewReference"

    # ---------------------------------------------------------------------
    # Create backup
    #
    # Only creates the backup once so the original Jellyfin file remains
    # recoverable even if the script is run multiple times.
    # ---------------------------------------------------------------------

    $BackupPath = "$FilePath.jellyfin-animated-intro.bak"

    if (-not (Test-Path -LiteralPath $BackupPath)) {

        try {

            Copy-Item `
                -LiteralPath $FilePath `
                -Destination $BackupPath

            Write-Host "    [+] Backup created:"
            Write-Host "        $BackupPath"
        }
        catch {

            Write-Host "    [!] Could not create backup."
            Write-Host "        $($_.Exception.Message)"
            continue
        }
    }
    else {

        Write-Host "    [=] Backup already exists:"
        Write-Host "        $BackupPath"
    }

    # ---------------------------------------------------------------------
    # Replace only background-image values inside .splashLogo CSS blocks
    # ---------------------------------------------------------------------

    $Evaluator = {

        param($Match)

        return (
            $Match.Groups[1].Value +
            $NewReference +
            $Match.Groups[3].Value
        )
    }

    $NewContent = [regex]::Replace(
        $Content,
        $SplashBlockPattern,
        $Evaluator
    )

    if ($NewContent -eq $Content) {

        Write-Host "    [=] File already appears to be configured."
        continue
    }

    # ---------------------------------------------------------------------
    # Save modified file as UTF-8 without BOM
    # ---------------------------------------------------------------------

    try {

        $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)

        [System.IO.File]::WriteAllText(
            $FilePath,
            $NewContent,
            $Utf8NoBom
        )

        $ChangesMade++
        $FilesChanged += $FilePath

        Write-Host "    [+] Splash configuration updated."
    }
    catch {

        Write-Host "    [!] Failed to update:"
        Write-Host "        $FilePath"
        Write-Host "        $($_.Exception.Message)"
        continue
    }
}

# -------------------------------------------------------------------------
# Summary
# -------------------------------------------------------------------------

Write-Host ""
Write-Host "================================="

if ($ChangesMade -gt 0) {

    Write-Host "[+] Jellyfin animated splash installed successfully."
    Write-Host "[+] Modified file(s): $ChangesMade"
    Write-Host ""

    foreach ($ChangedFile in $FilesChanged) {
        Write-Host "    $ChangedFile"
    }

    Write-Host ""
    Write-Host "[+] Installed image:"
    Write-Host "    $TargetFileName"
    Write-Host ""
    Write-Host "Restart Jellyfin, then hard-refresh the browser."
}
else {

    Write-Host "[!] No Jellyfin files were modified."
    Write-Host ""
    Write-Host "Possible reasons:"
    Write-Host "    - Jellyfin uses a different splash CSS selector."
    Write-Host "    - The splash image is embedded directly in the web client."
    Write-Host "    - Jellyfin is installed outside the configured search paths."
    Write-Host "    - The script was not run with sufficient permissions."
}

Write-Host "================================="
Write-Host ""

Read-Host "Press Enter to close"

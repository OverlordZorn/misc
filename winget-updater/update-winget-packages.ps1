param(
    [switch]$DryRun
)

# === LOGGING ===
$logFile = "$PSScriptRoot\winget-manager.log"

function Log {
    param([string]$Message)
    $timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$timestamp] $Message"
    Write-Output $line
    Add-Content -Path $logFile -Value $line
}

Log "=== Starting package check (DryRun=$DryRun) ==="

# === LOAD CONFIG FROM JSON ===
$configFile = "$PSScriptRoot\packages.json"
if (-not (Test-Path $configFile)) {
    Log "❌ Config file packages.json not found!"
    exit
}

$packages = Get-Content $configFile | ConvertFrom-Json

foreach ($packageId in $packages.PSObject.Properties.Name) {
    $blacklist = $packages.$packageId.Blacklist
    $fallback  = $packages.$packageId.Fallback

    Log "----------------------------"
    Log "Checking $packageId"
    Log "Blacklist: $($blacklist -join ', ') | Fallback: $fallback"

    # Get installed info
    $installedInfo = winget list --id $packageId | Select-String $packageId

    # === CASE: Package missing or after uninstall ===
    if (-not $installedInfo) {
        Log "⚠️ Package $packageId is not installed. Determining latest safe version..."

        # Get all available versions from winget
        $versions = (winget show --id $packageId | Select-String "Version:") -replace "Version:\s*", ""
        $allVersions = $versions | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }

        # Pick newest safe version
        $target = $allVersions | Where-Object { $_ -notin $blacklist } | Sort-Object {[version]$_} -Descending | Select-Object -First 1

        if (-not $target -and $fallback) {
            $target = $fallback
            Log "No safe version found in repository. Using fallback $fallback."
        }

        if ($target) {
            Log "⬇️ Installing version $target..."
            if (-not $DryRun) {
                winget install --id $packageId --version $target --silent --accept-source-agreements
            }
        } else {
            Log "❌ No safe version available for $packageId. Skipping installation."
        }
        continue
    }

    # Parse installed version
    $parts = $installedInfo.ToString().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
    $installedVersion = $parts[-2]
    Log "Installed version: $installedVersion"

    # === CASE 1: Installed version is blacklisted → uninstall & install safe ===
    if ($blacklist -contains $installedVersion) {
        Log "⚠️ Installed version $installedVersion is blacklisted. Uninstalling..."
        if (-not $DryRun) {
            winget uninstall --id $packageId --silent --accept-source-agreements
        }

        # Determine latest safe version
        $versions = (winget show --id $packageId | Select-String "Version:") -replace "Version:\s*", ""
        $allVersions = $versions | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" }
        $target = $allVersions | Where-Object { $_ -notin $blacklist } | Sort-Object {[version]$_} -Descending | Select-Object -First 1

        if (-not $target -and $fallback) {
            $target = $fallback
            Log "No safe previous version found. Using fallback $fallback."
        }

        if ($target) {
            Log "⬇️ Installing version $target..."
            if (-not $DryRun) {
                winget install --id $packageId --version $target --silent --accept-source-agreements
            }
        } else {
            Log "❌ No safe version available for $packageId."
        }
        continue
    }

    # === CASE 2: Installed version is safe → check for updates ===
    $upgradeInfo = winget upgrade --id $packageId | Select-String $packageId
    if ($upgradeInfo) {
        $upgradeParts = $upgradeInfo.ToString().Split(" ", [System.StringSplitOptions]::RemoveEmptyEntries)
        $availableVersion = $upgradeParts[-1]
        Log "Update available: $availableVersion"

        if ($blacklist -contains $availableVersion) {
            Log "⚠️ Update $availableVersion is blacklisted. Skipping."
        } else {
            Log "✅ Updating to $availableVersion..."
            if (-not $DryRun) {
                winget upgrade --id $packageId --silent --accept-source-agreements
            }
        }
    } else {
        Log "No updates available for $packageId."
    }
}

Log "=== Finished package check ==="

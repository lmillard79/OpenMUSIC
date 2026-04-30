#Requires -Version 5.1
<#
.SYNOPSIS
    Background-friendly scanner for MUSIC .sqz files on J and V drives.

.DESCRIPTION
    Recursively searches J: and V: drives for .sqz files.
    Low priority execution to avoid impacting other work.
    Results are saved to a CSV file for later analysis.

.PARAMETER OutputPath
    Path to save the results CSV. Default: D:\GitRepos\OpenMUSIC\data\sqz_inventory.csv

.PARAMETER MaxDepth
    Maximum directory depth to search. Default: 20 (sufficient for most structures)

.EXAMPLE
    .\find_sqz_files.ps1
    Searches J: and V: drives and saves results to default location.

.EXAMPLE
    .\find_sqz_files.ps1 -OutputPath "C:\temp\sqz_files.csv"
    Searches and saves to custom location.
#>

[CmdletBinding()]
param(
    [string]$OutputPath = "D:\GitRepos\OpenMUSIC\data\sqz_inventory.csv",
    [int]$MaxDepth = 20
)

# Set low process priority to be background-friendly
$process = Get-Process -Id $PID
$process.PriorityClass = 'BelowNormal'

$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()

Write-Host "Starting background scan for .sqz files on J: and V: drives..." -ForegroundColor Cyan
Write-Host "Process priority set to BelowNormal to minimize impact." -ForegroundColor Gray
Write-Host "Results will be saved to: $OutputPath" -ForegroundColor Gray
Write-Host ""

# Ensure output directory exists
$outputDir = Split-Path -Parent $OutputPath
if (-not (Test-Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
}

# Initialize results collection
$results = [System.Collections.Generic.List[PSObject]]::new()

# Track statistics
$stats = @{
    FilesFound = 0
    DirectoriesScanned = 0
    Errors = 0
    StartTime = Get-Date
}

# Function to scan a drive with error handling
function Scan-Drive {
    param(
        [string]$DriveLetter,
        [int]$MaxDepth
    )

    $drivePath = "${DriveLetter}:\"

    if (-not (Test-Path $drivePath)) {
        Write-Warning "Drive $drivePath is not available. Skipping."
        return
    }

    Write-Host "Scanning $drivePath..." -ForegroundColor Yellow

    try {
        # Use Get-ChildItem with -File and -Recurse for efficient scanning
        # -Depth parameter prevents excessive recursion on problematic directories
        $files = Get-ChildItem -Path $drivePath -Filter "*.sqz" -File -Recurse -Depth $MaxDepth -ErrorAction SilentlyContinue -ErrorVariable scanErrors

        foreach ($file in $files) {
            $result = [PSCustomObject]@{
                FilePath = $file.FullName
                FileName = $file.Name
                SizeBytes = $file.Length
                SizeKB = [math]::Round($file.Length / 1KB, 2)
                LastModified = $file.LastWriteTime
                Created = $file.CreationTime
                Drive = $DriveLetter
                Directory = $file.DirectoryName
            }
            $results.Add($result)
            $stats.FilesFound++

            # Progress indicator every 100 files
            if ($stats.FilesFound % 100 -eq 0) {
                Write-Host "  Found $($stats.FilesFound) files so far..." -ForegroundColor Gray
            }
        }

        # Count errors
        $stats.Errors += $scanErrors.Count

        if ($scanErrors.Count -gt 0) {
            Write-Host "  ($($scanErrors.Count) access errors - normal for restricted directories)" -ForegroundColor Gray
        }

    }
    catch {
        Write-Error "Failed to scan ${drivePath}: $_"
        $stats.Errors++
    }
}

# Scan J: drive
Scan-Drive -DriveLetter "J" -MaxDepth $MaxDepth

# Scan V: drive
Scan-Drive -DriveLetter "V" -MaxDepth $MaxDepth

# Export results
if ($results.Count -gt 0) {
    $results | Export-Csv -Path $OutputPath -NoTypeInformation -Encoding UTF8
    Write-Host ""
    Write-Host "Scan complete. Found $($results.Count) .sqz files." -ForegroundColor Green
    Write-Host "Results saved to: $OutputPath" -ForegroundColor Green

    # Show summary by drive
    Write-Host ""
    Write-Host "Summary by drive:" -ForegroundColor Cyan
    $results | Group-Object Drive | Select-Object Name, Count | ForEach-Object {
        Write-Host "  $($_.Name): drive - $($_.Count) files"
    }

    # Show largest files
    Write-Host ""
    Write-Host "Largest files:" -ForegroundColor Cyan
    $results | Sort-Object SizeBytes -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $($_.SizeKB) KB - $($_.FileName)"
    }

    # Show most recent
    Write-Host ""
    Write-Host "Most recently modified:" -ForegroundColor Cyan
    $results | Sort-Object LastModified -Descending | Select-Object -First 5 | ForEach-Object {
        Write-Host "  $($_.LastModified.ToString('yyyy-MM-dd')) - $($_.FileName)"
    }
}
else {
    Write-Host ""
    Write-Host "No .sqz files found on J: or V: drives." -ForegroundColor Yellow
}

$stopwatch.Stop()
Write-Host ""
Write-Host "Scan completed in $($stopwatch.Elapsed.ToString('hh\:mm\:ss'))." -ForegroundColor Gray
Write-Host "Errors encountered: $($stats.Errors)" -ForegroundColor Gray

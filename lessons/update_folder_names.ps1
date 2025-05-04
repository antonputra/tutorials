# PowerShell script to update lesson folder names with YouTube video titles

function Get-VideoIdFromReadme {
    param (
        [string]$readmePath
    )
    
    if (Test-Path $readmePath) {
        $content = Get-Content $readmePath -Raw
        if ($content -match 'youtu\.be/([a-zA-Z0-9_-]+)') {
            return $matches[1]
        }
        elseif ($content -match 'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)') {
            return $matches[1]
        }
    }
    return $null
}

function Format-FolderName {
    param (
        [string]$lessonNumber,
        [string]$videoTitle
    )
    
    # Remove special characters and replace spaces with hyphens
    $sanitizedTitle = $videoTitle -replace '[^\w\s-]', '' -replace '\s+', '-'
    return "$lessonNumber-$sanitizedTitle"
}

function Rename-LessonFolder {
    param (
        [string]$oldPath,
        [string]$newName
    )
    
    if (Test-Path $oldPath) {
        $parentPath = Split-Path $oldPath -Parent
        $newPath = Join-Path $parentPath $newName
        
        Write-Host "Renaming folder:"
        Write-Host "From: $oldPath"
        Write-Host "To: $newPath"
        
        try {
            Rename-Item -Path $oldPath -NewName $newName -ErrorAction Stop
            Write-Host "Successfully renamed folder" -ForegroundColor Green
        }
        catch {
            Write-Host "Error renaming folder: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "Folder not found: $oldPath" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Store the current directory
$scriptPath = $PSScriptRoot
$lessonsPath = Join-Path $scriptPath "lessons"

# Get all lesson folders
$lessonFolders = Get-ChildItem -Path $lessonsPath -Directory | Where-Object { $_.Name -match '^\d+$' }

Write-Host "Found $($lessonFolders.Count) lesson folders to process" -ForegroundColor Cyan

# Process each folder
foreach ($folder in $lessonFolders) {
    $readmePath = Join-Path $folder.FullName "README.md"
    $videoId = Get-VideoIdFromReadme -readmePath $readmePath
    
    if ($videoId) {
        Write-Host "Processing lesson $($folder.Name) with video ID: $videoId" -ForegroundColor Cyan
        
        try {
            # Here you would use the YouTube API to get the video title
            # For now, we'll use a hashtable for the examples we know
            $knownTitles = @{
                "dMca4jHaft8" = "Monitor-Containers-Kubernetes-Prometheus-cAdvisor-Grafana"
                "i3TcSeRO8gs" = "FastAPI-vs-NodeJS-Performance"
            }
            
            if ($knownTitles.ContainsKey($videoId)) {
                $newName = Format-FolderName -lessonNumber $folder.Name -videoTitle $knownTitles[$videoId]
                Rename-LessonFolder -oldPath $folder.FullName -newName $newName
            }
            else {
                Write-Host "No title found for video ID: $videoId" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "Error processing folder $($folder.Name): $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "No video ID found in README for lesson $($folder.Name)" -ForegroundColor Yellow
    }
}

Write-Host "Folder renaming complete. Please check if any file references need to be updated." -ForegroundColor Cyan

# List all renamed folders
Write-Host "Current lesson folders:" -ForegroundColor Cyan
Get-ChildItem -Path $lessonsPath -Directory | ForEach-Object {
    Write-Host $_.Name
} 
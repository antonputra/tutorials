# PowerShell script to rename lesson folders with video titles

# Function to safely rename folders
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

# Create a hashtable of lesson numbers and their new names
$lessonNames = @{
    "135" = "135-Monitor-Containers-Kubernetes-Prometheus-cAdvisor-Grafana"
    "236" = "236-FastAPI-vs-NodeJS-Performance"
}

# Rename each folder
foreach ($lesson in $lessonNames.GetEnumerator()) {
    $oldPath = Join-Path $lessonsPath $lesson.Key
    Rename-LessonFolder -oldPath $oldPath -newName $lesson.Value
}

# Update references in other files if needed
Write-Host "Folder renaming complete. Please check if any file references need to be updated." -ForegroundColor Cyan

# Optional: List all renamed folders
Write-Host "Current lesson folders:" -ForegroundColor Cyan
Get-ChildItem -Path $lessonsPath -Directory | ForEach-Object {
    Write-Host $_.Name
} 
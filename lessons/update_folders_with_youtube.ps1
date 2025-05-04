# PowerShell script to update lesson folder names using YouTube video titles

# Function to sanitize folder name
function Format-FolderName {
    param (
        [string]$lessonNumber,
        [string]$videoTitle
    )
    
    # Remove special characters and replace spaces with hyphens
    $sanitizedTitle = $videoTitle -replace '[^a-zA-Z0-9\s-]', '' -replace '\s+', '-'
    
    # Ensure the title is not too long (max 100 chars)
    if ($sanitizedTitle.Length -gt 100) {
        $sanitizedTitle = $sanitizedTitle.Substring(0, 100)
    }
    
    # Remove trailing hyphens and convert to lowercase
    $sanitizedTitle = $sanitizedTitle.Trim('-').ToLower()
    
    # Combine lesson number with sanitized title
    return "$lessonNumber-$sanitizedTitle"
}

# Function to extract lesson number from folder name
function Get-LessonNumber {
    param (
        [string]$folderName
    )
    
    if ($folderName -match '^\d+') {
        return $matches[0]
    }
    return $null
}

# Function to extract video ID from README content
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

# Create a hashtable of video titles
$videoTitles = @{
    'ECnlX00YcPI' = 'Go Golang vs Bun Performance Latency Throughput Saturation Availability'
    'dPO4v5q9ULU' = 'Bun vs Node.js Performance Latency Throughput Saturation Availability'
    'h2pCxj_Fkdc' = 'Go Golang vs Node.js Performance Latency Throughput Saturation Availability'
    'ZslbMp_T90k' = 'Node.js vs Go Golang Performance Latency Throughput Saturation Availability'
    'caNsPpRuBcw' = 'Django Python vs Go Golang Performance Latency Throughput Saturation Availability'
    'SR2LRhnL1AQ' = 'Actix Rust vs Zap Zig vs Zig Performance Latency Throughput Saturation Availability'
    'VxW0ijXAfOs' = 'Zap Zig vs Actix Rust Performance Latency Throughput Saturation Availability'
    'KA_w_jOGils' = 'Actix Rust vs Axum Rust vs Rocket Rust Performance Benchmark in Kubernetes'
    'ZfvpUDGGr24' = 'Rust vs Go Performance Benchmark in Kubernetes'
    'ok5DDDNsOaQ' = 'Fiber vs Gin vs Go stdlib Performance Latency Throughput Saturation Availability'
}

# Get all lesson folders
$lessonFolders = Get-ChildItem -Directory | Where-Object { $_.Name -match '^\d+' }

foreach ($folder in $lessonFolders) {
    $readmePath = Join-Path $folder.FullName "README.md"
    $lessonNumber = Get-LessonNumber $folder.Name
    
    if ($null -ne $lessonNumber) {
        $videoId = Get-VideoIdFromReadme $readmePath
        
        if ($null -ne $videoId -and $videoTitles.ContainsKey($videoId)) {
            $videoTitle = $videoTitles[$videoId]
            $newFolderName = Format-FolderName -lessonNumber $lessonNumber -videoTitle $videoTitle
            
            # Only rename if the folder name is different
            if ($folder.Name -ne $newFolderName) {
                Write-Host "Renaming folder '$($folder.Name)' to '$newFolderName'"
                try {
                    Rename-Item -Path $folder.FullName -NewName $newFolderName -ErrorAction Stop
                    Write-Host "Successfully renamed folder to '$newFolderName'" -ForegroundColor Green
                }
                catch {
                    Write-Host "Failed to rename folder '$($folder.Name)': $_" -ForegroundColor Red
                }
            }
            else {
                Write-Host "Folder '$($folder.Name)' already has the correct name" -ForegroundColor Yellow
            }
        }
        else {
            Write-Host "No video ID found or no title available for folder '$($folder.Name)'" -ForegroundColor Yellow
        }
    }
    else {
        Write-Host "Could not extract lesson number from folder '$($folder.Name)'" -ForegroundColor Red
    }
}

Write-Host "Folder renaming process completed" -ForegroundColor Green 
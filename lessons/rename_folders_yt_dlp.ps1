# Function to sanitize folder names
function Get-SanitizedName {
    param (
        [string]$title
    )
    
    # Remove special characters and replace spaces with hyphens
    $sanitized = $title -replace '[^\w\s-]', '' `
                       -replace '\s+', '-' `
                       -replace '-+', '-' `
                       -replace '^-+', '' `
                       -replace '-+$', ''
    
    # Convert to lowercase and limit length
    return $sanitized.ToLower().Substring(0, [Math]::Min(100, $sanitized.Length))
}

# Function to get video title using yt-dlp
function Get-VideoTitle {
    param (
        [string]$videoId
    )
    
    try {
        $url = "https://www.youtube.com/watch?v=$videoId"
        $title = & yt-dlp --get-title $url 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            return $title.Trim()
        }
        Write-Host "Error getting title for video $videoId" -ForegroundColor Red
        return $null
    }
    catch {
        Write-Host "Exception getting title for video $videoId : $_" -ForegroundColor Red
        return $null
    }
}

# Get all folders that match the pattern
$folders = Get-ChildItem -Directory | Where-Object { $_.Name -match '^\d+(-Video-[a-zA-Z0-9_-]+)?$' }

foreach ($folder in $folders) {
    # Extract lesson number and video ID
    if ($folder.Name -match '^(\d+)-Video-([a-zA-Z0-9_-]+)$') {
        $lessonNumber = $matches[1]
        $videoId = $matches[2]
        
        Write-Host "Processing folder $($folder.Name)..." -ForegroundColor Yellow
        
        # Get video title
        $title = Get-VideoTitle $videoId
        
        if ($title) {
            # Create new folder name
            $sanitizedTitle = Get-SanitizedName $title
            $newName = "$lessonNumber-$sanitizedTitle"
            
            # Rename folder if different
            if ($folder.Name -ne $newName) {
                try {
                    Write-Host "Renaming to: $newName" -ForegroundColor Cyan
                    Rename-Item -Path $folder.FullName -NewName $newName -ErrorAction Stop
                    Write-Host "Successfully renamed folder" -ForegroundColor Green
                }
                catch {
                    Write-Host "Error renaming folder: $_" -ForegroundColor Red
                }
            }
            else {
                Write-Host "Folder already has correct name" -ForegroundColor Green
            }
        }
        
        # Sleep to avoid rate limiting
        Start-Sleep -Milliseconds 200
    }
    else {
        Write-Host "Skipping folder $($folder.Name) - doesn't match pattern" -ForegroundColor Yellow
    }
}

Write-Host "Finished processing all folders" -ForegroundColor Green 
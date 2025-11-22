# Script to stop all old uvicorn servers except the newest one
Write-Host "Stopping old uvicorn servers..." -ForegroundColor Yellow

# Get all Python processes running uvicorn
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like '*uvicorn*' -and $_.CommandLine -like '*8000*'
}

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) uvicorn processes" -ForegroundColor Cyan
    
    # Sort by start time and get all except the newest one
    $oldProcesses = $pythonProcesses | Sort-Object StartTime | Select-Object -SkipLast 1
    
    if ($oldProcesses) {
        Write-Host "Stopping $($oldProcesses.Count) old processes..." -ForegroundColor Yellow
        foreach ($proc in $oldProcesses) {
            Write-Host "  Stopping PID $($proc.Id)..." -ForegroundColor Gray
            Stop-Process -Id $proc.Id -Force
        }
        Write-Host "✅ Old servers stopped!" -ForegroundColor Green
    } else {
        Write-Host "✅ Only one server running - nothing to stop!" -ForegroundColor Green
    }
    
    # Show remaining process
    Start-Sleep -Seconds 1
    $remaining = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
        $_.CommandLine -like '*uvicorn*' -and $_.CommandLine -like '*8000*'
    }
    
    if ($remaining) {
        Write-Host "`nRemaining server:" -ForegroundColor Cyan
        Write-Host "  PID: $($remaining.Id)" -ForegroundColor White
        Write-Host "  Started: $($remaining.StartTime)" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  No uvicorn servers found running" -ForegroundColor Red
}

Write-Host "`nDone! You can now test with WhatsApp." -ForegroundColor Green

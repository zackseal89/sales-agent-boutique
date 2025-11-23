# Setup Script for AI Settings Feature
# Run this to install all required dependencies

Write-Host "🚀 Setting up AI Settings Feature..." -ForegroundColor Green
Write-Host ""

# Navigate to dashboard directory
Set-Location -Path "dashboard"

Write-Host "📦 Installing npm dependencies..." -ForegroundColor Cyan
npm install date-fns

Write-Host ""
Write-Host "🎨 Installing shadcn/ui components..." -ForegroundColor Cyan
Write-Host "   This will install: alert, badge, tabs, select, dialog, scroll-area" -ForegroundColor Gray

# Install components one by one
$components = @("alert", "badge", "tabs", "select", "dialog", "scroll-area")

foreach ($component in $components) {
    Write-Host "   Installing $component..." -ForegroundColor Yellow
    npx -y shadcn-ui@latest add $component --overwrite
}

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run 'npm run dev' to start the dashboard"
Write-Host "  2. Navigate to http://localhost:3000/dashboard/ai-settings"
Write-Host "  3. Test the AI Settings page"
Write-Host ""

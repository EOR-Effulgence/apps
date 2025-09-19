# PDF2PNG/PDF2PPTX UV-based Build Script
# High-performance build using UV package manager

param(
    [string]$Version = "3.0.0",
    [string]$OutputDir = ".\release",
    [switch]$Clean = $false,
    [switch]$Test = $false,
    [switch]$Dev = $false,
    [switch]$Verbose = $false,
    [string]$PythonVersion = "3.11"
)

$ErrorActionPreference = "Stop"
$StopWatch = [System.Diagnostics.Stopwatch]::StartNew()

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
    Progress = "DarkCyan"
}

function Write-ColorOutput {
    param([string]$Message, [string]$Color = "White")
    Write-Host $Message -ForegroundColor $Colors[$Color]
}

function Write-Header {
    param([string]$Title)
    $border = "=" * 60
    Write-ColorOutput "" "Header"
    Write-ColorOutput $border "Header"
    Write-ColorOutput "  $Title" "Header"
    Write-ColorOutput $border "Header"
}

function Test-UvInstallation {
    Write-Header "UV Installation Check"

    try {
        $uvVersion = uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ UV found: $uvVersion" "Success"
            return $true
        }
    }
    catch {}

    Write-ColorOutput "❌ UV not found. Installing UV..." "Warning"

    # Install UV using the official installer
    try {
        if ($IsWindows -or $env:OS -eq "Windows_NT") {
            # Windows installation
            Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
        } else {
            # Unix-like installation
            Invoke-RestMethod https://astral.sh/uv/install.sh | sh
        }

        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")

        $uvVersion = uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✅ UV installed successfully: $uvVersion" "Success"
            return $true
        } else {
            throw "UV installation verification failed"
        }
    }
    catch {
        Write-ColorOutput "❌ Failed to install UV: $($_.Exception.Message)" "Error"
        Write-ColorOutput "Please install UV manually from: https://github.com/astral-sh/uv" "Info"
        return $false
    }
}

function Setup-UvEnvironment {
    Write-Header "UV Environment Setup"

    # Use pyproject_uv.toml if available
    $projectFile = if (Test-Path "pyproject_uv.toml") { "pyproject_uv.toml" } else { "pyproject.toml" }
    Write-ColorOutput "📋 Using project file: $projectFile" "Info"

    # Create UV project if needed
    if (-not (Test-Path ".python-version")) {
        Write-ColorOutput "🐍 Setting Python version to $PythonVersion..." "Info"
        uv python pin $PythonVersion
    }

    # Create/update virtual environment
    Write-ColorOutput "📦 Creating UV virtual environment..." "Info"
    uv venv --python $PythonVersion

    # Install dependencies
    Write-ColorOutput "📥 Installing dependencies with UV..." "Info"

    if ($Dev) {
        Write-ColorOutput "🔧 Installing development dependencies..." "Info"
        uv pip install -e ".[dev,build]"
    } else {
        Write-ColorOutput "🚀 Installing production dependencies..." "Info"
        uv pip install -e ".[build]"
    }

    Write-ColorOutput "✅ UV environment ready" "Success"
}

function Test-Dependencies {
    Write-Header "Dependency Verification"

    $requiredPackages = @("PyMuPDF", "python-pptx", "Pillow", "pyinstaller")

    foreach ($package in $requiredPackages) {
        try {
            $result = uv pip show $package 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-ColorOutput "✅ ${package}: installed" "Success"
            } else {
                Write-ColorOutput "❌ ${package}: missing" "Error"
                throw "${package} is not installed"
            }
        }
        catch {
            Write-ColorOutput "❌ Error checking ${package}" "Error"
            throw
        }
    }

    Write-ColorOutput "✅ All dependencies verified" "Success"
}

function Run-Tests {
    if (-not $Test) {
        return
    }

    Write-Header "Running Tests"

    Write-ColorOutput "🧪 Running test suite with UV..." "Info"

    # Run tests using UV
    uv run pytest tests/ -v

    if ($LASTEXITCODE -ne 0) {
        throw "Tests failed"
    }

    Write-ColorOutput "✅ All tests passed" "Success"
}

function Clean-BuildArtifacts {
    if ($Clean) {
        Write-Header "Cleaning Build Artifacts"

        $dirsToClean = @("build", "dist", "__pycache__", ".pytest_cache", ".mypy_cache", "*.egg-info")

        foreach ($dir in $dirsToClean) {
            if (Test-Path $dir) {
                Write-ColorOutput "🧹 Removing $dir..." "Info"
                Remove-Item -Recurse -Force $dir
            }
        }

        # Clean Python cache files
        Get-ChildItem -Path . -Recurse -Name "*.pyc" -ErrorAction SilentlyContinue | ForEach-Object {
            Remove-Item -Force $_
        }

        Write-ColorOutput "✅ Build artifacts cleaned" "Success"
    }
}

function Build-Application {
    Write-Header "Building Application with UV"

    Write-ColorOutput "🔨 Starting PyInstaller build..." "Info"
    Write-ColorOutput "   Version: $Version" "Info"
    Write-ColorOutput "   Build spec: build_windows.spec" "Info"

    # Use UV to run PyInstaller
    $buildStartTime = Get-Date

    uv run pyinstaller build_windows.spec --clean --noconfirm

    $buildEndTime = Get-Date

    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller build failed"
    }

    $buildDuration = $buildEndTime - $buildStartTime
    Write-ColorOutput "✅ Build completed in $([math]::Round($buildDuration.TotalMinutes, 1)) minutes" "Success"
}

function Validate-Build {
    Write-Header "Build Validation"

    $exePath = "dist\PDF2PNG_Converter.exe"

    if (-not (Test-Path $exePath)) {
        throw "Executable not found: $exePath"
    }

    # File size check
    $fileSize = (Get-Item $exePath).Length / 1MB
    Write-ColorOutput "📊 Executable size: $([math]::Round($fileSize, 1)) MB" "Info"

    # Quick test
    Write-ColorOutput "🧪 Running application test..." "Info"

    try {
        $process = Start-Process -FilePath $exePath -ArgumentList "--test-mode" -Wait -PassThru -WindowStyle Hidden

        if ($process.ExitCode -eq 0) {
            Write-ColorOutput "✅ Application test passed" "Success"
        } else {
            Write-ColorOutput "⚠️  Application test returned code: $($process.ExitCode)" "Warning"
        }
    }
    catch {
        Write-ColorOutput "⚠️  Could not run application test: $($_.Exception.Message)" "Warning"
    }
}

function Create-ReleasePackage {
    Write-Header "Creating Release Package"

    $releaseDir = "$OutputDir\PDF2PNG_Windows_v$Version"
    $zipPath = "$OutputDir\PDF2PNG_Windows_v$Version.zip"

    # Create release directory
    if (Test-Path $releaseDir) {
        Remove-Item -Recurse -Force $releaseDir
    }
    New-Item -ItemType Directory -Force -Path $releaseDir | Out-Null

    # Copy files
    Copy-Item "dist\PDF2PNG_Converter.exe" "$releaseDir\PDF2PNG_Converter.exe"

    $docs = @("README.md", "PDF2PNG_仕様書.md")
    foreach ($doc in $docs) {
        if (Test-Path $doc) {
            Copy-Item $doc $releaseDir
        }
    }

    # Create release notes
    $releaseNotes = @"
# PDF2PNG/PDF2PPTX Converter v$Version

Built with UV package manager for optimal performance.

## Features
- High-performance PDF to PNG conversion
- PowerPoint (PPTX) generation with A3 landscape layout
- Configurable labels and styling
- Modern MVP architecture
- Asynchronous processing

## System Requirements
- Windows 10/11 (64-bit)
- 4GB RAM recommended
- 500MB disk space

Build Date: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Build Tool: UV + PyInstaller
"@

    $releaseNotes | Out-File -FilePath "$releaseDir\RELEASE_NOTES.txt" -Encoding UTF8

    # Create ZIP
    if (Test-Path $zipPath) {
        Remove-Item -Force $zipPath
    }

    Compress-Archive -Path "$releaseDir\*" -DestinationPath $zipPath -CompressionLevel Optimal

    $zipSize = (Get-Item $zipPath).Length / 1MB
    Write-ColorOutput "✅ Release package created: $zipPath ($([math]::Round($zipSize, 1)) MB)" "Success"
}

function Show-BuildSummary {
    $totalTime = $StopWatch.Elapsed

    Write-Header "Build Summary"

    Write-ColorOutput "🎉 Build completed successfully!" "Success"
    Write-ColorOutput "" "Info"
    Write-ColorOutput "📊 Build Statistics:" "Info"
    Write-ColorOutput "   Total time: $([math]::Round($totalTime.TotalMinutes, 1)) minutes" "Info"
    Write-ColorOutput "   Version: $Version" "Info"
    Write-ColorOutput "   Built with: UV package manager" "Info"

    # Performance comparison
    Write-ColorOutput "" "Info"
    Write-ColorOutput "🚀 UV Performance Benefits:" "Success"
    Write-ColorOutput "   ⚡ 10-100x faster dependency resolution" "Success"
    Write-ColorOutput "   📦 Efficient caching and parallel downloads" "Success"
    Write-ColorOutput "   🔧 Reliable virtual environment management" "Success"

    $exePath = "dist\PDF2PNG_Converter.exe"
    if (Test-Path $exePath) {
        $fileSize = (Get-Item $exePath).Length / 1MB
        Write-ColorOutput "   📁 Executable size: $([math]::Round($fileSize, 1)) MB" "Info"
    }

    Write-ColorOutput "" "Info"
    Write-ColorOutput "📁 Output files:" "Info"
    Write-ColorOutput "   Executable: dist\PDF2PNG_Converter.exe" "Success"
    Write-ColorOutput "   Release package: $OutputDir\PDF2PNG_Windows_v$Version.zip" "Success"
}

# Main execution
try {
    Write-Header "PDF2PNG/PDF2PPTX v$Version Build (UV-powered)"

    if (-not (Test-UvInstallation)) {
        exit 1
    }

    Setup-UvEnvironment
    Test-Dependencies
    Run-Tests
    Clean-BuildArtifacts
    Build-Application
    Validate-Build
    Create-ReleasePackage

    Show-BuildSummary

    Write-ColorOutput "" "Success"
    Write-ColorOutput "🎉 UV-powered build completed successfully!" "Success"
    Write-ColorOutput "⚡ Enjoy the performance benefits of UV!" "Success"

}
catch {
    Write-ColorOutput "" "Error"
    Write-ColorOutput "❌ Build failed: $($_.Exception.Message)" "Error"

    if ($Verbose) {
        Write-ColorOutput "" "Error"
        Write-ColorOutput "Detailed error:" "Error"
        Write-ColorOutput $_.ScriptStackTrace "Error"
    }

    exit 1
}
finally {
    $StopWatch.Stop()
}
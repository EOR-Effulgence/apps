# PDF2PNG/PDF2PPTX v3.0 Build Validation Script
# Comprehensive validation of the built Windows executable

param(
    [string]$ExecutablePath = "dist\PDF2PNG_Converter.exe",
    [switch]$Quick = $false,
    [switch]$Benchmark = $false,
    [switch]$Verbose = $false,
    [string]$OutputReport = "validation_report.md"
)

$ErrorActionPreference = "Stop"
$ValidationStartTime = Get-Date

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error = "Red"
    Info = "Cyan"
    Header = "Magenta"
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

function Test-ExecutableExists {
    Write-Header "実行ファイル存在確認"

    if (-not (Test-Path $ExecutablePath)) {
        Write-ColorOutput "❌ 実行ファイルが見つかりません: $ExecutablePath" "Error"
        return $false
    }

    $fileInfo = Get-Item $ExecutablePath
    $fileSizeMB = [math]::Round($fileInfo.Length / 1MB, 1)

    Write-ColorOutput "✅ 実行ファイルが見つかりました" "Success"
    Write-ColorOutput "   パス: $ExecutablePath" "Info"
    Write-ColorOutput "   サイズ: $fileSizeMB MB" "Info"
    Write-ColorOutput "   作成日時: $($fileInfo.CreationTime)" "Info"

    # File size validation
    if ($fileSizeMB -lt 10) {
        Write-ColorOutput "⚠️  ファイルサイズが小さすぎます ($fileSizeMB MB)" "Warning"
    } elseif ($fileSizeMB -gt 200) {
        Write-ColorOutput "⚠️  ファイルサイズが大きすぎます ($fileSizeMB MB)" "Warning"
    }

    return $true
}

function Test-BasicFunctionality {
    Write-Header "基本機能テスト"

    $tests = @(
        @{ Name = "バージョン表示"; Args = @("--version"); ExpectedExitCode = 0 },
        @{ Name = "ヘルプ表示"; Args = @("--help"); ExpectedExitCode = 0 },
        @{ Name = "テストモード"; Args = @("--test-mode"); ExpectedExitCode = 0 }
    )

    $results = @{}

    foreach ($test in $tests) {
        Write-ColorOutput "🧪 実行中: $($test.Name)..." "Info"

        try {
            $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
            $process = Start-Process -FilePath $ExecutablePath -ArgumentList $test.Args -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput "test_output.log" -RedirectStandardError "test_error.log"
            $stopwatch.Stop()

            $duration = $stopwatch.ElapsedMilliseconds
            $exitCode = $process.ExitCode

            if ($exitCode -eq $test.ExpectedExitCode) {
                Write-ColorOutput "   ✅ 成功 (所要時間: $duration ms)" "Success"
                $results[$test.Name] = @{ Status = "Success"; Duration = $duration; ExitCode = $exitCode }
            } else {
                Write-ColorOutput "   ❌ 失敗 (終了コード: $exitCode, 期待値: $($test.ExpectedExitCode))" "Error"
                $results[$test.Name] = @{ Status = "Failed"; Duration = $duration; ExitCode = $exitCode }

                if (Test-Path "test_error.log") {
                    $errorContent = Get-Content "test_error.log" -Raw
                    if ($errorContent.Trim()) {
                        Write-ColorOutput "   エラー出力: $errorContent" "Error"
                    }
                }
            }
        }
        catch {
            Write-ColorOutput "   ❌ 例外が発生しました: $($_.Exception.Message)" "Error"
            $results[$test.Name] = @{ Status = "Exception"; Duration = 0; ExitCode = -1; Error = $_.Exception.Message }
        }
        finally {
            # Clean up log files
            Remove-Item -Path "test_output.log", "test_error.log" -ErrorAction SilentlyContinue
        }
    }

    return $results
}

function Test-PerformanceMetrics {
    if ($Quick) {
        Write-ColorOutput "⏭️  クイックモードのため、パフォーマンステストをスキップします" "Warning"
        return @{}
    }

    Write-Header "パフォーマンステスト"

    $performanceResults = @{}

    # Startup time test
    Write-ColorOutput "🏃 起動時間テスト実行中..." "Info"

    $startupTimes = @()
    for ($i = 1; $i -le 3; $i++) {
        Write-ColorOutput "   試行 $i/3..." "Info"

        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $process = Start-Process -FilePath $ExecutablePath -ArgumentList @("--test-mode") -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput "startup_test.log" -RedirectStandardError "startup_error.log"
        $stopwatch.Stop()

        if ($process.ExitCode -eq 0) {
            $startupTimes += $stopwatch.ElapsedMilliseconds
        } else {
            Write-ColorOutput "   ⚠️  試行 $i が失敗しました (終了コード: $($process.ExitCode))" "Warning"
        }

        # Clean up
        Remove-Item -Path "startup_test.log", "startup_error.log" -ErrorAction SilentlyContinue
    }

    if ($startupTimes.Count -gt 0) {
        $avgStartupTime = ($startupTimes | Measure-Object -Average).Average
        $minStartupTime = ($startupTimes | Measure-Object -Minimum).Minimum
        $maxStartupTime = ($startupTimes | Measure-Object -Maximum).Maximum

        Write-ColorOutput "   ✅ 起動時間 - 平均: $([math]::Round($avgStartupTime)) ms, 最小: $minStartupTime ms, 最大: $maxStartupTime ms" "Success"

        $performanceResults["StartupTime"] = @{
            Average = $avgStartupTime
            Min = $minStartupTime
            Max = $maxStartupTime
            Samples = $startupTimes.Count
        }

        # Performance evaluation
        if ($avgStartupTime -gt 10000) {  # More than 10 seconds
            Write-ColorOutput "   ⚠️  起動時間が遅すぎます" "Warning"
        } elseif ($avgStartupTime -lt 3000) {  # Less than 3 seconds
            Write-ColorOutput "   🚀 優秀な起動時間です" "Success"
        }
    } else {
        Write-ColorOutput "   ❌ 起動時間テストが失敗しました" "Error"
    }

    # Memory usage test (using Task Manager data)
    Write-ColorOutput "🧠 メモリ使用量テスト実行中..." "Info"

    try {
        $process = Start-Process -FilePath $ExecutablePath -ArgumentList @("--test-mode") -PassThru -WindowStyle Hidden
        Start-Sleep -Seconds 2  # Let the process initialize

        if (-not $process.HasExited) {
            $processInfo = Get-Process -Id $process.Id -ErrorAction SilentlyContinue
            if ($processInfo) {
                $memoryMB = [math]::Round($processInfo.WorkingSet / 1MB, 1)
                Write-ColorOutput "   ✅ メモリ使用量: $memoryMB MB" "Success"

                $performanceResults["MemoryUsage"] = @{
                    WorkingSetMB = $memoryMB
                }

                if ($memoryMB -gt 500) {
                    Write-ColorOutput "   ⚠️  メモリ使用量が多すぎます" "Warning"
                } elseif ($memoryMB -lt 100) {
                    Write-ColorOutput "   🎯 効率的なメモリ使用量です" "Success"
                }
            }
        }

        # Clean up process
        if (-not $process.HasExited) {
            $process.Kill()
        }
        $process.WaitForExit(5000)
    }
    catch {
        Write-ColorOutput "   ⚠️  メモリ使用量テストでエラーが発生しました: $($_.Exception.Message)" "Warning"
    }

    return $performanceResults
}

function Test-DependencyAnalysis {
    Write-Header "依存関係分析"

    # Check for common DLL dependencies
    try {
        # Use PowerShell to check file dependencies (basic check)
        Write-ColorOutput "🔍 実行ファイルの基本分析中..." "Info"

        $fileInfo = Get-Item $ExecutablePath
        $hasVersionInfo = $fileInfo.VersionInfo.FileVersion -ne $null

        if ($hasVersionInfo) {
            Write-ColorOutput "   ✅ バージョン情報: $($fileInfo.VersionInfo.FileVersion)" "Success"
            Write-ColorOutput "   ✅ 製品名: $($fileInfo.VersionInfo.ProductName)" "Success"
            Write-ColorOutput "   ✅ 説明: $($fileInfo.VersionInfo.FileDescription)" "Success"
        } else {
            Write-ColorOutput "   ⚠️  バージョン情報が見つかりません" "Warning"
        }

        # Check digital signature (if available)
        $signature = Get-AuthenticodeSignature $ExecutablePath
        if ($signature.Status -eq "Valid") {
            Write-ColorOutput "   ✅ デジタル署名: 有効" "Success"
        } elseif ($signature.Status -eq "NotSigned") {
            Write-ColorOutput "   ⚠️  デジタル署名: なし" "Warning"
        } else {
            Write-ColorOutput "   ⚠️  デジタル署名: $($signature.Status)" "Warning"
        }
    }
    catch {
        Write-ColorOutput "   ⚠️  依存関係分析でエラーが発生しました: $($_.Exception.Message)" "Warning"
    }
}

function Test-SecurityScan {
    Write-Header "セキュリティスキャン"

    # Basic security checks
    Write-ColorOutput "🔒 基本的なセキュリティチェック実行中..." "Info"

    $securityResults = @{}

    # File size reasonableness
    $fileSizeMB = [math]::Round((Get-Item $ExecutablePath).Length / 1MB, 1)
    if ($fileSizeMB -gt 500) {
        Write-ColorOutput "   ⚠️  ファイルサイズが異常に大きいです ($fileSizeMB MB)" "Warning"
        $securityResults["FileSizeWarning"] = $fileSizeMB
    } else {
        Write-ColorOutput "   ✅ ファイルサイズは適正です ($fileSizeMB MB)" "Success"
    }

    # Check for suspicious strings (basic analysis)
    Write-ColorOutput "   🔍 実行ファイルの内容チェック中..." "Info"

    try {
        # This is a very basic check - in a real scenario you'd use proper tools
        $fileContent = [System.IO.File]::ReadAllText($ExecutablePath, [System.Text.Encoding]::ASCII)

        $suspiciousPatterns = @("password", "admin", "secret", "hack")
        $foundSuspicious = $false

        foreach ($pattern in $suspiciousPatterns) {
            if ($fileContent -like "*$pattern*") {
                Write-ColorOutput "   ⚠️  疑わしい文字列が見つかりました: $pattern" "Warning"
                $foundSuspicious = $true
            }
        }

        if (-not $foundSuspicious) {
            Write-ColorOutput "   ✅ 明らかに疑わしい文字列は見つかりませんでした" "Success"
        }
    }
    catch {
        Write-ColorOutput "   ⚠️  ファイル内容チェックでエラーが発生しました" "Warning"
    }

    return $securityResults
}

function Run-BenchmarkTests {
    if (-not $Benchmark) {
        return @{}
    }

    Write-Header "ベンチマークテスト"

    Write-ColorOutput "📊 詳細なベンチマークテスト実行中..." "Info"

    $benchmarkResults = @{}

    # Multiple startup time measurements
    Write-ColorOutput "   🏃 詳細起動時間ベンチマーク (10回実行)..." "Info"

    $startupTimes = @()
    for ($i = 1; $i -le 10; $i++) {
        Write-Progress -Activity "起動時間ベンチマーク" -Status "試行 $i/10" -PercentComplete ($i * 10)

        $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
        $process = Start-Process -FilePath $ExecutablePath -ArgumentList @("--test-mode") -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput "benchmark_$i.log" -RedirectStandardError "benchmark_err_$i.log"
        $stopwatch.Stop()

        if ($process.ExitCode -eq 0) {
            $startupTimes += $stopwatch.ElapsedMilliseconds
        }

        # Clean up
        Remove-Item -Path "benchmark_$i.log", "benchmark_err_$i.log" -ErrorAction SilentlyContinue
    }

    Write-Progress -Activity "起動時間ベンチマーク" -Completed

    if ($startupTimes.Count -gt 0) {
        $stats = $startupTimes | Measure-Object -Average -Minimum -Maximum -StandardDeviation

        $benchmarkResults["DetailedStartupTimes"] = @{
            Average = $stats.Average
            Minimum = $stats.Minimum
            Maximum = $stats.Maximum
            StandardDeviation = $stats.StandardDeviation
            SampleCount = $stats.Count
        }

        Write-ColorOutput "   📈 起動時間統計:" "Info"
        Write-ColorOutput "      平均: $([math]::Round($stats.Average)) ms" "Info"
        Write-ColorOutput "      最小: $($stats.Minimum) ms" "Info"
        Write-ColorOutput "      最大: $($stats.Maximum) ms" "Info"
        Write-ColorOutput "      標準偏差: $([math]::Round($stats.StandardDeviation, 1)) ms" "Info"
    }

    return $benchmarkResults
}

function Generate-ValidationReport {
    param(
        [hashtable]$BasicTests,
        [hashtable]$PerformanceResults,
        [hashtable]$SecurityResults,
        [hashtable]$BenchmarkResults
    )

    Write-Header "検証レポート生成"

    $reportContent = @"
# PDF2PNG/PDF2PPTX v3.0 Build Validation Report

**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Executable:** $ExecutablePath
**Total Validation Time:** $([math]::Round(($(Get-Date) - $ValidationStartTime).TotalMinutes, 1)) minutes

## Executive Summary

"@

    # Calculate overall status
    $overallStatus = "PASS"
    $failedTests = 0
    $totalTests = 0

    # Basic functionality summary
    $reportContent += "`n### Basic Functionality Tests`n`n"
    foreach ($test in $BasicTests.Keys) {
        $totalTests++
        $result = $BasicTests[$test]
        if ($result.Status -eq "Success") {
            $reportContent += "- ✅ **$test**: PASS ($($result.Duration) ms)`n"
        } else {
            $reportContent += "- ❌ **$test**: FAIL (Exit code: $($result.ExitCode))`n"
            $failedTests++
            $overallStatus = "FAIL"
        }
    }

    # Performance summary
    if ($PerformanceResults.Count -gt 0) {
        $reportContent += "`n### Performance Metrics`n`n"

        if ($PerformanceResults.ContainsKey("StartupTime")) {
            $startup = $PerformanceResults["StartupTime"]
            $avgTime = [math]::Round($startup.Average)
            $status = if ($avgTime -lt 5000) { "🚀 EXCELLENT" } elseif ($avgTime -lt 10000) { "✅ GOOD" } else { "⚠️ SLOW" }
            $reportContent += "- **Startup Time**: $status (Average: $avgTime ms)`n"
        }

        if ($PerformanceResults.ContainsKey("MemoryUsage")) {
            $memory = $PerformanceResults["MemoryUsage"]
            $memMB = $memory.WorkingSetMB
            $status = if ($memMB -lt 100) { "🎯 EXCELLENT" } elseif ($memMB -lt 200) { "✅ GOOD" } else { "⚠️ HIGH" }
            $reportContent += "- **Memory Usage**: $status ($memMB MB)`n"
        }
    }

    # Overall status
    $reportContent += "`n## Overall Assessment`n`n"
    $successRate = [math]::Round((($totalTests - $failedTests) / $totalTests) * 100, 1)

    if ($overallStatus -eq "PASS") {
        $reportContent += "🎉 **BUILD VALIDATION: PASSED** ($successRate% success rate)`n`n"
        $reportContent += "The executable has successfully passed all validation tests and is ready for distribution.`n"
    } else {
        $reportContent += "❌ **BUILD VALIDATION: FAILED** ($successRate% success rate)`n`n"
        $reportContent += "The executable has failed one or more validation tests. Please review the issues before distribution.`n"
    }

    # Detailed results
    $reportContent += "`n## Detailed Test Results`n`n"

    # Add detailed test information
    foreach ($testName in $BasicTests.Keys) {
        $test = $BasicTests[$testName]
        $reportContent += "### $testName`n`n"
        $reportContent += "- **Status**: $($test.Status)`n"
        $reportContent += "- **Duration**: $($test.Duration) ms`n"
        $reportContent += "- **Exit Code**: $($test.ExitCode)`n"

        if ($test.ContainsKey("Error")) {
            $reportContent += "- **Error**: $($test.Error)`n"
        }

        $reportContent += "`n"
    }

    # Benchmark results
    if ($BenchmarkResults.Count -gt 0 -and $BenchmarkResults.ContainsKey("DetailedStartupTimes")) {
        $reportContent += "### Detailed Benchmark Results`n`n"
        $benchmark = $BenchmarkResults["DetailedStartupTimes"]
        $reportContent += "**Startup Time Analysis (10 samples):**`n"
        $reportContent += "- Average: $([math]::Round($benchmark.Average)) ms`n"
        $reportContent += "- Minimum: $($benchmark.Minimum) ms`n"
        $reportContent += "- Maximum: $($benchmark.Maximum) ms`n"
        $reportContent += "- Standard Deviation: $([math]::Round($benchmark.StandardDeviation, 1)) ms`n"
        $reportContent += "`n"
    }

    # Recommendations
    $reportContent += "## Recommendations`n`n"

    if ($PerformanceResults.ContainsKey("StartupTime")) {
        $avgTime = $PerformanceResults["StartupTime"].Average
        if ($avgTime -gt 8000) {
            $reportContent += "- Consider optimizing startup time (currently $([math]::Round($avgTime)) ms)`n"
        }
    }

    if ($PerformanceResults.ContainsKey("MemoryUsage")) {
        $memMB = $PerformanceResults["MemoryUsage"].WorkingSetMB
        if ($memMB -gt 300) {
            $reportContent += "- Consider optimizing memory usage (currently $memMB MB)`n"
        }
    }

    $reportContent += "- Regular validation testing is recommended for future builds`n"
    $reportContent += "- Consider implementing automated validation in CI/CD pipeline`n"

    # Save report
    try {
        $reportContent | Out-File -FilePath $OutputReport -Encoding UTF8
        Write-ColorOutput "✅ 検証レポートが生成されました: $OutputReport" "Success"
    }
    catch {
        Write-ColorOutput "⚠️  レポート生成でエラーが発生しました: $($_.Exception.Message)" "Warning"
    }

    return $overallStatus
}

# Main execution
try {
    Write-Header "PDF2PNG/PDF2PPTX v3.0 Build Validation"

    # Initialize results
    $validationResults = @{
        BasicTests = @{}
        PerformanceResults = @{}
        SecurityResults = @{}
        BenchmarkResults = @{}
    }

    # Run validation tests
    if (-not (Test-ExecutableExists)) {
        exit 1
    }

    $validationResults.BasicTests = Test-BasicFunctionality
    $validationResults.PerformanceResults = Test-PerformanceMetrics
    Test-DependencyAnalysis
    $validationResults.SecurityResults = Test-SecurityScan
    $validationResults.BenchmarkResults = Run-BenchmarkTests

    # Generate report
    $overallStatus = Generate-ValidationReport @validationResults

    # Final summary
    Write-Header "検証完了"

    $endTime = Get-Date
    $totalDuration = $endTime - $ValidationStartTime

    Write-ColorOutput "⏱️  総所要時間: $([math]::Round($totalDuration.TotalMinutes, 1)) 分" "Info"

    if ($overallStatus -eq "PASS") {
        Write-ColorOutput "🎉 すべての検証テストが成功しました！" "Success"
        Write-ColorOutput "   実行ファイルは配布準備完了です。" "Success"
        exit 0
    } else {
        Write-ColorOutput "❌ 一部の検証テストが失敗しました。" "Error"
        Write-ColorOutput "   詳細は検証レポートを確認してください: $OutputReport" "Error"
        exit 1
    }
}
catch {
    Write-ColorOutput "❌ 検証プロセスでエラーが発生しました: $($_.Exception.Message)" "Error"
    if ($Verbose) {
        Write-ColorOutput $_.ScriptStackTrace "Error"
    }
    exit 1
}
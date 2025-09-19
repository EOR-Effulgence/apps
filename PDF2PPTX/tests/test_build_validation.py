"""
Build validation tests for PDF2PNG/PDF2PPTX Converter v3.0

These tests validate that the built executable works correctly
and meets performance requirements.
"""

import pytest
import subprocess
import tempfile
import time
import os
import psutil
from pathlib import Path
from typing import Optional


class TestBuildValidation:
    """Test suite for validating the built executable."""

    @pytest.fixture(scope="class")
    def executable_path(self) -> Optional[Path]:
        """Get path to the built executable."""
        possible_paths = [
            Path("dist/PDF2PNG_Converter.exe"),
            Path("dist/PDF2PNG_Converter.exe"),
            Path("dist/PDF2PPTX_Converter.exe"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        pytest.skip("No executable found for testing")

    def test_executable_exists(self, executable_path: Path):
        """Test that the executable file exists and is accessible."""
        assert executable_path.exists(), f"Executable not found at {executable_path}"
        assert executable_path.is_file(), f"Path is not a file: {executable_path}"

        # Check file size (should be reasonable but not too large)
        file_size_mb = executable_path.stat().st_size / (1024 * 1024)
        assert 10 <= file_size_mb <= 200, f"Executable size is unusual: {file_size_mb:.1f}MB"

    def test_executable_permissions(self, executable_path: Path):
        """Test that the executable has proper permissions."""
        if os.name == 'nt':  # Windows
            # On Windows, check if file is executable
            assert executable_path.suffix.lower() == '.exe'
        else:  # Unix-like
            # Check execute permissions
            assert os.access(executable_path, os.X_OK)

    def test_version_command(self, executable_path: Path):
        """Test that the executable responds to --version command."""
        try:
            result = subprocess.run(
                [str(executable_path), "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Should exit successfully
            assert result.returncode == 0, f"Version command failed: {result.stderr}"

            # Should contain version information
            output = result.stdout.strip()
            assert "PDF2PNG" in output or "PDF2PPTX" in output
            assert "3.0" in output  # Version 3.0.x

        except subprocess.TimeoutExpired:
            pytest.fail("Version command timed out")
        except FileNotFoundError:
            pytest.fail(f"Could not execute {executable_path}")

    def test_help_command(self, executable_path: Path):
        """Test that the executable responds to --help command."""
        try:
            result = subprocess.run(
                [str(executable_path), "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Should exit successfully
            assert result.returncode == 0, f"Help command failed: {result.stderr}"

            # Should contain usage information
            output = result.stdout.strip()
            assert "usage:" in output.lower() or "convert" in output.lower()

        except subprocess.TimeoutExpired:
            pytest.fail("Help command timed out")

    def test_test_mode(self, executable_path: Path):
        """Test that the executable runs successfully in test mode."""
        try:
            result = subprocess.run(
                [str(executable_path), "--test-mode"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Should exit successfully
            assert result.returncode == 0, f"Test mode failed: {result.stderr}"

            # Should contain success indicators
            output = result.stdout.strip()
            assert "✅" in output or "passed" in output.lower()
            assert "All tests passed" in output or "Build validation completed" in output

        except subprocess.TimeoutExpired:
            pytest.fail("Test mode timed out")

    def test_startup_time(self, executable_path: Path):
        """Test that the executable starts up within reasonable time."""
        start_time = time.time()

        try:
            # Start process and immediately terminate
            process = subprocess.Popen(
                [str(executable_path), "--test-mode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for process to complete or timeout
            try:
                stdout, stderr = process.communicate(timeout=15)
                end_time = time.time()

                startup_time = end_time - start_time

                # Should start within 15 seconds (generous for cold start)
                assert startup_time < 15, f"Startup time too slow: {startup_time:.1f}s"

                # Log the actual startup time for monitoring
                print(f"Startup time: {startup_time:.2f} seconds")

            except subprocess.TimeoutExpired:
                process.terminate()
                pytest.fail("Application startup timed out")

        except Exception as e:
            pytest.fail(f"Could not test startup time: {e}")

    def test_memory_usage(self, executable_path: Path):
        """Test that the executable has reasonable memory usage."""
        try:
            # Start the process in test mode
            process = subprocess.Popen(
                [str(executable_path), "--test-mode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            try:
                # Get process info
                proc = psutil.Process(process.pid)

                # Wait a moment for the process to initialize
                time.sleep(2)

                # Check memory usage
                memory_info = proc.memory_info()
                memory_mb = memory_info.rss / (1024 * 1024)

                # Should use reasonable amount of memory (less than 500MB for test mode)
                assert memory_mb < 500, f"Memory usage too high: {memory_mb:.1f}MB"

                print(f"Memory usage: {memory_mb:.1f}MB")

                # Wait for process to complete
                process.wait(timeout=30)

            except psutil.NoSuchProcess:
                # Process completed quickly, which is fine
                pass
            except subprocess.TimeoutExpired:
                process.terminate()
                pytest.fail("Memory test timed out")

        except Exception as e:
            pytest.fail(f"Could not test memory usage: {e}")

    def test_no_obvious_errors(self, executable_path: Path):
        """Test that the executable doesn't produce obvious errors."""
        try:
            result = subprocess.run(
                [str(executable_path), "--test-mode"],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Check stderr for common error patterns
            stderr = result.stderr.lower()

            error_patterns = [
                "traceback",
                "error:",
                "exception",
                "failed to",
                "could not",
                "import error",
                "module not found",
                "dll load failed"
            ]

            for pattern in error_patterns:
                assert pattern not in stderr, f"Found error pattern '{pattern}' in stderr: {result.stderr}"

        except subprocess.TimeoutExpired:
            pytest.fail("Error check timed out")

    @pytest.mark.slow
    def test_gui_startup(self, executable_path: Path):
        """Test that GUI starts up without immediate crashes (slow test)."""
        try:
            # Start GUI process
            process = subprocess.Popen(
                [str(executable_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for GUI to initialize
            time.sleep(5)

            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                pytest.fail(f"GUI process exited unexpectedly: {stderr.decode()}")

            # Terminate the GUI process
            process.terminate()

            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't shut down gracefully
                process.kill()

            print("GUI startup test completed successfully")

        except Exception as e:
            pytest.fail(f"GUI startup test failed: {e}")

    def test_file_dependencies(self, executable_path: Path):
        """Test that the executable doesn't require external files that aren't bundled."""
        # This test runs the executable from a temporary directory
        # to ensure it doesn't depend on files in the original location

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            temp_exe = temp_path / executable_path.name

            # Copy executable to temporary location
            import shutil
            shutil.copy2(executable_path, temp_exe)

            try:
                # Run from the temporary location
                result = subprocess.run(
                    [str(temp_exe), "--test-mode"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=temp_dir
                )

                assert result.returncode == 0, f"Executable failed when run from different location: {result.stderr}"

            except subprocess.TimeoutExpired:
                pytest.fail("Dependency test timed out")


class TestPerformanceBenchmarks:
    """Performance benchmark tests for the executable."""

    @pytest.fixture(scope="class")
    def executable_path(self) -> Optional[Path]:
        """Get path to the built executable."""
        possible_paths = [
            Path("dist/PDF2PNG_Converter.exe"),
            Path("dist/PDF2PNG_Converter.exe"),
            Path("dist/PDF2PPTX_Converter.exe"),
        ]

        for path in possible_paths:
            if path.exists():
                return path

        pytest.skip("No executable found for benchmarking")

    @pytest.mark.benchmark
    def test_startup_benchmark(self, executable_path: Path, benchmark):
        """Benchmark the startup time of the executable."""
        def run_startup():
            result = subprocess.run(
                [str(executable_path), "--test-mode"],
                capture_output=True,
                timeout=30
            )
            assert result.returncode == 0
            return result

        # Run benchmark
        result = benchmark(run_startup)

        # Validate result
        assert result.returncode == 0

    @pytest.mark.benchmark
    def test_memory_benchmark(self, executable_path: Path):
        """Benchmark memory usage of the executable."""
        memory_readings = []

        try:
            process = subprocess.Popen(
                [str(executable_path), "--test-mode"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            proc = psutil.Process(process.pid)

            # Take memory readings every 0.5 seconds
            for _ in range(10):
                try:
                    memory_mb = proc.memory_info().rss / (1024 * 1024)
                    memory_readings.append(memory_mb)
                    time.sleep(0.5)
                except psutil.NoSuchProcess:
                    break

            process.wait(timeout=30)

            # Analyze memory usage
            if memory_readings:
                max_memory = max(memory_readings)
                avg_memory = sum(memory_readings) / len(memory_readings)

                print(f"Max memory: {max_memory:.1f}MB")
                print(f"Avg memory: {avg_memory:.1f}MB")

                # Performance assertions
                assert max_memory < 300, f"Peak memory usage too high: {max_memory:.1f}MB"
                assert avg_memory < 200, f"Average memory usage too high: {avg_memory:.1f}MB"

        except Exception as e:
            pytest.fail(f"Memory benchmark failed: {e}")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
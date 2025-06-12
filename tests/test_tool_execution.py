"""Tests for development tools execution."""

import subprocess

import pytest


class TestToolExecution:
    """Test that development tools can be executed successfully."""

    def test_ruff_formatter_execution(self):
        """Test that Ruff formatter can be executed successfully."""
        # Simply check that ruff format --help runs successfully
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--help"],
            capture_output=True,
            text=True,
        )

        # Verify ruff formatter executed successfully
        assert result.returncode == 0, "Ruff formatter should run successfully"
        assert "format" in result.stdout.lower(), (
            "Output should contain format command info"
        )

    def test_ruff_linter_execution(self):
        """Test that Ruff linter can be executed successfully."""
        # Simply check that ruff check --help runs successfully
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "--help"],
            capture_output=True,
            text=True,
        )

        # Verify ruff linter executed successfully
        assert result.returncode == 0, "Ruff linter should run successfully"
        assert "check" in result.stdout.lower(), (
            "Output should contain check command info"
        )

    @pytest.mark.skip(reason="This test is not ready yet")
    def test_mypy_type_checker_execution(self):
        """Test that MyPy type checker can be executed successfully."""
        # Simply check that mypy --version runs successfully
        result = subprocess.run(
            ["uv", "run", "mypy", "--version"],
            capture_output=True,
            text=True,
        )

        # Verify mypy executed successfully
        assert result.returncode == 0, "MyPy should run successfully"
        assert "mypy" in result.stdout.lower(), (
            "Output should contain mypy version info"
        )

    def test_pytest_execution(self):
        """Test that pytest can be executed successfully."""
        # Simply check that pytest --version runs successfully
        result = subprocess.run(
            ["uv", "run", "pytest", "--version"],
            capture_output=True,
            text=True,
        )

        # Verify pytest executed successfully
        assert result.returncode == 0, "Pytest should run successfully"
        assert "pytest" in result.stdout, "Output should contain pytest version info"

    def test_coverage_analysis_execution(self):
        """Test that coverage can be executed successfully."""
        # Simply check that coverage --version runs successfully
        result = subprocess.run(
            ["uv", "run", "coverage", "--version"],
            capture_output=True,
            text=True,
        )

        # Verify coverage executed successfully
        assert result.returncode == 0, "Coverage should run successfully"
        assert "Coverage.py" in result.stdout, (
            "Output should contain Coverage.py version info"
        )

    def test_tool_error_handling(self):
        """Test basic error handling for development tools."""
        # Test command with invalid argument
        result = subprocess.run(
            ["uv", "run", "pytest", "--invalid-argument"],
            capture_output=True,
            text=True,
        )
        # Verify the command fails with invalid argument
        assert result.returncode != 0, "Command should fail with invalid argument"
        assert "error" in result.stderr.lower() or "usage" in result.stderr.lower(), (
            "Error output should contain error message or usage information"
        )

    def test_tools_available(self):
        """Test that all required development tools are available in the environment."""
        tools = ["ruff", "mypy", "pytest", "coverage"]

        for tool in tools:
            result = subprocess.run(
                ["uv", "run", tool, "--version"], capture_output=True, text=True
            )
            assert result.returncode == 0, (
                f"{tool} should be available and respond to --version"
            )

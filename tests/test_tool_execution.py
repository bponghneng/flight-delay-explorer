"""Tests for development tools execution."""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestToolExecution:
    """Test that development tools can be executed successfully."""

    def test_black_formatter_execution(self):
        """Test running Black formatter on sample code."""
        # Create a temporary Python file with poorly formatted code
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
def badly_formatted_function(x,y,z):
    return x+y+z


class   BadlyFormattedClass:
    def __init__(self,value):
        self.value=value
    def get_value(self):return self.value
"""
            )
            tmp_file.flush()
            tmp_path = Path(tmp_file.name)

        try:
            # Run black on the file
            result = subprocess.run(
                ["uv", "run", "black", "--check", "--diff", str(tmp_path)],
                capture_output=True,
                text=True,
            )

            # Black should find formatting issues (exit code 1)
            assert result.returncode == 1, "Black should find formatting issues"
            assert "would reformat" in result.stderr or "reformatted" in result.stderr

            # Now actually format the file
            format_result = subprocess.run(
                ["uv", "run", "black", str(tmp_path)], capture_output=True, text=True
            )

            # Black should successfully format the file
            assert (
                format_result.returncode == 0
            ), "Black should successfully format the file"

        finally:
            # Clean up
            tmp_path.unlink()

    def test_ruff_linter_execution(self):
        """Test running Ruff linter on sample code."""
        # Create a temporary Python file with linting issues
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
import os
import sys
import unused_module

def function_with_issues():
    x = 1
    y = 2
    # Unused variable
    unused_var = 42
    print("Hello world")
"""
            )
            tmp_file.flush()
            tmp_path = Path(tmp_file.name)

        try:
            # Run ruff on the file
            result = subprocess.run(
                ["uv", "run", "ruff", "check", str(tmp_path)],
                capture_output=True,
                text=True,
            )

            # Ruff should find linting issues
            assert result.returncode == 1, "Ruff should find linting issues"
            assert tmp_path.name in result.stdout, "Output should mention the file"

        finally:
            # Clean up
            tmp_path.unlink()

    @pytest.mark.skip(reason="This test is not ready yet")
    def test_mypy_type_checker_execution(self):
        """Test running MyPy type checker on sample code."""
        # Create a temporary Python file with type issues
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as tmp_file:
            tmp_file.write(
                """
def add_numbers(x, y):
    return x + y

def main():
    result = add_numbers("hello", 42)
    print(result)
"""
            )
            tmp_file.flush()
            tmp_path = Path(tmp_file.name)

        try:
            # Run mypy on the file
            result = subprocess.run(
                ["uv", "run", "mypy", str(tmp_path)], capture_output=True, text=True
            )

            # MyPy should find type issues (functions without type annotations)
            assert result.returncode == 1, "MyPy should find type issues"

        finally:
            # Clean up
            tmp_path.unlink()

    def test_pytest_execution(self):
        """Test running pytest on existing test suite."""
        # Run pytest on a simple test
        result = subprocess.run(
            ["uv", "run", "pytest", "tests/test_dev_tools.py", "-v"],
            capture_output=True,
            text=True,
        )

        # Pytest should run successfully on our dev tools tests
        assert (
            result.returncode == 0
        ), f"Pytest should run successfully: {result.stdout}"
        assert "passed" in result.stdout, "Tests should pass"

    def test_coverage_analysis_execution(self):
        """Test running coverage analysis on tests."""
        # Run pytest with coverage but without failing on low coverage for this test
        result = subprocess.run(
            [
                "uv",
                "run",
                "pytest",
                "--cov=src/flight_delay_explorer",
                "--cov-fail-under=0",
                "tests/test_dev_tools.py",
            ],
            capture_output=True,
            text=True,
        )

        # Coverage should run successfully even with 0% coverage
        assert (
            result.returncode == 0
        ), f"Coverage should run successfully: {result.stdout}"
        assert (
            "coverage report" in result.stdout or "%" in result.stdout
        ), "Output should contain coverage information"

    def test_tool_error_handling(self):
        """Test error handling for each tool with invalid inputs."""
        # Test black with invalid file
        black_result = subprocess.run(
            ["uv", "run", "black", "nonexistent_file.py"],
            capture_output=True,
            text=True,
        )
        assert black_result.returncode != 0, "Black should fail on nonexistent file"

        # Test ruff with invalid file
        ruff_result = subprocess.run(
            ["uv", "run", "ruff", "check", "nonexistent_file.py"],
            capture_output=True,
            text=True,
        )
        assert ruff_result.returncode != 0, "Ruff should fail on nonexistent file"

        # Test mypy with invalid file
        mypy_result = subprocess.run(
            ["uv", "run", "mypy", "nonexistent_file.py"], capture_output=True, text=True
        )
        assert mypy_result.returncode != 0, "MyPy should fail on nonexistent file"

    def test_tools_available(self):
        """Test that all required development tools are available in the environment."""
        tools = ["black", "ruff", "mypy", "pytest"]

        for tool in tools:
            result = subprocess.run(
                ["uv", "run", tool, "--version"], capture_output=True, text=True
            )
            assert (
                result.returncode == 0
            ), f"{tool} should be available and respond to --version"

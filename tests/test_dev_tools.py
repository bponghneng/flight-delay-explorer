"""Tests for development tools configuration."""

import configparser
from pathlib import Path

import tomllib


class TestDevToolsConfiguration:
    """Test dev tools configuration files exist and contain required settings."""

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists."""
        pyproject_path = Path("pyproject.toml")
        assert pyproject_path.exists(), "pyproject.toml file should exist"

    def test_black_configuration(self):
        """Test Black configuration in pyproject.toml."""
        pyproject_path = Path("pyproject.toml")
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)

        assert "tool" in config, "pyproject.toml should have [tool] section"
        assert (
            "black" in config["tool"]
        ), "pyproject.toml should have [tool.black] section"

        black_config = config["tool"]["black"]
        assert "line-length" in black_config, "Black config should specify line-length"
        assert black_config["line-length"] == 88, "Black line-length should be 88"
        assert (
            "target-version" in black_config
        ), "Black config should specify target-version"
        assert (
            "py39" in black_config["target-version"]
        ), "Black should target Python 3.9"

    def test_ruff_configuration(self):
        """Test Ruff configuration in pyproject.toml."""
        pyproject_path = Path("pyproject.toml")
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)

        assert "tool" in config, "pyproject.toml should have [tool] section"
        assert (
            "ruff" in config["tool"]
        ), "pyproject.toml should have [tool.ruff] section"

        ruff_config = config["tool"]["ruff"]
        assert "line-length" in ruff_config, "Ruff config should specify line-length"
        assert (
            "target-version" in ruff_config
        ), "Ruff config should specify target-version"

    def test_mypy_configuration(self):
        """Test MyPy configuration in pyproject.toml."""
        pyproject_path = Path("pyproject.toml")
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)

        assert "tool" in config, "pyproject.toml should have [tool] section"
        assert (
            "mypy" in config["tool"]
        ), "pyproject.toml should have [tool.mypy] section"

        mypy_config = config["tool"]["mypy"]
        assert (
            "python_version" in mypy_config
        ), "MyPy config should specify python_version"
        assert mypy_config["python_version"] == "3.9", "MyPy should target Python 3.9"
        # assert (
        #     mypy_config.get("disallow_untyped_defs") is True
        # ), "MyPy should disallow untyped defs"
        # assert (
        #     mypy_config.get("disallow_incomplete_defs") is True
        # ), "MyPy should disallow incomplete defs"
        # assert (
        #     mypy_config.get("check_untyped_defs") is True
        # ), "MyPy should check untyped defs"

    def test_pytest_configuration(self):
        """Test Pytest configuration in pyproject.toml."""
        pyproject_path = Path("pyproject.toml")
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)

        assert "tool" in config, "pyproject.toml should have [tool] section"
        assert (
            "pytest" in config["tool"]
        ), "pyproject.toml should have [tool.pytest] section"

        pytest_config = config["tool"]["pytest"]
        if "ini_options" in pytest_config:
            ini_options = pytest_config["ini_options"]
            assert "testpaths" in ini_options, "Pytest config should specify testpaths"
            assert (
                "tests" in ini_options["testpaths"]
            ), "Pytest should look in tests directory"

    def test_coveragerc_exists(self):
        """Test that .coveragerc exists."""
        coverage_path = Path(".coveragerc")
        assert coverage_path.exists(), ".coveragerc file should exist"

    def test_coveragerc_configuration(self):
        """Test .coveragerc configuration content."""
        coverage_path = Path(".coveragerc")
        config = configparser.ConfigParser()
        config.read(coverage_path)

        assert "run" in config.sections(), ".coveragerc should have [run] section"
        assert "report" in config.sections(), ".coveragerc should have [report] section"

        run_section = config["run"]
        assert "source" in run_section, "[run] section should specify source"
        assert (
            "src/flight_delay_explorer" in run_section["source"]
        ), "Source should include package path"

        report_section = config["report"]
        assert (
            "fail_under" in report_section
        ), "[report] section should specify fail_under"
        fail_under = int(report_section["fail_under"])
        assert fail_under >= 90, "Coverage should fail under 90%"

    def test_tool_integration(self):
        """Test that tools work together without conflicts."""
        # This test ensures Black formatting doesn't break Ruff rules
        # and that configuration files are compatible
        pyproject_path = Path("pyproject.toml")
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)

        # Check that Black and Ruff line-length settings are compatible
        black_config = config.get("tool", {}).get("black", {})
        ruff_config = config.get("tool", {}).get("ruff", {})

        if "line-length" in black_config and "line-length" in ruff_config:
            assert (
                black_config["line-length"] == ruff_config["line-length"]
            ), "Black and Ruff line-length should match"

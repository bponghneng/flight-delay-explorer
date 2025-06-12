"""Tests for Git workflow validation and processes."""

import os
from pathlib import Path


class TestGitWorkflows:
    """Test Git workflow processes and validations."""

    def test_git_hooks_exist_and_executable(self):
        """Test that Git hooks exist and are executable."""
        # Define the hooks we want to verify
        required_hooks = ["pre-commit", "pre-push"]

        for hook_name in required_hooks:
            hook_path = Path(".githooks") / hook_name

            # Check if hook exists
            assert hook_path.exists(), f"{hook_name} hook should exist in .githooks dir"

            # Check if hook is executable
            assert os.access(hook_path, os.X_OK), (
                f"{hook_name} hook should be executable"
            )

    def test_git_workflow_documentation_exists(self):
        """Test that workflow documentation exists."""
        contributing_path = Path("CONTRIBUTING.md")

        # Check if CONTRIBUTING.md exists
        assert contributing_path.exists(), "CONTRIBUTING.md should exist"

        with contributing_path.open() as f:
            content = f.read().lower()

        # Verify that key workflow sections are documented
        required_workflow_sections = ["git workflow", "branch naming"]

        for section in required_workflow_sections:
            assert section in content, f"CONTRIBUTING.md should document '{section}'"

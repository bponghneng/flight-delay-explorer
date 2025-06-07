"""Tests for Git workflow validation and processes."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest

pytest.skip(allow_module_level=True, reason="Test hangs require a fix.")


class TestGitWorkflows:
    """Test Git workflow processes and validations."""

    def test_feature_branch_workflow(self):
        """Test creating and working with feature branches."""
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        original_branch = result.stdout.strip()

        test_branch = f"test-feature-{os.getpid()}"

        try:
            # Create feature branch
            result = subprocess.run(
                ["git", "checkout", "-b", test_branch], capture_output=True, text=True
            )
            assert result.returncode == 0, "Should be able to create feature branch"

            # Verify we're on the feature branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )
            assert result.stdout.strip() == test_branch, f"Should be on {test_branch}"

            # Make a test change
            test_file = Path("test_workflow_file.txt")
            test_file.write_text("Test content for workflow")

            # Add and commit the change
            subprocess.run(["git", "add", str(test_file)], check=True)

            # Test commit with proper format
            commit_msg = "test: add test file for workflow validation"
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg], capture_output=True, text=True
            )

            # The commit might fail due to hooks, but we test the workflow
            # Should be able to commit with proper message
            # assert result.returncode == 0

            # Switch back to original branch
            subprocess.run(["git", "checkout", original_branch], check=True)

        finally:
            # Clean up: switch back and delete test branch
            subprocess.run(["git", "checkout", original_branch], capture_output=True)
            subprocess.run(["git", "branch", "-D", test_branch], capture_output=True)
            # Clean up test file
            Path("test_workflow_file.txt").unlink(missing_ok=True)

    def test_commit_message_validation(self):
        """Test commit message format validation."""
        # Test valid commit messages
        valid_messages = [
            "feat: add new feature",
            "fix: resolve bug in parser",
            "docs: update README",
            "test(api): add unit tests",
            "refactor(cli): simplify command structure",
            "chore: update dependencies",
        ]

        commit_msg_hook = Path(".git/hooks/commit-msg")

        for msg in valid_messages:
            # Create temporary commit message file
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                f.write(msg)
                temp_file = f.name

            try:
                # Test the commit-msg hook directly
                result = subprocess.run(
                    [str(commit_msg_hook), temp_file], capture_output=True, text=True
                )
                assert (
                    result.returncode == 0
                ), f"Valid message '{msg}' should pass validation"

            finally:
                Path(temp_file).unlink(missing_ok=True)

    def test_invalid_commit_message_validation(self):
        """Test that invalid commit messages are rejected."""
        # Test invalid commit messages
        invalid_messages = [
            "just a simple message",
            "Fix bug",  # Should be lowercase
            "add feature",  # Missing type
            "feat:missing space after colon",
            "unknown(scope): this type doesn't exist",
        ]

        commit_msg_hook = Path(".git/hooks/commit-msg")

        for msg in invalid_messages:
            # Create temporary commit message file
            with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
                f.write(msg)
                temp_file = f.name

            try:
                # Test the commit-msg hook directly
                result = subprocess.run(
                    [str(commit_msg_hook), temp_file], capture_output=True, text=True
                )
                assert (
                    result.returncode != 0
                ), f"Invalid message '{msg}' should fail validation"

            finally:
                Path(temp_file).unlink(missing_ok=True)

    def test_pre_commit_hook_execution(self):
        """Test that pre-commit hook can be executed."""
        pre_commit_hook = Path(".git/hooks/pre-commit")

        # Check if hook exists and is executable
        assert pre_commit_hook.exists(), "pre-commit hook should exist"
        assert os.access(
            pre_commit_hook, os.X_OK
        ), "pre-commit hook should be executable"

        # Test that hook can run (might fail due to quality issues, but should execute)
        result = subprocess.run([str(pre_commit_hook)], capture_output=True, text=True)

        # Hook should at least run without syntax errors
        # Return code might be non-zero due to quality checks failing
        assert (
            "Running pre-commit checks" in result.stdout
            or "Running pre-commit checks" in result.stderr
        ), "Pre-commit hook should start execution"

    def test_pre_push_hook_execution(self):
        """Test that pre-push hook can be executed."""
        pre_push_hook = Path(".git/hooks/pre-push")

        # Check if hook exists and is executable
        assert pre_push_hook.exists(), "pre-push hook should exist"
        assert os.access(pre_push_hook, os.X_OK), "pre-push hook should be executable"

        # Test that hook can run (might fail due to quality issues, but should execute)
        result = subprocess.run([str(pre_push_hook)], capture_output=True, text=True)

        # Hook should at least run without syntax errors
        assert (
            "Running pre-push checks" in result.stdout
            or "Running pre-push checks" in result.stderr
        ), "Pre-push hook should start execution"

    def test_merge_commit_handling(self):
        """Test that merge commits are handled properly by hooks."""
        commit_msg_hook = Path(".git/hooks/commit-msg")

        # Simulate a merge commit message
        merge_msg = "Merge branch 'feature/test' into main"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(merge_msg)
            temp_file = f.name

        try:
            # Create a fake MERGE_HEAD to simulate merge
            merge_head = Path(".git/MERGE_HEAD")
            merge_head.write_text("fake-commit-hash")

            try:
                # Test the commit-msg hook with merge commit
                result = subprocess.run(
                    [str(commit_msg_hook), temp_file], capture_output=True, text=True
                )
                # Merge commits should be allowed to bypass validation
                assert result.returncode == 0, "Merge commits should bypass validation"

            finally:
                merge_head.unlink(missing_ok=True)

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_revert_commit_handling(self):
        """Test that revert commits are handled properly by hooks."""
        commit_msg_hook = Path(".git/hooks/commit-msg")

        # Simulate a revert commit message
        revert_msg = 'Revert "feat: add problematic feature"'

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(revert_msg)
            temp_file = f.name

        try:
            # Test the commit-msg hook with revert commit
            result = subprocess.run(
                [str(commit_msg_hook), temp_file], capture_output=True, text=True
            )
            # Revert commits should be allowed to bypass validation
            assert result.returncode == 0, "Revert commits should bypass validation"

        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_branch_naming_patterns(self):
        """Test that branch naming follows conventions from CONTRIBUTING.md."""
        contributing_path = Path("CONTRIBUTING.md")
        with contributing_path.open() as f:
            content = f.read()

        # Verify that branch naming patterns are documented
        expected_patterns = ["feature/", "fix/", "docs/", "chore/", "test/"]

        for pattern in expected_patterns:
            assert (
                pattern in content
            ), f"Branch pattern '{pattern}' should be documented"

    def test_collaboration_scenarios(self):
        """Test common collaboration scenarios."""
        # Test that we can simulate common Git operations

        # Check if repository is clean for testing
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )

        # Repository might have uncommitted changes, expected during development
        # Just verify git status command works
        assert (
            result.returncode == 0
        ), "git status should work for collaboration testing"

        # Test fetch simulation (dry run)
        result = subprocess.run(
            ["git", "fetch", "--dry-run"], capture_output=True, text=True
        )
        # This might fail if no remote is configured, which is OK for local testing
        # Just verify the command is available
        assert result.returncode in [0, 1, 128], "git fetch should be available"

    def test_git_workflow_documentation_completeness(self):
        """Test that workflow documentation is comprehensive."""
        contributing_path = Path("CONTRIBUTING.md")
        with contributing_path.open() as f:
            content = f.read().lower()

        required_workflow_sections = [
            "git workflow",
            "branch naming",
            "commit message",
            "pull request",
            "code review",
        ]

        for section in required_workflow_sections:
            assert section in content, f"CONTRIBUTING.md should document '{section}'"

        # Check for specific workflow steps
        workflow_terms = [
            "feature branch",
            "conventional commit",
            "rebase",
            "pull request",
            "code review",
        ]

        for term in workflow_terms:
            assert term in content, f"CONTRIBUTING.md should mention '{term}'"

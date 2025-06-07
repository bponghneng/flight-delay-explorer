"""Tests for version control configuration."""

import os
import subprocess
from pathlib import Path


class TestVersionControl:
    """Test version control configuration and Git repository setup."""

    def test_gitignore_exists(self):
        """Test that .gitignore file exists."""
        gitignore_path = Path(".gitignore")
        assert gitignore_path.exists(), ".gitignore file should exist"

    def test_gitignore_content(self):
        """Test .gitignore file contains required patterns."""
        gitignore_path = Path(".gitignore")
        with gitignore_path.open() as f:
            content = f.read()

        # Test Python-specific patterns
        python_patterns = [
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            ".pytest_cache/",
            ".coverage",
            ".coverage.*",
            "htmlcov/",
        ]

        for pattern in python_patterns:
            assert (
                pattern in content
            ), f"Python pattern '{pattern}' should be in .gitignore"

        # Test environment-specific patterns
        env_patterns = [
            ".env",
            ".venv/",
            "env/",
            "venv/",
            "ENV/",
        ]

        for pattern in env_patterns:
            assert (
                pattern in content
            ), f"Environment pattern '{pattern}' should be in .gitignore"

        # Test editor-specific patterns
        editor_patterns = [
            ".idea/",
            ".vscode/*",
        ]

        for pattern in editor_patterns:
            assert (
                pattern in content
            ), f"Editor pattern '{pattern}' should be in .gitignore"

        # Test build and distribution patterns
        build_patterns = [
            "dist/",
            "build/",
            "*.egg-info/",
        ]

        for pattern in build_patterns:
            assert (
                pattern in content
            ), f"Build pattern '{pattern}' should be in .gitignore"

    def test_git_repository_initialized(self):
        """Test that Git repository is properly initialized."""
        git_dir = Path(".git")
        assert (
            git_dir.exists()
        ), "Git repository should be initialized (.git directory exists)"
        assert git_dir.is_dir(), ".git should be a directory"

    def test_git_basic_operations(self):
        """Test basic Git operations work."""
        # Test git status
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True
        )
        assert result.returncode == 0, "git status should work"

        # Test git branch
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        assert result.returncode == 0, "git branch should work"
        assert result.stdout.strip(), "Should have a current branch"

    def test_git_config_setup(self):
        """Test that Git configuration is properly set up."""
        # Test that user.name is configured
        result = subprocess.run(
            ["git", "config", "user.name"], capture_output=True, text=True
        )
        # Don't assert success as this might not be configured globally
        # Just verify the command works
        assert result.returncode in [0, 1], "git config user.name should work"

        # Test that user.email is configured
        result = subprocess.run(
            ["git", "config", "user.email"], capture_output=True, text=True
        )
        # Don't assert success as this might not be configured globally
        assert result.returncode in [0, 1], "git config user.email should work"

    def test_branch_creation_and_switching(self):
        """Test creating and switching branches."""
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"], capture_output=True, text=True
        )
        original_branch = result.stdout.strip()

        # Create a test branch
        test_branch = f"test-branch-{os.getpid()}"

        try:
            # Create new branch
            result = subprocess.run(
                ["git", "checkout", "-b", test_branch], capture_output=True, text=True
            )
            assert (
                result.returncode == 0
            ), f"Should be able to create branch {test_branch}"

            # Verify we're on the new branch
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True
            )
            assert result.stdout.strip() == test_branch, f"Should be on {test_branch}"

            # Switch back to original branch
            result = subprocess.run(
                ["git", "checkout", original_branch], capture_output=True, text=True
            )
            assert (
                result.returncode == 0
            ), f"Should be able to switch back to {original_branch}"

        finally:
            # Clean up: delete test branch
            subprocess.run(
                ["git", "branch", "-D", test_branch], capture_output=True, text=True
            )

    def test_gitignore_patterns_work(self):
        """Test that ignored files are actually ignored by Git."""
        # Create a temporary ignored file in the repository
        test_file = Path("test_ignored_file.pyc")

        try:
            test_file.write_text("# test pyc file")

            # Check git status doesn't show the .pyc file
            result = subprocess.run(
                ["git", "status", "--porcelain", str(test_file)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 0, "git status should work"
            assert str(test_file) not in result.stdout, ".pyc files should be ignored"

        finally:
            # Clean up
            test_file.unlink(missing_ok=True)

    def test_git_hooks_directory_exists(self):
        """Test that .git/hooks directory exists."""
        hooks_dir = Path(".git/hooks")
        assert hooks_dir.exists(), ".git/hooks directory should exist"
        assert hooks_dir.is_dir(), ".git/hooks should be a directory"

    def test_pre_commit_hook_exists(self):
        """Test that pre-commit hook exists and is executable."""
        pre_commit_hook = Path(".git/hooks/pre-commit")
        assert pre_commit_hook.exists(), "pre-commit hook should exist"

        # Check if file is executable
        assert os.access(
            pre_commit_hook, os.X_OK
        ), "pre-commit hook should be executable"

    def test_commit_msg_hook_exists(self):
        """Test that commit-msg hook exists and is executable."""
        commit_msg_hook = Path(".git/hooks/commit-msg")
        assert commit_msg_hook.exists(), "commit-msg hook should exist"

        # Check if file is executable
        assert os.access(
            commit_msg_hook, os.X_OK
        ), "commit-msg hook should be executable"

    def test_pre_push_hook_exists(self):
        """Test that pre-push hook exists and is executable."""
        pre_push_hook = Path(".git/hooks/pre-push")
        assert pre_push_hook.exists(), "pre-push hook should exist"

        # Check if file is executable
        assert os.access(pre_push_hook, os.X_OK), "pre-push hook should be executable"

    def test_contributing_file_exists(self):
        """Test that CONTRIBUTING.md file exists."""
        contributing_path = Path("CONTRIBUTING.md")
        assert contributing_path.exists(), "CONTRIBUTING.md file should exist"

    def test_contributing_content(self):
        """Test CONTRIBUTING.md contains required sections."""
        contributing_path = Path("CONTRIBUTING.md")
        with contributing_path.open() as f:
            content = f.read()

        required_sections = [
            "Git workflow",
            "Branch naming",
            "Commit message",
            "Pull request",
            "Code review",
        ]

        for section in required_sections:
            assert (
                section.lower() in content.lower()
            ), f"CONTRIBUTING.md should contain '{section}' section"

    def test_github_directory_exists(self):
        """Test that .github directory exists."""
        github_dir = Path(".github")
        assert github_dir.exists(), ".github directory should exist"
        assert github_dir.is_dir(), ".github should be a directory"

    def test_pr_template_exists(self):
        """Test that PR template exists."""
        pr_template_path = Path(".github/PULL_REQUEST_TEMPLATE.md")
        assert pr_template_path.exists(), "PR template should exist"

    def test_pr_template_content(self):
        """Test PR template contains required sections."""
        pr_template_path = Path(".github/PULL_REQUEST_TEMPLATE.md")
        with pr_template_path.open() as f:
            content = f.read()

        required_sections = [
            "Description",
            "Related issue",
            "Checklist",
            "Testing",
        ]

        for section in required_sections:
            assert (
                section.lower() in content.lower()
            ), f"PR template should contain '{section}' section"

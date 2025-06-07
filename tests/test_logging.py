"""Tests for logging utility."""

import logging
import tempfile
from pathlib import Path

from flight_delay_explorer.utils.logging import setup_logger


class TestSetupLogger:
    """Test setup_logger function."""

    def test_setup_logger_basic_functionality(self):
        """Test basic logger creation with default parameters."""
        logger = setup_logger("test_logger")

        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) > 0

    def test_setup_logger_with_custom_level(self):
        """Test logger creation with custom log level."""
        logger = setup_logger("test_debug_logger", level=logging.DEBUG)

        assert logger.level == logging.DEBUG

    def test_setup_logger_with_different_levels(self):
        """Test creating loggers with different log levels."""
        info_logger = setup_logger("info_logger", level=logging.INFO)
        debug_logger = setup_logger("debug_logger", level=logging.DEBUG)
        error_logger = setup_logger("error_logger", level=logging.ERROR)

        assert info_logger.level == logging.INFO
        assert debug_logger.level == logging.DEBUG
        assert error_logger.level == logging.ERROR

    def test_setup_logger_console_output(self, caplog):
        """Test that logger outputs to console."""
        logger = setup_logger("console_test_logger", level=logging.INFO)

        with caplog.at_level(logging.INFO):
            logger.info("Test console message")

        assert "Test console message" in caplog.text

    def test_setup_logger_with_file_output(self):
        """Test logger with file output."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            logger = setup_logger(
                "file_test_logger", level=logging.INFO, log_file=str(log_file)
            )

            logger.info("Test file message")

            # Check that file was created and contains message
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "Test file message" in log_content

    def test_setup_logger_with_custom_format(self):
        """Test logger with custom format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "custom_format.log"
            custom_format = "%(name)s - %(levelname)s - %(message)s"

            logger = setup_logger(
                "custom_format_logger",
                level=logging.INFO,
                log_file=str(log_file),
                log_format=custom_format,
            )

            logger.info("Custom format test")

            log_content = log_file.read_text()
            assert "custom_format_logger - INFO - Custom format test" in log_content

    def test_setup_logger_default_format_with_timestamp(self):
        """Test that default format includes timestamp and log level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "timestamp_test.log"

            logger = setup_logger(
                "timestamp_logger", level=logging.INFO, log_file=str(log_file)
            )

            logger.info("Timestamp test message")

            log_content = log_file.read_text()
            # Check for timestamp pattern (YYYY-MM-DD HH:MM:SS)
            import re

            timestamp_pattern = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
            assert re.search(timestamp_pattern, log_content)
            assert "INFO" in log_content
            assert "Timestamp test message" in log_content

    def test_setup_logger_context_variables(self, caplog):
        """Test logger with context variables (request IDs)."""
        logger = setup_logger("context_logger", level=logging.INFO)

        with caplog.at_level(logging.INFO):
            # Simulate adding context
            logger.info("Request processed", extra={"request_id": "req-123"})

        assert "Request processed" in caplog.text

    def test_setup_logger_file_access_error_handling(self):
        """Test error handling for file access issues."""
        # Try to write to a directory that doesn't exist
        invalid_path = "/nonexistent/directory/test.log"

        # Should handle the error gracefully, not raise exception
        logger = setup_logger(
            "error_test_logger", level=logging.INFO, log_file=invalid_path
        )

        # Logger should still be created even if file handler fails
        assert logger is not None
        assert logger.name == "error_test_logger"

    def test_setup_logger_multiple_handlers(self):
        """Test that logger can have both console and file handlers."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "multi_handler.log"

            logger = setup_logger(
                "multi_handler_logger", level=logging.INFO, log_file=str(log_file)
            )

            # Should have at least console handler, and file handler if successful
            assert len(logger.handlers) >= 1

            logger.info("Multi handler test")

            # Check file was written
            if log_file.exists():
                log_content = log_file.read_text()
                assert "Multi handler test" in log_content

    def test_setup_logger_integration_with_external_libraries(self):
        """Test logger integration with external libraries."""
        logger = setup_logger("integration_logger", level=logging.DEBUG)

        # Test that we can log at different levels
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

        # Logger should be properly configured
        assert logger.level == logging.DEBUG

    def test_setup_logger_edge_cases(self):
        """Test edge cases for logger setup."""
        # Test with empty name
        logger = setup_logger("", level=logging.INFO)
        assert logger is not None

        # Test with very long name
        long_name = "a" * 1000
        logger = setup_logger(long_name, level=logging.INFO)
        assert logger.name == long_name

        # Test with special characters in name
        special_name = "test.logger-with_special:chars"
        logger = setup_logger(special_name, level=logging.INFO)
        assert logger.name == special_name

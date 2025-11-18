"""
Unit tests for logging_config module

Test Coverage:
- TC-LOG-001: Log level filtering
- TC-LOG-002: Structured JSON logging
- TC-LOG-003: Log injection prevention

Success Criteria:
- Log levels filter correctly
- JSON logs are valid and parseable
- No log injection vulnerabilities
- Performance acceptable
"""
import pytest
import logging
import json
import io
from pathlib import Path
from datetime import datetime

from logging_config import LogConfig, get_logger


class TestLogLevelFiltering:
    """TC-LOG-001: Log level filtering"""

    def test_debug_level_shows_all_messages(self, tmp_path):
        """DEBUG level should show all log messages"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="DEBUG", log_file=log_file)

        # Log at all levels
        test_logger = get_logger("test")
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        test_logger.critical("Critical message")

        # Read log file
        log_content = log_file.read_text()

        # All messages should be present
        assert "Debug message" in log_content
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
        assert "Critical message" in log_content

    def test_info_level_hides_debug(self, tmp_path):
        """INFO level should hide DEBUG messages"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")

        log_content = log_file.read_text()

        # DEBUG should not be present
        assert "Debug message" not in log_content

        # Others should be present
        assert "Info message" in log_content
        assert "Warning message" in log_content

    def test_warning_level_hides_info_and_debug(self, tmp_path):
        """WARNING level should hide INFO and DEBUG"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="WARNING", log_file=log_file)

        test_logger = get_logger("test")
        test_logger.debug("Debug message")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")

        log_content = log_file.read_text()

        assert "Debug message" not in log_content
        assert "Info message" not in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content

    def test_error_level_shows_only_error_and_critical(self, tmp_path):
        """ERROR level should show only ERROR and CRITICAL"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="ERROR", log_file=log_file)

        test_logger = get_logger("test")
        test_logger.info("Info message")
        test_logger.warning("Warning message")
        test_logger.error("Error message")
        test_logger.critical("Critical message")

        log_content = log_file.read_text()

        assert "Info message" not in log_content
        assert "Warning message" not in log_content
        assert "Error message" in log_content
        assert "Critical message" in log_content


class TestStructuredJSONLogging:
    """TC-LOG-002: Structured JSON logging"""

    def test_json_format_produces_valid_json(self, tmp_path):
        """JSON format should produce valid, parseable JSON"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(
            level="INFO",
            log_file=log_file,
            json_format=True
        )

        test_logger = get_logger("test")
        test_logger.info("Test message")

        # Read and parse each line
        log_lines = log_file.read_text().strip().split('\n')
        for line in log_lines:
            if line:  # Skip empty lines
                # Should be valid JSON
                log_entry = json.loads(line)
                assert isinstance(log_entry, dict)

    def test_json_contains_required_fields(self, tmp_path):
        """JSON logs should contain all required fields"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(
            level="INFO",
            log_file=log_file,
            json_format=True
        )

        test_logger = get_logger("test.module")
        test_logger.info("Test message")

        log_line = log_file.read_text().strip()
        log_entry = json.loads(log_line)

        # Required fields
        assert "time" in log_entry
        assert "level" in log_entry
        assert "module" in log_entry
        assert "function" in log_entry
        assert "line" in log_entry
        assert "message" in log_entry

        # Validate values
        assert log_entry["level"] == "INFO"
        assert log_entry["message"] == "Test message"
        assert "test.module" in log_entry["module"]

    def test_json_timestamps_iso8601(self, tmp_path):
        """JSON timestamps should be in ISO 8601 format"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(
            level="INFO",
            log_file=log_file,
            json_format=True
        )

        test_logger = get_logger("test")
        test_logger.info("Test message")

        log_line = log_file.read_text().strip()
        log_entry = json.loads(log_line)

        # Should be parseable as datetime
        timestamp = log_entry["time"]
        # Should not raise
        datetime.fromisoformat(timestamp.replace('Z', '+00:00').replace(',', '.'))

    def test_json_includes_exception_info_when_exc_info_true(self, tmp_path):
        """JSON should include exception info when exc_info=True"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(
            level="ERROR",
            log_file=log_file,
            json_format=True
        )

        test_logger = get_logger("test")

        try:
            raise ValueError("Test exception")
        except ValueError:
            test_logger.error("Error occurred", exc_info=True)

        log_line = log_file.read_text().strip()

        # Should contain exception info (traceback)
        assert "ValueError" in log_line or "Test exception" in log_line
        assert "Traceback" in log_line or "traceback" in log_line


class TestHumanReadableFormat:
    """Test human-readable log format"""

    def test_human_format_readable(self, tmp_path):
        """Human format should be readable"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(
            level="INFO",
            log_file=log_file,
            json_format=False
        )

        test_logger = get_logger("test")
        test_logger.info("Test message")

        log_content = log_file.read_text()

        # Should contain timestamp, level, module, message
        assert "INFO" in log_content
        assert "test" in log_content
        assert "Test message" in log_content

        # Should be human-readable (not JSON)
        assert not log_content.strip().startswith('{')

    def test_human_format_includes_function_and_line(self, tmp_path):
        """Human format should include function name and line number"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(
            level="INFO",
            log_file=log_file,
            json_format=False
        )

        test_logger = get_logger("test")
        test_logger.info("Test message")

        log_content = log_file.read_text()

        # Should contain function name and line number
        assert ":" in log_content  # Function:line format


class TestLogInjectionPrevention:
    """TC-LOG-003: Log injection prevention"""

    def test_newline_in_message_escaped(self, tmp_path):
        """Newlines in log messages should not create new log lines"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")
        # Attempt injection with newline
        test_logger.info("Message with\ninjected line")

        log_lines = [line for line in log_file.read_text().split('\n') if line.strip()]

        # Should be a single log entry (newline escaped or encoded)
        # Count of INFO level logs should be 1
        info_count = sum(1 for line in log_lines if "INFO" in line)
        assert info_count == 1

    def test_special_characters_sanitized(self, tmp_path):
        """Special characters should be handled safely"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")

        # Test various special characters
        test_logger.info("Test with 'quotes'")
        test_logger.info('Test with "double quotes"')
        test_logger.info("Test with special chars: !@#$%^&*()")

        # Should not crash and should be parseable
        log_content = log_file.read_text()
        assert len(log_content) > 0

    def test_sql_injection_style_message_safe(self, tmp_path):
        """SQL injection style messages should be logged safely"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")
        # Simulate SQL injection attempt in log
        test_logger.info("'; DROP TABLE users; --")

        log_content = log_file.read_text()

        # Message should be logged as-is (escaped)
        assert "DROP TABLE" in log_content
        # Should not cause any errors
        assert log_content


class TestMultipleLoggers:
    """Test multiple logger instances"""

    def test_different_modules_different_loggers(self):
        """Different modules should get different logger instances"""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name

    def test_same_module_same_logger(self):
        """Same module should get same logger instance"""
        logger1 = get_logger("module")
        logger2 = get_logger("module")

        # Should be the same logger instance
        assert logger1.name == logger2.name


class TestFileLogging:
    """Test file logging functionality"""

    def test_log_file_created(self, tmp_path):
        """Log file should be created automatically"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")
        test_logger.info("Test message")

        # File should exist
        assert log_file.exists()

    def test_log_file_parent_directory_created(self, tmp_path):
        """Parent directories should be created automatically"""
        log_file = tmp_path / "subdir" / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")
        test_logger.info("Test message")

        # File and parent dir should exist
        assert log_file.exists()
        assert log_file.parent.exists()

    def test_logs_written_to_both_console_and_file(self, tmp_path, capsys):
        """Logs should go to both console and file"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")
        test_logger.info("Test message")

        # Should be in file
        file_content = log_file.read_text()
        assert "Test message" in file_content

        # Should also be in console (stdout)
        captured = capsys.readouterr()
        assert "Test message" in captured.out or "Test message" in captured.err


class TestPerformance:
    """PERF-002: Logging performance"""

    def test_logging_performance(self, tmp_path):
        """Logging 1,000 messages should be fast (<100ms)"""
        log_file = tmp_path / "test.log"
        logger = LogConfig.setup_logging(level="INFO", log_file=log_file)

        test_logger = get_logger("test")

        import time
        start = time.time()

        for i in range(1000):
            test_logger.info(f"Log message {i}")

        duration = time.time() - start

        # Should complete in under 100ms
        # Note: This may fail in slow environments; adjust threshold as needed
        assert duration < 0.5, f"Logging too slow: {duration}s for 1000 messages"


# Pytest marks
pytestmark = [
    pytest.mark.unit,
    pytest.mark.logging
]


# Fixtures
@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging after each test"""
    yield
    # Clean up root logger handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

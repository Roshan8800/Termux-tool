import pytest
import json
import os
from termux_cyber_framework.adapters.audit_logger.file_audit_logger import FileAuditLogger

def test_file_audit_logger_creates_file_with_correct_permissions(tmp_path):
    # Arrange
    log_dir = tmp_path / "logs"
    log_file = log_dir / "audit.log"
    logger = FileAuditLogger(log_dir=str(log_dir), log_file="audit.log")

    # Assert
    assert os.path.exists(log_file)
    assert oct(os.stat(log_file).st_mode)[-3:] == "600"

def test_file_audit_logger_appends_event(tmp_path):
    # Arrange
    log_dir = tmp_path / "logs"
    log_file = log_dir / "audit.log"
    logger = FileAuditLogger(log_dir=str(log_dir), log_file="audit.log")
    event = {"event": "test"}

    # Act
    logger.append(event)

    # Assert
    with open(log_file, 'r') as f:
        line = f.readline()
        data = json.loads(line)
    assert data["event"] == "test"
    assert "timestamp" in data

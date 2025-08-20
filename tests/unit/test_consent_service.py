import pytest
import json
import os
from termux_cyber_framework.core.use_cases.consent.consent_service import ConsentService
from termux_cyber_framework.core.domain.models import Command

def test_consent_service_get_consent_yes(monkeypatch, tmp_path):
    # Arrange
    log_dir = tmp_path / "logs"
    log_file = log_dir / "consent_log.jsonl"
    service = ConsentService(log_dir=str(log_dir), log_file="consent_log.jsonl")
    command = Command(tool_name="test", args=[], raw_command="test")
    monkeypatch.setattr('builtins.input', lambda _: 'y')

    # Act
    result = service.get_consent(command)

    # Assert
    assert result is True
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        line = f.readline()
        data = json.loads(line)
    assert data["consent_given"] is True

def test_consent_service_get_consent_no(monkeypatch, tmp_path):
    # Arrange
    log_dir = tmp_path / "logs"
    log_file = log_dir / "consent_log.jsonl"
    service = ConsentService(log_dir=str(log_dir), log_file="consent_log.jsonl")
    command = Command(tool_name="test", args=[], raw_command="test")
    monkeypatch.setattr('builtins.input', lambda _: 'n')

    # Act
    result = service.get_consent(command)

    # Assert
    assert result is False
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        line = f.readline()
        data = json.loads(line)
    assert data["consent_given"] is False

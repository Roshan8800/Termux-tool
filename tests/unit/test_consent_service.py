import pytest
import json
import os
from termux_cyber_framework.core.use_cases.consent.consent_service import ConsentService
from termux_cyber_framework.core.domain.models import Command

def test_consent_service_get_consent_yes(monkeypatch, tmp_path):
    # Arrange
    log_file = tmp_path / "consent_log.json"
    service = ConsentService(log_file=str(log_file))
    command = Command(tool_name="nmap", args=["-sV", "localhost"], raw_command="nmap -sV localhost")
    monkeypatch.setattr('builtins.input', lambda: 'y')

    # Act
    result = service.get_consent(command)

    # Assert
    assert result is True
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        data = json.load(f)
    assert data[0]["consent_given"] is True

def test_consent_service_get_consent_no(monkeypatch, tmp_path):
    # Arrange
    log_file = tmp_path / "consent_log.json"
    service = ConsentService(log_file=str(log_file))
    command = Command(tool_name="nmap", args=["-sV", "localhost"], raw_command="nmap -sV localhost")
    monkeypatch.setattr('builtins.input', lambda: 'n')

    # Act
    result = service.get_consent(command)

    # Assert
    assert result is False
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        data = json.load(f)
    assert data[0]["consent_given"] is False

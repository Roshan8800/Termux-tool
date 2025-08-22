import pytest
import json
import os
from termux_cyber_framework.agents.security_compliance_agent import SecurityComplianceAgent
from termux_cyber_framework.core.domain.models import Command

def test_security_compliance_agent_get_consent_yes(monkeypatch, tmp_path):
    # Arrange
    log_file = tmp_path / "consent_log.json"
    agent = SecurityComplianceAgent(log_file=str(log_file))
    command = Command(tool_name="nmap", args=["-sV", "localhost"], raw_command="nmap -sV localhost")
    monkeypatch.setattr('builtins.input', lambda: 'y')

    # Act
    result = agent.get_consent(command)

    # Assert
    assert result is True
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        data = json.load(f)
    assert data[0]["consent_given"] is True

def test_security_compliance_agent_get_consent_no(monkeypatch, tmp_path):
    # Arrange
    log_file = tmp_path / "consent_log.json"
    agent = SecurityComplianceAgent(log_file=str(log_file))
    command = Command(tool_name="nmap", args=["-sV", "localhost"], raw_command="nmap -sV localhost")
    monkeypatch.setattr('builtins.input', lambda: 'n')

    # Act
    result = agent.get_consent(command)

    # Assert
    assert result is False
    assert os.path.exists(log_file)
    with open(log_file, 'r') as f:
        data = json.load(f)
    assert data[0]["consent_given"] is False

import pytest
import subprocess
import time
from termux_cyber_framework.core.command_runner import CommandRunner

def test_command_runner_success():
    # Arrange
    runner = CommandRunner()
    command = ["echo", "hello"]

    # Act
    result = runner.run(command)

    # Assert
    assert result.returncode == 0
    assert result.stdout == "hello\n"

def test_command_runner_timeout_soft_kill(tmp_path):
    # Arrange
    runner = CommandRunner()
    log_file = tmp_path / "test.log"
    command = ["python", "tests/unit/sleep.py", "5"]

    # Act & Assert
    with pytest.raises(subprocess.TimeoutExpired):
        runner.run(command, timeout=1, output_log_file=str(log_file))

    with open(log_file, "r") as f:
        log_content = f.read()
    assert "--- TIMEOUT ---" in log_content

def test_command_runner_timeout_hard_kill(tmp_path):
    # Arrange
    runner = CommandRunner()
    log_file = tmp_path / "test.log"
    # This command will ignore SIGTERM
    command = ["python", "-c", "import time; import signal; signal.signal(signal.SIGTERM, signal.SIG_IGN); time.sleep(20)"]

    # Act & Assert
    with pytest.raises(subprocess.TimeoutExpired):
        runner.run(command, timeout=1, output_log_file=str(log_file))

    with open(log_file, "r") as f:
        log_content = f.read()
    assert "--- TIMEOUT ---" in log_content

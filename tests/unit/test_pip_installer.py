import pytest
import subprocess
from termux_cyber_framework.adapters.tool_installer.pip_installer import PipInstallerAdapter
from termux_cyber_framework.core.domain.models import Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from tests.mocks import MockCommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

@pytest.fixture
def pip_tool():
    install_info = InstallInfo(
        method="pip",
        source="test-package",
        python_module="test_package"
    )
    return Tool(name="test-pip", description="Test pip tool", install_info=install_info, run_command="test-pip")

@pytest.fixture
def config_allow():
    return Config(allow_system_install=True)

@pytest.fixture
def config_disallow():
    return Config(allow_system_install=False)

def test_pip_install_success(tmp_path, pip_tool, config_allow):
    # Arrange
    mock_runner = MockCommandRunner({
        "python3 -m pip install test-package": {"returncode": 0}
    })
    installer = PipInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.install(pip_tool, config_allow)

    # Assert
    assert result is True

def test_pip_install_failure(tmp_path, pip_tool, config_allow):
    # Arrange
    mock_runner = MockCommandRunner({
        "python3 -m pip install test-package": {"exception": subprocess.CalledProcessError(1, "pip install", "error")}
    })
    installer = PipInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.install(pip_tool, config_allow)

    # Assert
    assert result is False

def test_pip_install_disallowed(tmp_path, pip_tool, config_disallow):
    # Arrange
    installer = PipInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act & Assert
    with pytest.raises(PermissionError, match="System-level installation for 'test-pip' is not allowed by policy."):
        installer.install(pip_tool, config_disallow)

def test_is_installed_success_module(tmp_path, pip_tool):
    # Arrange
    mock_runner = MockCommandRunner({
        "python3 -c import test_package": {"returncode": 0}
    })
    installer = PipInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(pip_tool)

    # Assert
    assert result is True

def test_is_installed_success_which(tmp_path, pip_tool, monkeypatch):
    # Arrange
    pip_tool.install_info.python_module = None
    monkeypatch.setattr("shutil.which", lambda x: "/usr/local/bin/test-pip")
    installer = PipInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(pip_tool)

    # Assert
    assert result is True

def test_is_installed_failure(tmp_path, pip_tool, monkeypatch):
    # Arrange
    pip_tool.install_info.python_module = None
    monkeypatch.setattr("shutil.which", lambda x: None)
    installer = PipInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(pip_tool)

    # Assert
    assert result is False

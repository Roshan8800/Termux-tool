import pytest
import subprocess
from termux_cyber_framework.adapters.tool_installer.pkg_installer import PkgInstallerAdapter
from termux_cyber_framework.core.domain.models import Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from tests.mocks import MockCommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

@pytest.fixture
def pkg_tool():
    install_info = InstallInfo(
        method="pkg",
        source="test-package"
    )
    return Tool(name="test-pkg", description="Test pkg tool", install_info=install_info, run_command="test-pkg")

@pytest.fixture
def config_allow():
    return Config(allow_system_install=True)

@pytest.fixture
def config_disallow():
    return Config(allow_system_install=False)

def test_pkg_install_success(tmp_path, pkg_tool, config_allow):
    # Arrange
    mock_runner = MockCommandRunner({
        "pkg install test-package -y": {"returncode": 0}
    })
    installer = PkgInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.install(pkg_tool, config_allow)

    # Assert
    assert result is True

def test_pkg_install_failure(tmp_path, pkg_tool, config_allow):
    # Arrange
    mock_runner = MockCommandRunner({
        "pkg install test-package -y": {"exception": subprocess.CalledProcessError(1, "pkg install", "error")}
    })
    installer = PkgInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.install(pkg_tool, config_allow)

    # Assert
    assert result is False

def test_pkg_install_disallowed(tmp_path, pkg_tool, config_disallow):
    # Arrange
    installer = PkgInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act & Assert
    with pytest.raises(PermissionError, match="System-level installation for 'test-pkg' is not allowed by policy."):
        installer.install(pkg_tool, config_disallow)

def test_is_installed_success(tmp_path, pkg_tool, monkeypatch):
    # Arrange
    monkeypatch.setattr("shutil.which", lambda x: "/usr/local/bin/test-pkg")
    installer = PkgInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(pkg_tool)

    # Assert
    assert result is True

def test_is_installed_failure(tmp_path, pkg_tool, monkeypatch):
    # Arrange
    monkeypatch.setattr("shutil.which", lambda x: None)
    installer = PkgInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(pkg_tool)

    # Assert
    assert result is False

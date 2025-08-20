import pytest
import subprocess
from termux_cyber_framework.adapters.tool_installer.git_installer import GitInstallerAdapter
from termux_cyber_framework.core.domain.models import Tool, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from tests.mocks import MockCommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

@pytest.fixture
def git_tool():
    install_info = InstallInfo(
        method="git",
        source="https://github.com/test/test.git",
        path="tools/test",
        health_check="test --version"
    )
    return Tool(name="test", description="Test tool", install_info=install_info, run_command="test")

@pytest.fixture
def config():
    return Config(allow_system_install=True)

def test_git_install_success(tmp_path, git_tool, config):
    # Arrange
    clone_path = tmp_path / git_tool.install_info.path
    git_tool.install_info.path = str(clone_path)
    mock_runner = MockCommandRunner({
        f"git clone {git_tool.install_info.source} {clone_path}": {"returncode": 0}
    })
    installer = GitInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.install(git_tool, config)

    # Assert
    assert result is True

def test_git_install_failure(tmp_path, git_tool, config):
    # Arrange
    clone_path = tmp_path / git_tool.install_info.path
    git_tool.install_info.path = str(clone_path)
    mock_runner = MockCommandRunner({
        f"git clone {git_tool.install_info.source} {clone_path}": {"exception": subprocess.CalledProcessError(1, "git clone", "error")}
    })
    installer = GitInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.install(git_tool, config)

    # Assert
    assert result is False

def test_is_installed_success(tmp_path, git_tool):
    # Arrange
    clone_path = tmp_path / git_tool.install_info.path
    clone_path.mkdir(parents=True)
    git_tool.install_info.path = str(clone_path)
    mock_runner = MockCommandRunner({
        git_tool.install_info.health_check: {"returncode": 0}
    })
    installer = GitInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(git_tool)

    # Assert
    assert result is True

def test_is_installed_failure_no_path(tmp_path, git_tool):
    # Arrange
    installer = GitInstallerAdapter(MockCommandRunner(), InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(git_tool)

    # Assert
    assert result is False

def test_is_installed_failure_health_check(tmp_path, git_tool):
    # Arrange
    clone_path = tmp_path / git_tool.install_info.path
    clone_path.mkdir(parents=True)
    git_tool.install_info.path = str(clone_path)
    mock_runner = MockCommandRunner({
        git_tool.install_info.health_check: {"exception": subprocess.CalledProcessError(1, "test --version", "error")}
    })
    installer = GitInstallerAdapter(mock_runner, InstallLogger(log_dir=str(tmp_path)))

    # Act
    result = installer.is_installed(git_tool)

    # Assert
    assert result is False

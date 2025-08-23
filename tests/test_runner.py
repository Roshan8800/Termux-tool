import pytest
from termux_cyber_framework.adapters.tool_runner.generic_runner import GenericRunner
from termux_cyber_framework.adapters.plugins.nmap_adapter import NmapAdapter
from termux_cyber_framework.adapters.plugins.sqlmap_adapter import SqlmapAdapter
from termux_cyber_framework.core.domain.models import Tool, Command, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from termux_cyber_framework.core.domain.run_paths import RunPaths
from tests.mocks import MockCommandRunner

# --- Fixtures ---

@pytest.fixture
def generic_tool():
    install_info = InstallInfo(method="pkg", source="echo")
    return Tool(name="echo", description="Echo tool", install_info=install_info, run_command="echo")

@pytest.fixture
def nmap_tool():
    install_info = InstallInfo(method="pkg", source="nmap")
    return Tool(name="nmap", description="Network scanner", install_info=install_info, run_command="nmap")

@pytest.fixture
def sqlmap_tool():
    install_info = InstallInfo(method="git", source="https://github.com/sqlmapproject/sqlmap.git", path="tools/sqlmap")
    return Tool(name="sqlmap", description="SQL injection tool", install_info=install_info, run_command="python3 tools/sqlmap/sqlmap.py")

# --- GenericRunner Tests ---

def test_generic_runner_success(generic_tool, tmp_path):
    # Arrange
    command = Command(tool_name="echo", args=["hello"], raw_command="echo hello")
    mock_runner = MockCommandRunner({
        "echo hello": {"returncode": 0, "stdout": "hello\n"}
    })
    adapter = GenericRunner(command_runner=mock_runner)

    # Act
    paths = RunPaths(run_dir=tmp_path, base_filename="test_run", output_log_file=tmp_path / "run.log")
    result = adapter.run(generic_tool, command, paths)

    # Assert
    assert result.success is True
    assert result.output == "hello\n"

# --- NmapAdapter Tests ---

def test_nmap_adapter_adds_default_args(nmap_tool, tmp_path):
    # Arrange
    command = Command(tool_name="nmap", args=["localhost"], raw_command="nmap localhost")
    mock_runner = MockCommandRunner()
    adapter = NmapAdapter(command_runner=mock_runner)

    # Act
    paths = RunPaths(run_dir=tmp_path, base_filename="test_run", output_log_file=tmp_path / "run.log")
    adapter.run(nmap_tool, command, paths)

    # Assert
    assert "-T3" in command.args
    assert "-sV" in command.args

def test_nmap_adapter_chunks_cidr(nmap_tool, tmp_path):
    # Arrange
    command = Command(tool_name="nmap", args=["192.168.1.0/30"], raw_command="nmap 192.168.1.0/30")
    mock_runner = MockCommandRunner()
    adapter = NmapAdapter(command_runner=mock_runner)

    # Act
    paths = RunPaths(run_dir=tmp_path, base_filename="test_run", output_log_file=tmp_path / "run.log")
    adapter.run(nmap_tool, command, paths)

    # Assert
    assert mock_runner.call_count == 2 # /30 gives 2 usable hosts
    assert "192.168.1." in mock_runner.last_command[-1]

# --- SqlmapAdapter Tests ---

def test_sqlmap_adapter_adds_default_args(sqlmap_tool, tmp_path):
    # Arrange
    command = Command(tool_name="sqlmap", args=["-u", "http://test.com"], raw_command="sqlmap -u http://test.com")
    mock_runner = MockCommandRunner()
    adapter = SqlmapAdapter(command_runner=mock_runner)

    # Act
    paths = RunPaths(run_dir=tmp_path, base_filename="test_run", output_log_file=tmp_path / "run.log")
    adapter.run(sqlmap_tool, command, paths)

    # Assert
    assert "--batch" in command.args
    assert "--threads" in command.args
    assert "1" in command.args

def test_sqlmap_adapter_parses_output(sqlmap_tool, tmp_path):
    # Arrange
    command = Command(tool_name="sqlmap", args=["-u", "http://test.com"], raw_command="sqlmap -u http://test.com")
    output = "parameter 'id' is vulnerable. a MySQL database"
    mock_runner = MockCommandRunner({
        "python3 tools/sqlmap/sqlmap.py -u http://test.com --batch --threads 1": {"returncode": 0, "stdout": output}
    })
    adapter = SqlmapAdapter(command_runner=mock_runner)

    # Act
    paths = RunPaths(run_dir=tmp_path, base_filename="test_run", output_log_file=tmp_path / "run.log")
    result = adapter.run(sqlmap_tool, command, paths)

    # Assert
    assert len(result.findings) == 1
    assert result.findings[0]["type"] == "SQL_INJECTION"
    assert result.findings[0]["parameter"] == "id"
    assert result.findings[0]["dbms"] == "MySQL"

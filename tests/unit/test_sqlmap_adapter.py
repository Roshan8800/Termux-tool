import pytest
from termux_cyber_framework.adapters.tool_runner.sqlmap_adapter import SqlmapAdapter
from termux_cyber_framework.core.domain.models import Tool, Command, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from tests.mocks import MockCommandRunner
from termux_cyber_framework.adapters.logger.install_logger import InstallLogger

@pytest.fixture
def sqlmap_tool():
    install_info = InstallInfo(method="git", source="https://github.com/sqlmapproject/sqlmap.git", path="tools/sqlmap")
    return Tool(name="sqlmap", description="SQL injection tool", install_info=install_info, run_command="python3 tools/sqlmap/sqlmap.py")

def test_sqlmap_adapter_adds_default_args(sqlmap_tool):
    # Arrange
    command = Command(tool_name="sqlmap", args=["-u", "http://test.com"], raw_command="sqlmap -u http://test.com")
    mock_runner = MockCommandRunner()
    adapter = SqlmapAdapter(command_runner=mock_runner)

    # Act
    adapter.run(sqlmap_tool, command)

    # Assert
    assert "--batch" in command.args
    assert "--threads" in command.args
    assert "1" in command.args

def test_sqlmap_adapter_parses_output(sqlmap_tool):
    # Arrange
    command = Command(tool_name="sqlmap", args=["-u", "http://test.com"], raw_command="sqlmap -u http://test.com")
    output = "parameter 'id' is vulnerable. a MySQL database"
    mock_runner = MockCommandRunner({
        "python3 tools/sqlmap/sqlmap.py -u http://test.com --batch --threads 1": {"returncode": 0, "stdout": output}
    })
    adapter = SqlmapAdapter(command_runner=mock_runner)

    # Act
    result = adapter.run(sqlmap_tool, command)

    # Assert
    assert len(result.findings) == 1
    assert result.findings[0]["type"] == "SQL_INJECTION"
    assert result.findings[0]["parameter"] == "id"
    assert result.findings[0]["dbms"] == "MySQL"

import pytest
from termux_cyber_framework.adapters.tool_runner.nmap_adapter import NmapAdapter
from termux_cyber_framework.core.domain.models import Tool, Command, InstallInfo
from termux_cyber_framework.core.domain.config import Config
from tests.mocks import MockCommandRunner

@pytest.fixture
def nmap_tool():
    install_info = InstallInfo(method="pkg", source="nmap")
    return Tool(name="nmap", description="Network scanner", install_info=install_info, run_command="nmap")

def test_nmap_adapter_adds_default_args(nmap_tool):
    # Arrange
    command = Command(tool_name="nmap", args=["localhost"], raw_command="nmap localhost")
    mock_runner = MockCommandRunner()
    adapter = NmapAdapter(command_runner=mock_runner)

    # Act
    adapter.run(nmap_tool, command)

    # Assert
    assert "-T3" in command.args
    assert "-sV" in command.args

def test_nmap_adapter_chunks_cidr(nmap_tool):
    # Arrange
    command = Command(tool_name="nmap", args=["192.168.1.0/30"], raw_command="nmap 192.168.1.0/30")
    mock_runner = MockCommandRunner()
    adapter = NmapAdapter(command_runner=mock_runner)

    # Act
    adapter.run(nmap_tool, command)

    # Assert
    assert mock_runner.call_count == 2 # /30 gives 2 usable hosts
    assert "192.168.1." in mock_runner.last_command[-1]

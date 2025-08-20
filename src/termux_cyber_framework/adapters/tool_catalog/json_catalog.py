import json
import os
from typing import List
from termux_cyber_framework.core.domain.models import Tool
from termux_cyber_framework.core.use_cases.ports import ToolCatalogPort

class JsonCatalogAdapter(ToolCatalogPort):
    """
    A ToolCatalogPort implementation that loads tools from a JSON file.
    """
    def __init__(self, manifest_path: str):
        self.manifest_path = manifest_path

    def get_tools(self) -> List[Tool]:
        if not os.path.exists(self.manifest_path):
            return []
        with open(self.manifest_path, 'r') as f:
            tool_data = json.load(f)
            return [Tool(**data) for data in tool_data]

import json
import os
from typing import List
from termux_cyber_framework.core.domain.models import ExecutionResult

class ExecutionHistory:
    """
    An adapter to persist execution history to a JSON file.
    """
    def __init__(self, history_path: str = "data/execution_history.json"):
        self.history_path = history_path
        if not os.path.exists(self.history_path):
            with open(self.history_path, 'w') as f:
                json.dump([], f)

    def append(self, result: ExecutionResult):
        with open(self.history_path, 'r+') as f:
            history = json.load(f)
            history.append(result.model_dump())
            f.seek(0)
            json.dump(history, f, indent=4)

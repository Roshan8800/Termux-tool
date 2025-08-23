import json
from datetime import datetime
import os
from termux_cyber_framework.agents.file_manager_agent import FileManagerAgent
from termux_cyber_framework.core.use_cases.ports import AuditLoggerPort

class FileAuditLogger(AuditLoggerPort):
    """
    An audit logger that appends events to a JSONL file using the FileManagerAgent.
    """
    def __init__(self, file_manager: FileManagerAgent, log_dir="logs", log_file="audit.log"):
        self.file_manager = file_manager
        self.log_path = os.path.join(log_dir, log_file)
        # The FileManagerAgent will handle directory creation, so we just need
        # to ensure the file exists for the first append.
        if not self.file_manager.path_exists(self.log_path):
            self.file_manager.write_file(self.log_path, "")
            # os.chmod is a separate concern, for now we simplify
            # self.file_manager.chmod(self.log_path, 0o600)

    def append(self, event: dict):
        """
        Appends an event to the audit log file.
        """
        try:
            event["timestamp"] = datetime.now().isoformat()
            line_to_append = json.dumps(event) + "\n"
            self.file_manager.append_file(self.log_path, line_to_append)
        except Exception as e:
            # The file_manager's logger will already log the error.
            # We might want a fallback print here if the logger itself fails.
            print(f"CRITICAL: Error writing to audit log: {e}")

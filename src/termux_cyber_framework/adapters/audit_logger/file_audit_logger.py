import json
import os
from datetime import datetime

class FileAuditLogger:
    """
    An audit logger that appends events to a JSONL file.
    """
    def __init__(self, log_dir="logs", log_file="audit.log"):
        self.log_path = os.path.join(log_dir, log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        # Ensure the log file exists and has the correct permissions
        if not os.path.exists(self.log_path):
            open(self.log_path, 'a').close()
            os.chmod(self.log_path, 0o600)

    def append(self, event: dict):
        """
        Appends an event to the audit log file.
        """
        try:
            event["timestamp"] = datetime.now().isoformat()
            with open(self.log_path, "a") as f:
                f.write(json.dumps(event) + "\n")
        except Exception as e:
            print(f"Error writing to audit log: {e}")

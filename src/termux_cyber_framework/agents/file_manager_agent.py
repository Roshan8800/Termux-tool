import os
import shutil
from termux_cyber_framework.core.use_cases.ports import LoggerPort, LogLevel
from typing import Optional

class FileManagerAgent:
    """
    A centralized agent for handling all file system operations with logging
    and error handling.
    """
    def __init__(self, logger: LoggerPort):
        self.logger = logger

    def read_file(self, path: str) -> Optional[str]:
        self.logger.log(f"Reading file: {path}", level=LogLevel.DEBUG)
        try:
            with open(path, 'r') as f:
                return f.read()
        except (IOError, FileNotFoundError) as e:
            self.logger.log(f"Error reading file {path}: {e}", level=LogLevel.ERROR)
            return None

    def write_file(self, path: str, content: str) -> bool:
        self.logger.log(f"Writing to file: {path}", level=LogLevel.DEBUG)
        try:
            # Ensure the directory exists before writing
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            return True
        except IOError as e:
            self.logger.log(f"Error writing to file {path}: {e}", level=LogLevel.ERROR)
            return False

    def append_file(self, path: str, content: str) -> bool:
        self.logger.log(f"Appending to file: {path}", level=LogLevel.DEBUG)
        try:
            dir_path = os.path.dirname(path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            with open(path, 'a') as f:
                f.write(content)
            return True
        except IOError as e:
            self.logger.log(f"Error appending to file {path}: {e}", level=LogLevel.ERROR)
            return False

    def create_directory(self, path: str) -> bool:
        self.logger.log(f"Creating directory: {path}", level=LogLevel.DEBUG)
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError as e:
            self.logger.log(f"Error creating directory {path}: {e}", level=LogLevel.ERROR)
            return False

    def copy_file(self, src: str, dest: str) -> bool:
        self.logger.log(f"Copying file from {src} to {dest}", level=LogLevel.DEBUG)
        try:
            shutil.copy(src, dest)
            return True
        except (IOError, shutil.Error) as e:
            self.logger.log(f"Error copying file from {src} to {dest}: {e}", level=LogLevel.ERROR)
            return False

    def delete_file(self, path: str) -> bool:
        self.logger.log(f"Deleting file: {path}", level=LogLevel.DEBUG)
        try:
            if os.path.exists(path) and os.path.isfile(path):
                os.remove(path)
            return True
        except OSError as e:
            self.logger.log(f"Error deleting file {path}: {e}", level=LogLevel.ERROR)
            return False

    def delete_directory(self, path: str) -> bool:
        self.logger.log(f"Deleting directory: {path}", level=LogLevel.DEBUG)
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            return True
        except OSError as e:
            self.logger.log(f"Error deleting directory {path}: {e}", level=LogLevel.ERROR)
            return False

    def path_exists(self, path: str) -> bool:
        """Checks if a path (file or directory) exists."""
        return os.path.exists(path)

from pydantic import BaseModel
from pathlib import Path

class RunPaths(BaseModel):
    """
    A value object to hold the paths for the report files.
    """
    summary_file: Path
    output_log_file: Path

from pydantic import BaseModel
from pathlib import Path
from typing import Optional

class RunPaths(BaseModel):
    """
    A value object to hold the paths for the report files.
    """
    run_dir: Path
    base_filename: str
    output_log_file: Optional[Path] = None

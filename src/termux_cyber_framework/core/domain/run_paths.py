from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List

class RunPaths(BaseModel):
    """
    A value object to hold the paths for the report files.
    """
    run_dir: Path
    base_filename: str
    output_log_file: Optional[Path] = None
    report_files: List[str] = Field(default_factory=list)

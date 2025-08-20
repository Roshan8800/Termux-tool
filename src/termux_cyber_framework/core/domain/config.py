from pydantic import BaseModel, Field
from typing import Optional

class Config(BaseModel):
    """
    Holds the configuration for the framework.
    """
    allow_system_install: bool = Field(False, description="Whether to allow system-level installations (e.g., with pkg).")
    session_id: Optional[str] = Field(None, description="The session ID for the current run.")
    consent_hash: Optional[str] = Field(None, description="A hash representing the user's consent.")
    dry_run: bool = Field(False, description="If True, the framework will not perform any actions.")

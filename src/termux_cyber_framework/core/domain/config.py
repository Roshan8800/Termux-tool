from pydantic import BaseModel, Field

class Config(BaseModel):
    """
    Holds the configuration for the framework.
    """
    allow_system_install: bool = Field(False, description="Whether to allow system-level installations (e.g., with pkg).")

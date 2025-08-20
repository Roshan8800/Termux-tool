from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class Severity(str, Enum):
    """Enumeration for vulnerability severity levels."""
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class NetworkDevice(BaseModel):
    """Represents a device discovered on the network."""
    ip_address: str = Field(..., description="The IP address of the device.")
    mac_address: Optional[str] = Field(None, description="The MAC address of the device.")
    hostname: Optional[str] = Field(None, description="The hostname of the device.")
    open_ports: list[int] = Field(default_factory=list, description="A list of open TCP ports.")

class Vulnerability(BaseModel):
    """Represents a security vulnerability found on a device."""
    cve_id: Optional[str] = Field(None, description="The CVE identifier for the vulnerability (e.g., CVE-2021-44228).")
    description: str = Field(..., description="A description of the vulnerability.")
    severity: Severity = Field(..., description="The severity level of the vulnerability.")
    device: NetworkDevice = Field(..., description="The device affected by the vulnerability.")

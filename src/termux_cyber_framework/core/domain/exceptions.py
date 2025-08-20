class DomainError(Exception):
    """Base class for domain-specific exceptions."""
    pass

class InvalidDeviceError(DomainError):
    """Raised when a network device has invalid properties."""
    pass

class VulnerabilityNotFoundError(DomainError):
    """Raised when a vulnerability is not found."""
    pass

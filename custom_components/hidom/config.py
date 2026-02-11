"""Configuration classes for HiDOM."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class HiDOMConfig:
    """Main HiDOM configuration."""
    host: str
    scan_interval_climate: int = 10
    scan_interval_sensor: int = 30
    timeout: int = 10
    
    @classmethod
    def from_entry_data(cls, data: Dict[str, Any]) -> 'HiDOMConfig':
        """Create configuration from config entry data."""
        return cls(
            host=data["host"],
            scan_interval_climate=data.get("scan_interval", 10),
            scan_interval_sensor=data.get("sensor_scan_interval", 30),
            timeout=data.get("timeout", 10)
        )

@dataclass
class DeviceConfig:
    """Device configuration."""
    name: str
    scan_interval: int = 10
    retry_count: int = 3
    
    @classmethod
    def from_device_data(cls, data: Dict[str, Any]) -> 'DeviceConfig':
        """Create configuration from device data."""
        return cls(
            name=data.get("name", "Unknown Device"),
            scan_interval=data.get("scan_interval", 10),
            retry_count=data.get("retry_count", 3)
        )
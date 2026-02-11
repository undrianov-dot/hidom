"""Base entity for HiDOM integration."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo

from ..const import DOMAIN

class HiDOMBaseEntity(CoordinatorEntity, ABC):
    """Base class for all HiDOM entities."""
    
    def __init__(self, coordinator, host: str, device_info: Optional[DeviceInfo] = None):
        """Initialize."""
        super().__init__(coordinator)
        self._host = host
        
        if device_info:
            self._attr_device_info = device_info
        else:
            self._attr_device_info = self._create_device_info(host)
    
    def _create_device_info(self, host: str) -> DeviceInfo:
        """Create default device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, host)},
            name=f"HiDOM Hub ({host})",
            manufacturer="Hisense",
            model="HiDOM Hub",
            configuration_url=f"http://{host}",
        )
    
    @property
    @abstractmethod
    def unique_id(self) -> str:
        """Return unique entity identifier."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return entity name."""
        pass
    
    @abstractmethod
    def _update_from_coordinator(self) -> None:
        """Update data from coordinator."""
        pass
    
    @property
    def available(self) -> bool:
        """Check entity availability."""
        if not self.coordinator.last_update_success:
            return False
        return self._is_device_data_available()
    
    @abstractmethod
    def _is_device_data_available(self) -> bool:
        """Check if device data is available."""
        pass
    
    async def async_added_to_hass(self) -> None:
        """Called when entity is added to HA."""
        await super().async_added_to_hass()
        self._update_from_coordinator()
    
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        self._update_from_coordinator()
        self.async_write_ha_state()
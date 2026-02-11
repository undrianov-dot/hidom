"""Entity factory for HiDOM integration."""
import logging
from typing import List

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from ..device.manager import HiDOMDeviceManager
from ..const import DOMAIN
from .climate import HiDOMClimateEntity
from .sensor import (
    HiDOMRawMeterSensor,
    HiDOMEnergyMeterSensor,
    HiDOMPowerSensor
)

_LOGGER = logging.getLogger(__name__)

class HiDOMEntityFactory:
    """Factory for creating HiDOM entities."""
    
    @staticmethod
    def create_climate_entities(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities
    ) -> None:
        """Create climate entities."""
        data = hass.data[DOMAIN][entry.entry_id]
        coordinator = data["coordinator_climate"]
        device_manager = data["device_manager"]
        host = data["host"]
        
        entities = []
        
        if coordinator.data:
            for uid, device_data in coordinator.data.items():
                entity = HiDOMClimateEntity(
                    coordinator=coordinator,
                    device_manager=device_manager,
                    device_uid=uid,
                    host=host,
                    device_data=device_data
                )
                entities.append(entity)
        
        if entities:
            async_add_entities(entities)
            _LOGGER.info("Created %s climate entities", len(entities))
    
    @staticmethod
    def create_sensor_entities(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities
    ) -> None:
        """Create sensor entities."""
        data = hass.data[DOMAIN][entry.entry_id]
        coordinator = data["coordinator_sensor"]
        host = data["host"]
        
        entities = [
            HiDOMRawMeterSensor(coordinator, host),
            HiDOMEnergyMeterSensor(coordinator, host),
            HiDOMPowerSensor(coordinator, host),
        ]
        
        async_add_entities(entities)
        _LOGGER.info("Created %s sensor entities", len(entities))
"""HiDOM (Hisense DOM) integration."""
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .api.client import HiDOMAPIClient
from .device.manager import HiDOMDeviceManager

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HiDOM from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Create API client
    session = aiohttp_client.async_get_clientsession(hass)
    api_client = HiDOMAPIClient(
        host=entry.data["host"],
        session=session
    )
    
    # Create device manager
    device_manager = HiDOMDeviceManager(api_client)
    
    # Coordinator for climate devices
    async def update_climate_data():
        """Update climate devices data."""
        return await device_manager.get_idu_devices()
    
    coordinator_climate = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_climate",
        update_method=update_climate_data,
        update_interval=timedelta(seconds=10),
    )
    
    # Coordinator for power meter data
    async def update_sensor_data():
        """Update sensor data."""
        return await api_client.get_power_data()
    
    coordinator_sensor = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_sensor",
        update_method=update_sensor_data,
        update_interval=timedelta(seconds=30),
    )
    
    # Initialize coordinators
    try:
        await coordinator_climate.async_config_entry_first_refresh()
        await coordinator_sensor.async_config_entry_first_refresh()
    except Exception as e:
        _LOGGER.warning("Initial refresh failed: %s", e)
    
    # Store dependencies
    hass.data[DOMAIN][entry.entry_id] = {
        "api_client": api_client,
        "device_manager": device_manager,
        "coordinator_climate": coordinator_climate,
        "coordinator_sensor": coordinator_sensor,
        "host": entry.data["host"]
    }
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(
        entry, ["climate", "sensor"]
    )
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, ["climate", "sensor"]
    )
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    
    return unload_ok
"""Services for HiDOM integration."""
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN

SERVICE_REFRESH_DEVICES = "refresh_devices"
SERVICE_SYNC_TIME = "sync_time"
SERVICE_SET_GLOBAL_TEMP = "set_global_temperature"

SERVICE_SCHEMA_REFRESH_DEVICES = vol.Schema({})

SERVICE_SCHEMA_SYNC_TIME = vol.Schema({})

SERVICE_SCHEMA_SET_GLOBAL_TEMP = vol.Schema({
    vol.Required("temperature"): vol.All(vol.Coerce(int), vol.Range(16, 30)),
})

async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for HiDOM."""
    
    async def handle_refresh_devices(call: ServiceCall) -> None:
        """Handle refresh_devices service call."""
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]["coordinator_climate"]
            await coordinator.async_refresh()
    
    async def handle_sync_time(call: ServiceCall) -> None:
        """Handle sync_time service call."""
        # Placeholder for time synchronization service
        pass
    
    async def handle_set_global_temp(call: ServiceCall) -> None:
        """Handle set_global_temperature service call."""
        temperature = call.data["temperature"]
        
        for entry_id in hass.data[DOMAIN]:
            coordinator = hass.data[DOMAIN][entry_id]["coordinator_climate"]
            device_manager = hass.data[DOMAIN][entry_id]["device_manager"]
            
            if coordinator.data:
                for device_uid in coordinator.data:
                    # Update each device
                    await device_manager.update_device(
                        device_id=device_uid,
                        temp=temperature,
                        onoff=1  # Ensure device is on
                    )
            
            # Refresh coordinator
            await coordinator.async_refresh()
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_DEVICES,
        handle_refresh_devices,
        schema=SERVICE_SCHEMA_REFRESH_DEVICES,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SYNC_TIME,
        handle_sync_time,
        schema=SERVICE_SCHEMA_SYNC_TIME,
    )
    
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_GLOBAL_TEMP,
        handle_set_global_temp,
        schema=SERVICE_SCHEMA_SET_GLOBAL_TEMP,
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload HiDOM services."""
    hass.services.async_remove(DOMAIN, SERVICE_REFRESH_DEVICES)
    hass.services.async_remove(DOMAIN, SERVICE_SYNC_TIME)
    hass.services.async_remove(DOMAIN, SERVICE_SET_GLOBAL_TEMP)
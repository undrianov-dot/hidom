"""Climate entity for HiDOM."""
import logging

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .base import HiDOMBaseEntity
from ..device.manager import HiDOMDeviceManager
from ..api.models import IDUDevice
from ..const import (
    MODE_MAP, MODE_REVERSE_MAP, 
    FAN_MAP, FAN_REVERSE_MAP,
    MODE_COOL
)

_LOGGER = logging.getLogger(__name__)

# Mode mapping
DEVICE_TO_HVAC = {
    "cool": HVACMode.COOL,
    "heat": HVACMode.HEAT,
    "dry": HVACMode.DRY,
    "fan_only": HVACMode.FAN_ONLY,
}

HVAC_TO_DEVICE = {
    HVACMode.COOL: "cool",
    HVACMode.HEAT: "heat",
    HVACMode.DRY: "dry",
    HVACMode.FAN_ONLY: "fan_only",
}

class HiDOMClimateEntity(HiDOMBaseEntity, ClimateEntity):
    """HiDOM indoor unit representation."""
    
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE |
        ClimateEntityFeature.FAN_MODE |
        ClimateEntityFeature.TURN_OFF |
        ClimateEntityFeature.TURN_ON
    )
    _attr_hvac_modes = [
        HVACMode.OFF, HVACMode.COOL, HVACMode.HEAT, 
        HVACMode.DRY, HVACMode.FAN_ONLY
    ]
    _attr_fan_modes = ["auto", "low", "medium", "high"]
    _attr_min_temp = 16
    _attr_max_temp = 30
    _attr_target_temperature_step = 1
    
    def __init__(
        self,
        coordinator,
        device_manager: HiDOMDeviceManager,
        device_uid: str,
        host: str,
        device_data: IDUDevice
    ):
        """Initialize."""
        super().__init__(coordinator, host)
        
        self._device_manager = device_manager
        self._device_uid = device_uid
        self._device_data = device_data
        
        # Extract sys and addr
        if '_' in device_uid:
            s_part, addr_part = device_uid.split('_')
            self._sys = int(s_part[1:])
            self._addr = int(addr_part)
        else:
            self._sys = 1
            self._addr = 1
        
        # Entity settings
        self._attr_name = device_data.name or f"IDU {device_uid}"
        self._attr_unique_id = f"hidom_{device_uid}"
        
        # Current data cache
        self._current_data = device_data
        self._saved_settings = {
            "temp": 24,
            "mode": MODE_COOL,
            "fan": 4
        }
    
    @property
    def unique_id(self) -> str:
        return self._attr_unique_id
    
    @property
    def name(self) -> str:
        return self._attr_name
    
    def _update_from_coordinator(self) -> None:
        """Update data from coordinator."""
        if not self.coordinator.data:
            return
        
        device_data = self.coordinator.data.get(self._device_uid)
        if device_data:
            self._current_data = device_data
            
            # Save settings if device is on
            if device_data.power == 1:
                self._saved_settings = {
                    "temp": device_data.set_temp,
                    "mode": device_data.mode_code,
                    "fan": device_data.fan_code
                }
    
    def _is_device_data_available(self) -> bool:
        """Check if device data is available."""
        return self._device_uid in self.coordinator.data
    
    @property
    def target_temperature(self) -> float:
        if self._current_data and hasattr(self._current_data, 'set_temp'):
            return self._current_data.set_temp
        return self._saved_settings.get("temp", 24)
    
    @property
    def current_temperature(self) -> float:
        if self._current_data:
            return self._current_data.room_temp
        return None
    
    @property
    def hvac_mode(self) -> HVACMode:
        if not self._current_data:
            return HVACMode.OFF
        
        if self._current_data.power == 0:
            return HVACMode.OFF
        
        mode = self._current_data.mode
        return DEVICE_TO_HVAC.get(mode, HVACMode.COOL)
    
    @property
    def fan_mode(self) -> str:
        if self._current_data:
            fan = self._current_data.fan
            if fan not in self._attr_fan_modes:
                if "low" in fan:
                    return "low"
                elif "medium" in fan or "mid" in fan:
                    return "medium"
                elif "high" in fan:
                    return "high"
                else:
                    return "auto"
            return fan
        return "auto"
    
    async def async_set_temperature(self, **kwargs):
        """Set target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        
        self._saved_settings["temp"] = int(temperature)
        
        # If device is on, send command
        if self._current_data and self._current_data.power == 1:
            success = await self._device_manager.update_device(
                device_id=self._device_uid,
                onoff=1,
                mode=self._current_data.mode_code,
                fan=self._current_data.fan_code,
                temp=int(temperature)
            )
            
            if success:
                await self.coordinator.async_request_refresh()
    
    async def async_set_hvac_mode(self, hvac_mode):
        """Set HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            # Turn off device
            success = await self._device_manager.update_device(
                device_id=self._device_uid,
                onoff=0,
                mode=self._saved_settings["mode"],
                fan=self._saved_settings["fan"],
                temp=self._saved_settings["temp"]
            )
        else:
            # Turn on with selected mode
            device_mode = HVAC_TO_DEVICE.get(hvac_mode, "cool")
            mode_code = MODE_REVERSE_MAP.get(device_mode, MODE_COOL)
            
            self._saved_settings["mode"] = mode_code
            
            success = await self._device_manager.update_device(
                device_id=self._device_uid,
                onoff=1,
                mode=mode_code,
                fan=self._saved_settings["fan"],
                temp=self._saved_settings["temp"]
            )
        
        if success:
            await self.coordinator.async_request_refresh()
    
    async def async_set_fan_mode(self, fan_mode):
        """Set fan mode."""
        fan_code = FAN_REVERSE_MAP.get(fan_mode, 4)
        self._saved_settings["fan"] = fan_code
        
        if self._current_data and self._current_data.power == 1:
            success = await self._device_manager.update_device(
                device_id=self._device_uid,
                onoff=1,
                mode=self._current_data.mode_code,
                fan=fan_code,
                temp=self._current_data.set_temp
            )
            
            if success:
                await self.coordinator.async_request_refresh()
    
    async def async_turn_on(self):
        """Turn on device."""
        success = await self._device_manager.update_device(
            device_id=self._device_uid,
            onoff=1,
            mode=self._saved_settings["mode"],
            fan=self._saved_settings["fan"],
            temp=self._saved_settings["temp"]
        )
        
        if success:
            await self.coordinator.async_request_refresh()
    
    async def async_turn_off(self):
        """Turn off device."""
        success = await self._device_manager.update_device(
            device_id=self._device_uid,
            onoff=0,
            mode=self._saved_settings["mode"],
            fan=self._saved_settings["fan"],
            temp=self._saved_settings["temp"]
        )
        
        if success:
            await self.coordinator.async_request_refresh()
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        attrs = {}
        
        if self._current_data:
            attrs.update({
                "error_code": self._current_data.error_code,
                "status": self._current_data.status,
                "pipe_temperature": self._current_data.pipe_temp,
                "uid": self._device_uid,
                "sys": self._sys,
                "addr": self._addr,
            })
        
        return attrs
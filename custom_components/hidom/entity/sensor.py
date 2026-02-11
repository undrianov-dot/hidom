"""Sensor entities for HiDOM."""
import logging
import time

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy, UnitOfPower

from .base import HiDOMBaseEntity

_LOGGER = logging.getLogger(__name__)

class HiDOMRawMeterSensor(HiDOMBaseEntity, SensorEntity):
    """Raw power meter sensor."""
    
    _attr_icon = "mdi:meter-electric"
    
    def __init__(self, coordinator, host: str):
        """Initialize."""
        super().__init__(coordinator, host)
        self._attr_unique_id = f"hidom_raw_meter_{host.replace('.', '_')}"
        self._attr_name = "HiDOM Raw Power Meter"
    
    def _update_from_coordinator(self) -> None:
        """Update data from coordinator."""
        pass
    
    def _is_device_data_available(self) -> bool:
        return self.coordinator.data is not None
    
    @property
    def native_value(self):
        """Return raw value."""
        data = self.coordinator.data
        if data is None:
            return None
        
        try:
            return float(data)
        except (ValueError, TypeError):
            return data
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "data_source": "HiDOM Raw Meter",
            "ip_address": self._host,
        }

class HiDOMEnergyMeterSensor(HiDOMBaseEntity, SensorEntity):
    """Energy meter in kWh."""
    
    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_suggested_display_precision = 2
    
    def __init__(self, coordinator, host: str):
        """Initialize."""
        super().__init__(coordinator, host)
        self._attr_unique_id = f"hidom_energy_meter_{host.replace('.', '_')}"
        self._attr_name = "HiDOM Energy Meter"
    
    def _update_from_coordinator(self) -> None:
        """Update data from coordinator."""
        pass
    
    def _is_device_data_available(self) -> bool:
        return self.coordinator.data is not None
    
    @property
    def native_value(self):
        """Return value in kWh."""
        data = self.coordinator.data
        if data is None:
            return None
        
        try:
            # Convert watt-hours to kilowatt-hours
            power_wh = float(data)
            return round(power_wh / 1000.0, 2)
        except (ValueError, TypeError):
            return None
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        attrs = {
            "data_source": "HiDOM",
            "ip_address": self._host,
        }
        
        data = self.coordinator.data
        if data is not None:
            try:
                attrs["raw_value_wh"] = float(data)
                attrs["raw_value_kwh"] = round(float(data) / 1000, 3)
            except (ValueError, TypeError):
                attrs["raw_value"] = data
        
        return attrs

class HiDOMPowerSensor(HiDOMBaseEntity, SensorEntity):
    """Current power sensor."""
    
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.KILO_WATT
    _attr_suggested_display_precision = 3
    
    def __init__(self, coordinator, host: str):
        """Initialize."""
        super().__init__(coordinator, host)
        self._attr_unique_id = f"hidom_power_{host.replace('.', '_')}"
        self._attr_name = "HiDOM Current Power"
        
        # For power calculation
        self._last_energy = None
        self._last_update_time = None
        self._current_power = 0.0
    
    def _update_from_coordinator(self) -> None:
        """Update data from coordinator."""
        pass
    
    def _is_device_data_available(self) -> bool:
        return self.coordinator.data is not None
    
    @property
    def native_value(self):
        """Calculate current power."""
        data = self.coordinator.data
        
        if data is None:
            return round(self._current_power, 3)
        
        try:
            current_energy = float(data)
            current_time = time.time()
            
            if self._last_energy is not None and self._last_update_time is not None:
                # Calculate difference
                energy_diff_wh = current_energy - self._last_energy
                time_diff_hours = (current_time - self._last_update_time) / 3600.0
                
                if time_diff_hours > 0:
                    power_kw = (energy_diff_wh / time_diff_hours) / 1000.0
                    
                    # Smoothing
                    if self._current_power == 0:
                        self._current_power = power_kw
                    else:
                        self._current_power = 0.7 * self._current_power + 0.3 * power_kw
            
            # Update previous values
            self._last_energy = current_energy
            self._last_update_time = current_time
            
            return round(self._current_power, 3)
            
        except (ValueError, TypeError):
            return round(self._current_power, 3)
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "data_source": "HiDOM Power Calculation",
            "ip_address": self._host,
            "calculated_power_kw": round(self._current_power, 3),
        }
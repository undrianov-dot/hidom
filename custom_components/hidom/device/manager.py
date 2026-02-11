"""Device manager for HiDOM."""
import logging
import time
from typing import Dict, Optional, List
from abc import ABC, abstractmethod

from ..api.client import HiDOMAPIClient
from ..api.models import IDUDevice
from ..const import MODE_MAP, FAN_MAP

_LOGGER = logging.getLogger(__name__)

class DeviceManager(ABC):
    """Abstract device manager."""
    
    @abstractmethod
    async def get_devices(self, force_refresh: bool = False) -> Dict[str, IDUDevice]:
        """Get devices."""
        pass
    
    @abstractmethod
    async def update_device(self, device_id: str, **params) -> bool:
        """Update device."""
        pass

class HiDOMDeviceManager(DeviceManager):
    """HiDOM device manager with caching."""
    
    def __init__(self, api_client: HiDOMAPIClient):
        self._api = api_client
        self._miscdata_cache: Optional[Dict] = None
        self._miscdata_timestamp: float = 0
        self._idu_cache: Dict[str, IDUDevice] = {}
        self._idu_timestamp: float = 0
    
    async def get_idu_devices(self, force_refresh: bool = False) -> Dict[str, IDUDevice]:
        """Get all indoor units."""
        current_time = time.time()
        
        # Use cache if data is not stale (5 minutes)
        if (not force_refresh and 
            self._idu_cache and 
            current_time - self._idu_timestamp < 300):
            return self._idu_cache
        
        try:
            # Get topology
            miscdata = await self._api.get_miscdata()
            if not miscdata:
                return self._idu_cache or {}
            
            # Filter only IDU devices
            topo = miscdata.get("topo", [])
            idu_topo = [item for item in topo if item.get("type") == "IDU"]
            
            if not idu_topo:
                return {}
            
            # Prepare request for device data
            devs = [
                {"sys": item.get("sysAdr", 1), "addr": item.get("address", "1")}
                for item in idu_topo
            ]
            
            # Get device data
            idu_response = await self._api.get_idu_data(devs)
            if not idu_response:
                return self._idu_cache or {}
            
            # Process data
            devices = {}
            idu_dats = idu_response.get("dats", [])
            
            for idu_data in idu_dats:
                # Find corresponding topology item
                sys = idu_data.get("sys")
                addr = idu_data.get("addr")
                
                topo_item = next(
                    (t for t in idu_topo 
                     if t.get("sysAdr") == sys and str(t.get("address")) == str(addr)),
                    {}
                )
                
                # Create device object
                device = IDUDevice.from_api_data(topo_item, idu_data)
                
                # Transform codes to readable values
                self._process_device_data(device)
                
                # Store
                devices[device.uid] = device
            
            # Update cache
            self._idu_cache = devices
            self._idu_timestamp = current_time
            
            return devices
            
        except Exception as e:
            _LOGGER.error("Failed to get IDU devices: %s", e)
            return self._idu_cache or {}
    
    def _process_device_data(self, device: IDUDevice) -> None:
        """Process device data."""
        # Transform mode
        if device.mode_code in MODE_MAP:
            device.mode = MODE_MAP[device.mode_code]
        else:
            device.mode = "cool"
        
        # Transform fan speed
        if device.fan_code in FAN_MAP:
            device.fan = FAN_MAP[device.fan_code]
        elif device.fan_code in [16, 32, 64]:
            device.fan = "high"
        else:
            device.fan = "medium"
        
        # Determine status
        if device.error_code != 0:
            if device.error_code in [60, 61, 64, 65]:
                device.status = "offline"
            else:
                device.status = "alarm"
        else:
            device.status = "on" if device.power == 1 else "off"
    
    async def update_device(self, device_id: str, **params) -> bool:
        """Update device parameters."""
        try:
            # Parse device identifier
            if '_' not in device_id:
                return False
            
            s_part, addr_part = device_id.split('_')
            sys = int(s_part[1:])
            addr = int(addr_part)
            
            # Send command
            success = await self._api.set_idu(sys, addr, **params)
            
            # Invalidate cache on successful update
            if success:
                self._idu_timestamp = 0
            
            return success
            
        except (ValueError, KeyError) as e:
            _LOGGER.error("Invalid device ID format: %s", e)
            return False
    
    async def get_devices(self, force_refresh: bool = False) -> Dict[str, IDUDevice]:
        """Alias for compatibility."""
        return await self.get_idu_devices(force_refresh)
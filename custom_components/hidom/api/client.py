"""API client for HiDOM."""
import asyncio
import json
import logging
import aiohttp
from typing import Dict, Any, Optional, List

from .models import IDUDevice

_LOGGER = logging.getLogger(__name__)

class HiDOMAPIClient:
    """HTTP client for HiDOM API."""
    
    def __init__(self, host: str, session: aiohttp.ClientSession):
        self._host = host
        self._session = session
        self._base_url = f"http://{host}"
    
    async def get_miscdata(self) -> Optional[Dict[str, Any]]:
        """Get device topology."""
        url = f"{self._base_url}/cgi/get_miscdata.shtml"
        
        try:
            async with self._session.post(
                url,
                json={"ip": "127.0.0.1"},
                timeout=10
            ) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json(content_type=None)
                if data.get("status") != "success":
                    return None
                
                return data.get("miscdata", {})
                
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Failed to get miscdata: %s", e)
            return None
    
    async def get_idu_data(self, devs: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Get indoor unit data."""
        url = f"{self._base_url}/cgi/get_idu_data.shtml"
        
        try:
            async with self._session.post(
                url,
                json={"ip": "127.0.0.1", "devs": devs},
                timeout=15
            ) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json(content_type=None)
                if data.get("status") != "success":
                    return None
                
                return data
                
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Failed to get IDU data: %s", e)
            return None
    
    async def set_idu(self, sys: int, addr: int, **kwargs) -> bool:
        """Set indoor unit parameters."""
        url = f"{self._base_url}/cgi/set_idu.shtml"
        
        cmd_list = [{
            "seq": 1,
            "sys": sys,
            "iduAddr": addr,
            "regAddr": 78,
            "regVal": [
                kwargs.get("onoff", 1),
                kwargs.get("mode", 2),
                kwargs.get("fan", 4),
                kwargs.get("temp", 24),
                0
            ]
        }]
        
        try:
            async with self._session.post(
                url,
                json={"ip": "127.0.0.1", "cmdList": cmd_list},
                timeout=10
            ) as resp:
                if resp.status != 200:
                    return False
                
                data = await resp.json(content_type=None)
                return data.get("status") == "success"
                
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Failed to set IDU: %s", e)
            return False
    
    async def get_power_data(self) -> Optional[float]:
        """Get power meter data."""
        url = f"{self._base_url}/cgi/get_meter_pwr.shtml"
        
        try:
            # Create separate session to avoid MIME-type issues
            timeout = aiohttp.ClientTimeout(total=10)
            connector = aiohttp.TCPConnector(limit=1)
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "HomeAssistant"}
            ) as session:
                
                payload = {"ids": ["1", "2"], "ip": self._host}
                headers = {"Content-Type": "application/json"}
                
                async with session.post(
                    url, 
                    json=payload, 
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        return None
                    
                    raw_bytes = await response.read()
                    
                    try:
                        raw_text = raw_bytes.decode('ascii')
                    except UnicodeDecodeError:
                        raw_text = raw_bytes.decode('utf-8', errors='ignore')
                    
                    # Decode ASCII codes if response contains numbers
                    if raw_text.strip() and all(c.isdigit() or c.isspace() for c in raw_text.strip()):
                        try:
                            ascii_codes = [int(x) for x in raw_text.split()]
                            decoded_text = ''.join(chr(code) for code in ascii_codes)
                            raw_text = decoded_text
                        except Exception:
                            pass
                    
                    # Parse JSON
                    try:
                        data = json.loads(raw_text)
                        
                        if data.get("status") != "success":
                            return None
                        
                        # Find power meter data
                        for meter in data.get("dats", []):
                            if isinstance(meter, dict) and "pwr" in meter:
                                power_value = meter["pwr"]
                                try:
                                    power = float(power_value)
                                    if power >= 0:
                                        return power
                                except (ValueError, TypeError):
                                    continue
                        
                        return None
                        
                    except json.JSONDecodeError:
                        return None
                        
        except (asyncio.TimeoutError, aiohttp.ClientError) as e:
            _LOGGER.error("Failed to get power data: %s", e)
            return None
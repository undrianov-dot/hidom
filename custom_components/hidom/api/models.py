"""Data models for HiDOM API."""
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class IDUDevice:
    """Indoor unit model."""
    sys: int
    addr: int
    name: str
    code: str = ""
    pname: str = ""
    ppname: str = ""
    pppname: str = ""
    indoor_name: str = ""
    tenant_name: str = ""
    
    # State data
    power: int = 0
    mode_code: int = 2
    fan_code: int = 4
    set_temp: int = 24
    error_code: int = 0
    room_temp: Optional[float] = None
    pipe_temp: Optional[float] = None
    
    # Lock registers
    model1: int = 0
    model2: int = 0
    model3: int = 0
    model4: int = 0
    model5: int = 0
    
    # Transformed values
    mode: str = "cool"
    fan: str = "auto"
    status: str = "off"
    
    @property
    def uid(self) -> str:
        """Unique device identifier."""
        return f"S{self.sys}_{self.addr}"
    
    @classmethod
    def from_api_data(cls, topo_item: Dict[str, Any], idu_data: Dict[str, Any]) -> 'IDUDevice':
        """Create from API data."""
        raw_data = idu_data.get("data", [])
        
        device = cls(
            sys=topo_item.get("sysAdr", 1),
            addr=int(topo_item.get("address", 1)),
            name=topo_item.get("name", ""),
            code=topo_item.get("code", ""),
            pname=topo_item.get("pname", ""),
            ppname=topo_item.get("ppname", ""),
            pppname=topo_item.get("pppname", ""),
            indoor_name=topo_item.get("indoorName", ""),
            tenant_name=topo_item.get("tenantName", ""),
            
            power=raw_data[28] if len(raw_data) > 28 else 0,
            mode_code=raw_data[29] if len(raw_data) > 29 else 2,
            fan_code=raw_data[30] if len(raw_data) > 30 else 4,
            set_temp=raw_data[31] if len(raw_data) > 31 else 24,
            error_code=raw_data[35] if len(raw_data) > 35 else 0,
            room_temp=raw_data[39] if len(raw_data) > 39 else None,
            pipe_temp=raw_data[38] if len(raw_data) > 38 else None,
            
            model1=raw_data[72] if len(raw_data) > 72 else 0,
            model2=raw_data[73] if len(raw_data) > 73 else 0,
            model3=raw_data[74] if len(raw_data) > 74 else 0,
            model4=raw_data[75] if len(raw_data) > 75 else 0,
            model5=raw_data[77] if len(raw_data) > 77 else 0,
        )
        
        return device

@dataclass
class PowerData:
    """Power meter data model."""
    power_w: Optional[float] = None
    power_kw: Optional[float] = None
    
    @classmethod
    def from_watts(cls, watts: float) -> 'PowerData':
        """Create from watts."""
        return cls(
            power_w=watts,
            power_kw=watts / 1000.0 if watts is not None else None
        )
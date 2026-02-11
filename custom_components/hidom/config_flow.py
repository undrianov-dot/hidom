"""Config flow for HiDOM integration."""
import aiohttp
import asyncio
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import aiohttp_client

from .const import DOMAIN

class HiDOMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HiDOM."""
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        
        if user_input is not None:
            host = user_input.get("host", "").strip()
            
            # Check uniqueness
            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()
            
            # Test connection
            try:
                session = aiohttp_client.async_get_clientsession(self.hass)
                async with session.get(f"http://{host}/", timeout=5) as resp:
                    if resp.status != 200:
                        # Try another endpoint
                        async with session.get(
                            f"http://{host}/cgi/get_miscdata.shtml", 
                            timeout=5
                        ):
                            pass
            except (asyncio.TimeoutError, aiohttp.ClientError):
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
                
            if not errors:
                # Create entry
                return self.async_create_entry(
                    title=f"HiDOM ({host})",
                    data={"host": host}
                )
        
        # Input form
        data_schema = vol.Schema({
            vol.Required("host", default="10.99.3.100"): str,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
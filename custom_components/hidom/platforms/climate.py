"""Climate platform for HiDOM."""
from ..entity.factory import HiDOMEntityFactory

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up climate platform."""
    HiDOMEntityFactory.create_climate_entities(
        hass, entry, async_add_entities
    )
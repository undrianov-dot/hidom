"""Sensor platform for HiDOM."""
from ..entity.factory import HiDOMEntityFactory

async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensor platform."""
    HiDOMEntityFactory.create_sensor_entities(
        hass, entry, async_add_entities
    )
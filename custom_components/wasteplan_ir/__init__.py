"""
Custom integration to integrate Wasteplan IR with Home Assistant.

For more details about this integration, please refer to
https://github.com/thordy/wasteplan_ir
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .coordinator import WasteplanIRDataUpdateCoordinator
from .api import (
    WasteplanIRApiClient,
)
from .const import DOMAIN, LOCATION_NAME

PLATFORMS: list[Platform] = [
    Platform.CALENDAR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    hass.data.setdefault(DOMAIN, {})

    hass.data[DOMAIN][entry.entry_id] = coordinator = WasteplanIRDataUpdateCoordinator(
        hass=hass,
        client=WasteplanIRApiClient(
            address=entry.data[LOCATION_NAME],
            session=async_get_clientsession(hass),
        ),
    )

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

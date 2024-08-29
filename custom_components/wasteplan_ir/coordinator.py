"""DataUpdateCoordinator for Wasteplan IR integration."""

from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import WasteplanIRApiClient, WasteplanIRApiClientError
from .const import DOMAIN, LOGGER, LOCATION_NAME


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class WasteplanIRDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: WasteplanIRApiClient,
    ) -> None:
        """Initialize."""
        self.client = client
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=5),
        )
        self.entities: list[WasteplanIREntity] = []

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self.client.async_get_pickups()
        except WasteplanIRApiClientError as exception:
            raise UpdateFailed(exception) from exception


class WasteplanIREntity(CoordinatorEntity):
    """Representation of a Wasteplan entity."""

    def __init__(
        self,
        coordinator: WasteplanIRDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize Wasteplan entity."""
        super().__init__(coordinator=coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(entry.data[LOCATION_NAME]))},
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://github.com/thordy/wasteplan_ir",
            manufacturer="Innherred Renovasjon",
            name="Innherred Renovasjon",
        )

"""Support for Wasteplan IR calendar."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.core import callback
from homeassistant.util import dt

from .const import CALENDAR_NAME, DOMAIN, LOCATION_NAME
from .coordinator import WasteplanIREntity

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.update_coordinator import DataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Wasteplan calendars based on a config entry."""
    coordinator: DataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WasteplanIRCalendar(coordinator, entry)])


class WasteplanIRCalendar(WasteplanIREntity, CalendarEntity):
    """Define a Wasteplan calendar."""

    _attr_icon = "mdi:delete-empty"

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the Wasteplan entity."""
        super().__init__(coordinator, entry)
        self._attr_name = entry.data[CALENDAR_NAME]
        self._attr_location = entry.data[LOCATION_NAME]
        self._event: CalendarEvent | None = None

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming event."""
        return self._event

    async def async_get_events(
        self,
        _: HomeAssistant,
        start_date: datetime,
        end_date: datetime,
    ) -> list[CalendarEvent]:
        """Return calendar events within a datetime range."""
        events: list[CalendarEvent] = []
        waste_summary = None
        waste_pickup = None

        for fraction_details in self.coordinator.data.values():
            for date in fraction_details["dates"]:
                waste_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S").replace(
                    hour=8, tzinfo=UTC
                )
                waste_pickup = dt.as_local(waste_date)
                waste_summary = fraction_details["fraction_name"]

                event = CalendarEvent(
                    summary=waste_summary,
                    description=fraction_details["frequency_human"],
                    start=waste_pickup,
                    end=waste_pickup + timedelta(hours=8),
                )

                if (
                    start_date.date() <= waste_date.date() <= end_date.date()
                    and event is not None
                ):
                    events.append(event)

        return events

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        next_waste_summary = None
        next_waste_pickup = None
        for fraction_details in self.coordinator.data.values():
            for date in fraction_details["dates"]:
                waste_date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S").replace(
                    hour=8, tzinfo=UTC
                )

                if (
                    waste_date
                    and (next_waste_pickup is None)
                    and waste_date.date() >= dt.now().date()
                ):
                    next_waste_pickup = dt.as_local(waste_date)
                    next_waste_summary = fraction_details["fraction_name"]

            self._event = None
            if next_waste_pickup is not None and next_waste_summary is not None:
                self._event = CalendarEvent(
                    summary=next_waste_summary,
                    start=next_waste_pickup,
                    end=next_waste_pickup + timedelta(hours=8),
                )

            super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()

"""Adds config flow for Wasteplan IR integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant import config_entries

from .const import CALENDAR_NAME, DOMAIN, LOCATION_NAME

if TYPE_CHECKING:
    from homeassistant.data_entry_flow import FlowResult


class WasteplanIRFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Wasteplan IR."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._errors: dict[str, str] = {}

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> FlowResult:
        """Handle a flow initialized by the user."""
        self._errors = {}

        if user_input is not None:
            address = user_input[LOCATION_NAME]
            calendar_name = user_input.get(CALENDAR_NAME)

            return self.async_create_entry(
                title=address,
                data={
                    CALENDAR_NAME: calendar_name,
                    LOCATION_NAME: address,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(LOCATION_NAME): str, vol.Required(CALENDAR_NAME): str}
            ),
            errors=self._errors,
        )

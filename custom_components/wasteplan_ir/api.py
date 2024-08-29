"""IR API Client."""

from __future__ import annotations

import socket
from typing import Any

import aiohttp
import async_timeout


class WasteplanIRApiClientError(Exception):
    """Exception to indicate a general API error."""


class WasteplanIRApiClientCommunicationError(
    WasteplanIRApiClientError,
):
    """Exception to indicate a communication error."""


class WasteplanIRApiClient:
    """WasteplanIRApiClient API Client."""

    def __init__(
        self,
        address: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize with address and session."""
        self._address = address
        self._session = session

    async def async_get_pickups(self) -> any:
        """Get pickup base data from IR."""
        return await self._api_wrapper(
            method="get",
            url="https://innherredrenovasjon.no/wp-json/ir/v1/garbage-disposal-dates-by-address?address="
            + self._address,
        )

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
    ) -> Any:
        """Get information from the API."""
        try:
            async with async_timeout.timeout(10):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                response.raise_for_status()
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise WasteplanIRApiClientCommunicationError(
                msg,
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise WasteplanIRApiClientCommunicationError(
                msg,
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            msg = f"Something really wrong happened! - {exception}"
            raise WasteplanIRApiClientError(
                msg,
            ) from exception

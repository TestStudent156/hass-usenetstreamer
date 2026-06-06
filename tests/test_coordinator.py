"""Tests for the UsenetStreamer coordinator."""
from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.usenetstreamer.api import CannotConnect
from custom_components.usenetstreamer.coordinator import (
    UsenetStreamerCoordinator,
)


async def test_coordinator_returns_data(hass):
    client = AsyncMock()
    client.async_get_data.return_value = {"addonVersion": "1.0", "values": {}}
    coord = UsenetStreamerCoordinator(hass, client, scan_interval=60)
    data = await coord._async_update_data()
    assert data["addonVersion"] == "1.0"


async def test_coordinator_wraps_errors(hass):
    client = AsyncMock()
    client.async_get_data.side_effect = CannotConnect
    coord = UsenetStreamerCoordinator(hass, client, scan_interval=60)
    with pytest.raises(UpdateFailed):
        await coord._async_update_data()

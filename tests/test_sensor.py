"""Tests for UsenetStreamer entities via full entry setup."""
from __future__ import annotations

from unittest.mock import patch

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.usenetstreamer.const import DOMAIN

ENTRY_DATA = {
    "host": "1.2.3.4", "port": 7000, "ssl": False,
    "admin_token": "TOK", "verify_ssl": True,
}
FAKE = {
    "addonVersion": "1.2.3",
    "values": {"INDEXER_MANAGER": "prowlarr",
               "INDEXER_MANAGER_INDEXERS": "-1",
               "EASYNEWS_ENABLED": "true",
               "NZB_TRIAGE_ENABLED": "false"},
}


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, data=ENTRY_DATA)
    entry.add_to_hass(hass)
    with patch(
        "custom_components.usenetstreamer.UsenetStreamerClient.async_get_data",
        return_value=FAKE,
    ):
        await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    return entry


async def test_version_sensor(hass: HomeAssistant):
    await _setup(hass)
    assert hass.states.get("sensor.usenetstreamer_addon_version").state == "1.2.3"


async def test_indexer_manager_sensor(hass: HomeAssistant):
    await _setup(hass)
    state = hass.states.get("sensor.usenetstreamer_indexer_manager")
    assert state.state == "prowlarr"


async def test_indexers_all(hass: HomeAssistant):
    await _setup(hass)
    state = hass.states.get("sensor.usenetstreamer_configured_indexers")
    assert state.state == "all"


async def test_easynews_binary_sensor(hass: HomeAssistant):
    await _setup(hass)
    assert hass.states.get("binary_sensor.usenetstreamer_easynews_enabled").state == "on"


async def test_reachable_binary_sensor(hass: HomeAssistant):
    await _setup(hass)
    assert hass.states.get("binary_sensor.usenetstreamer_reachable").state == "on"

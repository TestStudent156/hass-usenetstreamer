"""Sensor platform for UsenetStreamer."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import UsenetStreamerConfigEntry
from .coordinator import UsenetStreamerCoordinator
from .entity import UsenetStreamerEntity


def _indexers(data: dict[str, Any]) -> str:
    raw = str(data.get("values", {}).get("INDEXER_MANAGER_INDEXERS", "")).strip()
    if raw in ("", "-1"):
        return "all"
    return str(len([x for x in raw.split(",") if x.strip()]))


@dataclass(frozen=True, kw_only=True)
class UsSensorDescription(SensorEntityDescription):
    """Describes a UsenetStreamer sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[UsSensorDescription, ...] = (
    UsSensorDescription(
        key="addon_version", translation_key="addon_version",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: d.get("addonVersion"),
    ),
    UsSensorDescription(
        key="indexer_manager", translation_key="indexer_manager",
        value_fn=lambda d: d.get("values", {}).get("INDEXER_MANAGER"),
    ),
    UsSensorDescription(
        key="configured_indexers", translation_key="configured_indexers",
        value_fn=_indexers,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UsenetStreamerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        UsenetStreamerSensor(coordinator, entry.entry_id, desc)
        for desc in SENSORS
    )


class UsenetStreamerSensor(UsenetStreamerEntity, SensorEntity):
    """A single UsenetStreamer sensor."""

    entity_description: UsSensorDescription

    def __init__(
        self,
        coordinator: UsenetStreamerCoordinator,
        entry_id: str,
        description: UsSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)

"""Binary sensor platform for UsenetStreamer."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import UsenetStreamerConfigEntry
from .coordinator import UsenetStreamerCoordinator
from .entity import UsenetStreamerEntity


def _truthy(value: Any) -> bool:
    return str(value).strip().lower() in ("true", "1", "yes", "on")


@dataclass(frozen=True, kw_only=True)
class UsBinaryDescription(BinarySensorEntityDescription):
    """Describes a UsenetStreamer binary sensor."""

    value_fn: Callable[[UsenetStreamerCoordinator], bool]


BINARY_SENSORS: tuple[UsBinaryDescription, ...] = (
    UsBinaryDescription(
        key="reachable", translation_key="reachable",
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        value_fn=lambda c: c.last_update_success,
    ),
    UsBinaryDescription(
        key="easynews_enabled", translation_key="easynews_enabled",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda c: _truthy(
            c.data.get("values", {}).get("EASYNEWS_ENABLED")
        ),
    ),
    UsBinaryDescription(
        key="healthcheck_enabled", translation_key="healthcheck_enabled",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda c: _truthy(
            c.data.get("values", {}).get("NZB_TRIAGE_ENABLED")
        ),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UsenetStreamerConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        UsenetStreamerBinarySensor(coordinator, entry.entry_id, desc)
        for desc in BINARY_SENSORS
    )


class UsenetStreamerBinarySensor(UsenetStreamerEntity, BinarySensorEntity):
    """A single UsenetStreamer binary sensor."""

    entity_description: UsBinaryDescription

    def __init__(
        self,
        coordinator: UsenetStreamerCoordinator,
        entry_id: str,
        description: UsBinaryDescription,
    ) -> None:
        super().__init__(coordinator, entry_id)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        return self.entity_description.value_fn(self.coordinator)

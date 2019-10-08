"""Support for StarLine switch."""
from homeassistant.components.switch import SwitchDevice
from .account import StarlineAccount, StarlineDevice
from .const import DOMAIN
from .entity import StarlineEntity

SWITCH_TYPES = {
    "ign": ["Engine", "mdi:engine-outline", "mdi:engine-off-outline"],
    "webasto": ["Webasto", "mdi:radiator", "mdi:radiator-off"],
    "out": [
        "Additional Channel",
        "mdi:access-point-network",
        "mdi:access-point-network-off",
    ],
}


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up the StarLine switch."""
    account: StarlineAccount = hass.data[DOMAIN]
    entities = []
    for device in account.api.devices.values():
        if device.support_state:
            for key, value in SWITCH_TYPES.items():
                entities.append(StarlineSwitch(account, device, key, *value))
    async_add_entities(entities)
    return True


class StarlineSwitch(StarlineEntity, SwitchDevice):
    """Representation of a StarLine switch."""

    def __init__(
        self,
        account: StarlineAccount,
        device: StarlineDevice,
        key: str,
        name: str,
        icon_on: str,
        icon_off: str,
    ):
        """Initialize the switch."""
        super().__init__(account, device, key, name)
        self._icon_on = icon_on
        self._icon_off = icon_off

    @property
    def available(self):
        """Return True if entity is available."""
        return super().available and self._device.online

    @property
    def device_state_attributes(self):
        """Return the state attributes of the switch."""
        if self._key == "ign":
            return self._account.engine_attrs(self._device)
        return None

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon_on if self.is_on else self._icon_off

    @property
    def assumed_state(self):
        """Return True if unable to access real state of the entity."""
        return True

    @property
    def is_on(self):
        """Return True if entity is on."""
        return self._device.car_state[self._key]

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        await self._account.api.set_car_state(self._device.device_id, self._key, True)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        await self._account.api.set_car_state(self._device.device_id, self._key, False)

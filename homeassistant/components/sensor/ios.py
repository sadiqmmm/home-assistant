"""
Support for Home Assistant iOS app sensors.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/ecosystem/ios/
"""
from homeassistant.components import ios
from homeassistant.helpers.entity import Entity

DEPENDENCIES = ["ios"]

SENSOR_TYPES = {
    "level": ["Battery Level", "%"],
    "state": ["Battery State", None]
}

DEFAULT_ICON_LEVEL = "mdi:battery"
DEFAULT_ICON_STATE = "mdi:power-plug"


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the iOS sensor."""
    if discovery_info is None:
        return
    dev = list()
    for device_name, device in ios.devices().items():
        for sensor_type in ("level", "state"):
            dev.append(IOSSensor(sensor_type, device_name, device))

    add_devices(dev)


class IOSSensor(Entity):
    """Representation of an iOS sensor."""

    def __init__(self, sensor_type, device_name, device):
        """Initialize the sensor."""
        self._device_name = device_name
        self._name = device_name + " " + SENSOR_TYPES[sensor_type][0]
        self._device = device
        self.type = sensor_type
        self._state = None
        self._unit_of_measurement = SENSOR_TYPES[sensor_type][1]
        self.update()

    @property
    def name(self):
        """Return the name of the iOS sensor."""
        device_name = self._device[ios.ATTR_DEVICE][ios.ATTR_DEVICE_NAME]
        return "{} {}".format(device_name, SENSOR_TYPES[self.type][0])

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unique_id(self):
        """Return the unique ID of this sensor."""
        device_id = self._device[ios.ATTR_DEVICE_ID]
        return "sensor_ios_battery_{}_{}".format(self.type, device_id)

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement this sensor expresses itself in."""

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        device = self._device[ios.ATTR_DEVICE]
        device_battery = self._device[ios.ATTR_BATTERY]
        return {
            "Battery State": device_battery[ios.ATTR_BATTERY_STATE],
            "Battery Level": device_battery[ios.ATTR_BATTERY_LEVEL],
            "Device Type": device[ios.ATTR_DEVICE_TYPE],
            "Device Name": device[ios.ATTR_DEVICE_NAME],
            "Device Version": device[ios.ATTR_DEVICE_SYSTEM_VERSION],
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        device_battery = self._device[ios.ATTR_BATTERY]
        battery_state = device_battery[ios.ATTR_BATTERY_STATE]
        battery_level = device_battery[ios.ATTR_BATTERY_LEVEL]
        rounded_level = round(battery_level, -1)
        returning_icon_level = DEFAULT_ICON_LEVEL
        if battery_state == ios.ATTR_BATTERY_STATE_FULL:
            returning_icon_level = DEFAULT_ICON_LEVEL
            if battery_state == ios.ATTR_BATTERY_STATE_CHARGING:
                returning_icon_state = DEFAULT_ICON_STATE
            else:
                returning_icon_state = "{}-off".format(DEFAULT_ICON_STATE)
        elif battery_state == ios.ATTR_BATTERY_STATE_CHARGING:
            # Why is MDI missing 10, 50, 70?
            if rounded_level in (20, 30, 40, 60, 80, 90, 100):
                returning_icon_level = "{}-charging-{}".format(
                    DEFAULT_ICON_LEVEL, str(rounded_level))
                returning_icon_state = DEFAULT_ICON_STATE
            else:
                returning_icon_level = "{}-charging".format(
                    DEFAULT_ICON_LEVEL)
                returning_icon_state = DEFAULT_ICON_STATE
        elif battery_state == ios.ATTR_BATTERY_STATE_UNPLUGGED:
            if rounded_level < 10:
                returning_icon_level = "{}-outline".format(
                    DEFAULT_ICON_LEVEL)
                returning_icon_state = "{}-off".format(DEFAULT_ICON_STATE)
            elif battery_level > 95:
                returning_icon_state = "{}-off".format(DEFAULT_ICON_STATE)
                returning_icon_level = "{}-outline".format(
                    DEFAULT_ICON_LEVEL)
            else:
                returning_icon_level = "{}-{}".format(DEFAULT_ICON_LEVEL,
                                                      str(rounded_level))
                returning_icon_state = "{}-off".format(DEFAULT_ICON_STATE)
        elif battery_state == ios.ATTR_BATTERY_STATE_UNKNOWN:
            returning_icon_level = "{}-unknown".format(DEFAULT_ICON_LEVEL)
            returning_icon_state = "{}-unknown".format(DEFAULT_ICON_LEVEL)

        if self.type == "state":
            return returning_icon_state
        else:
            return returning_icon_level

    def update(self):
        """Get the latest state of the sensor."""
        self._device = ios.devices().get(self._device_name)
        self._state = self._device[ios.ATTR_BATTERY][self.type]

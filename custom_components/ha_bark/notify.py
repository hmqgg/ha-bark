import logging
import requests

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TARGET,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    BaseNotificationService
)
from homeassistant.const import CONF_HOST, CONF_TOKEN
from .const import ATTR_AUTO_COPY, ATTR_BADGE, ATTR_COPY, ATTR_GROUP, ATTR_ICON, ATTR_LEVEL, ATTR_SOUND, ATTR_URL, DATA_BARK

_LOGGER = logging.getLogger(__name__)


def get_service(hass, config, discovery_info=None):
    return BarkNotificationService(hass)


class BarkNotificationService(BaseNotificationService):

    def __init__(self, hass):
        """Initialize the service."""
        self.hass = hass

    @property
    def targets(self):
        """Return a dictionary of registered targets."""
        targets = {}
        for name in self.hass.data[DATA_BARK].keys():
            targets[name] = name
        return targets

    def send_message(self, message="", **kwargs):
        if not (targets := kwargs.get(ATTR_TARGET)):
            targets = self.hass.data[DATA_BARK].keys()

        for name in targets:
            if (config := self.hass.data[DATA_BARK].get(name)) is None:
                continue

            params = {}
            params["body"] = message
            params["device_key"] = config[CONF_TOKEN]

            if (
                (title := kwargs.get(ATTR_TITLE)) is not None
                and title != ATTR_TITLE_DEFAULT
            ):
                params[ATTR_TITLE] = title

            if (data := kwargs.get(ATTR_DATA)) is not None:
                if (copy := data.get(ATTR_COPY)) is not None:
                    params[ATTR_COPY] = copy
                    if data.get(ATTR_AUTO_COPY):
                        params[ATTR_AUTO_COPY] = 1
                if (badge := data.get(ATTR_BADGE)) is not None:
                    params[ATTR_BADGE] = badge
                if (purl := data.get(ATTR_URL)) is not None:
                    params[ATTR_URL] = purl
                if (group := data.get(ATTR_GROUP)) is not None:
                    params[ATTR_GROUP] = group
                if (icon := data.get(ATTR_ICON)) is not None:
                    params[ATTR_ICON] = icon
                if (sound := data.get(ATTR_SOUND)) is not None:
                    params[ATTR_SOUND] = sound
                if (level := data.get(ATTR_LEVEL)) is not None:
                    params[ATTR_LEVEL] = level

            try:
                resp = requests.post(
                    url=config[CONF_HOST] + "/push",
                    json=params
                )

                result = resp.json()
                if result.get("code") != 200:
                    _LOGGER.warning(result)
            except Exception as e:
                _LOGGER.error(e)

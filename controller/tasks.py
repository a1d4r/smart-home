import logging
from enum import Flag, auto

from .services import get_controllers_states, save_controller_state
from .models import Setting

logger = logging.getLogger(__name__)


class SmartHomeSettings:
    """Class representing Smart Home user settings."""
    def __init__(self):
        self.settings = {setting.controller_name: setting.value for setting in Setting.objects.all()}
        for setting in self.settings:
            if setting.endswith('light'):
                self.settings[setting] = bool(self.settings[setting])
        logger.debug(f'Settings: {self.settings}')

    def __getattr__(self, item):
        return self.settings[item]


class ControllerStates:
    """Class representing Smart Home controllers states."""
    READ_ONLY = {
        'leak_detector', 'outdoor_light', 'smoke_detector',
        'bedroom_temperature', 'boiler_temperature',
    }

    def __init__(self):
        self.states = get_controllers_states()

    def save(self):
        logger.debug(f'States: {self.states}')
        states_to_save = {state: value
                          for state, value in self.states.items()
                          if state not in self.READ_ONLY}
        save_controller_state(states_to_save)

    def __getattr__(self, item):
        return self.__dict__['states'][item]

    def __setattr__(self, key, value):
        """Set attr with constraints."""
        if key == 'states':
            return super().__setattr__(key, value)
        if not (
            # Do not open water if leak was detected
            key == 'cold_water' and value == True and self.leak_detector == True
            or key == 'hot_water' and value == True and self.leak_detector == True
            # Do not turn on boiler and washing machine if there is no cold water
            or key == 'boiler' and value == True and self.cold_water == False
            or key == 'washing_machine' and value == 'on' and self.cold_water == False
            # Do not control curtains if there are on manual control
            or key == 'curtains' and self.curtains == 'slightly_open'
            # Do not turn on devices if smoke was detected
            or key == 'air_conditioner' and value == True and self.smoke_detector == True
            or key == 'bedroom_light' and value == True and self.smoke_detector == True
            or key == 'bathroom_light' and value == True and self.smoke_detector == True
            or key == 'boiler' and value == True and self.smoke_detector == True
            or key == 'washing_machine' and value == 'on' and self.smoke_detector == True
        ):
            self.states[key] = value


class SmartHomeManager:
    """Manager for Smart Home reacting to events."""
    def __init__(self):
        self.states = ControllerStates()
        self.settings = SmartHomeSettings()
        # for some reasons boiler temperature might not be returned by API
        if not self.states.boiler_temperature:
            self.states.boiler_temperature = self.settings.hot_water_target_temperature

    def update_states(self):
        """Update controllers state and user settings."""
        self.__init__()

    def save_states(self):
        """Save controller states to react to events."""
        self.states.save()

    def check_events(self):
        """Check all controller states and react to events."""
        self.sync_lights()
        self.check_water_leak()
        self.check_cold_water_closed()
        self.control_boiler()
        self.control_curtains()
        self.check_smoke()
        self.control_conditioner()

    def sync_lights(self):
        """Sync room lights with the ones set by an user."""
        self.states.bedroom_light = self.settings.bedroom_light
        self.states.bathroom_light = self.settings.bathroom_light

    def check_water_leak(self):
        """If there is a water leak, close water valves."""
        if self.states.leak_detector:
            self.states.cold_water = False
            self.states.hot_water = False
            # TODO: Send a mail

    def check_cold_water_closed(self):
        """If the cold water is closed, turn off the boiler and washing machine."""
        if not self.states.cold_water:
            self.states.boiler = False
            self.states.washing_machine = 'off'

    def control_boiler(self):
        """Turn on/off boiler depending on the hot water temperature"""
        if self.states.boiler_temperature < 0.9 * self.settings.hot_water_target_temperature:
            self.states.boiler = True
        if self.states.boiler_temperature > 1.1 * self.settings.hot_water_target_temperature:
            self.states.boiler = False

    def control_curtains(self):
        """Open/Close curtains depending on the light inside and outside the house."""
        if self.states.outdoor_light < 50 and not self.states.bedroom_light:
            self.states.curtains = 'open'
        if self.states.outdoor_light > 50 or self.states.bedroom_light:
            self.states.curtains = 'close'

    def check_smoke(self):
        """Turn all all the devices if the smoke was detected."""
        if self.states.smoke_detector:
            self.states.air_conditioner = False
            self.states.bedroom_light = False
            self.states.bathroom_light = False
            self.states.boiler = False
            self.states.washing_machine = 'off'

    def control_conditioner(self):
        """Turn on/off air conditioner depending on the bedroom temperature"""
        if self.states.bedroom_temperature < 0.9 * self.settings.bedroom_target_temperature:
            self.states.air_conditioner = True
        if self.states.bedroom_temperature > 1.1 * self.settings.bedroom_target_temperature:
            self.states.air_conditioner = False

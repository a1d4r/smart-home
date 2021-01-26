from .services import get_controllers_state


from .models import Setting


class ControllerStates:
    """Class representing Smart Home controllers states."""
    def __init__(self):
        self.states = get_controllers_state()

    def __getattr__(self, item):
        return self.states[item]

    def __setattr__(self, key, value):
        """Set attr with constraints."""
        if not (
            # Do not open water if leak was detected
            key == 'cold_water' and value == True and self.leak_detector == True
            or key == 'hot_water' and value == True and self.leak_detector == True
            # Do not turn on boiler and washing machine if there is no cold water
            or key == 'boiler' and value == True and self.cold_water == False
            or key == 'washing_machine' and value == True and self.cold_water == False
            # Do not control curtains if there are on manual control
            or key == 'curtains' and self.curtains == 'slightly_open'
            # Do not turn on devices if smoke was detected
            or key == 'air_conditioner' and value == True and self.smoke_detector == True
            or key == 'bedroom_light' and value == True and self.smoke_detector == True
            or key == 'bathroom_light' and value == True and self.smoke_detector == True
            or key == 'boiler' and value == True and self.smoke_detector == True
            or key == 'washing_machine' and value == True and self.smoke_detector == True
        ):
            self.states['key'] = value


class SmartHomeSettings:
    """Class representing Smart Home user settings."""
    def __init__(self):
        self.settings = {setting.controller_name: setting.value for setting in Setting.objects.all()}

    def __getattr__(self, item):
        return self.settings[item]


class SmartHomeManager:
    """Manager for Smart Home reacting to events."""
    def __init__(self):
        self.states = ControllerStates()
        self.settings = SmartHomeSettings()

    def update_states(self):
        """Update controllers state and user settings."""
        self.__init__()

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
            self.states.washing_machine = False

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
            self.states.washing_machine = False

    def control_conditioner(self):
        """Turn on/off air conditioner depending on the bedroom temperature"""
        if self.states.bedroom_temperature < 0.9 * self.settings.bedroom_target_temperature:
            self.states.air_conditioner = True
        if self.states.bedroom_temperature > 1.1 * self.settings.bedroom_target_temperature:
            self.states.air_conditioner = False

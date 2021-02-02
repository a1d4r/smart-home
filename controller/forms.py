from django import forms
from crispy_forms import helper, layout

from .models import Setting
from .tasks import SmartHomeManager


class ControllerForm(forms.Form):
    bedroom_target_temperature = forms.IntegerField(
        min_value=16, max_value=50, label='Bedroom target temperature', required=True)
    hot_water_target_temperature = forms.IntegerField(
        min_value=24, max_value=80, label='Hot water target temperature', required=True)
    bedroom_light = forms.BooleanField(label='Bedroom light', required=False)
    bathroom_light = forms.BooleanField(label='Bathroom light', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(layout.Submit('submit', 'Save'))

    def save(self):
        for controller_name, value in self.cleaned_data.items():
            setting = Setting.objects.get(controller_name=controller_name)
            setting.value = value
            setting.save()
        manager = SmartHomeManager()
        manager.check_events()
        manager.save_states()


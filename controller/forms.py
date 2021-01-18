from django import forms
from crispy_forms import helper, layout


class ControllerForm(forms.Form):
    bedroom_target_temperature = forms.IntegerField(
        min_value=16, max_value=50, label='Bedroom target temperature', initial=21)
    hot_water_target_temperature = forms.IntegerField(
        min_value=24, max_value=80, label='Hot water target temperature', initial=80)
    bedroom_light = forms.BooleanField(label='Bedroom light')
    bathroom_light = forms.BooleanField(label='Bathroom light')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(layout.Submit('submit', 'Save'))

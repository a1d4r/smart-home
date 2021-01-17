from django import forms


class ControllerForm(forms.Form):
    bedroom_target_temperature = forms.IntegerField(
        min_value=16, max_value=50, label='Bedroom target temperature', initial=21)
    hot_water_target_temperature = forms.IntegerField(
        min_value=24, max_value=80, label='Hot water target temperature', initial=80)
    bedroom_light = forms.BooleanField(label='Bedroom light')
    bathroom_light = forms.BooleanField(label='Bathroom light')

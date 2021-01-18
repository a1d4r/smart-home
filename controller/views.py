from django.http import HttpResponse
from django.shortcuts import render

from .services import get_controllers_state
from .forms import ControllerForm
from .models import Setting


def controller(request):
    if request.method == 'POST':
        form = ControllerForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
        else:
            print('invalid form')
    else:
        settings = Setting.objects.all()
        form_data = {setting.controller_name: setting.value for setting in settings}
        form = ControllerForm(form_data)
    data = get_controllers_state()
    return render(request, 'controller/control.html',
                  context={'data': data, 'form': form})

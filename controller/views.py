from django.http import HttpResponse
from django.shortcuts import render

from .services import get_controllers_state
from .forms import ControllerForm


def controller(request):
    data = get_controllers_state()
    form = ControllerForm()
    return render(request, 'controller/control.html',
                  context={'data': data, 'form': form})

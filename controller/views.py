from django.http import HttpResponse
from django.shortcuts import render

from .services import get_controllers_state


def controller(request):
    data = get_controllers_state()
    return render(request, 'controller/control.html', context={'data': data})

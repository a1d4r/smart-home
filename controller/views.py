import logging
from django.shortcuts import render

from .services import get_controllers_states
from .forms import ControllerForm
from .models import Setting

logger = logging.getLogger(__name__)


def controller(request):
    if request.method == 'POST':
        form = ControllerForm(request.POST)
        if form.is_valid():
            logger.info(f'Accept form with data: {form.cleaned_data}')
            form.save()
        else:
            logger.info(f'Invalid form: {form.errors}')
    else:
        settings = Setting.objects.all()
        form_data = {setting.controller_name: setting.value for setting in settings}
        form = ControllerForm(form_data)
    data = get_controllers_states()
    context = {'data': get_controllers_states(), 'form': form}
    return render(request, 'controller/control.html', context=context)

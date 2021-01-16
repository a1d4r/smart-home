from django.http import HttpResponse
from django.shortcuts import render


def controller(request):
    return HttpResponse('Controller')

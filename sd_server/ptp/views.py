# Create your views here.
from django.shortcuts import render

def index(request):
    context = {}
    return render(request, 'index.html', context)


def ptp_index(request):
    context = {}
    return render(request, 'ptp/index.html', context)
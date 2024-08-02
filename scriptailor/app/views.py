# django_project/django_app/views.py
import requests
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest

def home(request):
    return render(request, 'home.html')


def flask_proxy(request):
    flask_url = 'http://127.0.0.1:5000' + request.path
    if request.method == 'POST':
        response = requests.post(flask_url, json=request.POST)
    else:
        response = requests.get(flask_url)
    return JsonResponse(response.json())



# Create your views here.

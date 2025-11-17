from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
def home( request ):
    return HttpResponse ('Un film pour les controler tous !')

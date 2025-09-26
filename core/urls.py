# Put the API adress here
from django.urls import path
from .api import generateResponseView

urlpatterns = [
    path('generate-response/', generateResponseView.as_view(), name='generate-response'),
]


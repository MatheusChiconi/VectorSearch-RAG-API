# Put the API adress here
from django.urls import path
from .api import generateResponseView

urlpatterns = [
    # API endpoints

    # api/generate-response/
    path('generate-response/', generateResponseView.as_view(), name='generate-response'),
]


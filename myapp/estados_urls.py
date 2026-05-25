from django.urls import path

from .views import (
    cilindro_view)

urlpatterns = [
        path('estados/', cilindro_view, name='cilindro'),
]
from django.urls import path

from .views_agua_estado import (
    cilindro_view)

urlpatterns = [
        path('estados/', cilindro_view, name='cilindro'),
]
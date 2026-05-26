from django.urls import path

from .views_agua_estado import (
    estado_view)

urlpatterns = [
        path('estados/', estado_view, name='estado'),
]
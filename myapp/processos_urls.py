from django.urls import path

from .views_gas_prop import (
    processo_view)

urlpatterns = [
        path('processos/', processo_view, name='processo'),
]
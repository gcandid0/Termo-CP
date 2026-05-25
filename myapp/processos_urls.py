from django.urls import path

from .views_gas_prop import (
    gasideal_view)

urlpatterns = [
        path('processos/', gasideal_view, name='gasideal'),
]
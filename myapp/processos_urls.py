from django.urls import path

from .views6 import (
    gasideal_view)

urlpatterns = [
        path('processos/', gasideal_view, name='gasideal'),
]
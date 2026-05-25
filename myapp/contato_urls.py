from django.urls import path

from .views_agua_estado import (
    contato_view)

urlpatterns = [
        path('contato/', contato_view, name='contato'),
]
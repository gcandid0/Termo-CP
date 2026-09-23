from django.urls import path

from .views_agua_estado import (
    ajuda_view)

urlpatterns = [
        path('ajuda/', ajuda_view, name='ajuda'),
]

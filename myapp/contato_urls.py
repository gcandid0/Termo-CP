from django.urls import path

from .views import (
    contato_view)

urlpatterns = [
        path('contato/', contato_view, name='contato'),
]
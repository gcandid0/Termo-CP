# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, agua_cls, subs_cls
from .views_unified import (
    ajuda_view,
    contato_view,
    estado_view,
    get_registered_views,
    homepage_view,
    sobre_view,
)


def processos_view(request):
    return render(request, 'processos.html')


(
    ask_known1_view,
    ask_known2_view,
    process_values_view,
    error_value_view,
    error_type_view7,
) = get_registered_views(1, 'estado')

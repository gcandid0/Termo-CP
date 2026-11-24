# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view18(request):
    return render(request, 'processos4.html')


(
    ask_known1_view18,
    ask_known2_view18,
    process_values_view18,
    error_value_view18,
    error_type_view7,
) = get_registered_views(3, 'estado')

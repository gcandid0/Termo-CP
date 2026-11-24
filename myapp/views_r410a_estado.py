# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view23(request):
    return render(request, 'processos5.html')


(
    ask_known1_view23,
    ask_known2_view23,
    process_values_view23,
    error_value_view23,
    error_type_view7,
) = get_registered_views(4, 'estado')

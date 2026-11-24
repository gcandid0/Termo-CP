# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view13(request):
    return render(request, 'processos3.html')


(
    ask_known1_view13,
    ask_known2_view13,
    process_values_view13,
    error_value_view13,
    error_type_view7,
) = get_registered_views(2, 'estado')

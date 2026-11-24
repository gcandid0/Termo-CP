# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view38(request):
    return render(request, 'processos8.html')


(
    ask_known1_view38,
    ask_known2_view38,
    process_values_view38,
    error_value_view38,
    error_type_view7,
) = get_registered_views(7, 'estado')

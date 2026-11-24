# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view24(request):
    return render(request, 'processos6.html')


(
    ask_known1_view24,
    ask_known2_view24,
    process_values_view24,
    error_value_view24,
    error_type_view7,
) = get_registered_views(4, 'propriedade')

# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view34(request):
    return render(request, 'processos6.html')


(
    ask_known1_view34,
    ask_known2_view34,
    process_values_view34,
    error_value_view34,
    error_type_view7,
) = get_registered_views(6, 'propriedade')

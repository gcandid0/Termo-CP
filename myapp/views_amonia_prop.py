# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view14(request):
    return render(request, 'processos6.html')


(
    ask_known1_view14,
    ask_known2_view14,
    process_values_view14,
    error_value_view14,
    error_type_view7,
) = get_registered_views(2, 'propriedade')

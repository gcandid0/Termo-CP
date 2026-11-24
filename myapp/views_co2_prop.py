# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view19(request):
    return render(request, 'processos6.html')


(
    ask_known1_view19,
    ask_known2_view19,
    process_values_view19,
    error_value_view19,
    error_type_view7,
) = get_registered_views(3, 'propriedade')

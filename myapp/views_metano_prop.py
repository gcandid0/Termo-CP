# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view39(request):
    return render(request, 'processos6.html')


(
    ask_known1_view39,
    ask_known2_view39,
    process_values_view39,
    error_value_view39,
    error_type_view7,
) = get_registered_views(7, 'propriedade')

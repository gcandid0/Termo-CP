# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view33(request):
    return render(request, 'processos7.html')


(
    ask_known1_view33,
    ask_known2_view33,
    process_values_view33,
    error_value_view33,
    error_type_view7,
) = get_registered_views(6, 'estado')

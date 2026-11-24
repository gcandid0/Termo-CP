# -*- coding: utf-8 -*-
from django.shortcuts import render
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views


def processos_view29(request):
    return render(request, 'processos6.html')


(
    ask_known1_view29,
    ask_known2_view29,
    process_values_view29,
    error_value_view29,
    error_type_view7,
) = get_registered_views(5, 'propriedade')

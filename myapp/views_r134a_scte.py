# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view31,
    ask_known1_view31,
    ask_known2_view31,
    ask_known3_view31,
    process_values_view31,
    error_value_view31,
    error_type_view31,
) = get_registered_views(5, 'scte')
error_type_view7 = error_type_view31

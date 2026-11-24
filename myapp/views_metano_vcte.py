# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view42,
    ask_known1_view42,
    ask_known2_view42,
    ask_known3_view42,
    ask_known4_view42,
    process_values_view42,
    error_value_view42,
    error_type_view42,
) = get_registered_views(7, 'vcte')
error_type_view7 = error_type_view42

# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view40,
    ask_known1_view40,
    ask_known2_view40,
    ask_known3_view40,
    ask_known4_view40,
    process_values_view40,
    error_value_view40,
    error_type_view40,
) = get_registered_views(7, 'pcte')
error_type_view7 = error_type_view40

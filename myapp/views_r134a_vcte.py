# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view32,
    ask_known1_view32,
    ask_known2_view32,
    ask_known3_view32,
    ask_known4_view32,
    process_values_view32,
    error_value_view32,
    error_type_view32,
) = get_registered_views(5, 'vcte')
error_type_view7 = error_type_view32

# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view25,
    ask_known1_view25,
    ask_known2_view25,
    ask_known3_view25,
    ask_known4_view25,
    process_values_view25,
    error_value_view25,
    error_type_view25,
) = get_registered_views(4, 'pcte')
error_type_view7 = error_type_view25

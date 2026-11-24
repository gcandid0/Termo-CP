# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view15,
    ask_known1_view15,
    ask_known2_view15,
    ask_known3_view15,
    ask_known4_view15,
    process_values_view15,
    error_value_view15,
    error_type_view15,
) = get_registered_views(2, 'pcte')
error_type_view7 = error_type_view15

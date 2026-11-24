# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view35,
    ask_known1_view35,
    ask_known2_view35,
    ask_known3_view35,
    ask_known4_view35,
    process_values_view35,
    error_value_view35,
    error_type_view35,
) = get_registered_views(6, 'pcte')
error_type_view7 = error_type_view35

# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view20,
    ask_known1_view20,
    ask_known2_view20,
    ask_known3_view20,
    ask_known4_view20,
    process_values_view20,
    error_value_view20,
    error_type_view20,
) = get_registered_views(3, 'pcte')
error_type_view7 = error_type_view20

# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view30,
    ask_known1_view30,
    ask_known2_view30,
    ask_known3_view30,
    ask_known4_view30,
    process_values_view30,
    error_value_view30,
    error_type_view30,
) = get_registered_views(5, 'pcte')
error_type_view7 = error_type_view30

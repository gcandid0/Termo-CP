# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, agua_cls, subs_cls
from .views_unified import get_registered_views

(
    homepage_view3,
    ask_known1_view3,
    ask_known2_view3,
    ask_known3_view3,
    ask_known4_view3,
    process_values_view3,
    error_value_view3,
    error_type_view3,
) = get_registered_views(1, 'pcte')

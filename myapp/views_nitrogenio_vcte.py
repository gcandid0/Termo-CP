# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view37,
    ask_known1_view37,
    ask_known2_view37,
    ask_known3_view37,
    ask_known4_view37,
    process_values_view37,
    error_value_view37,
    error_type_view37,
) = get_registered_views(6, 'vcte')
error_type_view7 = error_type_view37

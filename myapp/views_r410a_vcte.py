# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view27,
    ask_known1_view27,
    ask_known2_view27,
    ask_known3_view27,
    ask_known4_view27,
    process_values_view27,
    error_value_view27,
    error_type_view27,
) = get_registered_views(4, 'vcte')
error_type_view7 = error_type_view27

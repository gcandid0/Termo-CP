# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view17,
    ask_known1_view17,
    ask_known2_view17,
    ask_known3_view17,
    ask_known4_view17,
    process_values_view17,
    error_value_view17,
    error_type_view17,
) = get_registered_views(2, 'vcte')
error_type_view7 = error_type_view17

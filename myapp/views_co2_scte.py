# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view21,
    ask_known1_view21,
    ask_known2_view21,
    ask_known3_view21,
    process_values_view21,
    error_value_view21,
    error_type_view21,
) = get_registered_views(3, 'scte')
error_type_view7 = error_type_view21

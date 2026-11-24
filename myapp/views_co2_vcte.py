# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view22,
    ask_known1_view22,
    ask_known2_view22,
    ask_known3_view22,
    ask_known4_view22,
    process_values_view22,
    error_value_view22,
    error_type_view22,
) = get_registered_views(3, 'vcte')
error_type_view7 = error_type_view22

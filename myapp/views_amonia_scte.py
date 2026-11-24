# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view16,
    ask_known1_view16,
    ask_known2_view16,
    ask_known3_view16,
    process_values_view16,
    error_value_view16,
    error_type_view16,
) = get_registered_views(2, 'scte')
error_type_view7 = error_type_view16

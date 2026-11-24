# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view41,
    ask_known1_view41,
    ask_known2_view41,
    ask_known3_view41,
    process_values_view41,
    error_value_view41,
    error_type_view41,
) = get_registered_views(7, 'scte')
error_type_view7 = error_type_view41

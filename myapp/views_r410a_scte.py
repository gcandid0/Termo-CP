# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, subs_cls
from .views_unified import get_registered_views

(
    homepage_view26,
    ask_known1_view26,
    ask_known2_view26,
    ask_known3_view26,
    process_values_view26,
    error_value_view26,
    error_type_view26,
) = get_registered_views(4, 'scte')
error_type_view7 = error_type_view26

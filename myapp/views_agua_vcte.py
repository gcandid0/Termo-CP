# -*- coding: utf-8 -*-
from .thermo_engine import BoundariesException, TituloException, agua_cls, subs_cls
from .views_unified import get_registered_views

(
    homepage_view5,
    ask_known1_view5,
    ask_known2_view5,
    ask_known3_view5,
    ask_known4_view5,
    process_values_view5,
    error_value_view5,
    error_type_view5,
) = get_registered_views(1, 'vcte')

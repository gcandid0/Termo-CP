from django.urls import path

from .views_r410a_estado import (
    ask_known1_view23,
    ask_known2_view23,
    process_values_view23,
    error_value_view23,
    processos_view23,
)

from .views_r410a_prop import (
    ask_known1_view24,
    ask_known2_view24,
    process_values_view24,
    error_value_view24,
    error_type_view7
)

from .views_r410a_pcte import (
    ask_known1_view25,
    ask_known2_view25,
    ask_known3_view25,
    ask_known4_view25,
    process_values_view25,
    error_value_view25,
)

from .views_r410a_scte import (
    ask_known1_view26,
    ask_known2_view26,
    ask_known3_view26,
    process_values_view26,
    error_value_view26,
)

from .views_r410a_vcte import (
    ask_known1_view27,
    ask_known2_view27,
    ask_known3_view27,
    ask_known4_view27,
    process_values_view27,
    error_value_view27,
)

urlpatterns = [
    # --- VIEWS 23 (R410A - Estado) ---
    path('R410A-estado-1/', ask_known1_view23, name='ask_known1_23'),
    path('R410A-estado-2/', ask_known2_view23, name='ask_known2_23'),
    path('R410A-estado-resultados/', process_values_view23, name='process_values_23'),
    path('processos-R410A/', processos_view23, name='processos5'),

    # --- VIEWS 24 (R410A - Propridades) ---
    path('R410A-propriedade-1/', ask_known1_view24, name='ask_known1_24'),
    path('R410A-propriedade-2/', ask_known2_view24, name='ask_known2_24'),
    path('R410A-propriedade-resultados/', process_values_view24, name='process_values_24'),

    # --- VIEWS 25 (R410A - Pcte) ---
    path('R410A-pcte-1/', ask_known1_view25, name='ask_known1_25'),
    path('R410A-pcte-2/', ask_known2_view25, name='ask_known2_25'),
    path('R410A-pcte-3/', ask_known3_view25, name='ask_known3_25'),
    path('R410A-pcte-4/', ask_known4_view25, name='ask_known4_25'),
    path('R410A-pcte-resultados/', process_values_view25, name='process_values_25'),

    # --- VIEWS 26 (R410A - Scte) ---
    path('R410A-scte-1/', ask_known1_view26, name='ask_known1_26'),
    path('R410A-scte-2/', ask_known2_view26, name='ask_known2_26'),
    path('R410A-scte-3/', ask_known3_view26, name='ask_known3_26'),
    path('R410A-scte-resultados/', process_values_view26, name='process_values_26'),

    # --- VIEWS 27 (R410A - vcte) ---
    path('R410A-vcte-1/', ask_known1_view27, name='ask_known1_27'),
    path('R410A-vcte-2/', ask_known2_view27, name='ask_known2_27'),
    path('R410A-vcte-3/', ask_known3_view27, name='ask_known3_27'),
    path('R410A-vcte-4/', ask_known4_view27, name='ask_known4_27'),
    path('R410A-vcte-resultados/', process_values_view27, name='process_values_27'),

    # --- Tratamento de Erros ---
    path('error-value/23/', error_value_view23, name='error_value_23'),
    path('error-value/25/', error_value_view25, name='error_value_25'),
    path('error-type/7/', error_type_view7, name='error_type_7'),
    path('error-value/24/', error_value_view24, name='error_value_24'),
    path('error-type/25/', error_type_view7, name='error_type_25'),
    path('error-value/26/', error_value_view26, name='error_value_26'),
    path('error-type/26/', error_type_view7, name='error_type_26'),
    path('error-value/27/', error_value_view27, name='error_value_27'),
    path('error-type/27/', error_type_view7, name='error_type_27'),
]
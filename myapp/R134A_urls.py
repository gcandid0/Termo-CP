from django.urls import path

from .views28 import (
    ask_known1_view28,
    ask_known2_view28,
    process_values_view28,
    error_value_view28,
    processos_view28,
)

from .views29 import (
    ask_known1_view29,
    ask_known2_view29,
    process_values_view29,
    error_value_view29,
    error_type_view7
)

from .views30 import (
    ask_known1_view30,
    ask_known2_view30,
    ask_known3_view30,
    ask_known4_view30,
    process_values_view30,
    error_value_view30,
)

from .views31 import (
    ask_known1_view31,
    ask_known2_view31,
    ask_known3_view31,
    process_values_view31,
    error_value_view31,
)

from .views32 import (
    ask_known1_view32,
    ask_known2_view32,
    ask_known3_view32,
    ask_known4_view32,
    process_values_view32,
    error_value_view32,
)

urlpatterns = [
    # --- VIEWS 28 (R134A - Estado) ---
    path('R134A-estado-1/', ask_known1_view28, name='ask_known1_28'),
    path('R134A-estado-2/', ask_known2_view28, name='ask_known2_28'),
    path('R134A-estado-resultados/', process_values_view28, name='process_values_28'),
    path('processos-R134A/', processos_view28, name='processos6'),

    # --- VIEWS 29 (R134A - Propridades) ---
    path('R134A-propriedade-1/', ask_known1_view29, name='ask_known1_29'),
    path('R134A-propriedade-2/', ask_known2_view29, name='ask_known2_29'),
    path('R134A-propriedade-resultados/', process_values_view29, name='process_values_29'),

    # --- VIEWS 30 (R134A - Pcte) ---
    path('R134A-pcte-1/', ask_known1_view30, name='ask_known1_30'),
    path('R134A-pcte-2/', ask_known2_view30, name='ask_known2_30'),
    path('R134A-pcte-3/', ask_known3_view30, name='ask_known3_30'),
    path('R134A-pcte-4/', ask_known4_view30, name='ask_known4_30'),
    path('R134A-pcte-resultados/', process_values_view30, name='process_values_30'),

    # --- VIEWS 31 (R134A - Scte) ---
    path('R134A-scte-1/', ask_known1_view31, name='ask_known1_31'),
    path('R134A-scte-2/', ask_known2_view31, name='ask_known2_31'),
    path('R134A-scte-3/', ask_known3_view31, name='ask_known3_31'),
    path('R134A-scte-resultados/', process_values_view31, name='process_values_31'),

    # --- VIEWS 32 (R134A - vcte) ---
    path('R134A-vcte-1/', ask_known1_view32, name='ask_known1_32'),
    path('R134A-vcte-2/', ask_known2_view32, name='ask_known2_32'),
    path('R134A-vcte-3/', ask_known3_view32, name='ask_known3_32'),
    path('R134A-vcte-4/', ask_known4_view32, name='ask_known4_32'),
    path('R134A-vcte-resultados/', process_values_view32, name='process_values_32'),

    # --- Tratamento de Erros ---
    path('error-value/28/', error_value_view28, name='error_value_28'),
    path('error-value/30/', error_value_view30, name='error_value_30'),
    path('error-type/7/', error_type_view7, name='error_type_7'),
    path('error-value/29/', error_value_view29, name='error_value_29'),
    path('error-type/30/', error_type_view7, name='error_type_30'),
    path('error-value/31/', error_value_view31, name='error_value_31'),
    path('error-type/31/', error_type_view7, name='error_type_31'),
    path('error-value/32/', error_value_view32, name='error_value_32'),
    path('error-type/32/', error_type_view7, name='error_type_32'),
]
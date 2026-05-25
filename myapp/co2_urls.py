from django.urls import path

from .views_co2_estado import (
    ask_known1_view18,
    ask_known2_view18,
    process_values_view18,
    error_value_view18,
    processos_view18,
)

from .views_co2_prop import (
    ask_known1_view19,
    ask_known2_view19,
    process_values_view19,
    error_value_view19,
    error_type_view7
)

from .views_co2_pcte import (
    ask_known1_view20,
    ask_known2_view20,
    ask_known3_view20,
    ask_known4_view20,
    process_values_view20,
    error_value_view20,
)

from .views_co2_scte import (
    ask_known1_view21,
    ask_known2_view21,
    ask_known3_view21,
    process_values_view21,
    error_value_view21,
)

from .views_co2_vcte import (
    ask_known1_view22,
    ask_known2_view22,
    ask_known3_view22,
    ask_known4_view22,
    process_values_view22,
    error_value_view22,
)

urlpatterns = [
    # --- VIEWS 18 (CO2 - Estado) ---
    path('co2-estado-1/', ask_known1_view18, name='ask_known1_18'),
    path('co2-estado-2/', ask_known2_view18, name='ask_known2_18'),
    path('co2-estado-resultados/', process_values_view18, name='process_values_18'),
    path('processos-co2/', processos_view18, name='processos4'),

    # --- VIEWS 19 (CO2 - Propridades) ---
    path('co2-propriedade-1/', ask_known1_view19, name='ask_known1_19'),
    path('co2-propriedade-2/', ask_known2_view19, name='ask_known2_19'),
    path('co2-propriedade-resultados/', process_values_view19, name='process_values_19'),

    # --- VIEWS 20 (CO2 - Pcte) ---
    path('co2-pcte-1/', ask_known1_view20, name='ask_known1_20'),
    path('co2-pcte-2/', ask_known2_view20, name='ask_known2_20'),
    path('co2-pcte-3/', ask_known3_view20, name='ask_known3_20'),
    path('co2-pcte-4/', ask_known4_view20, name='ask_known4_20'),
    path('co2-pcte-resultados/', process_values_view20, name='process_values_20'),

    # --- VIEWS 21 (CO2 - Scte) ---
    path('co2-scte-1/', ask_known1_view21, name='ask_known1_21'),
    path('co2-scte-2/', ask_known2_view21, name='ask_known2_21'),
    path('co2-scte-3/', ask_known3_view21, name='ask_known3_21'),
    path('co2-scte-resultados/', process_values_view21, name='process_values_21'),

    # --- VIEWS 22 (CO2 - vcte) ---
    path('co2-vcte-1/', ask_known1_view22, name='ask_known1_22'),
    path('co2-vcte-2/', ask_known2_view22, name='ask_known2_22'),
    path('co2-vcte-3/', ask_known3_view22, name='ask_known3_22'),
    path('co2-vcte-4/', ask_known4_view22, name='ask_known4_22'),
    path('co2-vcte-resultados/', process_values_view22, name='process_values_22'),

    # --- Tratamento de Erros ---
    path('error-value/18/', error_value_view18, name='error_value_18'),
    path('error-value/20/', error_value_view20, name='error_value_20'),
    path('error-type/7/', error_type_view7, name='error_type_7'),
    path('error-value/19/', error_value_view19, name='error_value_19'),
    path('error-type/20/', error_type_view7, name='error_type_20'),
    path('error-value/21/', error_value_view21, name='error_value_21'),
    path('error-type/21/', error_type_view7, name='error_type_21'),
    path('error-value/22/', error_value_view22, name='error_value_22'),
    path('error-type/22/', error_type_view7, name='error_type_22'),
]
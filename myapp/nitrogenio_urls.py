from django.urls import path

from .views33 import (
    ask_known1_view33,
    ask_known2_view33,
    process_values_view33,
    error_value_view33,
    processos_view33,
)

from .views34 import (
    ask_known1_view34,
    ask_known2_view34,
    process_values_view34,
    error_value_view34,
    error_type_view7
)

from .views35 import (
    ask_known1_view35,
    ask_known2_view35,
    ask_known3_view35,
    ask_known4_view35,
    process_values_view35,
    error_value_view35,
)

from .views36 import (
    ask_known1_view36,
    ask_known2_view36,
    ask_known3_view36,
    process_values_view36,
    error_value_view36,
)

from .views37 import (
    ask_known1_view37,
    ask_known2_view37,
    ask_known3_view37,
    ask_known4_view37,
    process_values_view37,
    error_value_view37,
)

urlpatterns = [
    # --- VIEWS 33 (nitrogenio - Estado) ---
    path('nitrogenio-estado-1/', ask_known1_view33, name='ask_known1_33'),
    path('nitrogenio-estado-2/', ask_known2_view33, name='ask_known2_33'),
    path('nitrogenio-estado-resultados/', process_values_view33, name='process_values_33'),
    path('processos-nitrogenio/', processos_view33, name='processos7'),

    # --- VIEWS 34 (nitrogenio - Propridades) ---
    path('nitrogenio-propriedade-1/', ask_known1_view34, name='ask_known1_34'),
    path('nitrogenio-propriedade-2/', ask_known2_view34, name='ask_known2_34'),
    path('nitrogenio-propriedade-resultados/', process_values_view34, name='process_values_34'),

    # --- VIEWS 35 (nitrogenio - Pcte) ---
    path('nitrogenio-pcte-1/', ask_known1_view35, name='ask_known1_35'),
    path('nitrogenio-pcte-2/', ask_known2_view35, name='ask_known2_35'),
    path('nitrogenio-pcte-3/', ask_known3_view35, name='ask_known3_35'),
    path('nitrogenio-pcte-4/', ask_known4_view35, name='ask_known4_35'),
    path('nitrogenio-pcte-resultados/', process_values_view35, name='process_values_35'),

    # --- VIEWS 36 (nitrogenio - Scte) ---
    path('nitrogenio-scte-1/', ask_known1_view36, name='ask_known1_36'),
    path('nitrogenio-scte-2/', ask_known2_view36, name='ask_known2_36'),
    path('nitrogenio-scte-3/', ask_known3_view36, name='ask_known3_36'),
    path('nitrogenio-scte-resultados/', process_values_view36, name='process_values_36'),

    # --- VIEWS 37 (nitrogenio - vcte) ---
    path('nitrogenio-vcte-1/', ask_known1_view37, name='ask_known1_37'),
    path('nitrogenio-vcte-2/', ask_known2_view37, name='ask_known2_37'),
    path('nitrogenio-vcte-3/', ask_known3_view37, name='ask_known3_37'),
    path('nitrogenio-vcte-4/', ask_known4_view37, name='ask_known4_37'),
    path('nitrogenio-vcte-resultados/', process_values_view37, name='process_values_37'),

    # --- Tratamento de Erros ---
    path('error-value/33/', error_value_view33, name='error_value_33'),
    path('error-value/35/', error_value_view35, name='error_value_35'),
    path('error-type/7/', error_type_view7, name='error_type_7'),
    path('error-value/34/', error_value_view34, name='error_value_34'),
    path('error-type/35/', error_type_view7, name='error_type_35'),
    path('error-value/36/', error_value_view36, name='error_value_36'),
    path('error-type/36/', error_type_view7, name='error_type_36'),
    path('error-value/37/', error_value_view37, name='error_value_37'),
    path('error-type/37/', error_type_view7, name='error_type_37'),
]
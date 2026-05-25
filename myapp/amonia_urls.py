from django.urls import path

from .views_amonia_estado import (
    ask_known1_view13,
    ask_known2_view13,
    process_values_view13,
    error_value_view13,
    processos_view13,
)

from .views_amonia_prop import (
    ask_known1_view14,
    ask_known2_view14,
    process_values_view14,
    error_value_view14,
    error_type_view7
)

from .views_amonia_pcte import (
    ask_known1_view15,
    ask_known2_view15,
    ask_known3_view15,
    ask_known4_view15,
    process_values_view15,
    error_value_view15,
)

from .views_amonia_scte import (
    ask_known1_view16,
    ask_known2_view16,
    ask_known3_view16,
    process_values_view16,
    error_value_view16,
)

from .views_amonia_vcte import (
    ask_known1_view17,
    ask_known2_view17,
    ask_known3_view17,
    ask_known4_view17,
    process_values_view17,
    error_value_view17,
)

urlpatterns = [
    # --- VIEWS 13 (Amônia - Estado) ---
    path('amonia-estado-1/', ask_known1_view13, name='ask_known1_13'),
    path('amonia-estado-2/', ask_known2_view13, name='ask_known2_13'),
    path('amonia-estado-resultados/', process_values_view13, name='process_values_13'),
    path('processos-amonia/', processos_view13, name='processos3'),

    # --- VIEWS 14 (Amônia - Propridades) ---
    path('amonia-propriedade-1/', ask_known1_view14, name='ask_known1_14'),
    path('amonia-propriedade-2/', ask_known2_view14, name='ask_known2_14'),
    path('amonia-propriedade-resultados/', process_values_view14, name='process_values_14'),

    # --- VIEWS 15 (Amônia - Pcte) ---
    path('amonia-pcte-1/', ask_known1_view15, name='ask_known1_15'),
    path('amonia-pcte-2/', ask_known2_view15, name='ask_known2_15'),
    path('amonia-pcte-3/', ask_known3_view15, name='ask_known3_15'),
    path('amonia-pcte-4/', ask_known4_view15, name='ask_known4_15'),
    path('amonia-pcte-resultados/', process_values_view15, name='process_values_15'),

    # --- VIEWS 16 (Amônia - Scte) ---
    path('amonia-scte-1/', ask_known1_view16, name='ask_known1_16'),
    path('amonia-scte-2/', ask_known2_view16, name='ask_known2_16'),
    path('amonia-scte-3/', ask_known3_view16, name='ask_known3_16'),
    path('amonia-scte-resultados/', process_values_view16, name='process_values_16'),

    # --- VIEWS 17 (Amônia - vcte) ---
    path('amonia-vcte-1/', ask_known1_view17, name='ask_known1_17'),
    path('amonia-vcte-2/', ask_known2_view17, name='ask_known2_17'),
    path('amonia-vcte-3/', ask_known3_view17, name='ask_known3_17'),
    path('amonia-vcte-4/', ask_known4_view17, name='ask_known4_17'),
    path('amonia-vcte-resultados/', process_values_view17, name='process_values_17'),

    # --- Tratamento de Erros ---
    path('error-value/13/', error_value_view13, name='error_value_13'),
    path('error-value/15/', error_value_view15, name='error_value_15'),
    path('error-type/7/', error_type_view7, name='error_type_7'),
    path('error-value/14/', error_value_view14, name='error_value_14'),
    path('error-type/15/', error_type_view7, name='error_type_15'),
    path('error-value/16/', error_value_view16, name='error_value_16'),
    path('error-type/16/', error_type_view7, name='error_type_16'),
    path('error-value/17/', error_value_view17, name='error_value_17'),
    path('error-type/17/', error_type_view7, name='error_type_17'),
]
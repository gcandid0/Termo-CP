from django.urls import path

from .views_metano_estado import (
    ask_known1_view38,
    ask_known2_view38,
    process_values_view38,
    error_value_view38,
    processos_view38,
)

from .views_metano_prop import (
    ask_known1_view39,
    ask_known2_view39,
    process_values_view39,
    error_value_view39,
    error_type_view7
)

from .views_metano_pcte import (
    ask_known1_view40,
    ask_known2_view40,
    ask_known3_view40,
    ask_known4_view40,
    process_values_view40,
    error_value_view40,
)

from .views_metano_scte import (
    ask_known1_view41,
    ask_known2_view41,
    ask_known3_view41,
    process_values_view41,
    error_value_view41,
)

from .views_metano_vcte import (
    ask_known1_view42,
    ask_known2_view42,
    ask_known3_view42,
    ask_known4_view42,
    process_values_view42,
    error_value_view42,
)

urlpatterns = [
    # --- VIEWS 38 (metano - Estado) ---
    path('metano-estado-1/', ask_known1_view38, name='ask_known1_38'),
    path('metano-estado-2/', ask_known2_view38, name='ask_known2_38'),
    path('metano-estado-resultados/', process_values_view38, name='process_values_38'),
    path('processos-metano/', processos_view38, name='processos8'),

    # --- VIEWS 39 (metano - Propridades) ---
    path('metano-propriedade-1/', ask_known1_view39, name='ask_known1_39'),
    path('metano-propriedade-2/', ask_known2_view39, name='ask_known2_39'),
    path('metano-propriedade-resultados/', process_values_view39, name='process_values_39'),

    # --- VIEWS 40 (metano - Pcte) ---
    path('metano-pcte-1/', ask_known1_view40, name='ask_known1_40'),
    path('metano-pcte-2/', ask_known2_view40, name='ask_known2_40'),
    path('metano-pcte-3/', ask_known3_view40, name='ask_known3_40'),
    path('metano-pcte-4/', ask_known4_view40, name='ask_known4_40'),
    path('metano-pcte-resultados/', process_values_view40, name='process_values_40'),

    # --- VIEWS 41 (metano - Scte) ---
    path('metano-scte-1/', ask_known1_view41, name='ask_known1_41'),
    path('metano-scte-2/', ask_known2_view41, name='ask_known2_41'),
    path('metano-scte-3/', ask_known3_view41, name='ask_known3_41'),
    path('metano-scte-resultados/', process_values_view41, name='process_values_41'),

    # --- VIEWS 42 (metano - vcte) ---
    path('metano-vcte-1/', ask_known1_view42, name='ask_known1_42'),
    path('metano-vcte-2/', ask_known2_view42, name='ask_known2_42'),
    path('metano-vcte-3/', ask_known3_view42, name='ask_known3_42'),
    path('metano-vcte-4/', ask_known4_view42, name='ask_known4_42'),
    path('metano-vcte-resultados/', process_values_view42, name='process_values_42'),

    # --- Tratamento de Erros ---
    path('error-value/38/', error_value_view38, name='error_value_38'),
    path('error-value/40/', error_value_view40, name='error_value_40'),
    path('error-type/7/', error_type_view7, name='error_type_7'),
    path('error-value/39/', error_value_view39, name='error_value_39'),
    path('error-type/40/', error_type_view7, name='error_type_40'),
    path('error-value/41/', error_value_view41, name='error_value_41'),
    path('error-type/41/', error_type_view7, name='error_type_41'),
    path('error-value/42/', error_value_view42, name='error_value_42'),
    path('error-type/42/', error_type_view7, name='error_type_42'),
]
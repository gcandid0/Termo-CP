from django.urls import path

from .views_agua_estado import (
    homepage_view, ask_known1_view, ask_known2_view, process_values_view,
    error_value_view, error_type_view7, cilindro_view, processos_view,
    sobre_view
)
from .views_agua_pcte import (
    homepage_view3, ask_known1_view3, ask_known2_view3, process_values_view3,
    error_value_view3, error_type_view3, ask_known3_view3, ask_known4_view3
)
from .views_agua_scte import (
    homepage_view4, ask_known3_view4, ask_known1_view4, ask_known2_view4,
    process_values_view4, error_value_view4, error_type_view4
)
from .views_agua_vcte import (
    homepage_view5, ask_known1_view5, ask_known2_view5, process_values_view5,
    error_value_view5, error_type_view5, ask_known3_view5, ask_known4_view5
)

urlpatterns = [
    # --- VIEWS INSTITUCIONAIS ---
    path('', homepage_view, name='homepage'),  # Homepage Principal
    path('sobre/', sobre_view, name='sobre'),   # Nova rota Sobre

    # --- VIEWS ORIGINAIS (Módulo 1) ---
    path('agua-estado-1/', ask_known1_view, name='ask_known1'),
    path('agua-estado-2/', ask_known2_view, name='ask_known2'),
    path('agua-estado-resultados/', process_values_view, name='process_values'),
    path('agua/', cilindro_view, name='cilindro'),
    path('processos-agua/', processos_view, name='processos'),

    # Erros Módulo 1 (Atualizado para type7)
    path('error-value/1/', error_value_view, name='error_value'),
    path('error-type/7/', error_type_view7, name='error_type7'),

    # --- VIEWS 3 (Processo 1) ---
    path('inicio/3/', homepage_view3, name='homepage3'),
    path('agua-pcte-1/', ask_known1_view3, name='ask_known1_3'),
    path('agua-pcte-2/', ask_known2_view3, name='ask_known2_3'),
    path('agua-pcte-3/', ask_known3_view3, name='ask_known3_3'),
    path('agua-pcte-4/', ask_known4_view3, name='ask_known4_3'),
    path('agua-pcte-resultados/', process_values_view3, name='process_values_3'),
    # Erros Módulo 3
    path('error-value/3/', error_value_view3, name='error_value_3'),
    path('error-type/3/', error_type_view3, name='error_type_3'),

    # --- VIEWS 4 (Processo 2) ---
    path('inicio/4/', homepage_view4, name='homepage4'),
    path('agua-adiabatico-1/', ask_known1_view4, name='ask_known1_4'),
    path('agua-adiabatico-2/', ask_known2_view4, name='ask_known2_4'),
    path('agua-adiabatico-3/', ask_known3_view4, name='ask_known3_4'),
    path('agua-adiabatico-resultados/', process_values_view4, name='process_values_4'),
    # Erros Módulo 4
    path('error-value/4/', error_value_view4, name='error_value_4'),
    path('error-type/4/', error_type_view4, name='error_type_4'),

    # --- VIEWS 5 (Processo 3) ---
    path('inicio/5/', homepage_view5, name='homepage5'),
    path('agua-vcte-1/', ask_known1_view5, name='ask_known1_5'),
    path('agua-vcte-2/', ask_known2_view5, name='ask_known2_5'),
    path('agua-vcte-3/', ask_known3_view5, name='ask_known3_5'),
    path('agua-vcte-4/', ask_known4_view5, name='ask_known4_5'),
    path('agua-vcte-resultados/', process_values_view5, name='process_values_5'),
    # Erros Módulo 5
    path('error-value/5/', error_value_view5, name='error_value_5'),
    path('error-type/5/', error_type_view5, name='error_type_5'),

    # Rotas adicionais de erro genéricas (opcional, para pegar links antigos)
    path('error-type3/', error_type_view3, name='error_type3_legacy'),
    path('error-type4/', error_type_view4, name='error_type4_legacy'),
    path('error-type5/', error_type_view5, name='error_type5_legacy'),
]
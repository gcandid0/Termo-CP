# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from myapp.views_extras import (
    api_compartilhar_view,
    api_exercicio_corrigir_view,
    api_exercicio_gerar_view,
    api_log_uso_view,
    exercicios_poe_view,
    shared_simulation_view,
)
from myapp.views_unified import (
    api_calculate_state_view,
    ask_mass_view,
    parameterized_process_results_view,
    parameterized_process_step_view,
    parameterized_state_results_view,
    parameterized_state_step_view,
)

urlpatterns = [
    # Favicon oficial do TERMO-CP (logo do README)
    path('favicon.ico', RedirectView.as_view(url='/static/myapp/img/favicon.png', permanent=False)),
    path('favicon.png', RedirectView.as_view(url='/static/myapp/img/favicon.png', permanent=False)),
    re_path(r'^.+?/favicon\.(ico|png)$', RedirectView.as_view(url='/static/myapp/img/favicon.png', permanent=False)),

    # Modo Exercício (POE), Link Compartilhável e Estatísticas Anônimas
    path('exercicios/', exercicios_poe_view, name='exercicios_poe'),
    path('api/exercicios/gerar/', api_exercicio_gerar_view, name='api_exercicio_gerar'),
    path('api/exercicios/corrigir/', api_exercicio_corrigir_view, name='api_exercicio_corrigir'),
    path('api/log-uso/', api_log_uso_view, name='api_log_uso'),
    path('api/compartilhar/', api_compartilhar_view, name='api_compartilhar'),
    path('s/<str:codigo>/', shared_simulation_view, name='shared_simulation'),

    # Fallback para servir arquivos estáticos mesmo quando DEBUG=False localmente
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'myapp' / 'static'}),

    # Página dedicada de entrada de Massa do sistema (kg)
    path('massa/<str:flow_key>/', ask_mass_view, name='ask_mass'),

    # Rotas Parametrizadas e Unificadas (Item 2)
    path('calc/<slug:substance>/<slug:mode>/<int:step>/', parameterized_state_step_view, name='param_state_step'),
    path('calc/<slug:substance>/<slug:mode>/resultados/', parameterized_state_results_view, name='param_state_results'),
    path('calc/<slug:substance>/processo/<slug:process_type>/<int:step>/', parameterized_process_step_view, name='param_process_step'),
    path('calc/<slug:substance>/processo/<slug:process_type>/resultados/', parameterized_process_results_view, name='param_process_results'),
    path('api/v1/estado/', api_calculate_state_view, name='api_calculate_state'),

    # Rotas Legadas (Mantidas para 100% de retrocompatibilidade)
    path('', include('myapp.agua_urls')),
    path('admin/', admin.site.urls),
    path('agua/', include('myapp.agua_urls')),
    path('gas/', include('myapp.gas_urls')),
    path('amonia/', include('myapp.amonia_urls')),
    path('co2/', include('myapp.co2_urls')),
    path('R410A/', include('myapp.R410A_urls')),
    path('R134A/', include('myapp.R134A_urls')),
    path('nitrogenio/', include('myapp.nitrogenio_urls')),
    path('metano/', include('myapp.metano_urls')),
    path('', include('myapp.estados_urls')),
    path('', include('myapp.processos_urls')),
    path('', include('myapp.contato_urls')),
    path('', include('myapp.ajuda_urls')),
]

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', include('myapp.cilindro_urls')),  # Inclui as URLs do aplicativo myapp
    path('admin/', admin.site.urls),
    path('agua/', include('myapp.cilindro_urls')),  # Inclui as URLs específicas para "cilindro/"
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
]

# Redirecionamentos para as páginas iniciais
urlpatterns += [
    path('', RedirectView.as_view(url='/cilindro/')),  # Redireciona a página inicial para "cilindro/"
]

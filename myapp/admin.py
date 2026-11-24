from django.contrib import admin
from .models import MensagemContato


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'enviado_por_email', 'criado_em')
    list_filter = ('enviado_por_email', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('criado_em',)

import csv
from django.contrib import admin
from django.http import HttpResponse
from .models import MensagemContato, SimulacaoCompartilhada, UsoSimulacao


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'enviado_por_email', 'criado_em')
    list_filter = ('enviado_por_email', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('criado_em',)


@admin.action(description='Exportar estatísticas selecionadas para CSV (Excel)')
def exportar_uso_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="termo_cp_estatisticas_uso.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['ID', 'Substância', 'Tipo de Simulação', 'Idioma', 'Data/Hora'])
    for obj in queryset:
        writer.writerow([obj.id, obj.substancia, obj.tipo, obj.idioma, obj.criado_em.strftime('%d/%m/%Y %H:%M:%S')])
    return response


@admin.register(UsoSimulacao)
class UsoSimulacaoAdmin(admin.ModelAdmin):
    list_display = ('substancia', 'tipo', 'idioma', 'criado_em')
    list_filter = ('substancia', 'tipo', 'idioma', 'criado_em')
    search_fields = ('substancia', 'tipo', 'idioma')
    readonly_fields = ('criado_em',)
    date_hierarchy = 'criado_em'
    actions = [exportar_uso_csv]


@admin.register(SimulacaoCompartilhada)
class SimulacaoCompartilhadaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'substancia', 'tipo', 'criado_em')
    list_filter = ('substancia', 'tipo', 'criado_em')
    search_fields = ('codigo', 'titulo', 'substancia')
    readonly_fields = ('codigo', 'criado_em')

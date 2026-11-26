import csv
import json
from datetime import timedelta

from django.contrib import admin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.urls import path
from django.utils import timezone

from .models import MensagemContato, SimulacaoCompartilhada, TentativaExercicio, UsoSimulacao

admin.site.site_header = 'TERMO-CP · Painel Científico & Administrativo'
admin.site.site_title = 'TERMO-CP Admin'
admin.site.index_title = 'Dashboard de Uso e Pesquisa'


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


@admin.action(description='Exportar resoluções do Modo Exercício para CSV (Excel)')
def exportar_exercicios_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="termo_cp_modo_exercicio.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Código', 'Estudante', 'Substância', 'Tipo', 'Nível',
        'Pontuação (%)', 'Acertos Análise', 'Tentativas', 'Tempo (s)',
        'Usou Dica', 'Idioma', 'Justificativa', 'Data/Hora',
    ])
    for obj in queryset:
        writer.writerow([
            obj.codigo, obj.nome_aluno, obj.substancia, obj.tipo, obj.nivel,
            obj.pontuacao, obj.poe_acertos, obj.tentativas, obj.tempo_segundos,
            'Sim' if obj.usou_dica else 'Não', obj.idioma, obj.justificativa,
            obj.criado_em.strftime('%d/%m/%Y %H:%M:%S'),
        ])
    return response


@admin.register(TentativaExercicio)
class TentativaExercicioAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'nome_aluno', 'substancia', 'tipo', 'nivel',
        'pontuacao', 'poe_acertos', 'tentativas', 'tempo_segundos', 'usou_dica', 'criado_em',
    )
    list_filter = ('substancia', 'tipo', 'nivel', 'usou_dica', 'idioma', 'criado_em')
    search_fields = ('codigo', 'nome_aluno', 'substancia', 'justificativa')
    readonly_fields = ('codigo', 'criado_em')
    date_hierarchy = 'criado_em'
    actions = [exportar_exercicios_csv]


# ==============================================================================
# DASHBOARD ANALÍTICO PARA ARTIGOS CIENTÍFICOS NO DJANGO ADMIN
# ==============================================================================

_LANG_LABELS = {
    'pt-br': 'Português (PT-BR)',
    'en': 'English (EN)',
    'es': 'Español (ES)',
    'fr': 'Français (FR)',
    'zh': '中文 (ZH)',
}


def build_admin_analytics(periodo='all'):
    now = timezone.now()
    qs_uso = UsoSimulacao.objects.all()
    qs_ex = TentativaExercicio.objects.all()
    qs_share = SimulacaoCompartilhada.objects.all()
    qs_msg = MensagemContato.objects.all()

    days_map = {'7': 7, '30': 30, '90': 90}
    days = days_map.get(str(periodo))
    if days:
        cutoff = now - timedelta(days=days)
        qs_uso = qs_uso.filter(criado_em__gte=cutoff)
        qs_ex = qs_ex.filter(criado_em__gte=cutoff)
        qs_share = qs_share.filter(criado_em__gte=cutoff)
        qs_msg = qs_msg.filter(criado_em__gte=cutoff)

    total_sims = qs_uso.count()
    sims_7d = UsoSimulacao.objects.filter(criado_em__gte=now - timedelta(days=7)).count()
    total_ex = qs_ex.count()
    total_shares = qs_share.count()
    total_msgs = qs_msg.count()

    ex_agg = qs_ex.aggregate(avg_score=Avg('pontuacao'), avg_time=Avg('tempo_segundos'))
    avg_score = round(float(ex_agg['avg_score'] or 0.0), 1)
    avg_time = int(round(float(ex_agg['avg_time'] or 0.0)))
    hint_count = qs_ex.filter(usou_dica=True).count()
    hint_pct = round((hint_count / total_ex) * 100.0, 1) if total_ex else 0.0

    def _with_pct(rows, key_field, total, label_map=None):
        out = []
        for r in rows:
            raw_k = r[key_field] or 'Não informado'
            lbl = label_map.get(raw_k, raw_k) if label_map else raw_k
            cnt = r['total']
            pct = round((cnt / total) * 100.0, 1) if total else 0.0
            out.append({'label': lbl, 'raw': raw_k, 'count': cnt, 'pct': pct})
        return out

    by_sub = _with_pct(
        qs_uso.values('substancia').annotate(total=Count('id')).order_by('-total', 'substancia'),
        'substancia', total_sims,
    )
    by_type = _with_pct(
        qs_uso.values('tipo').annotate(total=Count('id')).order_by('-total', 'tipo'),
        'tipo', total_sims,
    )
    by_lang = _with_pct(
        qs_uso.values('idioma').annotate(total=Count('id')).order_by('-total', 'idioma'),
        'idioma', total_sims, _LANG_LABELS,
    )

    # Evolução diária (últimos 30 dias ou janela selecionada)
    timeline_days = days or 30
    tl_cutoff = now - timedelta(days=timeline_days)
    daily_qs = (
        UsoSimulacao.objects.filter(criado_em__gte=tl_cutoff)
        .annotate(day=TruncDate('criado_em'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    daily_map = {r['day']: r['total'] for r in daily_qs if r['day']}
    timeline_labels = []
    timeline_values = []
    for i in range(timeline_days - 1, -1, -1):
        d = (now - timedelta(days=i)).date()
        timeline_labels.append(d.strftime('%d/%m'))
        timeline_values.append(daily_map.get(d, 0))

    # Desempenho no Modo Exercício por substância
    ex_by_sub_qs = (
        qs_ex.values('substancia')
        .annotate(total=Count('id'), avg_score=Avg('pontuacao'))
        .order_by('-total', 'substancia')
    )
    ex_by_sub = [
        {
            'label': r['substancia'] or 'Outro',
            'count': r['total'],
            'avg_score': round(float(r['avg_score'] or 0.0), 1),
        }
        for r in ex_by_sub_qs
    ]

    chart_payload = {
        'by_sub': {'labels': [x['label'] for x in by_sub], 'values': [x['count'] for x in by_sub]},
        'by_type': {'labels': [x['label'] for x in by_type], 'values': [x['count'] for x in by_type]},
        'by_lang': {'labels': [x['label'] for x in by_lang], 'values': [x['count'] for x in by_lang]},
        'timeline': {'labels': timeline_labels, 'values': timeline_values},
        'ex_by_sub': {
            'labels': [x['label'] for x in ex_by_sub],
            'scores': [x['avg_score'] for x in ex_by_sub],
            'counts': [x['count'] for x in ex_by_sub],
        },
    }

    return {
        'periodo': str(periodo),
        'total_sims': total_sims,
        'sims_7d': sims_7d,
        'total_ex': total_ex,
        'avg_score': avg_score,
        'avg_time': avg_time,
        'hint_pct': hint_pct,
        'total_shares': total_shares,
        'total_msgs': total_msgs,
        'by_sub': by_sub,
        'by_type': by_type,
        'by_lang': by_lang,
        'ex_by_sub': ex_by_sub,
        'chart_json': json.dumps(chart_payload, ensure_ascii=False),
    }


def exportar_relatorio_artigo_view(request):
    """Exporta CSV consolidado (tabelas de frequência n e %) pronto para artigos científicos."""
    periodo = request.GET.get('periodo', 'all')
    data = build_admin_analytics(periodo)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="termo_cp_resumo_artigo_{periodo}.csv"'
    response.write('\ufeff')
    w = csv.writer(response, delimiter=';')

    w.writerow(['TERMO-CP — Relatório Estatístico Consolidado (Artigo Científico)'])
    w.writerow(['Gerado em', timezone.now().strftime('%d/%m/%Y %H:%M:%S')])
    w.writerow(['Filtro de período', 'Todos' if periodo == 'all' else f'Últimos {periodo} dias'])
    w.writerow([])

    w.writerow(['INDICADORES GERAIS', 'VALOR'])
    w.writerow(['Total de Simulações', data['total_sims']])
    w.writerow(['Simulações (últimos 7 dias)', data['sims_7d']])
    w.writerow(['Exercícios Concluídos', data['total_ex']])
    w.writerow(['Média de Acerto nos Exercícios (%)', data['avg_score']])
    w.writerow(['Tempo Médio por Exercício (s)', data['avg_time']])
    w.writerow(['Uso de Dica de Fórmula (%)', data['hint_pct']])
    w.writerow(['Links Compartilhados', data['total_shares']])
    w.writerow(['Mensagens de Contato', data['total_msgs']])
    w.writerow([])

    w.writerow(['SIMULAÇÕES POR SUBSTÂNCIA', 'Frequência (n)', 'Percentual (%)'])
    for r in data['by_sub']:
        w.writerow([r['label'], r['count'], f"{r['pct']:.1f}%"])
    w.writerow([])

    w.writerow(['SIMULAÇÕES POR TIPO DE PROCESSO', 'Frequência (n)', 'Percentual (%)'])
    for r in data['by_type']:
        w.writerow([r['label'], r['count'], f"{r['pct']:.1f}%"])
    w.writerow([])

    w.writerow(['DISTRIBUIÇÃO POR IDIOMA', 'Frequência (n)', 'Percentual (%)'])
    for r in data['by_lang']:
        w.writerow([r['label'], r['count'], f"{r['pct']:.1f}%"])
    w.writerow([])

    if data['ex_by_sub']:
        w.writerow(['MODO EXERCÍCIO POR SUBSTÂNCIA', 'Resoluções (n)', 'Média de Acerto (%)'])
        for r in data['ex_by_sub']:
            w.writerow([r['label'], r['count'], f"{r['avg_score']:.1f}%"])

    return response


# Injeta o Dashboard Analítico na home do Django Admin e registra a URL de exportação
_orig_admin_index = admin.site.index
_orig_admin_get_urls = admin.site.get_urls


def _custom_admin_index(request, extra_context=None):
    ctx = dict(extra_context or {})
    periodo = request.GET.get('periodo', 'all')
    if periodo not in ('all', '7', '30', '90'):
        periodo = 'all'
    ctx['analytics'] = build_admin_analytics(periodo)
    return _orig_admin_index(request, extra_context=ctx)


def _custom_admin_get_urls():
    custom = [
        path(
            'exportar-estatisticas-artigo/',
            admin.site.admin_view(exportar_relatorio_artigo_view),
            name='termo_cp_export_article_csv',
        ),
    ]
    return custom + _orig_admin_get_urls()


admin.site.index = _custom_admin_index
admin.site.get_urls = _custom_admin_get_urls

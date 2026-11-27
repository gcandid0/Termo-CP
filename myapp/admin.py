import csv
import json
import statistics
from datetime import timedelta

from django.contrib import admin
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html

from .models import MensagemContato, SimulacaoCompartilhada, TentativaExercicio, UsoSimulacao

admin.site.site_header = 'TERMO-CP · Painel Científico & Administrativo'
admin.site.site_title = 'TERMO-CP Admin'
admin.site.index_title = 'Dashboard de Uso e Pesquisa'


@admin.register(MensagemContato)
class MensagemContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'status_email_badge', 'criado_em')
    list_filter = ('enviado_por_email', 'criado_em')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('criado_em',)

    @admin.display(description='E-mail')
    def status_email_badge(self, obj):
        if obj.enviado_por_email:
            return format_html('<span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:999px;font-weight:700;font-size:11px;">✓ Enviado</span>')
        return format_html('<span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:999px;font-weight:700;font-size:11px;">Salvo no BD</span>')


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
    list_display = ('substancia', 'tipo', 'idioma_badge', 'criado_em')
    list_filter = ('substancia', 'tipo', 'idioma', 'criado_em')
    search_fields = ('substancia', 'tipo', 'idioma')
    readonly_fields = ('criado_em',)
    date_hierarchy = 'criado_em'
    actions = [exportar_uso_csv]

    @admin.display(description='Idioma')
    def idioma_badge(self, obj):
        colors = {
            'pt-br': ('#dcfce7', '#166534'),
            'en': ('#dbeafe', '#1e40af'),
            'es': ('#fef3c7', '#92400e'),
            'fr': ('#ede9fe', '#5b21b6'),
            'zh': ('#fee2e2', '#991b1b'),
        }
        bg, fg = colors.get(obj.idioma, ('#f1f5f9', '#334155'))
        return format_html(
            '<span style="background:{};color:{};padding:2px 8px;border-radius:999px;font-weight:700;font-size:11px;">{}</span>',
            bg, fg, obj.idioma.upper(),
        )


@admin.register(SimulacaoCompartilhada)
class SimulacaoCompartilhadaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'titulo', 'substancia', 'tipo', 'link_publico', 'criado_em')
    list_filter = ('substancia', 'tipo', 'criado_em')
    search_fields = ('codigo', 'titulo', 'substancia')
    readonly_fields = ('codigo', 'criado_em')

    @admin.display(description='Prévia')
    def link_publico(self, obj):
        return format_html(
            '<a href="/s/{}/" target="_blank" style="background:#eff6ff;color:#1b3668;padding:2px 9px;border-radius:6px;font-weight:700;font-size:11px;text-decoration:none;border:1px solid #bfdbfe;">Abrir /s/{}/ ↗</a>',
            obj.codigo, obj.codigo,
        )


@admin.action(description='Exportar resoluções do Modo Exercício para CSV (Excel)')
def exportar_exercicios_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="termo_cp_modo_exercicio.csv"'
    response.write('\ufeff')
    writer = csv.writer(response, delimiter=';')
    writer.writerow([
        'Código', 'Estudante', 'Turma', 'Modo', 'Substância', 'Tipo', 'Nível',
        'Pontuação (%)', 'Acertos POE', 'Tentativas', 'Tempo (s)',
        'Usou Dica', 'Idioma', 'Hipótese (Prever)', 'Explicação (Explicar)', 'Data/Hora',
    ])
    for obj in queryset:
        writer.writerow([
            obj.codigo, obj.nome_aluno, obj.codigo_turma, obj.modo, obj.substancia, obj.tipo, obj.nivel,
            obj.pontuacao, obj.poe_acertos, obj.tentativas, obj.tempo_segundos,
            'Sim' if obj.usou_dica else 'Não', obj.idioma, obj.justificativa, obj.explicacao_poe,
            obj.criado_em.strftime('%d/%m/%Y %H:%M:%S'),
        ])
    return response


@admin.register(TentativaExercicio)
class TentativaExercicioAdmin(admin.ModelAdmin):
    list_display = (
        'codigo', 'nome_aluno', 'codigo_turma', 'modo', 'substancia', 'tipo', 'nivel',
        'pontuacao_badge', 'tentativas', 'tempo_segundos', 'usou_dica', 'criado_em',
    )
    list_filter = ('codigo_turma', 'modo', 'substancia', 'tipo', 'nivel', 'usou_dica', 'idioma', 'criado_em')
    search_fields = ('codigo', 'nome_aluno', 'codigo_turma', 'substancia', 'justificativa', 'explicacao_poe')
    readonly_fields = ('codigo', 'criado_em')
    date_hierarchy = 'criado_em'
    actions = [exportar_exercicios_csv]

    @admin.display(description='Nota')
    def pontuacao_badge(self, obj):
        if obj.pontuacao >= 75:
            bg, fg = '#dcfce7', '#166534'
        elif obj.pontuacao >= 50:
            bg, fg = '#fef3c7', '#92400e'
        else:
            bg, fg = '#fee2e2', '#991b1b'
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:999px;font-weight:700;font-size:11px;">{}%</span>',
            bg, fg, round(obj.pontuacao, 1),
        )


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

_WEEKDAY_LABELS = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']


def build_admin_analytics(periodo='all', turma=''):
    now = timezone.now()
    qs_uso = UsoSimulacao.objects.all()
    qs_ex = TentativaExercicio.objects.all()
    qs_share = SimulacaoCompartilhada.objects.all()
    qs_msg = MensagemContato.objects.all()

    turmas_disponiveis = sorted(
        {t for t in TentativaExercicio.objects.exclude(codigo_turma='').values_list('codigo_turma', flat=True) if t}
    )
    turma = str(turma or '').strip().upper()[:40]
    if turma:
        qs_ex = qs_ex.filter(codigo_turma=turma)

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

    # Estatística descritiva completa do Modo Exercício
    scores = list(qs_ex.values_list('pontuacao', flat=True))
    times = list(qs_ex.values_list('tempo_segundos', flat=True))
    avg_score = round(statistics.mean(scores), 1) if scores else 0.0
    median_score = round(statistics.median(scores), 1) if scores else 0.0
    stdev_score = round(statistics.stdev(scores), 1) if len(scores) >= 2 else 0.0
    min_score = round(min(scores), 1) if scores else 0.0
    max_score = round(max(scores), 1) if scores else 0.0
    pass_rate = round((sum(1 for s in scores if s >= 75.0) / len(scores)) * 100.0, 1) if scores else 0.0

    avg_time = int(round(statistics.mean(times))) if times else 0
    median_time = int(round(statistics.median(times))) if times else 0

    hint_count = qs_ex.filter(usou_dica=True).count()
    hint_pct = round((hint_count / total_ex) * 100.0, 1) if total_ex else 0.0
    avg_with_hint = round(float(qs_ex.filter(usou_dica=True).aggregate(a=Avg('pontuacao'))['a'] or 0.0), 1)
    avg_no_hint = round(float(qs_ex.filter(usou_dica=False).aggregate(a=Avg('pontuacao'))['a'] or 0.0), 1)

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

    # Evolução diária
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

    # Distribuição por dia da semana (0=Seg .. 6=Dom)
    weekday_counts = [0] * 7
    for dt in qs_uso.values_list('criado_em', flat=True):
        if dt:
            local_dt = timezone.localtime(dt)
            weekday_counts[local_dt.weekday()] += 1

    # Matriz Cruzada Substância x Tipo de Processo (Top 8 x Top 6)
    top_subs = [x['raw'] for x in by_sub[:8]]
    top_types = [x['raw'] for x in by_type[:6]]
    cross_qs = (
        qs_uso.filter(substancia__in=top_subs, tipo__in=top_types)
        .values('substancia', 'tipo')
        .annotate(total=Count('id'))
    )
    cross_map = {(r['substancia'], r['tipo']): r['total'] for r in cross_qs}
    cross_matrix = []
    for s in top_subs:
        row_vals = [cross_map.get((s, t), 0) for t in top_types]
        cross_matrix.append({'substancia': s, 'values': row_vals, 'total': sum(row_vals)})

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

    # Atividade recente
    recent_sims = list(qs_uso.order_by('-criado_em')[:8])
    recent_ex = list(qs_ex.order_by('-criado_em')[:5])

    # Texto descritivo automático pronto para seção de Resultados de artigo
    periodo_txt = 'todo o período registrado' if periodo == 'all' else f'os últimos {periodo} dias'
    if total_sims > 0:
        top_sub_txt = f"{by_sub[0]['label']} ({by_sub[0]['count']} simulações; {by_sub[0]['pct']}%)" if by_sub else '—'
        top_type_txt = f"{by_type[0]['label']} ({by_type[0]['count']}; {by_type[0]['pct']}%)" if by_type else '—'
        langs_txt = ', '.join(f"{x['label']}: {x['pct']}%" for x in by_lang[:5])
        article_summary = (
            f"Durante {periodo_txt}, foram registradas {total_sims} simulações anônimas na plataforma TERMO-CP "
            f"(além de {total_shares} simulações compartilhadas via link curto). "
            f"A substância mais simulada foi {top_sub_txt}, e o tipo de análise mais frequente foi {top_type_txt}. "
            f"Quanto à internacionalização, a distribuição de acessos por idioma foi: {langs_txt}."
        )
        if total_ex > 0:
            article_summary += (
                f" No Modo Exercício, foram concluídas {total_ex} resoluções avaliativas, "
                f"com média de acerto de {avg_score}% (mediana = {median_score}%, desvio-padrão = {stdev_score}%, "
                f"taxa de aproveitamento ≥ 75% de {pass_rate}%) e tempo médio de {avg_time} s por questão."
            )
    else:
        article_summary = (
            "Ainda não há simulações registradas neste período. Assim que os estudantes utilizarem a plataforma, "
            "este bloco gerará automaticamente um parágrafo descritivo com as métricas consolidadas para o seu artigo."
        )

    chart_payload = {
        'by_sub': {'labels': [x['label'] for x in by_sub], 'values': [x['count'] for x in by_sub], 'pcts': [x['pct'] for x in by_sub]},
        'by_type': {'labels': [x['label'] for x in by_type], 'values': [x['count'] for x in by_type], 'pcts': [x['pct'] for x in by_type]},
        'by_lang': {'labels': [x['label'] for x in by_lang], 'values': [x['count'] for x in by_lang], 'pcts': [x['pct'] for x in by_lang]},
        'timeline': {'labels': timeline_labels, 'values': timeline_values},
        'weekday': {'labels': _WEEKDAY_LABELS, 'values': weekday_counts},
        'ex_by_sub': {
            'labels': [x['label'] for x in ex_by_sub],
            'scores': [x['avg_score'] for x in ex_by_sub],
            'counts': [x['count'] for x in ex_by_sub],
        },
    }

    return {
        'periodo': str(periodo),
        'turma': turma,
        'turmas_disponiveis': turmas_disponiveis,
        'total_sims': total_sims,
        'sims_7d': sims_7d,
        'total_ex': total_ex,
        'avg_score': avg_score,
        'median_score': median_score,
        'stdev_score': stdev_score,
        'min_score': min_score,
        'max_score': max_score,
        'pass_rate': pass_rate,
        'avg_time': avg_time,
        'median_time': median_time,
        'hint_pct': hint_pct,
        'avg_with_hint': avg_with_hint,
        'avg_no_hint': avg_no_hint,
        'total_shares': total_shares,
        'total_msgs': total_msgs,
        'by_sub': by_sub,
        'by_type': by_type,
        'by_lang': by_lang,
        'ex_by_sub': ex_by_sub,
        'cross_types': top_types,
        'cross_matrix': cross_matrix,
        'recent_sims': recent_sims,
        'recent_ex': recent_ex,
        'article_summary': article_summary,
        'chart_json': json.dumps(chart_payload, ensure_ascii=False),
    }


def exportar_relatorio_artigo_view(request):
    """Exporta CSV consolidado (tabelas de frequência n e %, estatística descritiva e matriz cruzada)."""
    periodo = request.GET.get('periodo', 'all')
    turma = request.GET.get('turma', '')
    data = build_admin_analytics(periodo, turma=turma)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="termo_cp_resumo_artigo_{periodo}.csv"'
    response.write('\ufeff')
    w = csv.writer(response, delimiter=';')

    w.writerow(['TERMO-CP — Relatório Estatístico Consolidado (Artigo Científico)'])
    w.writerow(['Gerado em', timezone.now().strftime('%d/%m/%Y %H:%M:%S')])
    w.writerow(['Filtro de período', 'Todos' if periodo == 'all' else f'Últimos {periodo} dias'])
    if data['turma']:
        w.writerow(['Filtro de Turma (Modo Exercício)', data['turma']])
    w.writerow([])

    w.writerow(['INDICADORES GERAIS', 'VALOR'])
    w.writerow(['Total de Simulações', data['total_sims']])
    w.writerow(['Simulações (últimos 7 dias)', data['sims_7d']])
    w.writerow(['Exercícios Concluídos', data['total_ex']])
    w.writerow(['Média de Acerto (%)', data['avg_score']])
    w.writerow(['Mediana de Acerto (%)', data['median_score']])
    w.writerow(['Desvio-Padrão (%)', data['stdev_score']])
    w.writerow(['Taxa de Aprovação >= 75% (%)', data['pass_rate']])
    w.writerow(['Média Com Dica (%)', data['avg_with_hint']])
    w.writerow(['Média Sem Dica (%)', data['avg_no_hint']])
    w.writerow(['Tempo Médio por Exercício (s)', data['avg_time']])
    w.writerow(['Tempo Mediano por Exercício (s)', data['median_time']])
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

    if data['cross_matrix']:
        w.writerow(['MATRIZ SUBSTÂNCIA x TIPO'] + data['cross_types'] + ['Total'])
        for row in data['cross_matrix']:
            w.writerow([row['substancia']] + row['values'] + [row['total']])
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
    turma = request.GET.get('turma', '')
    ctx['analytics'] = build_admin_analytics(periodo, turma=turma)
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

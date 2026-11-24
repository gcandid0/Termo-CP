# -*- coding: utf-8 -*-
"""
Motor Termodinâmico Desacoplado do TERMO-CP (Princípio DRY).
Centraliza:
  - Interpolação e busca em tabelas termodinâmicas (Água, Amônia, CO2, R-410a, R-134a, N2, CH4)
  - Cálculos de Estado e Processos (Isobárico, Isentrópico, Isocórico, Isotérmico, Politrópico)
  - Cálculos de Gás Ideal
  - Gerenciamento de Sessão Isolado por Substância/Fluxo/Aba (evita colisão entre abas e usuários)
"""

import json
import math
from math import exp, log
from django.core.exceptions import ValidationError
from . import tabelas_termoprop as tbs


class BoundariesException(Exception):
    """Exceção lançada quando propriedades excedem os limites das tabelas termodinâmicas."""
    pass


class TituloException(Exception):
    """Exceção lançada quando o título (x) é inválido para a fase."""
    pass


class CalculationTypeError(Exception):
    """Exceção interna para redirecionamento às rotas de erro de tipo."""
    pass


SUBSTANCE_CONFIG = {
    1: {
        'opt': 1,
        'slug': 'agua',
        'name': 'Água',
        'article_name': 'a água',
        'folder': 'agua',
        'file_prefix': 'agua',
        'min_pressure': 0.6113,
        'temp_unit': '°C',
    },
    2: {
        'opt': 2,
        'slug': 'amonia',
        'name': 'Amônia',
        'article_name': 'a amônia',
        'folder': 'amonia',
        'file_prefix': 'amonia',
        'min_pressure': 40.9,
        'temp_unit': '°C',
    },
    3: {
        'opt': 3,
        'slug': 'co2',
        'name': 'Dióxido de Carbono',
        'article_name': 'o dióxido de carbono',
        'folder': 'co2',
        'file_prefix': 'co2',
        'min_pressure': 400.0,
        'temp_unit': '°C',
    },
    4: {
        'opt': 4,
        'slug': 'r410a',
        'name': 'R-410a',
        'article_name': 'o R-410a',
        'folder': 'R410A',
        'file_prefix': 'R410A',
        'min_pressure': 50.0,
        'temp_unit': '°C',
    },
    5: {
        'opt': 5,
        'slug': 'r134a',
        'name': 'R-134a',
        'article_name': 'o R-134a',
        'folder': 'R134A',
        'file_prefix': 'R134A',
        'min_pressure': 8.3,
        'temp_unit': '°C',
    },
    6: {
        'opt': 6,
        'slug': 'nitrogenio',
        'name': 'Nitrogênio',
        'article_name': 'o nitrogênio',
        'folder': 'nitrogenio',
        'file_prefix': 'nitrogenio',
        'step_prefix': 'nkelvin',
        'min_pressure': 0.0,
        'temp_unit': 'K',
    },
    7: {
        'opt': 7,
        'slug': 'metano',
        'name': 'Metano',
        'article_name': 'o metano',
        'folder': 'metano',
        'file_prefix': 'metano',
        'step_prefix': 'mkelvin',
        'min_pressure': 0.0,
        'temp_unit': 'K',
    },
}

SUBSTANCE_BY_SLUG = {cfg['slug']: cfg for cfg in SUBSTANCE_CONFIG.values()}
SUBSTANCE_BY_SLUG['r410a'] = SUBSTANCE_CONFIG[4]
SUBSTANCE_BY_SLUG['R410A'] = SUBSTANCE_CONFIG[4]
SUBSTANCE_BY_SLUG['r134a'] = SUBSTANCE_CONFIG[5]
SUBSTANCE_BY_SLUG['R134A'] = SUBSTANCE_CONFIG[5]


# ==============================================================================
# GERENCIADOR DE SESSÃO ISOLADO POR ABAS E SUBSTÂNCIAS (Item 5)
# ==============================================================================

def _get_tab_scope(request, scope_key):
    """Retorna a chave de escopo combinando a substância/fluxo e um calc_id opcional da aba."""
    calc_id = None
    if hasattr(request, 'POST') and request.POST.get('calc_id'):
        calc_id = request.POST.get('calc_id')
    elif hasattr(request, 'GET') and request.GET.get('calc_id'):
        calc_id = request.GET.get('calc_id')
    if calc_id:
        return f"{scope_key}:{calc_id}"
    return scope_key


def set_flow_data(request, scope_key, data_dict, mirror_top_level=True):
    """
    Salva variáveis do wizard em um namespace isolado por substância/fluxo/aba
    dentro de request.session['termo_flows'][scope], evitando que duas abas
    de substâncias ou processos diferentes sobrescrevam os dados uma da outra.
    Também espelha no topo da sessão para total retrocompatibilidade.
    """
    scoped = _get_tab_scope(request, scope_key)
    flows = request.session.get('termo_flows')
    if not isinstance(flows, dict):
        flows = {}
    bucket = flows.get(scoped)
    if not isinstance(bucket, dict):
        bucket = {}
    for k, v in data_dict.items():
        bucket[k] = v
        if mirror_top_level:
            request.session[k] = v
    flows[scoped] = bucket
    request.session['termo_flows'] = flows
    request.session.modified = True


def get_flow_val(request, scope_key, key, default=None):
    """
    Lê uma variável do namespace isolado da substância/fluxo/aba.
    Faz fallback para o topo da request.session caso tenha sido populada diretamente.
    """
    scoped = _get_tab_scope(request, scope_key)
    flows = request.session.get('termo_flows')
    if isinstance(flows, dict):
        bucket = flows.get(scoped)
        if isinstance(bucket, dict) and key in bucket:
            return bucket[key]
        base_bucket = flows.get(scope_key)
        if isinstance(base_bucket, dict) and key in base_bucket:
            return base_bucket[key]
    return request.session.get(key, default)


def has_flow_keys(request, scope_key, keys):
    """Verifica se todas as chaves informadas existem no fluxo ou na sessão."""
    return all(get_flow_val(request, scope_key, k) is not None for k in keys)


def clear_flow_cycle(request, scope_key, legacy_instance=None):
    """Limpa o histórico de estados e pontos de gráfico do ciclo da substância."""
    set_flow_data(request, scope_key, {
        'lista_estados': [],
        'pontos_grafico': [],
    }, mirror_top_level=False)
    request.session['lista_estados'] = json.dumps([])
    request.session['pontos_grafico'] = []
    if 'dados_processo' in request.session:
        del request.session['dados_processo']
    if legacy_instance is not None:
        if hasattr(legacy_instance, 'limpar_estados'):
            legacy_instance.limpar_estados()
        if hasattr(legacy_instance, 'limpar_gas'):
            legacy_instance.limpar_gas()
    request.session.modified = True


def get_flow_cycle(request, scope_key, legacy_instance=None):
    """
    Recupera (lista_estados, pontos_grafico) isolados na sessão para a substância atual.
    """
    lista_estados = get_flow_val(request, scope_key, 'lista_estados')
    if lista_estados is None:
        raw = request.session.get('lista_estados')
        if isinstance(raw, str):
            try:
                lista_estados = json.loads(raw)
            except Exception:
                lista_estados = []
        elif isinstance(raw, list):
            lista_estados = list(raw)
        elif legacy_instance is not None and getattr(legacy_instance, 'lista_estados', None):
            lista_estados = list(legacy_instance.lista_estados)
        else:
            lista_estados = []

    pontos_grafico = get_flow_val(request, scope_key, 'pontos_grafico')
    if pontos_grafico is None:
        pontos_grafico = list(request.session.get('pontos_grafico', []))

    return list(lista_estados), list(pontos_grafico)


def save_flow_cycle(request, scope_key, lista_estados, pontos_grafico, legacy_instance=None):
    """Salva o histórico de estados e curvas do ciclo na sessão isolada por substância."""
    serializable_estados = json.loads(json.dumps(lista_estados, default=str))
    set_flow_data(request, scope_key, {
        'lista_estados': serializable_estados,
        'pontos_grafico': pontos_grafico,
    }, mirror_top_level=False)
    request.session['lista_estados'] = json.dumps(serializable_estados, default=str)
    request.session['pontos_grafico'] = pontos_grafico
    request.session['dados_processo'] = serializable_estados
    if legacy_instance is not None and hasattr(legacy_instance, 'lista_estados'):
        legacy_instance.lista_estados = list(lista_estados)
    request.session.modified = True


# ==============================================================================
# MOTOR DE PROPRIEDADES TERMODINÂMICAS (TABELAS B.1 A B.7)
# ==============================================================================

class subs_cls:
    """
    Calcula o estado termodinâmico de substâncias puras (Água, Amônia, CO2,
    R-410a, R-134a, Nitrogênio e Metano) a partir de duas propriedades independentes.
    Usa as tabelas em cache (singleton) sem mutação in-place.
    """

    classe = 'Subs'

    def __init__(self, opt, a, b, c, d):
        self.n = opt
        self.index1 = a
        self.index2 = b
        self.known1 = c
        self.known2 = d
        self.results = []
        self.x = self.run()

    def select_table(self, opt):
        """Seleciona as tabelas de propriedades em cache de acordo com a substância."""
        t = tbs.tabelas
        if opt == 1:
            self.tabela = t.B_1_1
            self.liq_comp = t.B_1_4
            self.vap_sup = t.B_1_3
        elif opt == 2:
            self.tabela = t.B_2_1
            self.vap_sup = t.B_2_2
        elif opt == 3:
            self.tabela = t.B_3_1
            self.vap_sup = t.B_3_2
        elif opt == 4:
            self.tabela = t.B_4_1
            self.vap_sup = t.B_4_2
        elif opt == 5:
            self.tabela = t.B_5_1
            self.vap_sup = t.B_5_2
        elif opt == 6:
            self.tabela = t.B_6_1
            self.vap_sup = t.B_6_2
            self.props[0][2] = 'K'
        elif opt == 7:
            self.tabela = t.B_7_1
            self.vap_sup = t.B_7_2
            self.props[0][2] = 'K'

        if opt in tbs._BOUNDARIES_CACHE:
            self.boundaries = tbs.get_cached_boundaries(opt)

    def find_phase(self):
        """Determina a fase da substância (1: líq. comprimido, 2: vapor superaq., 3: saturação)."""
        if self.index1 == 0:
            self.prop1_T()
        if self.index1 == 1:
            self.prop1_p()

    def prop1_T(self):
        """Determina a fase e propriedades de saturação quando a propriedade 1 é T."""
        if self.known1 > self.tabela[0][-1]:
            self.phase = 2
            if self.index2 == 6:
                self.tag_error = 1
        else:
            self.sat_props(0, self.known1)

            if self.index2 == 1:
                if self.known2 == self.sat_list[1][2]:
                    self.phase = 3
                    self.tag_error = 1
                if self.known2 > self.sat_list[1][2]:
                    self.phase = 1
                if self.known2 < self.sat_list[1][2]:
                    self.phase = 2

            if 1 < self.index2 < 6:
                low = self.sat_list[(self.index2 * 2) - 2][2]
                high = self.sat_list[(self.index2 * 2) - 1][2]
                if low <= self.known2 <= high:
                    self.phase = 3
                if self.known2 < low:
                    self.phase = 1
                if self.known2 > high:
                    self.phase = 2

            if self.index2 == 6:
                self.phase = 3

    def prop1_p(self):
        """Determina a fase e propriedades de saturação quando a propriedade 1 é p."""
        if self.n == 1 and self.known1 > self.tabela[0][-1]:
            if self.index2 == 0 and self.known2 < self.tabela[1][-1]:
                self.phase = 1
            else:
                self.phase = 2
                if self.index2 == 6:
                    self.tag_error = 1
        elif self.n != 1 and self.known1 > self.tabela[1][-1]:
            if self.index2 == 0 and self.known2 < self.tabela[0][-1]:
                self.phase = 1
            else:
                self.phase = 2
                if self.index2 == 6:
                    self.tag_error = 1
        else:
            if self.n == 1:
                self.sat_props(0, self.known1)
                ref = self.sat_list[1][2]
            else:
                self.sat_props(1, self.known1)
                ref = self.sat_list[0][2]

            if self.index2 == 0:
                if self.known2 == ref:
                    self.phase = 3
                    self.tag_error = 1
                if self.known2 < ref:
                    self.phase = 1
                if self.known2 > ref:
                    self.phase = 2

            if 1 < self.index2 < 6:
                low = self.sat_list[(self.index2 * 2) - 2][2]
                high = self.sat_list[(self.index2 * 2) - 1][2]
                if low <= self.known2 <= high:
                    self.phase = 3
                if self.known2 < low:
                    self.phase = 1
                if self.known2 > high:
                    self.phase = 2

            if self.index2 == 6:
                self.phase = 3

    def find_props(self):
        """Determina as propriedades da substância de acordo com a fase."""
        try:
            if self.tag_error == 0:
                # LÍQUIDO COMPRIMIDO
                if self.phase == 1:
                    self.props.pop(-1)
                    if self.index1 == 1 or self.index2 == 1:
                        self.looking_for_p_in_lc()
                    if self.index1 != 1 and self.index2 != 1:
                        if self.n == 1:
                            self.looking_for_not_p_in_lc()
                        else:
                            raise TypeError("Erro de propriedades")

                # VAPOR SUPERAQUECIDO
                if self.phase == 2:
                    self.props.pop(-1)
                    if self.index1 == 1 or self.index2 == 1:
                        self.looking_for_p_in_vs()
                    if self.index1 != 1 and self.index2 != 1:
                        self.looking_for_not_p_in_vs()

                # REGIÃO DE SATURAÇÃO
                if self.phase == 3:
                    if self.index1 == 0:
                        self.props[1][3] = self.sat_list[1][2]

                    if self.index1 == 1:
                        self.props[0][3] = self.sat_list[1][2] if self.n == 1 else self.sat_list[0][2]

                    if 1 < self.index2 < 6:
                        yl_index = 2 * (self.index2 - 1)
                        yv_index = (2 * (self.index2 - 1)) + 1
                        yl = self.sat_list[yl_index][2]
                        yv = self.sat_list[yv_index][2]
                        self.props[6][3] = 100 * self.calc_x(self.known2, yl, yv)
                    if self.index2 == 6:
                        self.props[6][3] = self.known2
                    titulo = self.props[6][3] / 100
                    for i in range(2, 6):
                        yl_index = 2 * (i - 1)
                        yv_index = (2 * (i - 1)) + 1
                        yl = self.sat_list[yl_index][2]
                        yv = self.sat_list[yv_index][2]
                        self.props[i][3] = self.calc_y(titulo, yl, yv)

                self.get_props()

            if self.tag_error == 1:
                raise TypeError("Tag de erro acionada")

        except TypeError:
            raise TypeError("Valores fora do limite da tabela.")

    def get_props(self):
        """Retorna lista textual das propriedades calculadas."""
        result = []
        if not (0 <= self.index1 < len(self.props) and 0 <= self.index2 < len(self.props)):
            raise IndexError("Índices fornecidos estão fora dos limites da lista de propriedades.")

        header = (
            f'As propriedades de {self.subs[self.n - 1]} a {self.props[self.index1][3]} {self.props[self.index1][2]} '
            f'e {self.props[self.index2][3]} {self.props[self.index2][2]} são:'
        )
        result.append(header)

        for i in range(len(self.props)):
            if i != self.index1 and i != self.index2:
                if i == 2:
                    result.append(f'{self.props[i][1]} = {round(self.props[i][3], 6):.6f} {self.props[i][2]}')
                elif i == 5:
                    result.append(f'{self.props[i][1]} = {round(self.props[i][3], 4):.4f} {self.props[i][2]}')
                else:
                    result.append(f'{self.props[i][1]} = {round(self.props[i][3], 2):.2f} {self.props[i][2]}')

        return result

    def run(self):
        """Executa o fluxo de determinação de fase e interpolação de propriedades."""
        self.subs = ['a água', 'a amônia', 'o dióxido de carbono', 'o R-410a', 'o R-134a', 'o nitrogênio', 'o metano']
        self.tabela = []
        self.liq_comp = []
        self.vap_sup = []
        self.sat = []
        self.sat_list = []
        self.lgt = []
        self.props = [
            ['Temperatura', 'T', '°C', 0],
            ['Pressão', 'p', 'kPa', 0],
            ['Volume específico', 'v', 'm³/kg', 0],
            ['Energia interna específica', 'u', 'kJ/kg', 0],
            ['Entalpia específica', 'h', 'kJ/kg', 0],
            ['Entropia específica', 's', 'kJ/kg.K', 0],
            ['Título', 'x', '%', -1],
        ]
        self.props[self.index1][3] = self.known1
        self.props[self.index2][3] = self.known2
        self.index_aux1 = 0
        self.index_aux2 = 0
        self.phase = 0
        self.tag1 = -1
        self.tag2 = -1
        self.tag_error = 0
        self.list_props = [
            'temperatura', 'pressão', 'volume específico',
            'energia interna específica', 'entalpia específica',
            'entropia específica', 'título',
        ]
        self.str_prop = ''
        self.boundaries = [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 100]]
        self.results = []

        self.select_table(self.n)

        if hasattr(self, 'vap_sup') and self.vap_sup:
            if self.known1 < self.boundaries[self.index1][0] or self.known1 > self.boundaries[self.index1][1]:
                raise BoundariesException
            if self.known2 < self.boundaries[self.index2][0] or self.known2 > self.boundaries[self.index2][1]:
                raise BoundariesException

        if self.n == 1 and self.index1 == 1:
            self.tabela = tbs.tabelas.B_1_2

        self.find_phase()
        self.find_props()
        self.results = [self.phase, self.sat_list, self.props]
        return self.results

    @staticmethod
    def interpolate(xm, x, xp, ym, yp):
        return (((x - xm) / (xp - xm)) * (yp - ym)) + ym

    @staticmethod
    def calc_x(x, xl, xv):
        return (x - xl) / (xv - xl)

    @staticmethod
    def calc_y(x, yl, yv):
        return yl + (x * (yv - yl))

    def find_index(self, iterator, comp1, comp2, n, anterior=0):
        for i in range(len(iterator)):
            if i >= n:
                if comp1 == comp2[i]:
                    self.tag1 = 1
                    anterior = i
                    break
                elif comp1 < comp2[i]:
                    anterior = i - 1
                    self.tag1 = -1
                    break
        return anterior

    def sat_props(self, n, known):
        tabela = self.tabela
        self.index_aux1 = self.find_index(tabela[0], known, tabela[n], 2)
        a = []

        if self.tag1 == 1:
            for i in range(len(tabela)):
                a.append([tabela[i][0], tabela[i][1], tabela[i][self.index_aux1]])

        if self.tag1 == -1:
            for i in range(len(tabela)):
                if i != n:
                    value = self.interpolate(
                        tabela[n][self.index_aux1], known, tabela[n][self.index_aux1 + 1],
                        tabela[i][self.index_aux1], tabela[i][self.index_aux1 + 1],
                    )
                    a.append([tabela[i][0], tabela[i][1], value])
                else:
                    a.append([tabela[i][0], tabela[i][1], known])
        self.sat_list = a

    def looking_for_p_in_lc(self):
        if self.n == 1:
            tabela_lc = self.liq_comp
            self.tabela = tbs.tabelas.B_1_1
        if self.index1 == 1:
            p = self.known1
            self.str_prop = self.props[self.index2][0]
        if self.index2 == 1:
            p = self.known2

        if (self.n == 1 and p < tabela_lc[0][2]) or (self.n != 1):
            if self.index1 == 0 or self.index2 == 0:
                aux_index = 0
            else:
                aux_index = (2 * self.index2) - 2

            tabela = self.tabela
            target_known = self.known2 if self.index1 == 1 else self.known1
            self.index_aux1 = self.find_index(tabela[aux_index], target_known, tabela[aux_index], 2)

            a = []
            if self.tag1 == 1:
                for i in range(len(tabela)):
                    if i % 2 == 0:
                        a.append(tabela[i][self.index_aux1])

            if self.tag1 == -1:
                for i in range(len(tabela)):
                    if i % 2 == 0:
                        value = self.interpolate(
                            tabela[aux_index][self.index_aux1], target_known,
                            tabela[aux_index][self.index_aux1 + 1],
                            tabela[i][self.index_aux1], tabela[i][self.index_aux1 + 1],
                        )
                        a.append(value)

            for i in range(len(a)):
                if i != self.index2 - 1 and i != 0:
                    self.props[i + 1][3] = a[i]
                elif i == 0:
                    self.props[i][3] = a[i]

        if self.n == 1 and p > tabela_lc[0][2]:
            if p > tabela_lc[-1][2]:
                self.tag_error = 1
                self.str_prop = self.list_props[1]
                raise TypeError

            anterior = 0
            for i in range(len(tabela_lc)):
                if p == tabela_lc[i][2]:
                    self.tag1 = 1
                    anterior = i
                    break
                elif p < tabela_lc[i][2]:
                    anterior = i - 1
                    self.tag1 = -1
                    break
            self.index_aux2 = anterior

            a = []
            if self.tag1 == 1:
                for i in range(len(tabela_lc[self.index_aux2][3])):
                    b = [
                        tabela_lc[self.index_aux2][3][i][j]
                        for j in range(len(tabela_lc[self.index_aux2][3][0]))
                        if j > 1
                    ]
                    a.append(b)

            if self.tag1 == -1:
                for i in range(len(tabela_lc[self.index_aux2][3])):
                    b = []
                    row_len = len(tabela_lc[self.index_aux2][3][0])
                    for j in range(row_len):
                        if 1 < j < row_len - 1:
                            value = self.interpolate(
                                tabela_lc[self.index_aux2][2], p, tabela_lc[self.index_aux2 + 1][2],
                                tabela_lc[self.index_aux2][3][i][j], tabela_lc[self.index_aux2 + 1][3][i][j],
                            )
                            b.append(value)

                    if self.index1 == 0:
                        self.tabela = tbs.tabelas.B_1_2
                        self.sat_props(0, self.known2)
                    if i == 0:
                        b.append(self.sat_list[1][2])
                    else:
                        b.append(self.sat_list[2 * i][2])
                    a.append(b)

            other = 0
            if self.index1 == 1:
                if self.index2 != 0:
                    self.str_prop = self.list_props[self.index2]
                    other = self.index2 - 1
                    if self.known2 < min(a[other]) or self.known2 > max(a[other]):
                        raise TypeError

                self.index_aux2 = self.find_index(a[other], self.known2, a[other], 0)

                if self.tag1 == 1:
                    for i in range(len(a)):
                        if i != other:
                            target_idx = 0 if i == 0 else i + 1
                            self.props[target_idx][3] = a[i][self.index_aux2]

                if self.tag1 == -1:
                    for i in range(len(a)):
                        if i != other:
                            target_idx = 0 if i == 0 else i + 1
                            self.props[target_idx][3] = self.interpolate(
                                a[other][self.index_aux2], self.known2, a[other][self.index_aux2 + 1],
                                a[i][self.index_aux2], a[i][self.index_aux2 + 1],
                            )

            if self.index2 == 1:
                self.str_prop = self.list_props[0]
                if self.known1 < min(a[other]) or self.known1 > max(a[other]):
                    raise TypeError

                self.index_aux2 = self.find_index(a[other], self.known1, a[other], 0)

                if self.tag1 == 1:
                    for i in range(len(a)):
                        if i > other:
                            self.props[i + 1][3] = a[i][self.index_aux2]

                if self.tag1 == -1:
                    for i in range(len(a)):
                        if i > other:
                            self.props[i + 1][3] = self.interpolate(
                                a[other][self.index_aux2], self.known1, a[other][self.index_aux2 + 1],
                                a[i][self.index_aux2], a[i][self.index_aux2 + 1],
                            )

    def looking_for_not_p_in_lc(self):
        tabela_lc = self.liq_comp
        for i in range(len(tabela_lc)):
            self.index_aux1 = self.find_index(tabela_lc[i][3][0], self.known1, tabela_lc[i][3][0], 2)

            b = []
            c = []
            if self.tag1 == 1:
                b.append(tabela_lc[i][2])
                for k in range(len(tabela_lc[i][3])):
                    b.append(tabela_lc[i][3][k][self.index_aux1])
                b_anterior = b

            if self.tag1 == -1:
                b.append(tabela_lc[i][2])
                b.append(self.known1)
                for k in range(len(tabela_lc[i][3])):
                    if k > 0:
                        value = self.interpolate(
                            tabela_lc[i][3][0][self.index_aux1], self.known1,
                            tabela_lc[i][3][0][self.index_aux1 + 1],
                            tabela_lc[i][3][k][self.index_aux1],
                            tabela_lc[i][3][k][self.index_aux1 + 1],
                        )
                        b.append(value)
                b_anterior = b

            if self.known2 == b_anterior[self.index2 - 1]:
                for k in range(len(b_anterior)):
                    if k != self.index2 - 1:
                        try:
                            self.props[k + 1][3] = b_anterior[k]
                        except IndexError:
                            pass
                break

            if i == len(tabela_lc) - 1:
                self.str_prop = self.list_props[self.index2]
                raise TypeError

            c.append(tabela_lc[i + 1][2])
            for k in range(len(tabela_lc[i + 1][3])):
                value = self.interpolate(
                    tabela_lc[i + 1][3][0][self.index_aux1], self.known1,
                    tabela_lc[i + 1][3][0][self.index_aux1 + 1],
                    tabela_lc[i + 1][3][k][self.index_aux1],
                    tabela_lc[i + 1][3][k][self.index_aux1 + 1],
                )
                c.append(value)
            b_proximo = c

            p_aux = [b_anterior[0], b_proximo[0]]
            b_anterior[0] = b_anterior[1]
            b_proximo[0] = b_proximo[1]
            b_anterior[1] = p_aux[0]
            b_proximo[1] = p_aux[1]

            if (
                (self.index2 == 4 and self.known2 < b_proximo[self.index2] and i < len(tabela_lc) - 1)
                or (self.index2 != 4 and self.known2 > b_proximo[self.index2] and i < len(tabela_lc) - 1)
            ):
                for k in range(len(b_anterior)):
                    if k != 0 and k != self.index2:
                        value = self.interpolate(
                            b_anterior[self.index2], self.known2, b_proximo[self.index2],
                            b_anterior[k], b_proximo[k],
                        )
                        try:
                            self.props[k][3] = value
                        except IndexError:
                            pass
                break

    def looking_for_p_in_vs(self):
        tabela_vs = self.vap_sup
        if self.index1 == 1:
            p = self.known1
            self.str_prop = self.props[self.index2][0]
        if self.index2 == 1:
            p = self.known2

        if p > tabela_vs[-1][2] or p < tabela_vs[0][2]:
            self.tag_error = 1
            self.str_prop = self.list_props[1]
            raise TypeError

        anterior = 0
        for i in range(len(tabela_vs)):
            if p == tabela_vs[i][2]:
                self.tag1 = 1
                anterior = i
                break
            elif p < tabela_vs[i][2]:
                anterior = i - 1
                self.tag1 = -1
                break
        self.index_aux2 = anterior

        a = []
        if self.tag1 == 1:
            for i in range(len(tabela_vs[self.index_aux2][3])):
                b = [
                    tabela_vs[self.index_aux2][3][i][j]
                    for j in range(len(tabela_vs[self.index_aux2][3][0]))
                    if j > 1
                ]
                a.append(b)

        if self.tag1 == -1:
            # Cópia local das linhas quando marcador == 1 para NUNCA mutar a tabela global em cache
            marcador = 1 if tabela_vs[self.index_aux2][3][0][3] != tabela_vs[self.index_aux2 + 1][3][0][3] else 0
            rows_curr = [
                (row[:3] + row[4:]) if marcador == 1 else row
                for row in tabela_vs[self.index_aux2][3]
            ]
            rows_next = tabela_vs[self.index_aux2 + 1][3]
            row_len = len(rows_curr[0])

            for i in range(len(rows_curr)):
                b = []
                if self.index1 == 0:
                    if self.n == 1:
                        self.tabela = tbs.tabelas.B_1_2
                        self.sat_props(0, self.known2)
                    else:
                        self.sat_props(1, self.known2)
                if i == 0:
                    b.append(self.sat_list[1][2] if self.n == 1 else self.sat_list[0][2])
                else:
                    b.append(self.sat_list[(2 * i) + 1][2])

                for j in range(3, row_len):
                    value = self.interpolate(
                        tabela_vs[self.index_aux2][2], p, tabela_vs[self.index_aux2 + 1][2],
                        rows_curr[i][j], rows_next[i][j],
                    )
                    b.append(value)
                a.append(b)

        other = 0
        if self.index1 == 1:
            self.str_prop = self.list_props[self.index2]
            if self.index2 != 0:
                other = self.index2 - 1
                if self.known2 < min(a[other]) or self.known2 > max(a[other]):
                    raise TypeError

            self.index_aux1 = self.find_index(a[other], self.known2, a[other], 0)

            if self.tag1 == 1:
                for i in range(len(a)):
                    if i != other:
                        target_idx = 0 if i == 0 else i + 1
                        self.props[target_idx][3] = a[i][self.index_aux1]

            if self.tag1 == -1:
                for i in range(len(a)):
                    if i != other:
                        target_idx = 0 if i == 0 else i + 1
                        self.props[target_idx][3] = self.interpolate(
                            a[other][self.index_aux1], self.known2, a[other][self.index_aux1 + 1],
                            a[i][self.index_aux1], a[i][self.index_aux1 + 1],
                        )

        if self.index2 == 1:
            self.str_prop = self.list_props[0]
            if self.known1 < min(a[other]) or self.known1 > max(a[other]):
                raise TypeError

            self.index_aux2 = self.find_index(a[other], self.known1, a[other], 0)

            if self.tag1 == 1:
                for i in range(len(a)):
                    if i > other:
                        self.props[i + 1][3] = a[i][self.index_aux2]

            if self.tag1 == -1:
                for i in range(len(a)):
                    if i > other:
                        self.props[i + 1][3] = self.interpolate(
                            a[other][self.index_aux2], self.known1, a[other][self.index_aux2 + 1],
                            a[i][self.index_aux2], a[i][self.index_aux2 + 1],
                        )

    def looking_for_not_p_in_vs(self):
        tabela_vs = self.vap_sup
        for i in range(len(tabela_vs)):
            self.index_aux1 = self.find_index(tabela_vs[i][3][0], self.known1, tabela_vs[i][3][0], 2)

            b = []
            c = []
            if self.tag1 == 1:
                b.append(tabela_vs[i][2])
                for k in range(len(tabela_vs[i][3])):
                    b.append(tabela_vs[i][3][k][self.index_aux1])
                b_anterior = b

            if self.tag1 == -1:
                b.append(tabela_vs[i][2])
                b.append(self.known1)
                for k in range(len(tabela_vs[i][3])):
                    if k > 0:
                        value = self.interpolate(
                            tabela_vs[i][3][0][self.index_aux1], self.known1,
                            tabela_vs[i][3][0][self.index_aux1 + 1],
                            tabela_vs[i][3][k][self.index_aux1],
                            tabela_vs[i][3][k][self.index_aux1 + 1],
                        )
                        b.append(value)
                b_anterior = b

            if self.known2 == b_anterior[self.index2 - 1]:
                for k in range(len(b_anterior)):
                    if k != self.index2 - 1:
                        try:
                            self.props[k + 1][3] = b_anterior[k]
                        except IndexError:
                            pass
                break

            if i == len(tabela_vs) - 1:
                self.str_prop = self.list_props[self.index2]
                raise TypeError

            # Ajusta índice sem mutar tabela_vs[i] in-place
            if tabela_vs[i][3][0][3] != tabela_vs[i + 1][3][0][3]:
                self.index_aux1 = self.index_aux1 - 1

            c.append(tabela_vs[i + 1][2])
            for k in range(len(tabela_vs[i + 1][3])):
                try:
                    value = self.interpolate(
                        tabela_vs[i + 1][3][0][self.index_aux1],
                        self.known1,
                        tabela_vs[i + 1][3][0][self.index_aux1 + 1],
                        tabela_vs[i + 1][3][k][self.index_aux1],
                        tabela_vs[i + 1][3][k][self.index_aux1 + 1],
                    )
                except IndexError:
                    raise TypeError("Índices fora dos limites da tabela.")
                c.append(value)
            b_proximo = c

            if self.known2 > b_proximo[self.index2] and i < len(tabela_vs) - 1:
                for k in range(len(b_anterior)):
                    if k != 1 and k != self.index2:
                        value = self.interpolate(
                            b_anterior[self.index2], self.known2, b_proximo[self.index2],
                            b_anterior[k], b_proximo[k],
                        )
                        self.props[k][3] = value
                self.props[1][3] = self.props[0][3]
                self.props[0][3] = self.known1
                break


# Alias de retrocompatibilidade para views de água
agua_cls = subs_cls


# ==============================================================================
# FUNÇÕES DE ALTO NÍVEL PARA ESTADOS E PROCESSOS DE SUBSTÂNCIAS PURAS
# ==============================================================================

def format_mass_display(mass):
    """Formata a massa para exibição (ex: 1.0 -> 1.0, 2.5 -> 2.5)."""
    m = float(mass or 1.0)
    return round(m, 4) if m != int(m) else round(m, 1)


def extract_and_validate_state(results, min_pressure=None, err_msg_pressure=None, require_sat_volumes=True, mass=1.0):
    """
    Extrai e valida as propriedades de um resultado [fase, sat_list, props].
    Multiplica os volumes totais das fases líquida (VolumeL) e vapor (VolumeV) pela massa m.
    Levanta CalculationTypeError ou ValidationError em caso de inconsistência.
    """
    m = float(mass or 1.0)
    fase = results[0]
    try:
        temperatura = round(results[2][0][3], 2)
        pressao = round(results[2][1][3], 2)
        if min_pressure is not None and pressao < min_pressure:
            raise ValidationError(err_msg_pressure or "Erro: A pressão não pode ser negativa.")
        volume_esp = round(results[2][2][3], 8)
        energia_int = round(results[2][3][3], 2)
        entalpia_esp = round(results[2][4][3], 2)
        entropia_esp = round(results[2][5][3], 4)
    except (IndexError, TypeError):
        raise CalculationTypeError

    if (energia_int == 0 and entalpia_esp == 0 and entropia_esp == 0) or volume_esp == 0:
        raise CalculationTypeError

    if pressao == 0 and entropia_esp == 0:
        raise CalculationTypeError

    if fase == 3:
        tit = round(results[2][6][3], 2)
        try:
            volume_v = results[1][3][2]
            volume_l = results[1][2][2]
            VolumeL_esp = round((1 - (tit / 100)) * volume_l, 8)
            VolumeV_esp = (tit / 100) * volume_v
            VolumeL = round(VolumeL_esp * m, 8)
            VolumeV = VolumeV_esp * m
        except (IndexError, TypeError):
            raise CalculationTypeError
    else:
        tit = None
        VolumeL = None
        VolumeV = None
        VolumeL_esp = None
        VolumeV_esp = None

    try:
        volume_v = results[1][3][2]
    except IndexError:
        volume_v = None

    try:
        volume_l = results[1][2][2]
    except IndexError:
        volume_l = None

    if require_sat_volumes:
        if volume_v is None or volume_l is None:
            raise CalculationTypeError
    else:
        if fase == 3 and (volume_v is None or volume_l is None):
            raise CalculationTypeError

    return {
        'fase': fase,
        'temperatura': round(temperatura, 2),
        'pressao': pressao,
        'volume_esp': volume_esp,
        'energia_int': energia_int,
        'entalpia_esp': entalpia_esp,
        'entropia_esp': entropia_esp,
        'tit': tit,
        'volume_v': volume_v,
        'volume_l': volume_l,
        'VolumeV': VolumeV,
        'VolumeL': VolumeL,
        'VolumeV_esp': VolumeV_esp,
        'VolumeL_esp': VolumeL_esp,
        'results': results,
    }


def compute_single_state_context(opt, prop1, prop2, val1, val2, mass=1.0):
    """Calcula um único estado termodinâmico (módulos 'estado' e 'propriedade')."""
    m = float(mass or 1.0)
    h = subs_cls(opt, prop1, prop2, val1, val2)
    st = extract_and_validate_state(h.results, min_pressure=None, require_sat_volumes=False, mass=m)
    return {
        'fase': st['fase'],
        'massa': format_mass_display(m),
        'massa_float': m,
        'temperatura': st['temperatura'],
        'pressao': st['pressao'],
        'volume_especifico': round(st['volume_esp'], 6),
        'energia_interna': st['energia_int'],
        'entalpia_especifica': st['entalpia_esp'],
        'entropia_especifica': st['entropia_esp'],
        'teste': h.results,
        'titulo': st['tit'],
        'titulo_fracao': format_quality_fraction(st['tit']),
        'VolumeV': round(st['VolumeV'], 6) if st['VolumeV'] is not None else None,
        'VolumeL': round(st['VolumeL'], 6) if st['VolumeL'] is not None else None,
        'VolumeL_esp': round(st['VolumeL_esp'], 8) if st['VolumeL_esp'] is not None else None,
        'volume_v': st['volume_v'],
        'volume_l': st['volume_l'],
    }


def compute_pcte_process_context(opt, state1_inputs, third_prop, third_val, temp_viz, lista_estados, pontos_grafico, mass=1.0):
    """Calcula processo isobárico (Pressão Constante) para qualquer substância pura (opt 1..7)."""
    m = float(mass or 1.0)
    min_p = SUBSTANCE_CONFIG[opt]['min_pressure']

    if lista_estados:
        ultimo_estado = lista_estados[-1]
        st1 = extract_and_validate_state(
            ultimo_estado,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão inicial não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
    else:
        prop1, prop2, val1, val2 = state1_inputs
        h1 = subs_cls(opt, prop1, prop2, val1, val2)
        st1 = extract_and_validate_state(
            h1.results,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão calculada ou inserida não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
        lista_estados.append(h1.results)

    pressao = st1['pressao']
    entalpia_esp = st1['entalpia_esp']
    entropia_esp = st1['entropia_esp']
    volume_esp = st1['volume_esp']

    if third_prop == 8:
        calor = third_val
        entalpia_esp3 = round((calor / m) + entalpia_esp, 6)
        h2 = subs_cls(opt, 1, 4, pressao, entalpia_esp3)
    else:
        h2 = subs_cls(opt, 1, third_prop, pressao, third_val)

    st2 = extract_and_validate_state(
        h2.results,
        min_pressure=min_p,
        err_msg_pressure="Erro: A pressão resultante do segundo estado não pode ser negativa.",
        require_sat_volumes=True,
        mass=m,
    )

    if third_prop != 8:
        calor = round(m * (st2['entalpia_esp'] - entalpia_esp), 6)
    entropia_ger = round(m * (st2['entropia_esp'] - entropia_esp) - (calor / (temp_viz + 273.15)), 6)
    trabalho = round(m * (st2['volume_esp'] - volume_esp) * pressao, 6)

    # Geração de microprocessos via Entalpia (h)
    val_inicial = entalpia_esp
    val_final = st2['entalpia_esp']
    pontos_criticos = []
    try:
        h_sat_l = subs_cls(opt, 1, 6, pressao, 0)
        h_sat_v = subs_cls(opt, 1, 6, pressao, 100)
        val_sat_l = h_sat_l.results[2][4][3]
        val_sat_v = h_sat_v.results[2][4][3]
        limite_inf = min(val_inicial, val_final)
        limite_sup = max(val_inicial, val_final)
        if limite_inf < val_sat_l < limite_sup:
            pontos_criticos.append(val_sat_l)
        if limite_inf < val_sat_v < limite_sup:
            pontos_criticos.append(val_sat_v)
    except Exception:
        pass

    num_passos = 150
    passo = (val_final - val_inicial) / num_passos if val_final != val_inicial else 0
    valores_iteracao = [val_inicial + (i * passo) for i in range(1, num_passos)]
    valores_iteracao.extend(pontos_criticos)
    valores_iteracao = sorted(list(set(valores_iteracao)), reverse=(val_inicial > val_final))

    ramo_atual = [{
        'T': st1['temperatura'],
        'P': round(pressao, 2),
        'v': round(volume_esp, 6),
        's': round(entropia_esp, 4),
        'h': round(entalpia_esp, 2),
        'u': round(entalpia_esp - pressao * volume_esp, 6),
        'fase': st1['fase'],
        'vl': round(st1['volume_l'], 8) if st1['volume_l'] else round(volume_esp, 8),
    }]

    for val_atual in valores_iteracao:
        try:
            h_micro = subs_cls(opt, 1, 4, pressao, val_atual)
            v_micro = h_micro.results[2][2][3]
            if v_micro != 0:
                fase_micro = h_micro.results[0]
                try:
                    vl_micro = h_micro.results[1][2][2] if fase_micro == 3 else v_micro
                except IndexError:
                    vl_micro = v_micro
                ramo_atual.append({
                    'T': round(h_micro.results[2][0][3], 2),
                    'P': round(h_micro.results[2][1][3], 2),
                    'v': round(v_micro, 6),
                    's': round(h_micro.results[2][5][3], 4),
                    'h': round(h_micro.results[2][4][3], 2),
                    'u': round(h_micro.results[2][4][3] - h_micro.results[2][1][3] * v_micro, 6),
                    'fase': fase_micro,
                    'vl': round(vl_micro, 8),
                })
        except (IndexError, TypeError, BoundariesException):
            continue

    ramo_atual.append({
        'T': st2['temperatura'],
        'P': round(st2['pressao'], 2),
        'v': round(st2['volume_esp'], 6),
        's': round(st2['entropia_esp'], 4),
        'h': round(st2['entalpia_esp'], 2),
        'u': round(st2['entalpia_esp'] - st2['pressao'] * st2['volume_esp'], 6),
        'fase': st2['fase'],
        'vl': round(st2['volume_l'], 8) if st2['volume_l'] else round(st2['volume_esp'], 8),
    })

    pontos_grafico.append(ramo_atual)
    lista_estados.append(h2.results)

    context = {
        'fase': st1['fase'],
        'massa': format_mass_display(m),
        'massa_float': m,
        'temperatura': st1['temperatura'],
        'pressao': st1['pressao'],
        'volume_especifico': st1['volume_esp'],
        'energia_interna': st1['energia_int'],
        'entalpia_especifica': st1['entalpia_esp'],
        'entropia_especifica': st1['entropia_esp'],
        'titulo': st1['tit'],
        'titulo_fracao': format_quality_fraction(st1['tit']),
        'volume_v': st1['volume_v'],
        'volume_l': st1['volume_l'],
        'VolumeV': st1['VolumeV'],
        'VolumeL': st1['VolumeL'],
        'VolumeL_esp': st1['VolumeL_esp'],
        'fase2': st2['fase'],
        'temperatura2': st2['temperatura'],
        'pressao2': st2['pressao'],
        'volume_especifico2': st2['volume_esp'],
        'energia_interna2': st2['energia_int'],
        'entalpia_especifica2': st2['entalpia_esp'],
        'entropia_especifica2': st2['entropia_esp'],
        'titulo2': st2['tit'],
        'titulo2_fracao': format_quality_fraction(st2['tit']),
        'volume_v2': st2['volume_v'],
        'volume_l2': st2['volume_l'],
        'VolumeV2': st2['VolumeV'],
        'VolumeL2': st2['VolumeL'],
        'VolumeL2_esp': st2['VolumeL_esp'],
        'TempViz': temp_viz,
        'Escolha': third_prop,
        'Calor': calor,
        'Sger': entropia_ger,
        'Trabalho': trabalho,
        'teste3': lista_estados,
        'pontos_grafico_json': json.dumps(pontos_grafico),
    }
    return context, lista_estados, pontos_grafico


def compute_scte_process_context(opt, state1_inputs, third_prop, third_val, lista_estados, pontos_grafico, mass=1.0):
    """Calcula processo isentrópico (Adiabático Reversível) para qualquer substância pura (opt 1..7)."""
    m = float(mass or 1.0)
    min_p = SUBSTANCE_CONFIG[opt]['min_pressure']

    if lista_estados:
        ultimo_estado = lista_estados[-1]
        st1 = extract_and_validate_state(
            ultimo_estado,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão inicial não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
    else:
        pontos_grafico = []
        prop1, prop2, val1, val2 = state1_inputs
        h1 = subs_cls(opt, prop1, prop2, val1, val2)
        st1 = extract_and_validate_state(
            h1.results,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão calculada ou inserida não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
        lista_estados.append(h1.results)

    pressao = st1['pressao']
    energia_int = st1['energia_int']
    entalpia_esp = st1['entalpia_esp']
    entropia_esp = st1['entropia_esp']
    volume_esp = st1['volume_esp']

    if third_prop == 7:
        energia_int3 = round((third_val / m) + energia_int, 6)
        h2 = subs_cls(opt, 1, 4, pressao, energia_int3)
        st2 = extract_and_validate_state(
            h2.results,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão resultante do segundo estado não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
        trabalho = round(m * (st2['energia_int'] - energia_int), 6)
        teste = h2.results
        teste3 = None
    else:
        h2 = subs_cls(opt, third_prop, 5, third_val, entropia_esp)
        st2 = extract_and_validate_state(
            h2.results,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão resultante do segundo estado não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
        trabalho = round(m * (st2['energia_int'] - energia_int), 6)
        lista_estados.append(h2.results)
        teste = lista_estados[-1]
        teste3 = lista_estados

    estado_inicial = {
        'T': round(st1['temperatura'], 6), 'P': round(pressao, 6), 'v': round(volume_esp, 10),
        's': round(entropia_esp, 6), 'h': round(entalpia_esp, 6),
        'u': round(entalpia_esp - pressao * volume_esp, 6), 'fase': st1['fase'],
    }
    estado_final = {
        'T': round(st2['temperatura'], 6), 'P': round(st2['pressao'], 6), 'v': round(st2['volume_esp'], 10),
        's': round(st2['entropia_esp'], 6), 'h': round(st2['entalpia_esp'], 6),
        'u': round(st2['entalpia_esp'] - st2['pressao'] * st2['volume_esp'], 6), 'fase': st2['fase'],
    }

    is_isobaric = (third_prop == 7)
    cruzou_domo = (st1['fase'] != st2['fase'])
    pt_fronteira = None

    if cruzou_domo:
        if is_isobaric:
            val_a, val_b, fixo_val = entalpia_esp, st2['entalpia_esp'], pressao
        else:
            val_a, val_b, fixo_val = pressao, st2['pressao'], entropia_esp

        for _ in range(60):
            val_mid = (val_a + val_b) / 2.0
            try:
                if is_isobaric:
                    h_mid = subs_cls(opt, 1, 4, fixo_val, val_mid)
                else:
                    h_mid = subs_cls(opt, 1, 5, val_mid, fixo_val)
                if h_mid.results[0] == st1['fase']:
                    val_a = val_mid
                else:
                    val_b = val_mid
            except Exception:
                val_b = val_mid

        val_front = val_a if st1['fase'] == 3 else val_b
        try:
            if is_isobaric:
                h_front_calc = subs_cls(opt, 1, 4, fixo_val, val_front)
            else:
                h_front_calc = subs_cls(opt, 1, 5, val_front, fixo_val)
            pt_fronteira = {
                'T': round(h_front_calc.results[2][0][3], 6),
                'P': round(h_front_calc.results[2][1][3], 6),
                'v': round(h_front_calc.results[2][2][3], 10),
                's': round(h_front_calc.results[2][5][3], 6),
                'h': round(h_front_calc.results[2][4][3], 6),
                'u': round(h_front_calc.results[2][4][3] - h_front_calc.results[2][1][3] * h_front_calc.results[2][2][3], 6),
                'fase': 'fronteira',
            }
        except Exception:
            pass

    def gerar_segmento(pt_A, pt_B, num_pontos):
        segmento = []
        if not pt_A or not pt_B:
            return segmento
        use_log_P = pt_A['P'] > 0 and pt_B['P'] > 0
        use_log_v = pt_A['v'] > 0 and pt_B['v'] > 0
        if use_log_P:
            log_P_A, log_P_B = math.log10(pt_A['P']), math.log10(pt_B['P'])
        if use_log_v:
            log_v_A, log_v_B = math.log10(pt_A['v']), math.log10(pt_B['v'])

        for i in range(num_pontos + 1):
            f = i / float(num_pontos)
            t_i = pt_A['T'] + f * (pt_B['T'] - pt_A['T'])
            s_i = pt_A['s'] + f * (pt_B['s'] - pt_A['s'])
            h_i = pt_A['h'] + f * (pt_B['h'] - pt_A['h'])
            p_i = 10 ** (log_P_A + f * (log_P_B - log_P_A)) if use_log_P else pt_A['P'] + f * (pt_B['P'] - pt_A['P'])
            v_i = 10 ** (log_v_A + f * (log_v_B - log_v_A)) if use_log_v else pt_A['v'] + f * (pt_B['v'] - pt_A['v'])

            if is_isobaric:
                p_i = pt_A['P']
            else:
                s_i = pt_A['s']

            segmento.append({
                'T': round(t_i, 6), 'P': round(p_i, 6), 'v': round(v_i, 10),
                's': round(s_i, 6), 'h': round(h_i, 6), 'u': round(h_i - p_i * v_i, 6),
            })
        return segmento

    if pt_fronteira:
        trecho1 = gerar_segmento(estado_inicial, pt_fronteira, 150)
        trecho2 = gerar_segmento(pt_fronteira, estado_final, 150)
        if trecho1:
            trecho1.pop()
        pontos_finais = trecho1 + trecho2
    else:
        pontos_finais = gerar_segmento(estado_inicial, estado_final, 300)

    pontos_grafico.append(pontos_finais)

    context = {
        'fase': st1['fase'],
        'massa': format_mass_display(m),
        'massa_float': m,
        'temperatura': st1['temperatura'],
        'pressao': st1['pressao'],
        'volume_especifico': st1['volume_esp'],
        'energia_interna': st1['energia_int'],
        'entalpia_especifica': st1['entalpia_esp'],
        'entropia_especifica': st1['entropia_esp'],
        'titulo': st1['tit'],
        'titulo_fracao': format_quality_fraction(st1['tit']),
        'volume_v': st1['volume_v'],
        'volume_l': st1['volume_l'],
        'VolumeV': st1['VolumeV'],
        'VolumeL': st1['VolumeL'],
        'VolumeL_esp': st1['VolumeL_esp'],
        'fase2': st2['fase'],
        'temperatura2': st2['temperatura'],
        'pressao2': st2['pressao'],
        'volume_especifico2': st2['volume_esp'],
        'energia_interna2': st2['energia_int'],
        'entalpia_especifica2': st2['entalpia_esp'],
        'entropia_especifica2': st2['entropia_esp'],
        'titulo2': st2['tit'],
        'titulo2_fracao': format_quality_fraction(st2['tit']),
        'volume_v2': st2['volume_v'],
        'volume_l2': st2['volume_l'],
        'VolumeV2': st2['VolumeV'],
        'VolumeL2': st2['VolumeL'],
        'VolumeL2_esp': st2['VolumeL_esp'],
        'teste': teste,
        'teste3': teste3,
        'Escolha': third_prop,
        'Trabalho': trabalho,
        'pontos_grafico_json': json.dumps(pontos_grafico),
    }
    return context, lista_estados, pontos_grafico


def compute_vcte_process_context(opt, state1_inputs, third_prop, third_val, temp_viz, lista_estados, pontos_grafico, mass=1.0):
    """Calcula processo isocórico (Volume Constante) para qualquer substância pura (opt 1..7)."""
    m = float(mass or 1.0)
    min_p = SUBSTANCE_CONFIG[opt]['min_pressure']

    if lista_estados:
        ultimo_estado = lista_estados[-1]
        st1 = extract_and_validate_state(
            ultimo_estado,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão inicial não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
    else:
        pontos_grafico = []
        prop1, prop2, val1, val2 = state1_inputs
        h1 = subs_cls(opt, prop1, prop2, val1, val2)
        st1 = extract_and_validate_state(
            h1.results,
            min_pressure=min_p,
            err_msg_pressure="Erro: A pressão calculada ou inserida não pode ser negativa.",
            require_sat_volumes=True,
            mass=m,
        )
        lista_estados.append(h1.results)

    volume_esp = st1['volume_esp']
    energia_int = st1['energia_int']
    entalpia_esp = st1['entalpia_esp']
    entropia_esp = st1['entropia_esp']
    pressao = st1['pressao']
    temperatura = st1['temperatura']

    h2 = subs_cls(opt, third_prop, 2, third_val, volume_esp)
    st2 = extract_and_validate_state(
        h2.results,
        min_pressure=min_p,
        err_msg_pressure="Erro: A pressão resultante do segundo estado não pode ser negativa.",
        require_sat_volumes=True,
        mass=m,
    )

    calor = round(m * (st2['energia_int'] - energia_int), 6)
    entropia_ger = round(m * (st2['entropia_esp'] - entropia_esp) - (calor / (temp_viz + 273.15)), 6)

    lista_estados.append(h2.results)
    teste = lista_estados

    val_fixo = volume_esp
    estado_inicial = {
        'T': round(temperatura, 6), 'P': round(pressao, 6), 'v': round(val_fixo, 10),
        's': round(entropia_esp, 6), 'h': round(entalpia_esp, 6),
        'u': round(entalpia_esp - pressao * val_fixo, 6), 'fase': st1['fase'],
    }
    estado_final = {
        'T': round(st2['temperatura'], 6), 'P': round(st2['pressao'], 6), 'v': round(val_fixo, 10),
        's': round(st2['entropia_esp'], 6), 'h': round(st2['entalpia_esp'], 6),
        'u': round(st2['entalpia_esp'] - st2['pressao'] * val_fixo, 6), 'fase': st2['fase'],
    }

    pt_fronteira = None
    if st1['fase'] != st2['fase']:
        t_a, t_b = temperatura, st2['temperatura']
        for _ in range(60):
            t_mid = (t_a + t_b) / 2.0
            try:
                h_mid = subs_cls(opt, 0, 2, t_mid, val_fixo)
                if h_mid.results[0] == st1['fase']:
                    t_a = t_mid
                else:
                    t_b = t_mid
            except Exception:
                t_b = t_mid

        t_front = t_a if st1['fase'] == 3 else t_b
        try:
            h_front_calc = subs_cls(opt, 0, 2, t_front, val_fixo)
            pt_fronteira = {
                'T': round(t_front, 6),
                'P': round(h_front_calc.results[2][1][3], 6),
                'v': round(val_fixo, 10),
                's': round(h_front_calc.results[2][5][3], 6),
                'h': round(h_front_calc.results[2][4][3], 6),
                'u': round(h_front_calc.results[2][4][3] - h_front_calc.results[2][1][3] * val_fixo, 6),
                'fase': 'fronteira',
            }
        except Exception:
            pass

    def gerar_segmento(pt_A, pt_B, num_pontos):
        segmento = []
        if not pt_A or not pt_B:
            return segmento
        use_log_P = pt_A['P'] > 0 and pt_B['P'] > 0
        if use_log_P:
            log_P_A, log_P_B = math.log10(pt_A['P']), math.log10(pt_B['P'])
        for i in range(num_pontos + 1):
            f = i / float(num_pontos)
            t_i = pt_A['T'] + f * (pt_B['T'] - pt_A['T'])
            s_i = pt_A['s'] + f * (pt_B['s'] - pt_A['s'])
            h_i = pt_A['h'] + f * (pt_B['h'] - pt_A['h'])
            p_i = 10 ** (log_P_A + f * (log_P_B - log_P_A)) if use_log_P else pt_A['P'] + f * (pt_B['P'] - pt_A['P'])
            v_i = val_fixo
            segmento.append({
                'T': round(t_i, 6), 'P': round(p_i, 6), 'v': round(v_i, 10),
                's': round(s_i, 6), 'h': round(h_i, 6), 'u': round(h_i - p_i * v_i, 6),
            })
        return segmento

    if pt_fronteira:
        trecho1 = gerar_segmento(estado_inicial, pt_fronteira, 150)
        trecho2 = gerar_segmento(pt_fronteira, estado_final, 150)
        if trecho1:
            trecho1.pop()
        pontos_finais = trecho1 + trecho2
    else:
        pontos_finais = gerar_segmento(estado_inicial, estado_final, 300)

    pontos_grafico.append(pontos_finais)

    context = {
        'fase': st1['fase'],
        'massa': format_mass_display(m),
        'massa_float': m,
        'temperatura': st1['temperatura'],
        'pressao': st1['pressao'],
        'volume_especifico': st1['volume_esp'],
        'energia_interna': st1['energia_int'],
        'entalpia_especifica': st1['entalpia_esp'],
        'entropia_especifica': st1['entropia_esp'],
        'titulo': st1['tit'],
        'titulo_fracao': format_quality_fraction(st1['tit']),
        'volume_v': st1['volume_v'],
        'volume_l': st1['volume_l'],
        'VolumeV': st1['VolumeV'],
        'VolumeL': st1['VolumeL'],
        'VolumeL_esp': st1['VolumeL_esp'],
        'fase2': st2['fase'],
        'temperatura2': st2['temperatura'],
        'pressao2': st2['pressao'],
        'volume_especifico2': st2['volume_esp'],
        'energia_interna2': st2['energia_int'],
        'entalpia_especifica2': st2['entalpia_esp'],
        'entropia_especifica2': st2['entropia_esp'],
        'titulo2': st2['tit'],
        'titulo2_fracao': format_quality_fraction(st2['tit']),
        'volume_v2': st2['volume_v'],
        'volume_l2': st2['volume_l'],
        'VolumeV2': st2['VolumeV'],
        'VolumeL2': st2['VolumeL'],
        'VolumeL2_esp': st2['VolumeL_esp'],
        'teste': teste,
        'teste3': teste,
        'TempViz': temp_viz,
        'Escolha': third_prop,
        'Calor': calor,
        'Sger': entropia_ger,
        'pontos_grafico_json': json.dumps(pontos_grafico),
    }
    return context, lista_estados, pontos_grafico


# ==============================================================================
# MOTOR DE GÁS IDEAL
# ==============================================================================

def to_kelvin(T):
    return T + 273.15 if T is not None else None


def to_celsius(T):
    return T - 273.15 if T is not None else None


def rd(x):
    return round(x, 4) if x is not None else None


def resolve_ideal_gas_constants(c1_idx, c1_val, c2_idx, c2_val):
    """
    Resolve Cv0, Cp0, R, K a partir de duas constantes informadas pelo usuário
    (11: Cv0, 12: Cp0, 13: R, 14: K).
    """
    const_values = {c1_idx: c1_val, c2_idx: c2_val}
    Cv0 = const_values.get(11)
    Cp0 = const_values.get(12)
    R = const_values.get(13)
    K = const_values.get(14)

    if Cp0 is not None and Cv0 is not None:
        R = Cp0 - Cv0
        K = Cp0 / Cv0 if Cv0 != 0 else None
    elif Cp0 is not None and R is not None:
        Cv0 = Cp0 - R
        K = Cp0 / Cv0 if Cv0 != 0 else None
    elif Cv0 is not None and R is not None:
        Cp0 = Cv0 + R
        K = Cp0 / Cv0 if Cv0 != 0 else None
    elif R is not None and K is not None:
        if K != 1:
            Cv0 = R / (K - 1)
            Cp0 = K * Cv0
    elif Cv0 is not None and K is not None:
        Cp0 = K * Cv0
        R = Cp0 - Cv0
    elif Cp0 is not None and K is not None:
        if K != 0:
            Cv0 = Cp0 / K
            R = Cp0 - Cv0

    return Cv0, Cp0, R, K


def compute_ideal_gas_single_state(prop1, prop2, val1, val2, R_val):
    """
    Calcula (temperatura_c, pressao, volume) pela equação de estado p*v = R*T.
    0: Temperatura (°C), 1: Pressão (kPa), 2: Volume específico (m³/kg).
    """
    temperatura_c = pressao = volume = None
    if prop1 == 0 and prop2 == 1:
        temperatura_c = val1
        temperatura_k = temperatura_c + 273.15
        pressao = val2
        volume = (R_val * temperatura_k) / pressao
    elif prop1 == 0 and prop2 == 2:
        temperatura_c = val1
        temperatura_k = temperatura_c + 273.15
        volume = val2
        pressao = (temperatura_k * R_val) / volume
    elif prop1 == 1 and prop2 == 0:
        pressao = val1
        temperatura_c = val2
        temperatura_k = temperatura_c + 273.15
        volume = (R_val * temperatura_k) / pressao
    elif prop1 == 1 and prop2 == 2:
        pressao = val1
        volume = val2
        temperatura_k = (pressao * volume) / R_val
        temperatura_c = temperatura_k - 273.15
    elif prop1 == 2 and prop2 == 0:
        volume = val1
        temperatura_c = val2
        temperatura_k = temperatura_c + 273.15
        pressao = (temperatura_k * R_val) / volume
    elif prop1 == 2 and prop2 == 1:
        volume = val1
        pressao = val2
        temperatura_k = (pressao * volume) / R_val
        temperatura_c = temperatura_k - 273.15
    return temperatura_c, pressao, volume



def format_quality_fraction(tit_pct):
    """Converte o título percentual (0..100) em fração decimal formatada (0.0000..1.0000)."""
    if tit_pct is None or tit_pct == '':
        return None
    try:
        val = float(str(tit_pct).replace(',', '.')) / 100.0
        return f"{val:.4f}"
    except (TypeError, ValueError):
        return None


def compute_cycle_balance(process_list):
    """
    Calcula o balanço termodinâmico global de uma sequência de processos encadeados.
    Cada item em process_list deve ser um dict com chaves numéricas/string 'Q', 'W', 'Sger'.
    Retorna dict com W_liq, Q_H, Q_L, Q_liq, Sger_total, eficiencia_termica (%), cop_refrigeracao e cop_bomba_calor.
    """
    def _to_float(v):
        if v is None or v == '':
            return 0.0
        return float(str(v).replace(',', '.'))

    w_liq = 0.0
    q_h = 0.0
    q_l = 0.0
    q_liq = 0.0
    sger_total = 0.0

    for proc in process_list or []:
        q = _to_float(proc.get('Q', 0.0))
        w = _to_float(proc.get('W', 0.0))
        sger = _to_float(proc.get('Sger', 0.0))
        w_liq += w
        q_liq += q
        if q > 0:
            q_h += q
        elif q < 0:
            q_l += abs(q)
        sger_total += sger

    eficiencia = round((w_liq / q_h) * 100.0, 2) if (w_liq > 0 and q_h > 0) else None
    cop_ref = round(q_h / abs(w_liq), 3) if (w_liq < 0 and q_h > 0) else None
    cop_bc = round(q_l / abs(w_liq), 3) if (w_liq < 0 and q_l > 0) else None

    return {
        'W_liq': round(w_liq, 4),
        'Q_H': round(q_h, 4),
        'Q_L': round(q_l, 4),
        'Q_liq': round(q_liq, 4),
        'Sger_total': round(sger_total, 5),
        'eficiencia_termica': eficiencia,
        'cop_refrigeracao': cop_ref,
        'cop_bomba_calor': cop_bc,
    }

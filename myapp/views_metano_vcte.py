# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from .forms import vcteKelvin, vcteKelvin2, vcteKelvin3, vcteKelvin4
from django.core.exceptions import ValidationError
from . import tabelas_termoprop as tbs
from . import estados as std
import json

if not hasattr(std, 'instancia_estados'):
    std.instancia_estados = std.estados_cls()

estados = std.instancia_estados

def homepage_view42(request):
    return render(request, 'Inicio.html')

###############################################################################

def ask_known1_view42(request):
    estados.limpar_estados()  # limpa a lista
    if request.method == 'POST':
        form = vcteKelvin(request.POST)
        if form.is_valid():
            property_choice = form.cleaned_data['property_choice']
            value_input = form.cleaned_data['value_input']
            # Armazena as escolhas e valores na sessão
            request.session['property_choice'] = property_choice
            request.session['value_input'] = value_input
            # Armazena as propriedades excluídas para a próxima view
            request.session['excluded_properties'] = [int(property_choice)]
            return redirect('ask_known2_42')
    else:
        form = vcteKelvin()

    return render(request, 'metano/mkelvin-vcte-1.html', {'form': form})

###############################################################################

def ask_known2_view42(request):
    # Recupera as propriedades excluídas da sessão
    excluded_properties = request.session.get('excluded_properties', [])

    if request.method == 'POST':
        form = vcteKelvin2(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            second_property_choice = form.cleaned_data['property_choice']
            second_value_input = form.cleaned_data['value_input']
            # Armazena as novas escolhas e valores na sessão
            request.session['second_property_choice'] = second_property_choice
            request.session['second_value_input'] = second_value_input
            # Atualiza a lista de propriedades excluídas
            excluded_properties.append(int(second_property_choice))
            request.session['excluded_properties'] = excluded_properties
            return redirect('ask_known3_42')
    else:
        form = vcteKelvin2(excluded_properties=excluded_properties)

    return render(request, 'metano/mkelvin-vcte-2.html', {'form': form})

###############################################################################

def ask_known3_view42(request):
    if request.method == 'POST':
        form = vcteKelvin3(request.POST)
        if form.is_valid():
            temp_value_input = form.cleaned_data['value_input']
            # Armazena o valor da temperatura da vizinhança
            request.session['temp_value_input'] = temp_value_input
            return redirect('ask_known4_42')
    else:
        form = vcteKelvin3()

    return render(request, 'metano/mkelvin-vcte-3.html', {'form': form})

###############################################################################

def ask_known4_view42(request):
    if request.method == 'POST':
        form = vcteKelvin4(request.POST)
        if form.is_valid():
            third_property_choice = form.cleaned_data['property_choice']
            third_value_input = form.cleaned_data['value_input']
            # Armazena as novas escolhas e valores na sessão
            request.session['third_property_choice'] = third_property_choice
            request.session['third_value_input'] = third_value_input
            # Atualiza a lista de propriedades excluídas
            request.session['excluded_properties'] = [int(third_property_choice)]
            return redirect('process_values_42')
    else:
        form = vcteKelvin4()

    return render(request, 'metano/mkelvin-vcte-4.html', {'form': form})

###############################################################################

class subs_cls:
    """SUBS"""
    '''
    Calcula e imprime o valor das propriedades de diferentes substâncias a partir do valor conhecido de duas propriedades. Valores dados pelas tabelas B.2 a B.7.
    '''

    classe = 'Subs'

###############################################################################

    def __init__(self, opt, a, b, c, d):
        '''Construtor'''
        self.n = opt
        self.index1 = a
        self.index2 = b
        self.known1 = c
        self.known2 = d
        self.results = []
        self.run()

   ###############################################################################

    def select_table(self, opt):
        '''Seleciona as tabelas de propriedades de acordo com a substância'''
        if opt == 1:
            self.tabela = tbs.tabelas_cls().B_1_1
            self.liq_comp = tbs.tabelas_cls().B_1_4
            self.vap_sup = tbs.tabelas_cls().B_1_3
        if opt == 2:
            self.tabela = tbs.tabelas_cls().B_2_1
            self.vap_sup = tbs.tabelas_cls().B_2_2
        if opt == 3:
            self.tabela = tbs.tabelas_cls().B_3_1
            self.vap_sup = tbs.tabelas_cls().B_3_2
        if opt == 4:
            self.tabela = tbs.tabelas_cls().B_4_1
            self.vap_sup = tbs.tabelas_cls().B_4_2
        if opt == 5:
            self.tabela = tbs.tabelas_cls().B_5_1
            self.vap_sup = tbs.tabelas_cls().B_5_2
        if opt == 6:
            self.tabela = tbs.tabelas_cls().B_6_1
            self.vap_sup = tbs.tabelas_cls().B_6_2
            self.props[0][2] = 'K'
        if opt == 7:
            self.tabela = tbs.tabelas_cls().B_7_1
            self.vap_sup = tbs.tabelas_cls().B_7_2
            self.props[0][2] = 'K'

        #Definindo os limites das tabelas para cada propriedade
        if hasattr(self, 'vap_sup'):
            self.boundaries[0][0] = min(self.tabela[0][2],self.vap_sup[0][3][0][2])
            self.boundaries[0][1] = self.vap_sup[-1][3][0][-1]
            self.boundaries[1][0] = min(self.tabela[1][2],self.vap_sup[0][2])
            self.boundaries[1][1] = max(self.tabela[1][-1],self.vap_sup[-1][2])
            if self.n == 1: self.boundaries[1][1] = self.liq_comp[-1][2]

            self.boundaries[2][0] = self.tabela[2][2]
            if self.n == 1: self.boundaries[2][0] = self.liq_comp[-1][3][1][2]
            self.boundaries[2][1] = max(self.tabela[3][2],self.vap_sup[0][3][1][-1])

            self.boundaries[3][0] = self.tabela[4][2]
            umax = []
            for i in range(len(self.vap_sup)):
                a = self.vap_sup[i][3][2][2:]
                umax.append(max(a))
            self.boundaries[3][1] = max(umax)

            self.boundaries[4][0] = self.tabela[6][2]
            hmax = []
            for i in range(len(self.vap_sup)):
                a = self.vap_sup[i][3][3][2:]
                hmax.append(max(a))
            self.boundaries[4][1] = max(hmax)

            self.boundaries[5][0] = self.tabela[8][2]
            self.boundaries[5][1] = self.vap_sup[0][3][4][-1]

###############################################################################

    def find_phase(self):
        '''Determina a fase da substância'''
        if self.index1 == 0: #prop1 = T
            self.prop1_T()
        if self.index1 == 1: #prop1 = p
            self.prop1_p()

###############################################################################

    def prop1_T(self):
        '''Determina a fase da substância e as propriedades de saturação quando a propriedade 1 é T'''
        if self.known1 > self.tabela[0][-1]:
            self.phase = 2
            if self.index2 == 6: #x
                self.tag_error = 1
        else:
            self.sat_props(0,self.known1)

            if self.index2 == 1: #p
                if self.known2 == self.sat_list[1][2]:
                    self.phase = 3
                    self.tag_error = 1
                if self.known2 > self.sat_list[1][2]:
                    self.phase = 1
                if self.known2 < self.sat_list[1][2]:
                    self.phase = 2

            if self.index2 > 1 and self.index2 < 6: #v, u, h, s
                if self.known2 >= self.sat_list[((self.index2)*2)-2][2] and self.known2 <= self.sat_list[((self.index2)*2)-1][2]:
                    self.phase = 3
                if self.known2 < self.sat_list[((self.index2)*2)-2][2]:
                    self.phase = 1
                if self.known2 > self.sat_list[((self.index2)*2)-1][2]:
                    self.phase = 2

            if self.index2 == 6: #x
                self.phase = 3

###############################################################################

    def prop1_p(self):
        '''Determina a fase da substância e as propriedades de saturação quando a propriedade 1 é p'''
        if self.n == 1 and self.known1 > self.tabela[0][-1]:
            if self.index2 == 0 and self.known2 < self.tabela[1][-1]:
                self.phase = 1
            else:
                self.phase = 2
                if self.index2 == 6: #x
                    self.tag_error = 1

        elif self.n != 1 and self.known1 > self.tabela[1][-1]:
            if self.index2 == 0 and self.known2 < self.tabela[0][-1]:
                self.phase = 1
            else:
                self.phase = 2
                if self.index2 == 6: #x
                    self.tag_error = 1
        else:
            if self.n == 1: self.sat_props(0,self.known1)
            if self.n != 1: self.sat_props(1,self.known1)

            if self.n == 1: ref = self.sat_list[1][2]
            if self.n != 1: ref = self.sat_list[0][2]
            if self.index2 == 0: #T
                if self.known2 == ref:
                    self.phase = 3
                    self.tag_error = 1
                if self.known2 < ref:
                    self.phase = 1
                if self.known2 > ref:
                    self.phase = 2

            if self.index2 > 1 and self.index2 < 6: #v, u, h, s
                if self.known2 >= self.sat_list[((self.index2)*2)-2][2] and self.known2 <= self.sat_list[((self.index2)*2)-1][2]:
                    self.phase = 3
                if self.known2 < self.sat_list[((self.index2)*2)-2][2]:
                    self.phase = 1
                if self.known2 > self.sat_list[((self.index2)*2)-1][2]:
                    self.phase = 2

            if self.index2 == 6: #x
                self.phase = 3

###############################################################################

    def find_props(self):
        '''Determina as propriedade da substância de acordo com a fase'''
        try:
            if self.tag_error == 0:
                #LÍQUIDO COMPRIMIDO
                if self.phase == 1:
                    self.props.pop(-1)
                    if self.index1 == 1 or self.index2 == 1:
                        self.looking_for_p_in_lc()
                    if self.index1 != 1 and self.index2 != 1:
                        if self.n == 1: self.looking_for_not_p_in_lc()
                        else:
                            raise TypeError("Erro de propriedades")

                #VAPOR SUPERAQUECIDO
                if self.phase == 2:
                    self.props.pop(-1)
                    if self.index1 == 1 or self.index2 == 1:
                        self.looking_for_p_in_vs()
                    if self.index1 != 1 and self.index2 != 1:
                        self.looking_for_not_p_in_vs()

                #REGIÃO DE SATURAÇÃO
                if self.phase == 3:
                    if self.index1 == 0: #T
                        self.props[1][3] = self.sat_list[1][2]

                    if self.index1 == 1: #p
                        if self.n == 1: self.props[0][3] = self.sat_list[1][2]
                        if self.n != 1: self.props[0][3] = self.sat_list[0][2]

                    if self.index2 > 1 and self.index2 < 6: #v, u, h, s
                        yl_index = 2*(self.index2-1)
                        yv_index = (2*(self.index2-1))+1
                        yl = self.sat_list[yl_index][2]
                        yv = self.sat_list[yv_index][2]
                        self.props[6][3] = 100*self.calc_x(self.known2,yl,yv)
                    if self.index2 == 6: #x
                        self.props[6][3] = self.known2
                    titulo = self.props[6][3]/100
                    for i in range(2,6):
                        yl_index = 2*(i-1)
                        yv_index = (2*(i-1))+1
                        yl = self.sat_list[yl_index][2]
                        yv = self.sat_list[yv_index][2]
                        self.props[i][3] = self.calc_y(titulo,yl,yv)

                self.get_props()

            if self.tag_error == 1:
                raise TypeError("Tag de erro acionada")

        except TypeError:
            raise TypeError("Valores fora do limite da tabela.")

###############################################################################

    def get_props(self):
        '''Retorna as propriedades da substância de acordo com os valores informados'''
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

###############################################################################

    def run(self):
        '''Executa os métodos de forma ordenada para determinação das propriedades termodinâmicas da substância'''
        self.subs = ['a água', 'a amônia', 'o dióxido de carbono', 'o R-410a', 'o R-134a', 'o nitrogênio', 'o metano']
        self.tabela = []
        self.liq_comp = []
        self.vap_sup = []
        self.sat = []
        self.sat_list = []
        self.lgt = []
        self.props = [['Temperatura','T','°C',0],['Pressão','p','kPa',0],['Volume específico','v','m³/kg',0],['Energia interna específica','u','kJ/kg',0],['Entalpa específica','h','kJ/kg',0],['Entropia específica','s','kJ/kg.K',0],['Título','x','%',-1]]
        self.props[self.index1][3] = self.known1
        self.props[self.index2][3] = self.known2
        self.index_aux1 = 0
        self.index_aux2 = 0
        self.phase = 0
        self.tag1 = -1
        self.tag2 = -1
        self.tag_error = 0
        self.list_props = ['temperatura', 'pressão', 'volume específico', 'eneriga interna específica', 'entalpia específica', 'entropia específica', 'título']
        self.str_prop = ''
        self.boundaries = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,100]]
        self.results = []

        self.select_table(self.n)

        # Validar Limites
        if hasattr(self, 'vap_sup'):
            if self.known1 < self.boundaries[self.index1][0] or self.known1 > self.boundaries[self.index1][1]:
                raise BoundariesException
            if self.known2 < self.boundaries[self.index2][0] or self.known2 > self.boundaries[self.index2][1]:
                raise BoundariesException

        if self.n == 1 and self.index1 == 1:
            self.tabela = tbs.tabelas_cls().B_1_2

        self.find_phase()
        self.find_props()
        self.results = [self.phase, self.sat_list, self.props]
        return self.results

###############################################################################
    # TOOLS FUNCTIONS
###############################################################################

    def interpolate(self, xm, x, xp, ym, yp):
        value = (((x-xm)/(xp-xm))*(yp-ym))+ym
        return(value)

    def calc_x(self, x, xl, xv):
        value = (x-xl)/(xv-xl)
        return(value)

    def calc_y(self, x, yl, yv):
        value = yl+(x*(yv-yl))
        return(value)

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
                else: continue
        return(anterior)

    def sat_props(self,n,known):
        tabela = self.tabela
        self.index_aux1 = self.find_index(tabela[0], known, tabela[n], 2)
        a = []

        if self.tag1 == 1:
            for i in range(len(tabela)):
                b = []
                b.append(tabela[i][0])
                b.append(tabela[i][1])
                b.append(tabela[i][self.index_aux1])
                a.append(b)

        if self.tag1 == -1:
            for i in range(len(tabela)):
                b = []
                if i != n:
                    value = self.interpolate(tabela[n][self.index_aux1], known, tabela[n][self.index_aux1+1], tabela[i][self.index_aux1], tabela[i][self.index_aux1+1])
                    b.append(tabela[i][0])
                    b.append(tabela[i][1])
                    b.append(value)
                if i == n:
                    b.append(tabela[i][0])
                    b.append(tabela[i][1])
                    b.append(known)
                a.append(b)
        self.sat_list = a

    def looking_for_p_in_lc(self):
        if self.n == 1:
            tabela_lc = self.liq_comp
            self.tabela = tbs.tabelas_cls().B_1_1
        if self.index1 == 1:
            p = self.known1
            self.str_prop = self.props[self.index2][0]
        if self.index2 == 1:
            p = self.known2

        if (self.n == 1 and p < tabela_lc[0][2]) or (self.n != 1):
            if self.index1 == 0 or self.index2 == 0:
                aux_index = 0
            else:
                aux_index = (2*self.index2) - 2

            tabela = self.tabela
            if self.index1 == 1: self.index_aux1 = self.find_index(tabela[aux_index], self.known2, tabela[aux_index], 2)
            else: self.index_aux1 = self.find_index(tabela[aux_index], self.known1, tabela[aux_index], 2)

            a = []
            if self.tag1 == 1:
                for i in range(len(tabela)):
                    if i % 2 == 0:
                        a.append(tabela[i][self.index_aux1])

            if self.tag1 == -1:
                for i in range(len(tabela)):
                    if i % 2 == 0:
                        if self.index1 == 1:
                            value = self.interpolate(tabela[aux_index][self.index_aux1], self.known2, tabela[aux_index][self.index_aux1+1], tabela[i][self.index_aux1], tabela[i][self.index_aux1+1])
                        else:
                            value = self.interpolate(tabela[aux_index][self.index_aux1], self.known1, tabela[aux_index][self.index_aux1+1], tabela[i][self.index_aux1], tabela[i][self.index_aux1+1])
                        a.append(value)

            for i in range(len(a)):
                if i != self.index2-1 and i != 0:
                    self.props[i+1][3] = a[i]
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
                else: continue
            self.index_aux2 = anterior

            a = []
            if self.tag1 == 1:
                for i in range(len(tabela_lc[self.index_aux2][3])):
                    b = []
                    for j in range(len(tabela_lc[self.index_aux2][3][0])):
                        if j > 1:
                            b.append(tabela_lc[self.index_aux2][3][i][j])
                    a.append(b)

            if self.tag1 == -1:
                for i in range(len(tabela_lc[self.index_aux2][3])):
                    b = []
                    for j in range(len(tabela_lc[self.index_aux2][3][0])):
                        if j > 1 and j < len(tabela_lc[self.index_aux2][3][0]) - 1:
                            value = self.interpolate(tabela_lc[self.index_aux2][2], p, tabela_lc[self.index_aux2+1][2], tabela_lc[self.index_aux2][3][i][j], tabela_lc[self.index_aux2+1][3][i][j])
                            b.append(value)

                    if self.index1 == 0:
                        self.tabela = tbs.tabelas_cls().B_1_2
                        self.sat_props(0,self.known2)
                    if i == 0:
                        b.append(self.sat_list[1][2])
                    else:
                        b.append(self.sat_list[2*i][2])
                    a.append(b)

            other = 0
            if self.index1 == 1:
                if self.index2 != 0:
                    self.str_prop = self.list_props[self.index2]
                    other = self.index2 - 1
                    min_tab = min(a[other])
                    max_tab = max(a[other])
                    if self.known2 < min_tab or self.known2 > max_tab:
                        raise TypeError

                self.index_aux2 = self.find_index(a[other], self.known2, a[other], 0)

                b = []
                if self.tag1 == 1:
                    for i in range(len(a)):
                        if i != other:
                            if i == 0:
                                self.props[0][3] = a[i][self.index_aux2]
                            else:
                                self.props[i+1][3] = a[i][self.index_aux2]

                if self.tag1 == -1:
                    for i in range(len(a)):
                        if i != other:
                            if i == 0:
                                self.props[0][3] = self.interpolate(a[other][self.index_aux2], self.known2, a[other][self.index_aux2+1], a[i][self.index_aux2], a[i][self.index_aux2+1])
                            else:
                                self.props[i+1][3] = self.interpolate(a[other][self.index_aux2], self.known2, a[other][self.index_aux2+1], a[i][self.index_aux2], a[i][self.index_aux2+1])


            if self.index2 == 1:
                self.str_prop = self.list_props[0]
                min_tab = min(a[other])
                max_tab = max(a[other])
                if self.known1 < min_tab or self.known1 > max_tab:
                    raise TypeError

                self.index_aux2 = self.find_index(a[other], self.known1, a[other], 0)

                b = []
                if self.tag1 == 1:
                    for i in range(len(a)):
                        if i > other:
                            self.props[i+1][3] = a[i][self.index_aux2]

                if self.tag1 == -1:
                    for i in range(len(a)):
                        if i > other:
                            self.props[i+1][3] = self.interpolate(a[other][self.index_aux2], self.known1, a[other][self.index_aux2+1], a[i][self.index_aux2], a[i][self.index_aux2+1])

    def looking_for_not_p_in_lc(self):
        tabela_lc = self.liq_comp
        b_anterior = []
        b_proximo = []
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
                        value = self.interpolate(tabela_lc[i][3][0][self.index_aux1], self.known1, tabela_lc[i][3][0][self.index_aux1+1], tabela_lc[i][3][k][self.index_aux1], tabela_lc[i][3][k][self.index_aux1+1])
                        b.append(value)
                b_anterior = b

            if self.known2 == b_anterior[self.index2-1]:
                for k in range(len(b_anterior)):
                    if k != self.index2-1:
                        try:
                            self.props[k+1][3] = b_anterior[k]
                        except IndexError:
                            pass
                break

            if i == len(tabela_lc) - 1:
                self.str_prop = self.list_props[self.index2]
                raise TypeError

            c.append(tabela_lc[i+1][2])
            for k in range(len(tabela_lc[i+1][3])):
                value = self.interpolate(tabela_lc[i+1][3][0][self.index_aux1], self.known1, tabela_lc[i+1][3][0][self.index_aux1+1], tabela_lc[i+1][3][k][self.index_aux1], tabela_lc[i+1][3][k][self.index_aux1+1])
                c.append(value)
            b_proximo = c

            p_aux = [b_anterior[0], b_proximo[0]]
            b_anterior[0] = b_anterior[1]
            b_proximo[0] = b_proximo[1]
            b_anterior[1] = p_aux[0]
            b_proximo[1] = p_aux[1]

            if (self.index2 == 4 and self.known2 < b_proximo[self.index2] and i < len(tabela_lc)-1) or (self.index2 != 4 and self.known2 > b_proximo[self.index2] and i < len(tabela_lc)-1):
                for k in range(len(b_anterior)):
                    if k != 0 and k != self.index2:
                        value = self.interpolate(b_anterior[self.index2], self.known2, b_proximo[self.index2], b_anterior[k], b_proximo[k])
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
            else: continue
        self.index_aux2 = anterior

        a = []
        if self.tag1 == 1:
            for i in range(len(tabela_vs[self.index_aux2][3])):
                b = []
                for j in range(len(tabela_vs[self.index_aux2][3][0])):
                    if j > 1:
                        b.append(tabela_vs[self.index_aux2][3][i][j])
                a.append(b)

        if self.tag1 == -1:
            marcador = 0
            if tabela_vs[self.index_aux2][3][0][3] != tabela_vs[self.index_aux2+1][3][0][3]: marcador = 1
            for i in range(len(tabela_vs[self.index_aux2][3])):
                if marcador == 1: del tabela_vs[self.index_aux2][3][i][3]

                b = []
                if self.index1 == 0:
                    if self.n == 1:
                        self.tabela = tbs.tabelas_cls().B_1_2
                        self.sat_props(0,self.known2)
                    else: self.sat_props(1,self.known2)
                if i == 0:
                    if self.n == 1: b.append(self.sat_list[1][2])
                    else: b.append(self.sat_list[0][2])
                else:
                    b.append(self.sat_list[(2*i)+1][2])

                for j in range(len(tabela_vs[self.index_aux2][3][0])):
                    if j > 2 and j < len(tabela_vs[self.index_aux2][3][0]):
                        value = self.interpolate(tabela_vs[self.index_aux2][2], p, tabela_vs[self.index_aux2+1][2], tabela_vs[self.index_aux2][3][i][j], tabela_vs[self.index_aux2+1][3][i][j])
                        b.append(value)
                a.append(b)

        other = 0
        if self.index1 == 1:
            self.str_prop = self.list_props[self.index2]
            if self.index2 != 0:
                other = self.index2 - 1
                min_tab = min(a[other])
                max_tab = max(a[other])
                if self.known2 < min_tab or self.known2 > max_tab:
                    raise TypeError

            self.index_aux1 = self.find_index(a[other], self.known2, a[other], 0)

            b = []
            if self.tag1 == 1:
                for i in range(len(a)):
                    if i != other:
                        if i == 0:
                            self.props[0][3] = a[i][self.index_aux1]
                        else:
                            self.props[i+1][3] = a[i][self.index_aux1]

            if self.tag1 == -1:
                for i in range(len(a)):
                    if i != other:
                        if i == 0:
                            self.props[0][3] = self.interpolate(a[other][self.index_aux1], self.known2, a[other][self.index_aux1+1], a[i][self.index_aux1], a[i][self.index_aux1+1])
                        else:
                            self.props[i+1][3] = self.interpolate(a[other][self.index_aux1], self.known2, a[other][self.index_aux1+1], a[i][self.index_aux1], a[i][self.index_aux1+1])


        if self.index2 == 1:
            self.str_prop = self.list_props[0]
            min_tab = min(a[other])
            max_tab = max(a[other])
            if self.known1 < min_tab or self.known1 > max_tab:
                raise TypeError

            self.index_aux2 = self.find_index(a[other], self.known1, a[other], 0)

            b = []
            if self.tag1 == 1:
                for i in range(len(a)):
                    if i > other:
                        self.props[i+1][3] = a[i][self.index_aux2]

            if self.tag1 == -1:
                for i in range(len(a)):
                    if i > other:
                        self.props[i+1][3] = self.interpolate(a[other][self.index_aux2], self.known1, a[other][self.index_aux2+1], a[i][self.index_aux2], a[i][self.index_aux2+1])

    def looking_for_not_p_in_vs(self):
        tabela_vs = self.vap_sup
        b_anterior = []
        b_proximo = []
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
                        value = self.interpolate(tabela_vs[i][3][0][self.index_aux1], self.known1, tabela_vs[i][3][0][self.index_aux1+1], tabela_vs[i][3][k][self.index_aux1], tabela_vs[i][3][k][self.index_aux1+1])
                        b.append(value)
                b_anterior = b

            if self.known2 == b_anterior[self.index2-1]:
                for k in range(len(b_anterior)):
                    if k != self.index2-1:
                        self.props[k+1][3] = b_anterior[k]
                break

            if i == len(tabela_vs) - 1:
                self.str_prop = self.list_props[self.index2]
                raise TypeError

            marcador = 0
            if tabela_vs[i][3][0][3] != tabela_vs[i+1][3][0][3]: marcador = 1
            for j in range(len(tabela_vs[i][3])):
                if marcador == 1:
                    del tabela_vs[i][3][j][1]
                    self.index_aux1 = self.index_aux1 - 1
                    break

            c.append(tabela_vs[i+1][2])
            for k in range(len(tabela_vs[i+1][3])):
                try:
                    value = self.interpolate(
                        tabela_vs[i+1][3][0][self.index_aux1],
                        self.known1,
                        tabela_vs[i+1][3][0][self.index_aux1+1],
                        tabela_vs[i+1][3][k][self.index_aux1],
                        tabela_vs[i+1][3][k][self.index_aux1+1]
                    )
                except IndexError:
                    raise TypeError("Índices fora dos limites da tabela.")
                c.append(value)
            b_proximo = c

            if self.known2 > b_proximo[self.index2] and i < len(tabela_vs)-1:
                for k in range(len(b_anterior)):
                    if k != 1 and k != self.index2:
                        value = self.interpolate(b_anterior[self.index2], self.known2, b_proximo[self.index2], b_anterior[k], b_proximo[k])
                        self.props[k][3] = value
                self.props[1][3] = self.props[0][3]
                self.props[0][3] = self.known1
                break

###############################################################################

def process_values_view42(request):
    if 'property_choice' not in request.session or 'second_property_choice' not in request.session:
        return redirect('ask_known1_42')

    try:
        third_property_choice = int(request.session.get('third_property_choice'))
        third_value_input = float(request.session.get('third_value_input'))
        temp_value_input = float(request.session.get('temp_value_input'))
        request.session['lista_estados'] = json.dumps(estados.lista_estados, default=str)

        if estados.lista_estados:
            print("Usando o último estado salvo como condição inicial.")
            ultimo_estado = estados.lista_estados[-1]

            fase = ultimo_estado[0]
            temperatura = round(ultimo_estado[2][0][3], 2)
            pressao = round(ultimo_estado[2][1][3], 2)
            
            # VALIDAÇÃO DE PRESSÃO NEGATIVA - ESTADO 1 (Salvo)
            if pressao < 0:
                raise ValidationError("Erro: A pressão inicial não pode ser negativa.")

            volume_esp = round(ultimo_estado[2][2][3], 8)
            energia_int = round(ultimo_estado[2][3][3], 2)
            entalpia_esp = round(ultimo_estado[2][4][3], 2)
            entropia_esp = round(ultimo_estado[2][5][3], 4)

            if (energia_int == 0 and entalpia_esp == 0 and entropia_esp == 0) or volume_esp == 0:
                return redirect('error_type_42')

            if fase == 3:
                tit = round(ultimo_estado[2][6][3], 2)
                volume_v = ultimo_estado[1][3][2]
                volume_l = ultimo_estado[1][2][2]
                VolumeL = round((1 - (tit / 100)) * volume_l, 8)
                VolumeV = (tit / 100) * volume_v
            else:
                tit = None
                VolumeL = None
                VolumeV = None
                volume_v = None
                volume_l = None

            try:
                volume_v = ultimo_estado[1][3][2]
            except IndexError:
                volume_v = None
            try:
                volume_l = ultimo_estado[1][2][2]
            except IndexError:
                volume_l = None

            if volume_v is None or volume_l is None:
                return redirect('error_type_42')

        else:
            print("Sem estados salvos. Usando valores digitados.")
            request.session['pontos_grafico'] = []
            if hasattr(estados, 'pontos_grafico'):
                estados.pontos_grafico.clear()

            property_choice = int(request.session.get('property_choice'))
            second_property_choice = int(request.session.get('second_property_choice'))
            value_input = float(request.session.get('value_input'))
            second_value_input = float(request.session.get('second_value_input'))

            h = subs_cls(7, property_choice, second_property_choice, value_input, second_value_input)
            fase = h.results[0]
            try:
                temperatura = round(h.results[2][0][3], 2)
                pressao = round(h.results[2][1][3], 2)
                
                # VALIDAÇÃO DE PRESSÃO NEGATIVA - ESTADO 1 (Digitado)
                if pressao < 0:
                    raise ValidationError("Erro: A pressão calculada ou inserida não pode ser negativa.")

                volume_esp = round(h.results[2][2][3], 8)
                energia_int = round(h.results[2][3][3], 2)
                entalpia_esp = round(h.results[2][4][3], 2)
                entropia_esp = round(h.results[2][5][3], 4)
            except (IndexError, TypeError):
                return redirect('error_type_42')

            if (energia_int == 0 and entalpia_esp == 0 and entropia_esp == 0) or volume_esp == 0:
                return redirect('error_type_42')

            if fase == 3:
                tit = round(h.results[2][6][3], 2)
                volume_v = h.results[1][3][2]
                volume_l = h.results[1][2][2]
                VolumeL = round((1 - (tit / 100)) * volume_l, 8)
                VolumeV = (tit / 100) * volume_v
            else:
                tit = None
                VolumeL = None
                VolumeV = None
                volume_v = None
                volume_l = None

            try:
                volume_v = h.results[1][3][2]
            except IndexError:
                volume_v = None
            try:
                volume_l = h.results[1][2][2]
            except IndexError:
                volume_l = None

            if volume_v is None or volume_l is None:
                return redirect('error_type_42')

            estados.lista_estados.append(h.results)

        # Novo estado guiado pela View 5: Processo Isovolumétrico (Fixa Volume)
        h = subs_cls(7, third_property_choice, 2, third_value_input, volume_esp)

        fase2 = h.results[0]
        try:
            pressao2 = round(h.results[2][1][3], 2)
            
            # VALIDAÇÃO DE PRESSÃO NEGATIVA - ESTADO 2
            if pressao2 < 0:
                raise ValidationError("Erro: A pressão resultante do segundo estado não pode ser negativa.")

            temperatura2 = round(h.results[2][0][3], 2)
            volume_esp2 = round(h.results[2][2][3], 8)
            energia_int2 = round(h.results[2][3][3], 2)
            entalpia_esp2 = round(h.results[2][4][3], 2)
            entropia_esp2 = round(h.results[2][5][3], 4)
        except (IndexError, TypeError):
            return redirect('error_type_42')

        if (energia_int2 == 0 and entalpia_esp2 == 0 and entropia_esp2 == 0) or volume_esp2 == 0:
            return redirect('error_type_42')

        if fase2 == 3:
            tit2 = round(h.results[2][6][3], 2)
            volume_v2 = h.results[1][3][2]
            volume_l2 = h.results[1][2][2]
            VolumeL2 = round((1 - (tit2 / 100)) * volume_l2, 8)
            VolumeV2 = (tit2 / 100) * volume_v2
        else:
            tit2 = None
            VolumeL2 = None
            VolumeV2 = None
            volume_v2 = None
            volume_l2 = None

        try:
            volume_v2 = h.results[1][3][2]
        except IndexError:
            volume_v2 = None
        try:
            volume_l2 = h.results[1][2][2]
        except IndexError:
            volume_l2 = None

        if volume_v2 is None or volume_l2 is None:
            return redirect('error_type_42')

        escolha = third_property_choice
        temp_viz = temp_value_input
        calor = round((energia_int2 - energia_int), 6)
        entropia_ger = round((entropia_esp2 - entropia_esp) - (calor / (temp_viz + 273.15)), 6)

        estados.lista_estados.append(h.results)
        teste = estados.lista_estados

        # ==========================================================
        # GERAÇÃO DE MICROPROCESSOS: MATEMÁTICA PARAMÉTRICA (SOLUÇÃO ROBUSTA)
        # ==========================================================

        import math

        pontos_grafico = request.session.get('pontos_grafico', [])

        val_fixo = volume_esp
        
        estado_inicial = {
            'T': round(temperatura, 6), 'P': round(pressao, 6), 'v': round(val_fixo, 10),
            's': round(entropia_esp, 6), 'h': round(entalpia_esp, 6), 'fase': fase
        }

        estado_final = {
            'T': round(temperatura2, 6), 'P': round(pressao2, 6), 'v': round(val_fixo, 10),
            's': round(entropia_esp2, 6), 'h': round(entalpia_esp2, 6), 'fase': fase2
        }

        pt_fronteira = None
        cruzou_domo = (fase != fase2)

        if cruzou_domo:
            # 1. Busca Binária de Alta Precisão (Acha exatamente o vértice no domo)
            t_a = temperatura
            t_b = temperatura2
            
            # AUMENTO DE PRECISÃO: 60 iterações para cravar o ponto na 6ª casa decimal
            for _ in range(60):
                t_mid = (t_a + t_b) / 2.0
                try:
                    h_mid = subs_cls(7, 0, 2, t_mid, val_fixo)
                    if h_mid.results[0] == fase:
                        t_a = t_mid
                    else:
                        t_b = t_mid
                except Exception:
                    # Em caso de erro numérico na tabela, afasta do erro
                    t_b = t_mid 
            
            # O lado da mistura (fase 3) é matematicamente blindado contra erros
            t_front = t_a if fase == 3 else t_b
            
            try:
                h_front_calc = subs_cls(7, 0, 2, t_front, val_fixo)
                pt_fronteira = {
                    'T': round(t_front, 6),
                    'P': round(h_front_calc.results[2][1][3], 6),
                    'v': round(val_fixo, 10),
                    's': round(h_front_calc.results[2][5][3], 6),
                    'h': round(h_front_calc.results[2][4][3], 6),
                    'fase': 'fronteira'
                }
            except Exception:
                pass

        # 2. Motor de Geração Paramétrica (Livre das falhas numéricas da tabela)
        def gerar_segmento(pt_A, pt_B, num_pontos):
            segmento = []
            if not pt_A or not pt_B: return segmento
            
            # Aplica escala logarítmica para a Pressão (suaviza as curvas nos diagramas T-s e P-h)
            use_log_P = pt_A['P'] > 0 and pt_B['P'] > 0

            if use_log_P:
                log_P_A = math.log10(pt_A['P'])
                log_P_B = math.log10(pt_B['P'])
            
            for i in range(num_pontos + 1):
                f = i / float(num_pontos)
                
                # Interpolação linear para T, s, h
                t_i = pt_A['T'] + f * (pt_B['T'] - pt_A['T'])
                s_i = pt_A['s'] + f * (pt_B['s'] - pt_A['s'])
                h_i = pt_A['h'] + f * (pt_B['h'] - pt_A['h'])
                
                # Interpolação logarítmica para P
                if use_log_P:
                    p_i = 10 ** (log_P_A + f * (log_P_B - log_P_A))
                else:
                    p_i = pt_A['P'] + f * (pt_B['P'] - pt_A['P'])

                # Para processo isovolumétrico, o volume é 100% cravado
                v_i = val_fixo
                
                segmento.append({
                    'T': round(t_i, 6), 
                    'P': round(p_i, 6), 
                    'v': round(v_i, 10),
                    's': round(s_i, 6), 
                    'h': round(h_i, 6)
                })
            return segmento

        # 3. Construção dos Ramos (Densidade dobrada para evitar "degraus")
        pontos_finais = []
        
        if pt_fronteira:
            trecho1 = gerar_segmento(estado_inicial, pt_fronteira, 150)
            trecho2 = gerar_segmento(pt_fronteira, estado_final, 150)
            
            if trecho1: trecho1.pop()  # Evita duplicar o vértice
            pontos_finais = trecho1 + trecho2
        else:
            # Processo que não cruza o domo de saturação
            pontos_finais = gerar_segmento(estado_inicial, estado_final, 300)

        # ==========================================================
        # CONEXÃO FINAL
        # ==========================================================

        ramo_atual = pontos_finais
        pontos_grafico.append(ramo_atual)
        request.session['pontos_grafico'] = pontos_grafico
        
        # ==========================================================

        return render(request, 'metano/results-metano-vcte-5.html', {
            'fase': fase, 'temperatura': round(temperatura,2), 'pressao': pressao,
            'volume_especifico': volume_esp, 'energia_interna': energia_int, 'entalpia_especifica': entalpia_esp,
            'entropia_especifica': entropia_esp, 'titulo': tit, 'volume_v': volume_v, 'volume_l': volume_l,
            'VolumeV': VolumeV, 'VolumeL': VolumeL,
            'fase2': fase2, 'temperatura2': round(temperatura2,2), 'pressao2': pressao2,
            'volume_especifico2': volume_esp2, 'energia_interna2': energia_int2, 'entalpia_especifica2': entalpia_esp2,
            'entropia_especifica2': entropia_esp2, 'titulo2': tit2, 'volume_v2': volume_v2, 'volume_l2': volume_l2,
            'VolumeV2': VolumeV2, 'VolumeL2': VolumeL2,
            'teste': teste, 'teste3': teste,
            'TempViz': temp_viz, 'Escolha': escolha, 'Calor': calor, 'Sger': entropia_ger,
            'pontos_grafico_json': json.dumps(pontos_grafico)
        })

    except ValidationError as e:
        return render(request, 'erro_generico.html', {'message': str(e)})
    
    except BoundariesException:
        # Capturando os limites da tabela de forma dinâmica
        return render(request, 'erro_generico.html', {'message': 'Os valores fornecidos (ou calculados) estão fora dos limites das tabelas termodinâmicas'})

    except TypeError as e:
        # Captura erros como "Valores fora do limite da tabela." gerados dentro da subs_cls
        return render(request, 'erro_generico.html', {'message': str(e)})

    except IndexError:
        # Proteção adicional caso estoure índice nas interpolações da tabela
        return render(request, 'erro_generico.html', {'message': 'Ocorreu um erro ao acessar as tabelas termodinâmicas (valores fora do alcance esperado).'})
###############################################################################

class BoundariesException(Exception):
    pass

###############################################################################

class TituloException(Exception):
    pass

###############################################################################

def error_value_view42(request):
    # Renderiza a página de erro de valor
    return render(request, 'erro_generico.html')

def error_type_view42(request):
    # Renderiza a página de erro de tipo
    return render(request, 'erro_generico.html')
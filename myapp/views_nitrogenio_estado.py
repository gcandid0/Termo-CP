# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 23:14:36 2026

@author: gabri
"""

from django.shortcuts import render, redirect
from .forms import PropertyFormKelvinEst1, SecondPropertyFormKelvinEst1
from django.core.exceptions import ValidationError
from . import tabelas_termoprop as tbs

def processos_view33(request):
    return render(request, 'processos7.html')

###############################################################################

def ask_known1_view33(request):
    if request.method == 'POST':
        form = PropertyFormKelvinEst1(request.POST)
        if form.is_valid():
            property_choice = form.cleaned_data['property_choice']
            value_input = form.cleaned_data['value_input']
            request.session['property_choice'] = property_choice
            request.session['value_input'] = value_input
            excluded_properties = [property_choice]
            return redirect('ask_known2_33')
    else:
        form = PropertyFormKelvinEst1()

    return render(request, 'nitrogenio/nkelvin-estado-1.html', {'form': form})

###############################################################################

def ask_known2_view33(request):
    if request.method == 'POST':
        excluded_properties = [int(request.session.get('property_choice', 0))]
        form = SecondPropertyFormKelvinEst1(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            property_choice = form.cleaned_data['property_choice']
            value_input = form.cleaned_data['value_input']
            request.session['second_property_choice'] = property_choice
            request.session['second_value_input'] = value_input
            return redirect('process_values_33')
    else:
        excluded_properties = [int(request.session.get('property_choice', 0))]
        form = SecondPropertyFormKelvinEst1(excluded_properties=excluded_properties)

    return render(request, 'nitrogenio/nkelvin-estado-2.html', {'form': form})

###############################################################################

class subs_cls:
    """SUBS"""
    '''
    Calcula e imprime o valor das propriedades de diferentes substâncias a partir do valor conhecido de duas propriedades. Valores dados pelas tabelas B.2, B.3, B.4, B.5, B.6 e B.7.
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
        '''Determina a fase da substância: líquido comprimido, vapor superaquecido ou líquido e/ou vapor saturado(s)'''
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
        '''Executa os métodos de forma ordenada para determnação das propriedades termodinâmicas da substância'''
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
                        self.props[k+1][3] = b_anterior[k]
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
                        self.props[k][3] = value
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

def process_values_view33(request):
    if 'property_choice' not in request.session or 'second_property_choice' not in request.session:
        return redirect('ask_known1_33')

    try:
        property_choice = int(request.session.get('property_choice'))
        second_property_choice = int(request.session.get('second_property_choice'))
        value_input = float(request.session.get('value_input'))
        second_value_input = float(request.session.get('second_value_input'))

        # Instanciando a nova classe subs_cls. O valor '1' indica Água, mas pode ser tornado dinâmico futuramente.
        h = subs_cls(6, property_choice, second_property_choice, value_input, second_value_input)

        fase = h.results[0]

        # Tentativa de arredondamento com validação
        try:
            pressao = round(h.results[2][1][3], 2)
            temperatura = round(h.results[2][0][3], 2)
            volume_esp = round(h.results[2][2][3], 8)
            energia_int = round(h.results[2][3][3], 2)
            entalpia_esp = round(h.results[2][4][3], 2)
            entropia_esp = round(h.results[2][5][3], 4)
        except (IndexError, TypeError):
             return redirect('error_type_7')

        # === VALIDAÇÃO DE INTEGRIDADE (CONTRA RESULTADOS ZERADOS) ===
        if (energia_int == 0 and entalpia_esp == 0 and entropia_esp == 0) or volume_esp == 0:
            return redirect('error_type_7')

        if pressao == 0 and entropia_esp == 0:
             return redirect('error_type_7')
        # ============================================================

        if fase == 3:
            tit = round(h.results[2][6][3], 2)
            try:
                volume_v = round(h.results[1][3][2], 6)
                volume_l = round(h.results[1][2][2], 6)
                VolumeL = round((1 - (tit / 100)) * volume_l,8)
                VolumeV = (tit/100) * volume_v
            except (IndexError, TypeError):
                return redirect('error_type_7')
        else:
            tit = None
            VolumeL = None
            VolumeV = None

        try:
            volume_v = h.results[1][3][2]
        except IndexError:
            volume_v = None

        try:
            volume_l = h.results[1][2][2] # Corrigido aqui: o índice original do volume de líquido na sat_list é [1][2][2]
        except IndexError:
            volume_l = None

        # Se fase for de saturação e os volumes forem None, redireciona para a página de erro
        if fase == 3 and (volume_v is None or volume_l is None):
            return redirect('error_type_7')

        teste = h.results

        return render(request, 'nitrogenio/results-nitrogenio-estado-3.html', {
            'fase': fase,
            'temperatura': round(temperatura,2),
            'pressao': pressao,
            'volume_especifico': round(volume_esp, 6),
            'energia_interna': energia_int,
            'entalpia_especifica': entalpia_esp,
            'entropia_especifica': entropia_esp,
            'teste': teste,
            'titulo': tit,
            'VolumeV': round(VolumeV, 6) if VolumeV is not None else None,
            'VolumeL': round(VolumeL, 6) if VolumeL is not None else None,
            'volume_v': volume_v,
            'volume_l': volume_l,
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

def error_value_view33(request):
    # Renderiza a página de erro de valor
        return render(request, 'erro_generico.html')

def error_type_view7(request):
    # Renderiza a página de erro de tipo
        return render(request, 'erro_generico.html')
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from math import log, exp
import json
from . import estados as std

# Inicializa instância de gas
if not hasattr(std, 'instancia_gas'):
    std.instancia_gas = std.gas_cls()

gas = std.instancia_gas

# Garante lista_gas
if not hasattr(gas, 'lista_gas') or gas.lista_gas is None:
    gas.lista_gas = []

from .forms import (
    ConstantesTCte10, ConstantesTCte10_2,
    Prop1TCte10, Prop1TCte10_2, Prop2TCte10, TvizGasIdeal10
)

# Funções Auxiliares
def to_kelvin(T):
    return T + 273.15 if T is not None else None

def to_celsius(T):
    return T - 273.15 if T is not None else None

def rd(x):
    if x is None: return None
    return round(x, 4)

###############################################################################
# VIEWS DE FORMULÁRIO (Passos 1 a 6)
###############################################################################

def ask_known1_view10(request):
    # Limpa a lista ao iniciar um novo ciclo completo
    try:
        gas.limpar_gas()
    except Exception:
        gas.lista_gas = []

    request.session['lista_gas'] = json.dumps(gas.lista_gas, default=str)

    # ==========================================================
    # GARANTIA DE LIMPEZA DO GRÁFICO AO INICIAR NOVO CICLO
    # ==========================================================
    request.session['pontos_grafico'] = []
    request.session['historico_processos'] = []
    if 'dados_processo' in request.session:
        del request.session['dados_processo']
    if hasattr(gas, 'pontos_grafico_gas'):
        gas.pontos_grafico_gas.clear()
    # ==========================================================

    if request.method == 'POST':
        form = ConstantesTCte10(request.POST)
        if form.is_valid():
            request.session['property_choice'] = int(form.cleaned_data['property_choice'])
            request.session['value_input'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known2_10')
    else:
        form = ConstantesTCte10()
    return render(request, 'gas/ask_known1_10.html', {'form': form})

def ask_known2_view10(request):
    prop = request.session.get('property_choice')
    excluded = [str(prop)] if prop is not None else []

    if request.method == 'POST':
        form = ConstantesTCte10_2(request.POST, excluded_properties=excluded)
        if form.is_valid():
            second_property_choice = int(form.cleaned_data['property_choice'])
            second_value_input = float(form.cleaned_data['value_input'])

            # Validação de Constantes
            const1 = int(request.session.get('property_choice'))
            val1 = float(request.session.get('value_input'))
            const_values = {const1: val1, second_property_choice: second_value_input}

            Cv0 = const_values.get(11)
            Cp0 = const_values.get(12)
            R = const_values.get(13)
            K = const_values.get(14)

            # Lógica de determinação cruzada
            if Cp0 is not None and Cv0 is not None:
                R = Cp0 - Cv0
                K = Cp0 / Cv0 if Cv0 else None
            elif Cp0 is not None and R is not None:
                Cv0 = Cp0 - R
                K = Cp0 / Cv0 if Cv0 else None
            elif Cv0 is not None and R is not None:
                Cp0 = Cv0 + R
                K = Cp0 / Cv0 if Cv0 else None
            elif R is not None and K is not None:
                if K != 1:
                    Cv0 = R / (K - 1)
                    Cp0 = K * Cv0

            error_messages = []
            if R is not None and R <= 0: error_messages.append("R deve ser positivo.")
            if K is not None and K <= 1: error_messages.append("K deve ser maior que 1.")

            if error_messages:
                context = {"Cv0": Cv0, "Cp0": Cp0, "R": R, "K": K, "error_messages": error_messages}
                return render(request, "error_constants.html", context)

            # Salvando as escolhas validadas na sessão
            request.session['second_property_choice'] = second_property_choice
            request.session['second_value_input'] = second_value_input
            return redirect('ask_known3_10')
    else:
        form = ConstantesTCte10_2(excluded_properties=excluded)
    return render(request, 'gas/ask_known2_10.html', {'form': form})

def ask_known3_view10(request):
    # Primeira propriedade do Estado 1: usuário escolhe livremente entre T, p ou v
    if request.method == 'POST':
        form = Prop1TCte10(request.POST)
        if form.is_valid():
            request.session['state1_property_choice_1'] = str(form.cleaned_data['property_choice'])
            request.session['state1_value_input_1'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known4_10')
    else:
        form = Prop1TCte10()
    return render(request, 'gas/ask_known3_10.html', {'form': form})

def ask_known4_view10(request):
    # Segunda propriedade do Estado 1: exclui a já escolhida na etapa anterior
    first = request.session.get('state1_property_choice_1')
    excluded_properties = [str(first)] if first is not None else []

    if request.method == 'POST':
        form = Prop1TCte10_2(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            request.session['state1_property_choice_2'] = str(form.cleaned_data['property_choice'])
            request.session['state1_value_input_2'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known5_10')
    else:
        form = Prop1TCte10_2(excluded_properties=excluded_properties)
    return render(request, 'gas/ask_known4_10.html', {'form': form})

def ask_known5_view10(request):
    if request.method == 'POST':
        form = Prop2TCte10(request.POST)
        if form.is_valid():
            request.session['four_property_choice'] = int(form.cleaned_data['property_choice'])
            request.session['four_value_input'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known6_10')
    else:
        form = Prop2TCte10()
    return render(request, 'gas/ask_known5_10.html', {'form': form})

def ask_known6_view10(request):
    if request.method == 'POST':
        form = TvizGasIdeal10(request.POST)
        if form.is_valid():
            request.session['Tviz_value_input'] = float(form.cleaned_data['Tviz_value_input'])
            return redirect('process_values_10')
    else:
        form = TvizGasIdeal10()
    return render(request, 'gas/ask_known6_10.html', {'form': form})

###############################################################################
# LÓGICA DE CÁLCULO (Passo 7)
###############################################################################

def process_values_view10(request):
    try:
        # =====================================
        # 0️⃣ Ressincroniza a lista de estados com a SESSÃO do usuário atual
        # =====================================
        # IMPORTANTE: `gas` é uma instância única compartilhada no módulo (via
        # `std.instancia_gas`), reaproveitada por TODOS os processos de gás e
        # TODAS as requisições. Sem este passo, `gas.lista_gas` pode conter o
        # estado deixado por outro usuário ou por outro tipo de processo
        # (isobárico, isocórico, politrópico, etc.), fazendo o relatório final
        # exibir mais "Estados" do que processos realmente calculados nesta sessão.
        if 'lista_gas' not in request.session:
            request.session['lista_gas'] = json.dumps([])
        try:
            gas.lista_gas = json.loads(request.session['lista_gas'])
        except Exception:
            gas.lista_gas = []

        # =====================================
        # 1️⃣ Recupera constantes
        # =====================================
        c1_idx = int(request.session.get('property_choice'))
        c1_val = float(request.session.get('value_input'))
        c2_idx = int(request.session.get('second_property_choice'))
        c2_val = float(request.session.get('second_value_input'))

        map_const = {c1_idx: c1_val, c2_idx: c2_val}

        Cv0 = map_const.get(11)
        Cp0 = map_const.get(12)
        R   = map_const.get(13)
        K   = map_const.get(14)

        # Ajustes entre constantes
        if R is None and Cp0 is not None and Cv0 is not None:
            R = Cp0 - Cv0

        if Cv0 is None and Cp0 is not None and R is not None:
            Cv0 = Cp0 - R

        if Cp0 is None and Cv0 is not None and R is not None:
            Cp0 = Cv0 + R

        if K is None and Cp0 is not None and Cv0 is not None and Cv0 != 0:
            K = Cp0 / Cv0

        if R is None or R <= 0:
            return redirect('error_type10')

        # =====================================
        # 2️⃣ Escolhas de propriedades
        # =====================================
        p2_choice = int(request.session.get('four_property_choice'))
        p2_val    = float(request.session.get('four_value_input'))

        Tviz_C = float(request.session.get('Tviz_value_input'))
        Tviz_K = to_kelvin(Tviz_C)

        # =====================================
        # 3️⃣ ESTADO 1 + TEMPERATURA DO PROCESSO
        # =====================================

        if gas.lista_gas:
            ultimo = gas.lista_gas[-1]

            p1 = float(ultimo[4])
            T_input_C = float(ultimo[5])
            T_K = to_kelvin(T_input_C)
            v1 = float(ultimo[6])

        else:
            # Primeiro processo: Estado 1 definido por 2 propriedades livres (T, p ou v)
            s1p1 = int(request.session.get('state1_property_choice_1'))
            s1v1 = float(request.session.get('state1_value_input_1'))
            s1p2 = int(request.session.get('state1_property_choice_2'))
            s1v2 = float(request.session.get('state1_value_input_2'))

            T_K = p1 = v1 = None
            for prop, val in [(s1p1, s1v1), (s1p2, s1v2)]:
                if prop == 0:    # Temperatura (°C -> K)
                    T_K = to_kelvin(val)
                elif prop == 1:  # Pressão
                    p1 = val
                elif prop == 2:  # Volume específico
                    v1 = val

            try:
                # Equação de estado do gás ideal: p*v = R*T
                if T_K is None: T_K = (p1 * v1) / R
                if p1 is None: p1 = (R * T_K) / v1
                if v1 is None: v1 = (R * T_K) / p1
            except (TypeError, ZeroDivisionError):
                return redirect('error_type10')

            if T_K is None or p1 is None or v1 is None:
                return redirect('error_type10')

            T_input_C = to_celsius(T_K)

        # =====================================
        # 4️⃣ ESTADO 2
        # =====================================

        Q12_input = None

        if p2_choice == 1:
            p2 = p2_val
            v2 = (R * T_K) / p2

        elif p2_choice == 2:
            v2 = p2_val
            p2 = (R * T_K) / v2

        elif p2_choice == 8:
            Q12_input = p2_val
            v2 = v1 * exp(Q12_input / (R * T_K))
            p2 = (R * T_K) / v2

        else:
            return redirect('error_type10')

        if v1 <= 0 or v2 <= 0:
            return redirect('error_type10')

        # =====================================
        # 5️⃣ Cálculos isotérmicos
        # =====================================

        if Q12_input is not None:
            Q12 = Q12_input
            W12 = Q12_input
        else:
            W12 = R * T_K * log(v2 / v1)
            Q12 = W12

        delta_S = -R * log(p2 / p1)
        S_ger = delta_S - (Q12 / Tviz_K)


        # ==========================================================
        # GERAÇÃO DE MICROPROCESSOS PARA O DIAGRAMA (GÁS IDEAL)
        # ==========================================================
        pontos_grafico = request.session.get('pontos_grafico', [])

        num_passos = 150 # Usamos 15 passos para desenhar a hipérbole P-v perfeitamente
        passo_v = (v2 - v1) / num_passos if v1 != v2 else 0

        # Funções teóricas para o gráfico (Ref arbitrária: 273.15 K e 100 kPa)
        # Proteção caso Cp0 não tenha sido informado pelo usuário
        cp_calc = Cp0 if Cp0 else 0
        def calc_h(T_K): return cp_calc * T_K
        def calc_s(T_K, P_kPa):
            if T_K <= 0 or P_kPa <= 0: return 0
            return cp_calc * log(T_K / 273.15) - R * log(P_kPa / 100)

        ramo_atual = []

        # Ponto Inicial
        ramo_atual.append({
            'T': round(to_celsius(T_K), 2),
            'P': round(p1, 2),
            'v': round(v1, 6),
            's': round(calc_s(T_K, p1), 4),
            'h': round(calc_h(T_K), 2)
        })

        if passo_v != 0:
            for i in range(1, num_passos):
                v_micro = v1 + (i * passo_v)
                T_micro = T_K  # Processo Isotérmico (T constante)
                P_micro = (R * T_micro) / v_micro

                ramo_atual.append({
                    'T': round(to_celsius(T_micro), 2),
                    'P': round(P_micro, 2),
                    'v': round(v_micro, 6),
                    's': round(calc_s(T_micro, P_micro), 4),
                    'h': round(calc_h(T_micro), 2)
                })

        # Ponto Final
        ramo_atual.append({
            'T': round(to_celsius(T_K), 2),
            'P': round(p2, 2),
            'v': round(v2, 6),
            's': round(calc_s(T_K, p2), 4),
            'h': round(calc_h(T_K), 2)
        })

        pontos_grafico.append(ramo_atual)
        request.session['pontos_grafico'] = pontos_grafico

        # Sincroniza com a classe gas
        if hasattr(gas, 'pontos_grafico_gas'):
            gas.pontos_grafico_gas = pontos_grafico
        # ==========================================================

        # =====================================
        # 6️⃣ Salvar estado final
        # =====================================

        novo_estado = [
            float(Cv0) if Cv0 else 0,
            float(Cp0) if Cp0 else 0,
            float(R),
            float(K) if K else 0,
            float(p2),
            float(T_input_C),  # T permanece constante
            float(v2)
        ]

        gas.lista_gas.append(novo_estado)
        request.session['lista_gas'] = json.dumps(gas.lista_gas, default=str)

        # =====================================
        # 6️⃣.1 HISTÓRICO DE PROCESSOS (para o Relatório Final)
        # =====================================
        historico_processos = request.session.get('historico_processos', [])
        historico_processos.append({
            'TempViz': rd(Tviz_C),
            'Q': rd(Q12),
            'W': rd(W12),
            'Sger': rd(S_ger),
        })
        request.session['historico_processos'] = historico_processos

        # =====================================
        # 7️⃣ Contexto
        # =====================================

        context = {
            'Cv0': rd(Cv0),
            'Cp0': rd(Cp0),
            'R': rd(R),
            'K': rd(K),
            'T': rd(T_input_C),
            'p1': rd(p1),
            'v1': rd(v1),
            'p2': rd(p2),
            'v2': rd(v2),
            'Q12': rd(Q12),
            'W12': rd(W12),
            'Sger': rd(S_ger),
            'Tviz': rd(Tviz_C),
            'teste': gas.lista_gas,
            'pontos_grafico_json': json.dumps(pontos_grafico), # Envia para o Javascript desenhar
            'historico_processos_json': json.dumps(historico_processos) # Histórico p/ Relatório Final
        }

        return render(request, 'gas/results_10.html', context)

    except Exception as e:
        print(f"Erro process_values_10: {e}")
        return redirect('error_type10')

###############################################################################
# PÁGINA DE ERRO
###############################################################################
def error_type_view10(request):
    return render(request, 'erro_generico.html')
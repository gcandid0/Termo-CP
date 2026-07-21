from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from math import log
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
    ConstantesVCte9, ConstantesVCte9_2,
    VGasIdeal9, Prop1VCte9, Prop2VCte9, TvizGasIdeal9
)

# Funções Auxiliares
def to_kelvin(T): return T + 273.15 if T is not None else None
def to_celsius(T): return T - 273.15 if T is not None else None
def rd(x): return round(x, 4) if x is not None else None

###############################################################################
# VIEWS DE FORMULÁRIO (Passos 1 a 6)
###############################################################################

def ask_known1_view9(request):
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
        form = ConstantesVCte9(request.POST)
        if form.is_valid():
            request.session['property_choice'] = int(form.cleaned_data['property_choice'])
            request.session['value_input'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known2_9')
    else:
        form = ConstantesVCte9()
    return render(request, 'gas/ask_known1_9.html', {'form': form})

def ask_known2_view9(request):
    prop = request.session.get('property_choice')
    excluded = [str(prop)] if prop is not None else []

    if request.method == 'POST':
        form = ConstantesVCte9_2(request.POST, excluded_properties=excluded)
        if form.is_valid():
            second_property_choice = int(form.cleaned_data['property_choice'])
            second_value_input = float(form.cleaned_data['value_input'])

            # Validação
            const1 = int(request.session.get('property_choice'))
            val1 = float(request.session.get('value_input'))
            const_values = {const1: val1, second_property_choice: second_value_input}

            Cv0 = const_values.get(11); Cp0 = const_values.get(12)
            R = const_values.get(13); K = const_values.get(14)

            # Lógica Cruzada
            if Cp0 is not None and Cv0 is not None:
                R = Cp0 - Cv0; K = Cp0/Cv0 if Cv0 else None
            elif Cp0 is not None and R is not None:
                Cv0 = Cp0 - R; K = Cp0/Cv0 if Cv0 else None
            elif Cv0 is not None and R is not None:
                Cp0 = Cv0 + R; K = Cp0/Cv0 if Cv0 else None
            elif R is not None and K is not None and (K-1)!=0:
                Cv0 = R/(K-1); Cp0 = K*Cv0

            error_messages = []
            if R is not None and R <= 0: error_messages.append("R deve ser positivo.")

            if error_messages:
                context = {"Cv0": Cv0, "Cp0": Cp0, "R": R, "K": K, "error_messages": error_messages}
                return render(request, "error_constants.html", context)

            request.session['second_property_choice'] = second_property_choice
            request.session['second_value_input'] = second_value_input
            return redirect('ask_known3_9')
    else:
        form = ConstantesVCte9_2(excluded_properties=excluded)
    return render(request, 'gas/ask_known2_9.html', {'form': form})

def ask_known3_view9(request):
    if request.method == 'POST':
        form = VGasIdeal9(request.POST)
        if form.is_valid():
            request.session['V_value_input'] = float(form.cleaned_data['V_value_input'])
            return redirect('ask_known4_9')
    else:
        form = VGasIdeal9()
    return render(request, 'gas/ask_known3_9.html', {'form': form})

def ask_known4_view9(request):
    if request.method == 'POST':
        form = Prop1VCte9(request.POST)
        if form.is_valid():
            request.session['third_property_choice'] = int(form.cleaned_data['property_choice'])
            request.session['third_value_input'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known5_9')
    else:
        form = Prop1VCte9()
    return render(request, 'gas/ask_known4_9.html', {'form': form})

def ask_known5_view9(request):
    if request.method == 'POST':
        form = Prop2VCte9(request.POST)
        if form.is_valid():
            request.session['four_property_choice'] = int(form.cleaned_data['property_choice'])
            request.session['four_value_input'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known6_9')
    else:
        form = Prop2VCte9()
    return render(request, 'gas/ask_known5_9.html', {'form': form})

def ask_known6_view9(request):
    if request.method == 'POST':
        form = TvizGasIdeal9(request.POST)
        if form.is_valid():
            request.session['Tviz_value_input'] = float(form.cleaned_data['Tviz_value_input'])
            return redirect('process_values_9')
    else:
        form = TvizGasIdeal9()
    return render(request, 'gas/ask_known6_9.html', {'form': form})

###############################################################################
# CÁLCULOS FINAIS (VOLUME CONSTANTE)
###############################################################################

def process_values_view9(request):
    try:
        # =============================
        # 0️⃣ Ressincroniza a lista de estados com a SESSÃO do usuário atual
        # =============================
        # IMPORTANTE: `gas` é uma instância única compartilhada no módulo (via
        # `std.instancia_gas`), reaproveitada por TODOS os processos de gás e
        # TODAS as requisições. Sem este passo, `gas.lista_gas` pode conter o
        # estado deixado por outro usuário ou por outro tipo de processo
        # (isobárico, politrópico, etc.), fazendo o cálculo usar um "estado
        # anterior" que não é deste usuário/processo.
        if 'lista_gas' not in request.session:
            request.session['lista_gas'] = json.dumps([])
        try:
            gas.lista_gas = json.loads(request.session['lista_gas'])
        except Exception:
            gas.lista_gas = []

        # =============================
        # 1️⃣ Recupera dados da sessão
        # =============================
        V_input = float(request.session.get('V_value_input'))
        Tviz_input = float(request.session.get('Tviz_value_input'))

        c1_idx = int(request.session.get('property_choice'))
        c1_val = float(request.session.get('value_input'))
        c2_idx = int(request.session.get('second_property_choice'))
        c2_val = float(request.session.get('second_value_input'))

        prop1_idx = int(request.session.get('third_property_choice'))
        prop1_val = float(request.session.get('third_value_input'))

        prop2_idx = int(request.session.get('four_property_choice'))
        prop2_val = float(request.session.get('four_value_input'))

        # =============================
        # 2️⃣ Determina Constantes
        # =============================
        map_const = {c1_idx: c1_val, c2_idx: c2_val}

        Cv0 = map_const.get(11)
        Cp0 = map_const.get(12)
        R = map_const.get(13)
        K = map_const.get(14)

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
            Cv0 = R / (K - 1)
            Cp0 = K * Cv0

        if R is None or Cv0 is None:
            return redirect('error_type9')

        # =============================
        # 3️⃣ ESTADO 1 (INICIAL)
        # =============================

        # 🔥 SE EXISTIR ESTADO ANTERIOR → ELE É O INICIAL
        if gas.lista_gas:
            ultimo = gas.lista_gas[-1]

            # Estrutura salva:
            # [Cv, Cp, R, K, p, T_C, v]
            p1 = float(ultimo[4])
            T1 = to_kelvin(float(ultimo[5]))
            v1 = float(ultimo[6])

        else:
            # Primeiro processo
            v1 = V_input

            if prop1_idx == 0:  # T fornecido
                T1 = to_kelvin(prop1_val)
                p1 = (R * T1) / v1

            elif prop1_idx == 1:  # P fornecido
                p1 = prop1_val
                T1 = (p1 * v1) / R

            else:
                return redirect('error_type9')

        # =============================
        # 4️⃣ ESTADO 2 (FINAL)
        # =============================

        v2 = v1  # 🔥 Volume sempre constante

        if prop2_idx == 0:  # T fornecido
            T2 = to_kelvin(prop2_val)
            p2 = (R * T2) / v2

        elif prop2_idx == 1:  # P fornecido
            p2 = prop2_val
            T2 = (p2 * v2) / R

        elif prop2_idx == 8:  # Q fornecido
            Q12_input = prop2_val
            T2 = T1 + (Q12_input / Cv0)
            p2 = (R * T2) / v2

        else:
            return redirect('error_type9')

        # Validação mínima
        if T1 is None or T2 is None or p1 is None or p2 is None or T1 <= 0 or T2 <= 0:
            return redirect('error_type9')

        # =============================
        # 5️⃣ CÁLCULOS DO PROCESSO
        # =============================

        W12 = 0  # isocórico
        Q12 = Cv0 * (T2 - T1)

        Tviz_K = to_kelvin(Tviz_input)

        try:
            delta_S = Cv0 * log(T2 / T1)
            Sger = delta_S - (Q12 / Tviz_K)
        except:
            Sger = None

        # ==========================================================
        # GERAÇÃO DE MICROPROCESSOS PARA O DIAGRAMA (GÁS IDEAL)
        # ==========================================================
        pontos_grafico = request.session.get('pontos_grafico', [])

        num_passos = 150
        passo_T = (T2 - T1) / num_passos if T1 != T2 else 0

        # Funções teóricas para o gráfico (Ref arbitrária: 273.15 K e 100 kPa)
        def calc_h(T_K): return Cp0 * T_K
        def calc_s(T_K, P_kPa):
            if T_K <= 0 or P_kPa <= 0: return 0
            return Cp0 * log(T_K / 273.15) - R * log(P_kPa / 100)

        ramo_atual = []

        # Ponto Inicial
        ramo_atual.append({
            'T': round(to_celsius(T1), 2),
            'P': round(p1, 2),
            'v': round(v1, 6),
            's': round(calc_s(T1, p1), 4),
            'h': round(calc_h(T1), 2)
        })

        if passo_T != 0:
            for i in range(1, num_passos):
                T_micro = T1 + (i * passo_T)
                v_micro = v1  # Processo Isocórico
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
            'T': round(to_celsius(T2), 2),
            'P': round(p2, 2),
            'v': round(v2, 6),
            's': round(calc_s(T2, p2), 4),
            'h': round(calc_h(T2), 2)
        })

        pontos_grafico.append(ramo_atual)
        request.session['pontos_grafico'] = pontos_grafico

        # Sincroniza com a classe gas
        if hasattr(gas, 'pontos_grafico_gas'):
            gas.pontos_grafico_gas = pontos_grafico
        # ==========================================================

        # =============================
        # 6️⃣ SALVAR NOVO ESTADO
        # =============================

        T2_C = to_celsius(T2)

        novo_estado = [
            float(Cv0),
            float(Cp0),
            float(R),
            float(K),
            float(p2),
            float(T2_C),
            float(v2)
        ]

        gas.lista_gas.append(novo_estado)
        request.session['lista_gas'] = json.dumps(gas.lista_gas, default=str)

        # =============================
        # 6️⃣.1 HISTÓRICO DE PROCESSOS (para o Relatório Final)
        # =============================
        historico_processos = request.session.get('historico_processos', [])
        historico_processos.append({
            'TempViz': rd(Tviz_input),
            'Q': rd(Q12),
            'W': rd(W12),
            'Sger': rd(Sger),
        })
        request.session['historico_processos'] = historico_processos

        # =============================
        # 7️⃣ CONTEXTO PARA TEMPLATE
        # =============================

        context = {
            'Cv0': rd(Cv0),
            'Cp0': rd(Cp0),
            'R': rd(R),
            'K': rd(K),
            'V': rd(v1),
            'T1': rd(to_celsius(T1)),
            'T2': rd(T2_C),
            'p1': rd(p1),
            'p2': rd(p2),
            'Q12': rd(Q12),
            'W12': rd(W12),
            'Sger': rd(Sger),
            'Tviz': rd(Tviz_input),
            'teste': gas.lista_gas,
            'pontos_grafico_json': json.dumps(pontos_grafico), # Envia para o Chart.js
            'historico_processos_json': json.dumps(historico_processos) # Histórico p/ Relatório Final
        }

        return render(request, 'gas/results_9.html', context)

    except Exception as e:
        print(f"Erro process_values_9: {e}")
        return redirect('error_type9')

def error_type_view9(request):
    return render(request, 'erro_generico.html')
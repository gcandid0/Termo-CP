from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from math import log, isfinite, exp
import json
from . import estados as std

# Inicialização da estrutura de dados
if not hasattr(std, 'instancia_gas'):
    std.instancia_gas = std.gas_cls()

gas = std.instancia_gas

if not hasattr(gas, 'lista_gas') or gas.lista_gas is None:
    gas.lista_gas = []

from .forms import (
    ConstantesPoli11, ConstantesPoli11_2,
    Prop1Poli11, Prop1Poli11_2, Prop2TCte11,
    NGasIdeal11, TvizGasIdeal11
)

# Funções Auxiliares de Temperatura e Arredondamento
def to_kelvin(T): return T + 273.15 if T is not None else None
def to_celsius(T): return T - 273.15 if T is not None else None
def rd(x, ndigits=4):
    return round(x, ndigits) if isinstance(x, (int, float)) and isfinite(x) else None


# --- Funções de Fluxo de Formulário (Passos 1 a 7) ---

###############################################################################
# Passo 1 – Escolha da primeira constante
###############################################################################
def ask_known1_view11(request):
    # Limpa a lista de processos no início de um novo ciclo
    try:
        gas.limpar_gas()
    except Exception:
        gas.lista_gas = []
    request.session['lista_gas'] = json.dumps(gas.lista_gas, default=str)

    # ==========================================================
    # GARANTIA DE LIMPEZA DO GRÁFICO AO INICIAR NOVO CICLO
    # ==========================================================
    request.session['pontos_grafico'] = []
    if 'dados_processo' in request.session:
        del request.session['dados_processo']
    if hasattr(gas, 'pontos_grafico_gas'):
        gas.pontos_grafico_gas.clear()
    # ==========================================================

    if request.method == 'POST':
        form = ConstantesPoli11(request.POST)
        if form.is_valid():
            request.session['const_prop_1'] = str(form.cleaned_data['property_choice'])
            request.session['const_val_1'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known2_11')
    else:
        form = ConstantesPoli11()
    return render(request, 'ask_known1_11.html', {'form': form})


###############################################################################
# Passo 2 – Escolha da segunda constante (com verificação antecipada)
###############################################################################
def ask_known2_view11(request):
    prop = request.session.get('const_prop_1')
    excluded_properties = [str(prop)] if prop is not None else []

    if request.method == 'POST':
        form = ConstantesPoli11_2(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            second_property_choice = int(form.cleaned_data['property_choice'])
            second_value_input = float(form.cleaned_data['value_input'])

            const1 = int(request.session.get('const_prop_1')); val1 = float(request.session.get('const_val_1'))
            const_values = {const1: val1, second_property_choice: second_value_input}
            Cv0 = const_values.get(11); Cp0 = const_values.get(12); R = const_values.get(13); K = const_values.get(14)
            if Cp0 is not None and Cv0 is not None: R = Cp0 - Cv0; K = (Cp0 / Cv0) if Cv0 != 0 else None

            error_messages = []
            if Cp0 is not None and Cv0 is not None and Cp0 <= Cv0: error_messages.append("Cp deve ser maior que Cv.")
            if error_messages:
                context = {"mensagem_erro": "Erro nas Constantes: " + ", ".join(error_messages)}
                return render(request, "error_constants10.html", context)

            request.session['const_prop_2'] = str(second_property_choice)
            request.session['const_val_2'] = float(second_value_input)
            return redirect('ask_known3_11')

    else:
        form = ConstantesPoli11_2(excluded_properties=excluded_properties)
    return render(request, 'ask_known2_11.html', {'form': form})


###############################################################################
# Passo 3 – Primeira propriedade do estado 1
###############################################################################
def ask_known3_view11(request):
    if request.method == 'POST':
        form = Prop1Poli11(request.POST)
        if form.is_valid():
            request.session['state1_prop_1'] = str(form.cleaned_data['property_choice'])
            request.session['state1_val_1'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known4_11')
    else:
        form = Prop1Poli11()
    return render(request, 'ask_known3_11.html', {'form': form})


###############################################################################
# Passo 4 – Segunda propriedade do estado 1
###############################################################################
def ask_known4_view11(request):
    first = request.session.get('state1_prop_1')
    excluded_properties = [str(first)] if first is not None else []

    if request.method == 'POST':
        form = Prop1Poli11_2(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            request.session['state1_prop_2'] = str(form.cleaned_data['property_choice'])
            request.session['state1_val_2'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known5_11')
    else:
        form = Prop1Poli11_2(excluded_properties=excluded_properties)
    return render(request, 'ask_known4_11.html', {'form': form})


###############################################################################
# Passo 5 – Propriedade do estado 2 (p₂, v₂ ou Q₁₂)
###############################################################################
def ask_known5_view11(request):
    if request.method == 'POST':
        form = Prop2TCte11(request.POST)
        if form.is_valid():
            request.session['state2_prop'] = str(form.cleaned_data['property_choice'])
            request.session['state2_val'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known6_11')
    else:
        form = Prop2TCte11()
    return render(request, 'ask_known5_11.html', {'form': form})


###############################################################################
# Passo 6 – Expoente n
###############################################################################
def ask_known6_view11(request):
    if request.method == 'POST':
        form = NGasIdeal11(request.POST)
        if form.is_valid():
            request.session['n_value'] = float(form.cleaned_data['N_value_input'])
            return redirect('ask_known7_11')
    else:
        form = NGasIdeal11()
    return render(request, 'ask_known6_11.html', {'form': form})


###############################################################################
# Passo 7 – Temperatura da vizinhança
###############################################################################
def ask_known7_view11(request):
    if request.method == 'POST':
        form = TvizGasIdeal11(request.POST)
        if form.is_valid():
            request.session['tviz_value'] = float(form.cleaned_data['Tviz_value_input'])
            return redirect('process_values_11')
    else:
        form = TvizGasIdeal11()
    return render(request, 'ask_known7_11.html', {'form': form})


###############################################################################
# Passo 8 – Cálculos finais (Processo Politrópico)
###############################################################################
def process_values_view11(request):

    try:

        # =====================================
        # 0️⃣ LISTA DE ESTADOS
        # =====================================
        if 'lista_gas' not in request.session:
            request.session['lista_gas'] = json.dumps([])

        try:
            gas.lista_gas = json.loads(request.session['lista_gas'])
        except:
            gas.lista_gas = []

        # =====================================
        # 1️⃣ CONSTANTES
        # =====================================
        const1 = int(request.session.get('const_prop_1'))
        const2 = int(request.session.get('const_prop_2'))
        val1 = float(request.session.get('const_val_1'))
        val2 = float(request.session.get('const_val_2'))

        const_values = {const1: val1, const2: val2}

        Cv = const_values.get(11)
        Cp = const_values.get(12)
        R  = const_values.get(13)
        k  = const_values.get(14)

        if Cp and Cv:
            R = Cp - Cv
            k = Cp / Cv

        if R is None or R <= 0:
            return redirect('error_type11')

        if Cv is None:
            Cv = Cp - R
        if Cp is None:
            Cp = Cv + R
        if k is None:
            k = Cp / Cv

        # =====================================
        # 2️⃣ n e T_viz
        # =====================================
        n = float(request.session.get('n_value'))
        Tviz = to_kelvin(float(request.session.get('tviz_value')))

        # =====================================
        # 3️⃣ ESTADO 1 (CONTINUIDADE REAL)
        # =====================================
        if len(gas.lista_gas) > 0:

            ultimo = gas.lista_gas[-1]

            p1 = float(ultimo[4])
            T1 = to_kelvin(float(ultimo[5]))
            v1 = float(ultimo[6])

        else:

            s1p1 = int(request.session.get('state1_prop_1'))
            s1v1 = float(request.session.get('state1_val_1'))
            s1p2 = int(request.session.get('state1_prop_2'))
            s1v2 = float(request.session.get('state1_val_2'))

            T1 = p1 = v1 = None

            for prop, val in [(s1p1, s1v1), (s1p2, s1v2)]:
                if prop == 0:
                    T1 = to_kelvin(val)
                elif prop == 1:
                    p1 = val
                elif prop == 2:
                    v1 = val

            if T1 is None:
                T1 = p1 * v1 / R
            if p1 is None:
                p1 = R * T1 / v1
            if v1 is None:
                v1 = R * T1 / p1

        if None in (T1, p1, v1):
            return redirect('error_type11')

        # =====================================
        # 4️⃣ ESTADO 2 - DADO PELO USUÁRIO
        # =====================================
        s2p = int(request.session.get('state2_prop'))
        s2v = float(request.session.get('state2_val'))

        T2 = p2 = v2 = None
        Q_user = None

        if s2p == 0:
            T2 = to_kelvin(s2v)
        elif s2p == 1:
            p2 = s2v
        elif s2p == 2:
            v2 = s2v
        elif s2p == 8:
            Q_user = s2v

        # =====================================
        # 5️⃣ CÁLCULO DO ESTADO 2
        # =====================================

        if Q_user is not None:

            if abs(n - 1.0) > 1e-12:

                fator = Cv + R/(1 - n)
                T2 = T1 + Q_user / fator

                v2 = v1 * (T1 / T2)**(1/(n - 1))
                p2 = R * T2 / v2

            else:
                # isotérmico
                T2 = T1
                v2 = v1 * exp(Q_user/(R*T1))
                p2 = R*T2/v2

        else:

            if abs(n - 1.0) > 1e-12:

                if v2 is not None:
                    p2 = p1 * (v1/v2)**n
                    T2 = T1 * (v1/v2)**(n-1)

                elif p2 is not None:
                    v2 = v1 * (p1/p2)**(1/n)
                    T2 = T1 * (v1/v2)**(n-1)

                elif T2 is not None:
                    v2 = v1 * (T1/T2)**(1/(n-1))
                    p2 = p1 * (v1/v2)**n

            else:
                # isotérmico
                T2 = T1
                if v2 is not None:
                    p2 = p1 * v1 / v2
                elif p2 is not None:
                    v2 = p1 * v1 / p2

        if None in (T2, p2, v2):
            return redirect('error_type11')

        # =====================================
        # 6️⃣ TRABALHO
        # =====================================
        if abs(n - 1.0) > 1e-12:
            W = (p2*v2 - p1*v1)/(1 - n)
        else:
            W = R*T1*log(v2/v1)

        # =====================================
        # 7️⃣ CALOR REAL
        # =====================================
        Q = Q_user if Q_user is not None else Cv*(T2-T1) + W

        # =====================================
        # 8️⃣ ENTROPIA
        # =====================================
        delta_s = Cp*log(T2/T1) - R*log(p2/p1)
        Sger = delta_s - Q/Tviz

        processo_impossivel = Sger < 0

        # ==========================================================
        # GERAÇÃO DE MICROPROCESSOS PARA O DIAGRAMA (POLITRÓPICO)
        # ==========================================================
        pontos_grafico = request.session.get('pontos_grafico', [])

        num_passos = 150 # Usamos 15 passos para desenhar a curva Pv^n perfeitamente
        passo_v = (v2 - v1) / num_passos if v1 != v2 else 0

        # Funções teóricas para o gráfico (Ref arbitrária: 273.15 K e 100 kPa)
        # Proteção caso Cp não tenha sido informado pelo usuário
        cp_calc = Cp if Cp else 0
        def calc_h(T_K): return cp_calc * T_K
        def calc_s(T_K, P_kPa):
            if T_K <= 0 or P_kPa <= 0: return 0
            return cp_calc * log(T_K / 273.15) - R * log(P_kPa / 100)

        ramo_atual = []

        # Ponto Inicial
        ramo_atual.append({
            'T': round(to_celsius(T1), 2),
            'P': round(p1, 2),
            'v': round(v1, 6),
            's': round(calc_s(T1, p1), 4),
            'h': round(calc_h(T1), 2)
        })

        if passo_v != 0:
            for i in range(1, num_passos):
                v_micro = v1 + (i * passo_v)

                if abs(n - 1.0) > 1e-12:
                    P_micro = p1 * (v1/v_micro)**n
                else:
                    # Se n=1 é isotérmico
                    P_micro = p1 * v1 / v_micro

                T_micro = (P_micro * v_micro) / R

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


        # =====================================
        # 9️⃣ SALVAR ESTADO FINAL
        # =====================================
        novo_estado = [
            float(Cv),
            float(Cp),
            float(R),
            float(k),
            float(p2),
            float(to_celsius(T2)),
            float(v2)
        ]

        gas.lista_gas.append(novo_estado)
        request.session['lista_gas'] = json.dumps(gas.lista_gas)

        # =====================================
        # 🔟 CONTEXTO
        # =====================================
        context = {
            'Cv0': rd(Cv),
            'Cp0': rd(Cp),
            'R': rd(R),
            'K': rd(k),
            'n': rd(n),
            'T1': rd(to_celsius(T1)),
            'T2': rd(to_celsius(T2)),
            'p1': rd(p1),
            'p2': rd(p2),
            'v1': rd(v1),
            'v2': rd(v2),
            'Q12': rd(Q),
            'W12': rd(W),
            'Sger': rd(Sger),
            'processo_impossivel': processo_impossivel,
            'teste': gas.lista_gas,
            'Tviz': rd(Tviz-273.15),
            'pontos_grafico_json': json.dumps(pontos_grafico) # Envia para o Chart.js
        }

        return render(request, 'results_11.html', context)

    except Exception as e:
        print("ERRO POLITRÓPICO:", e)
        return redirect('error_type11')

def error_type_view11(request):
    return render(request, 'error_type7.html')
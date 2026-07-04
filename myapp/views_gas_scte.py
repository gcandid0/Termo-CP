from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from math import log, isfinite
import json
from . import estados as std # Necessário para a continuidade de estado

# Inicialização da estrutura de dados
if not hasattr(std, 'instancia_gas'):
    std.instancia_gas = std.gas_cls()

gas = std.instancia_gas

if not hasattr(gas, 'lista_gas') or gas.lista_gas is None:
    gas.lista_gas = []

from .forms import (
    ConstantesPoli12, ConstantesPoli12_2,
    Prop1_12, Prop1_2_12, Prop2_12
)

# Funções Auxiliares de Temperatura e Arredondamento
def to_kelvin(T): return T + 273.15 if T is not None else None
def to_celsius(T): return T - 273.15 if T is not None else None
def rd(x, ndigits=4):
    return round(x, ndigits) if isinstance(x, (int, float)) and isfinite(x) else None

# Helpers seguros para ler valores da sessão sem lançar TypeError/ValueError
# quando a chave não existir (sessão expirada, acesso direto à URL, etc.)
def safe_int(request, key, default=None):
    val = request.session.get(key)
    try:
        return int(val)
    except (TypeError, ValueError):
        return default

def safe_float(request, key, default=None):
    val = request.session.get(key)
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


###############################################################################
# ETAPAS DE COLETA DAS CONSTANTES E ESTADOS
###############################################################################
def ask_known1_view12(request):
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
        form = ConstantesPoli12(request.POST)
        if form.is_valid():
            request.session['const_prop_1'] = str(form.cleaned_data['property_choice'])
            request.session['const_val_1'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known2_12')
    else:
        form = ConstantesPoli12()
    return render(request, 'gas/ask_known1_12.html', {'form': form})


def ask_known2_view12(request):
    first = request.session.get('const_prop_1')
    excluded_properties = [str(first)] if first is not None else []

    if request.method == 'POST':
        form = ConstantesPoli12_2(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            second_prop = int(form.cleaned_data['property_choice'])
            second_val = float(form.cleaned_data['value_input'])

            # Validação de Constantes
            const1 = int(request.session.get('const_prop_1'))
            val1 = float(request.session.get('const_val_1'))
            const_values = {const1: val1, second_prop: second_val}

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
            request.session['const_prop_2'] = str(second_prop)
            request.session['const_val_2'] = second_val
            return redirect('ask_known3_12')
    else:
        form = ConstantesPoli12_2(excluded_properties=excluded_properties)
    return render(request, 'gas/ask_known2_12.html', {'form': form})


def ask_known3_view12(request):
    if request.method == 'POST':
        form = Prop1_12(request.POST)
        if form.is_valid():
            request.session['state1_prop_1'] = str(form.cleaned_data['property_choice'])
            request.session['state1_val_1'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known4_12')
    else:
        form = Prop1_12()
    return render(request, 'gas/ask_known3_12.html', {'form': form})


def ask_known4_view12(request):
    first = request.session.get('state1_prop_1')
    excluded_properties = [str(first)] if first is not None else []

    if request.method == 'POST':
        form = Prop1_2_12(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            request.session['state1_prop_2'] = str(form.cleaned_data['property_choice'])
            request.session['state1_val_2'] = float(form.cleaned_data['value_input'])
            return redirect('ask_known5_12')
    else:
        form = Prop1_2_12(excluded_properties=excluded_properties)
    return render(request, 'gas/ask_known4_12.html', {'form': form})


def ask_known5_view12(request):
    if request.method == 'POST':
        form = Prop2_12(request.POST)
        if form.is_valid():
            request.session['state2_prop'] = str(form.cleaned_data['property_choice'])
            request.session['state2_val'] = float(form.cleaned_data['value_input'])
            return redirect('process_values_12')
    else:
        form = Prop2_12()
    return render(request, 'gas/ask_known5_12.html', {'form': form})


###############################################################################
# PROCESSO ISENTRÓPICO (s = constante)
###############################################################################
def process_values_view12(request):
    try:
        # =====================================
        # 1️⃣ LISTA DE ESTADOS
        # =====================================
        if 'lista_gas' not in request.session:
            request.session['lista_gas'] = json.dumps([])

        try:
            gas.lista_gas = json.loads(request.session['lista_gas'])
        except:
            gas.lista_gas = []

        # =====================================
        # 2️⃣ CONSTANTES
        # =====================================
        cprop1 = safe_int(request, 'const_prop_1')
        cprop2 = safe_int(request, 'const_prop_2')
        cval1  = safe_float(request, 'const_val_1')
        cval2  = safe_float(request, 'const_val_2')

        if None in (cprop1, cprop2, cval1, cval2):
            return render(request, 'gas/results_12.html', {
                'mensagem': 'Sessão expirada ou incompleta. Por favor, reinicie o processo isentrópico desde o início.'
            })

        const_values = {cprop1: cval1, cprop2: cval2}

        Cv = const_values.get(11)
        Cp = const_values.get(12)
        R  = const_values.get(13)
        K  = const_values.get(14)

        # Dedução consistente das propriedades
        if Cp is not None and Cv is not None:
            R = Cp - Cv
            K = Cp / Cv if Cv != 0 else None
        elif Cp is not None and R is not None:
            Cv = Cp - R
            K = Cp / Cv if Cv != 0 else None
        elif Cv is not None and R is not None:
            Cp = Cv + R
            K = Cp / Cv if Cv != 0 else None
        elif R is not None and K is not None:
            if K != 1:
                Cv = R / (K - 1)
                Cp = K * Cv

        if R is None or R <= 0:
            return render(request, 'gas/results_12.html', {'mensagem': 'Erro: Faltam dados ou (R) é inválido.'})
        if K is None or K <= 1:
            return render(request, 'gas/results_12.html', {'mensagem': 'Erro: K deve ser > 1 para gás ideal isentrópico.'})

        # =====================================
        # 3️⃣ ESTADO 1 (CONTINUIDADE REAL)
        # =====================================
        if len(gas.lista_gas) > 0:
            ultimo = gas.lista_gas[-1]
            p1 = float(ultimo[4])
            T1 = to_kelvin(float(ultimo[5]))
            v1 = float(ultimo[6])

        else:
            s1p1 = safe_int(request, 'state1_prop_1')
            s1v1 = safe_float(request, 'state1_val_1')
            s1p2 = safe_int(request, 'state1_prop_2')
            s1v2 = safe_float(request, 'state1_val_2')

            if None in (s1p1, s1v1, s1p2, s1v2):
                return render(request, 'gas/results_12.html', {
                    'mensagem': 'Sessão expirada ou incompleta. Por favor, reinicie o processo isentrópico desde o início.'
                })

            T1 = p1 = v1 = None

            for prop, val in [(s1p1, s1v1), (s1p2, s1v2)]:
                if prop == 0:
                    T1 = to_kelvin(val)
                elif prop == 1:
                    p1 = val
                elif prop == 2:
                    v1 = val

            try:
                if T1 is None: T1 = (p1 * v1) / R
                if p1 is None: p1 = (R * T1) / v1
                if v1 is None: v1 = (R * T1) / p1
            except ZeroDivisionError:
                return render(request, 'gas/results_12.html', {'mensagem': 'Divisão por zero ao definir o Estado 1.'})

        if None in (T1, p1, v1):
            return render(request, 'gas/results_12.html', {'mensagem': 'Estado 1 incompleto ou inválido.'})

        # =====================================
        # 4️⃣ ESTADO 2
        # =====================================
        s2p = safe_int(request, 'state2_prop')
        s2v = safe_float(request, 'state2_val')

        if s2p is None or s2v is None:
            return render(request, 'gas/results_12.html', {
                'mensagem': 'Sessão expirada ou incompleta. Por favor, reinicie o processo isentrópico desde o início.'
            })

        T2 = p2 = v2 = None

        if s2p == 0:    # Temperatura (Celsius -> Kelvin)
            T2 = to_kelvin(s2v)
        elif s2p == 1:  # Pressão
            p2 = s2v
        elif s2p == 2:  # Volume Específico
            v2 = s2v
        elif s2p == 9:  # Trabalho (W12)
            W12_input = s2v
            # W12 = Cv * (T1 - T2)  ->  T2 = T1 - (W12 / Cv)
            T2 = T1 - (W12_input / Cv)
        elif s2p == 8:  # Calor (Q)
            return render(request, 'gas/results_12.html', {'mensagem': 'O calor (Q) em processo isentrópico é zero. Por favor, escolha outra variável.'})
        else:
            return render(request, 'gas/results_12.html', {'mensagem': f'Propriedade de entrada ({s2p}) desconhecida para o Estado 2.'})

        # =====================================
        # 5️⃣ RELAÇÕES ISENTRÓPICAS (s = constante)
        # =====================================
        try:
            if p2 is not None:
                T2 = T1 * (p2/p1)**((K-1)/K)
                v2 = v1 * (p1/p2)**(1/K)

            elif v2 is not None:
                T2 = T1 * (v1/v2)**(K-1)
                p2 = p1 * (v1/v2)**K

            elif T2 is not None:
                if T2 <= 0:
                    return render(request, 'gas/results_12.html', {'mensagem': 'Erro: A temperatura absoluta final (K) calculada é negativa ou zero.'})
                v2 = v1 * (T1/T2)**(1/(K-1))
                p2 = p1 * (v1/v2)**K

        except Exception as e:
            return render(request, 'gas/results_12.html', {'mensagem': f'Erro matemático ao relacionar estados (verifique entradas negativas): {e}'})

        if None in (T2, p2, v2):
            return render(request, 'gas/results_12.html', {'mensagem': 'As propriedades do Estado 2 não puderam ser resolvidas com os dados.'})

        # =====================================
        # 6️⃣ PROPRIEDADES DO PROCESSO
        # =====================================
        # Processo isentrópico: por definição, Q = 0 (adiabático) e Sger = 0
        # (internamente reversível, Δs = 0). Por isso essas variáveis não são
        # calculadas nem exibidas — só o trabalho (W) é relevante aqui.
        # W12 = \int p dv. Isentrópico: W = Cv * (T1 - T2)
        W12 = Cv * (T1 - T2)

        # ==========================================================
        # GERAÇÃO DE MICROPROCESSOS PARA O DIAGRAMA (ISENTRÓPICO)
        # ==========================================================
        pontos_grafico = request.session.get('pontos_grafico', [])

        num_passos = 150 # Usamos 15 passos para desenhar as curvas suavemente
        passo_v = (v2 - v1) / num_passos if v1 != v2 else 0

        # Funções teóricas (Referência 273.15 K e 100 kPa)
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

                # Relações Isentrópicas P(v) e T(v)
                P_micro = p1 * (v1/v_micro)**K
                T_micro = T1 * (v1/v_micro)**(K-1)

                # A entropia calculada deve ser rigorosamente igual a s1, mas calculamos dinamicamente por garantia
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
        # 7️⃣ SALVAR ESTADO
        # =====================================
        T2_C = to_celsius(T2)

        novo_estado = [
            float(Cv),
            float(Cp),
            float(R),
            float(K),
            float(p2),
            float(T2_C),
            float(v2)
        ]

        gas.lista_gas.append(novo_estado)
        request.session['lista_gas'] = json.dumps(gas.lista_gas)

        # =====================================
        # 8️⃣ CONTEXTO PARA O TEMPLATE HTML
        # =====================================
        context = {
            'Cv0': rd(Cv),
            'Cp0': rd(Cp),
            'R': rd(R),
            'K': rd(K),
            'T1': rd(to_celsius(T1)),
            'T2': rd(T2_C),
            'p1': rd(p1),
            'p2': rd(p2),
            'v1': rd(v1),
            'v2': rd(v2),
            'W12': rd(W12),
            'mensagem': "Processo isentrópico (s=constante) calculado com sucesso!",
            'teste': gas.lista_gas,
            'pontos_grafico_json': json.dumps(pontos_grafico) # Dados do Gráfico Interativo
        }

        return render(request, 'gas/results_12.html', context)

    except Exception as e:
        print("Erro geral no cálculo isentrópico:", e)
        return render(request, 'gas/results_12.html', {'mensagem': f'Erro crítico na view: {e}'})


def error_type_view12(request):
    return render(request, 'erro_generico.html')
# -*- coding: utf-8 -*-
import json
import math
import random
import time

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import SimulacaoCompartilhada, UsoSimulacao
from .thermo_engine import (
    compute_pcte_process_context,
    compute_scte_process_context,
    compute_single_state_context,
    compute_vcte_process_context,
)


# ==============================================================================
# 1. ESTATÍSTICAS ANÔNIMAS DE USO (/api/log-uso/)
# ==============================================================================

@csrf_exempt
@require_POST
def api_log_uso_view(request):
    """Registra anonimamente o uso de uma simulação (substância, tipo e idioma)."""
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    substancia = str(body.get('substancia', '')).strip()[:50]
    tipo = str(body.get('tipo', '')).strip()[:60]
    idioma = str(body.get('idioma', 'pt-br')).strip()[:10] or 'pt-br'

    if not substancia or not tipo:
        return JsonResponse({'ok': False, 'error': 'Campos obrigatórios ausentes'}, status=400)

    UsoSimulacao.objects.create(
        substancia=substancia,
        tipo=tipo,
        idioma=idioma,
    )
    return JsonResponse({'ok': True})


# ==============================================================================
# 2. LINK COMPARTILHÁVEL DE SIMULAÇÃO (/api/compartilhar/ e /s/<codigo>/)
# ==============================================================================

@csrf_exempt
@require_POST
def api_compartilhar_view(request):
    """Salva snapshot de uma simulação e retorna o link curto compartilhável /s/<codigo>/."""
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'JSON inválido'}, status=400)

    titulo = str(body.get('titulo', 'Simulação TERMO-CP')).strip()[:200]
    substancia = str(body.get('substancia', 'Substância')).strip()[:60]
    tipo = str(body.get('tipo', 'Simulação')).strip()[:60]
    payload = body.get('payload')

    if not isinstance(payload, dict):
        return JsonResponse({'ok': False, 'error': 'Payload inválido'}, status=400)

    sim = SimulacaoCompartilhada.objects.create(
        titulo=titulo,
        substancia=substancia,
        tipo=tipo,
        payload_json=json.dumps(payload, ensure_ascii=False),
    )
    share_url = request.build_absolute_uri(f'/s/{sim.codigo}/')
    return JsonResponse({'ok': True, 'codigo': sim.codigo, 'url': share_url})


@require_GET
def shared_simulation_view(request, codigo):
    """Exibe uma simulação compartilhada a partir do código curto /s/<codigo>/."""
    sim = get_object_or_404(SimulacaoCompartilhada, codigo=codigo.upper())
    try:
        payload = json.loads(sim.payload_json)
    except ValueError:
        payload = {}

    return render(request, 'shared_simulation.html', {
        'sim': sim,
        'payload': payload,
        'payload_json': sim.payload_json,
    })


# ==============================================================================
# 3. MODO EXERCÍCIO / AUTOAVALIAÇÃO POE COM TRAVA ANTI-BURLA (/exercicios/)
# ==============================================================================

_PURE_PRESETS = {
    1: {
        'name': 'Água', 'unit_t': '°C',
        'p_choices': [100.0, 200.0, 300.0, 400.0, 500.0],
        't1_choices': [40.0, 50.0, 60.0, 80.0],
        't2_choices': [150.0, 200.0, 250.0, 300.0],
        'p2_scte': [300.0, 400.0, 500.0, 600.0],
        'tviz_choices': [200.0, 250.0, 300.0, 350.0],
        'tviz_challenge': [30.0, 60.0, 80.0, 220.0],
    },
    2: {
        'name': 'Amônia', 'unit_t': '°C',
        'p_choices': [200.0, 300.0, 400.0, 500.0],
        't1_choices': [-10.0, 0.0, 10.0],
        't2_choices': [40.0, 50.0, 60.0, 80.0],
        'p2_scte': [500.0, 600.0, 800.0],
        'tviz_choices': [100.0, 120.0, 150.0],
        'tviz_challenge': [-20.0, 10.0, 110.0],
    },
    3: {
        'name': 'CO₂', 'unit_t': '°C',
        'p_choices': [800.0, 1000.0, 1400.0, 2000.0],
        't1_choices': [-20.0, -10.0, 0.0],
        't2_choices': [20.0, 40.0, 60.0],
        'p2_scte': [1400.0, 2000.0, 3000.0],
        'tviz_choices': [80.0, 100.0, 120.0],
        'tviz_challenge': [-30.0, 0.0, 90.0],
    },
    4: {
        'name': 'R-410A', 'unit_t': '°C',
        'p_choices': [400.0, 500.0, 800.0],
        't1_choices': [-10.0, 0.0, 10.0],
        't2_choices': [30.0, 40.0, 60.0],
        'p2_scte': [800.0, 1000.0, 1400.0],
        'tviz_choices': [80.0, 100.0, 120.0],
        'tviz_challenge': [-20.0, 5.0, 90.0],
    },
    5: {
        'name': 'R-134a', 'unit_t': '°C',
        'p_choices': [300.0, 400.0, 500.0],
        't1_choices': [10.0, 20.0, 30.0],
        't2_choices': [50.0, 60.0, 80.0],
        'p2_scte': [600.0, 800.0, 1000.0],
        'tviz_choices': [100.0, 120.0, 150.0],
        'tviz_challenge': [0.0, 20.0, 110.0],
    },
    6: {
        'name': 'Nitrogênio', 'unit_t': 'K',
        'p_choices': [200.0, 400.0, 500.0],
        't1_choices': [120.0, 140.0, 160.0],
        't2_choices': [200.0, 240.0, 280.0],
        'p2_scte': [600.0, 800.0, 1000.0],
        'tviz_choices': [300.0, 350.0, 400.0],
        'tviz_challenge': [100.0, 150.0, 320.0],
    },
    7: {
        'name': 'Metano', 'unit_t': 'K',
        'p_choices': [200.0, 400.0, 500.0],
        't1_choices': [140.0, 160.0, 180.0],
        't2_choices': [220.0, 260.0, 300.0],
        'p2_scte': [600.0, 800.0, 1000.0],
        'tviz_choices': [320.0, 360.0, 400.0],
        'tviz_challenge': [120.0, 180.0, 340.0],
    },
}

_IDEAL_GASES = [
    ('Ar (Gás Ideal)', 0.287, 1.005, 0.718),
    ('Nitrogênio N₂ (Gás Ideal)', 0.2968, 1.039, 0.743),
    ('Oxigênio O₂ (Gás Ideal)', 0.2598, 0.918, 0.658),
    ('CO₂ (Gás Ideal)', 0.1889, 0.846, 0.657),
]

MIN_SOLVE_SECONDS = 25


def _generate_ideal_gas_problem(proc_type, mass, challenge=False):
    g_name, R, cp0, cv0 = random.choice(_IDEAL_GASES)
    k = cp0 / cv0
    P1 = random.choice([100.0, 150.0, 200.0, 250.0])
    T1_C = random.choice([25.0, 30.0, 40.0, 50.0])
    T1_K = T1_C + 273.15
    v1 = (R * T1_K) / P1

    if proc_type == 'estado':
        V_tot = mass * v1
        prompt = {
            'substance': g_name, 'process': 'estado', 'mass': mass, 'unit_t': '°C',
            'formula_hint': 'Equação de Estado do Gás Ideal: P·v = R·T (com T em Kelvin: T[K] = T[°C] + 273,15) e V = m·v.',
            'given': [
                f'Gás: {g_name}', f'R = {R} kJ/kg·K',
                f'm = {mass} kg', f'P = {P1} kPa', f'T = {T1_C} °C',
            ],
            'ask_fields': ['v', 'V'],
            'is_state': True,
        }
        solution = {
            'v': round(v1, 5), 'V': round(V_tot, 5),
            'expected_vol': 'const', 'expected_heat': 'zero', 'expected_law2': 'possible',
            'steps': [
                f'1) Conversão obrigatória para Kelvin: T = {T1_C} + 273,15 = {T1_K:.2f} K.',
                f'2) Volume específico: v = R·T / P = ({R} × {T1_K:.2f}) / {P1} = {v1:.5f} m³/kg.',
                f'3) Volume total do cilindro: V = m · v = {mass} × {v1:.5f} = {V_tot:.5f} m³.',
            ],
        }
        return prompt, solution

    if proc_type == 'pcte':
        T2_C = random.choice([120.0, 150.0, 180.0, 220.0])
        T2_K = T2_C + 273.15
        P2 = P1
        v2 = (R * T2_K) / P2
        W = mass * P1 * (v2 - v1)
        Q = mass * cp0 * (T2_K - T1_K)
        Tviz_C = random.choice([20.0, 40.0, T2_C + 50.0]) if challenge else (T2_C + random.choice([40.0, 60.0, 80.0]))
        Tviz_K = Tviz_C + 273.15
        ds = cp0 * math.log(T2_K / T1_K) - R * math.log(P2 / P1)
        Sger = mass * ds - (Q / Tviz_K)
        prompt = {
            'substance': g_name, 'process': 'pcte', 'mass': mass, 'unit_t': '°C',
            'formula_hint': 'Isobárico (Gás Ideal): W = m·P·(v₂ − v₁) = m·R·(T₂ − T₁); Q = m·Cp0·(T₂ − T₁); Sger = m·Cp0·ln(T₂/T₁) − Q/T_viz(K).',
            'given': [
                f'R = {R} kJ/kg·K', f'Cp0 = {cp0} kJ/kg·K', f'Cv0 = {cv0} kJ/kg·K',
                f'm = {mass} kg', f'P₁ = {P1} kPa', f'T₁ = {T1_C} °C',
                f'T₂ = {T2_C} °C (P = constante)', f'T_viz = {Tviz_C} °C',
            ],
            'ask_fields': ['W', 'Q', 'Sger'],
            'is_state': False,
        }
        solution = {
            'W': round(W, 2), 'Q': round(Q, 2), 'Sger': round(Sger, 4),
            'expected_vol': 'expand' if v2 > v1 else 'compress',
            'expected_heat': 'in' if Q > 0 else 'out',
            'expected_law2': 'possible' if Sger >= -1e-6 else 'impossible',
            'steps': [
                f'1) Estado 1: T₁ = {T1_K:.2f} K, v₁ = R·T₁/P₁ = {v1:.5f} m³/kg.',
                f'2) Estado 2: T₂ = {T2_K:.2f} K, P₂ = {P2:.1f} kPa, v₂ = R·T₂/P₂ = {v2:.5f} m³/kg.',
                f'3) Trabalho isobárico: W = m·P·(v₂ − v₁) = {mass} × {P1} × ({v2:.5f} − {v1:.5f}) = {W:.2f} kJ.',
                f'4) Calor (1ª Lei): Q = m·Cp0·(T₂ − T₁) = {mass} × {cp0} × ({T2_K:.2f} − {T1_K:.2f}) = {Q:.2f} kJ.',
                f'5) Entropia gerada (2ª Lei): Sger = m·[Cp0·ln(T₂/T₁) − R·ln(P₂/P₁)] − Q/T_viz = {Sger:.4f} kJ/K.',
            ],
        }
    elif proc_type == 'vcte':
        T2_C = random.choice([120.0, 160.0, 200.0, 240.0])
        T2_K = T2_C + 273.15
        v2 = v1
        P2 = P1 * (T2_K / T1_K)
        W = 0.0
        Q = mass * cv0 * (T2_K - T1_K)
        Tviz_C = random.choice([20.0, 40.0, T2_C + 50.0]) if challenge else (T2_C + random.choice([40.0, 60.0, 80.0]))
        Tviz_K = Tviz_C + 273.15
        ds = cv0 * math.log(T2_K / T1_K)
        Sger = mass * ds - (Q / Tviz_K)
        prompt = {
            'substance': g_name, 'process': 'vcte', 'mass': mass, 'unit_t': '°C',
            'formula_hint': 'Isocórico (Gás Ideal): P₂/T₂ = P₁/T₁; W = 0; Q = m·Cv0·(T₂ − T₁); Sger = m·Cv0·ln(T₂/T₁) − Q/T_viz(K).',
            'given': [
                f'R = {R} kJ/kg·K', f'Cp0 = {cp0} kJ/kg·K', f'Cv0 = {cv0} kJ/kg·K',
                f'm = {mass} kg', f'P₁ = {P1} kPa', f'T₁ = {T1_C} °C',
                f'T₂ = {T2_C} °C (v = constante)', f'T_viz = {Tviz_C} °C',
            ],
            'ask_fields': ['P2', 'W', 'Q', 'Sger'],
            'is_state': False,
        }
        solution = {
            'P2': round(P2, 2), 'W': 0.0, 'Q': round(Q, 2), 'Sger': round(Sger, 4),
            'expected_vol': 'const',
            'expected_heat': 'in' if Q > 0 else 'out',
            'expected_law2': 'possible' if Sger >= -1e-6 else 'impossible',
            'steps': [
                f'1) Estado 1: T₁ = {T1_K:.2f} K, v₁ = R·T₁/P₁ = {v1:.5f} m³/kg.',
                f'2) Estado 2 (v₂ = v₁): P₂ = P₁·(T₂/T₁) = {P1} × ({T2_K:.2f}/{T1_K:.2f}) = {P2:.2f} kPa.',
                '3) Trabalho isocórico: fronteira fixa (dV = 0) ⇒ W = 0,00 kJ.',
                f'4) Calor (1ª Lei): Q = m·Cv0·(T₂ − T₁) = {mass} × {cv0} × ({T2_K:.2f} − {T1_K:.2f}) = {Q:.2f} kJ.',
                f'5) Entropia gerada (2ª Lei): Sger = m·Cv0·ln(T₂/T₁) − Q/T_viz = {Sger:.4f} kJ/K.',
            ],
        }
    elif proc_type == 'tcte':
        P2 = P1 * random.choice([0.5, 2.0, 2.5, 3.0])
        T2_K = T1_K
        v2 = (R * T2_K) / P2
        W = mass * R * T1_K * math.log(v2 / v1)
        Q = W
        Tviz_C = T1_C + (random.choice([-15.0, 25.0]) if challenge else (25.0 if Q > 0 else -15.0))
        Tviz_K = Tviz_C + 273.15
        ds = -R * math.log(P2 / P1)
        Sger = mass * ds - (Q / Tviz_K)
        prompt = {
            'substance': g_name, 'process': 'tcte', 'mass': mass, 'unit_t': '°C',
            'formula_hint': 'Isotérmico (Gás Ideal): ΔU = 0 ⇒ Q = W = m·R·T·ln(v₂/v₁) = m·R·T·ln(P₁/P₂); Sger = −m·R·ln(P₂/P₁) − Q/T_viz(K).',
            'given': [
                f'R = {R} kJ/kg·K', f'm = {mass} kg',
                f'P₁ = {P1} kPa', f'T₁ = T₂ = {T1_C} °C (isotérmico)',
                f'P₂ = {P2} kPa', f'T_viz = {Tviz_C} °C',
            ],
            'ask_fields': ['W', 'Q', 'Sger'],
            'is_state': False,
        }
        solution = {
            'W': round(W, 2), 'Q': round(Q, 2), 'Sger': round(Sger, 4),
            'expected_vol': 'expand' if v2 > v1 else 'compress',
            'expected_heat': 'in' if Q > 0 else 'out',
            'expected_law2': 'possible' if Sger >= -1e-6 else 'impossible',
            'steps': [
                f'1) Temperatura absoluta constante: T = {T1_K:.2f} K; v₁ = {v1:.5f} m³/kg, v₂ = {v2:.5f} m³/kg.',
                f'2) Trabalho isotérmico: W = m·R·T·ln(P₁/P₂) = {mass} × {R} × {T1_K:.2f} × ln({P1}/{P2}) = {W:.2f} kJ.',
                f'3) Como T = cte para gás ideal, ΔU = 0 ⇒ Q = W = {Q:.2f} kJ.',
                f'4) Entropia gerada (2ª Lei): Sger = −m·R·ln(P₂/P₁) − Q/T_viz(K) = {Sger:.4f} kJ/K.',
            ],
        }
    elif proc_type == 'poli':
        n = random.choice([1.2, 1.3, 1.5, 1.6])
        P2 = P1 * random.choice([2.0, 2.5, 3.0])
        T2_K = T1_K * ((P2 / P1) ** ((n - 1.0) / n))
        T2_C = T2_K - 273.15
        v2 = (R * T2_K) / P2
        W = (mass * R * (T2_K - T1_K)) / (1.0 - n)
        dU = mass * cv0 * (T2_K - T1_K)
        Q = dU + W
        Tviz_C = 25.0 if Q < 0 else (T2_C + 40.0)
        Tviz_K = Tviz_C + 273.15
        ds = cp0 * math.log(T2_K / T1_K) - R * math.log(P2 / P1)
        Sger = mass * ds - (Q / Tviz_K)
        prompt = {
            'substance': g_name, 'process': 'poli', 'mass': mass, 'unit_t': '°C',
            'formula_hint': f'Politrópico (n = {n}): T₂ = T₁·(P₂/P₁)^((n−1)/n); W = m·R·(T₂ − T₁)/(1 − n); Q = m·Cv0·(T₂ − T₁) + W.',
            'given': [
                f'R = {R} kJ/kg·K', f'Cp0 = {cp0} kJ/kg·K', f'Cv0 = {cv0} kJ/kg·K',
                f'm = {mass} kg', f'P₁ = {P1} kPa', f'T₁ = {T1_C} °C',
                f'P₂ = {P2} kPa', f'Expoente politrópico n = {n}', f'T_viz = {Tviz_C} °C',
            ],
            'ask_fields': ['T2', 'W', 'Q', 'Sger'],
            'is_state': False,
        }
        solution = {
            'T2': round(T2_C, 2), 'W': round(W, 2), 'Q': round(Q, 2), 'Sger': round(Sger, 4),
            'expected_vol': 'compress' if v2 < v1 else 'expand',
            'expected_heat': 'in' if Q > 0 else 'out',
            'expected_law2': 'possible' if Sger >= -1e-6 else 'impossible',
            'steps': [
                f'1) T₁ = {T1_K:.2f} K; T₂ = T₁·(P₂/P₁)^((n−1)/n) = {T2_K:.2f} K ({T2_C:.2f} °C).',
                f'2) Trabalho politrópico: W = m·R·(T₂ − T₁)/(1 − n) = {W:.2f} kJ.',
                f'3) Calor (1ª Lei): Q = m·Cv0·(T₂ − T₁) + W = {dU:.2f} + ({W:.2f}) = {Q:.2f} kJ.',
                f'4) Entropia gerada (2ª Lei): Sger = m·[Cp0·ln(T₂/T₁) − R·ln(P₂/P₁)] − Q/T_viz(K) = {Sger:.4f} kJ/K.',
            ],
        }
    else:  # scte
        P2 = P1 * random.choice([2.0, 2.5, 3.0, 4.0])
        T2_K = T1_K * ((P2 / P1) ** ((k - 1.0) / k))
        T2_C = T2_K - 273.15
        v2 = (R * T2_K) / P2
        W = (mass * R * (T2_K - T1_K)) / (1.0 - k)
        Q = 0.0
        prompt = {
            'substance': g_name, 'process': 'scte', 'mass': mass, 'unit_t': '°C',
            'formula_hint': 'Isentrópico (Gás Ideal): T₂ = T₁·(P₂/P₁)^((k−1)/k); Q = 0; Sger = 0; W = m·R·(T₂ − T₁)/(1 − k) = −m·Cv0·(T₂ − T₁).',
            'given': [
                f'R = {R} kJ/kg·K', f'Cp0 = {cp0} kJ/kg·K', f'Cv0 = {cv0} kJ/kg·K (k = {k:.3f})',
                f'm = {mass} kg', f'P₁ = {P1} kPa', f'T₁ = {T1_C} °C',
                f'P₂ = {P2} kPa (adiabático e reversível)',
            ],
            'ask_fields': ['T2', 'W', 'Q'],
            'is_state': False,
        }
        solution = {
            'T2': round(T2_C, 2), 'W': round(W, 2), 'Q': 0.0,
            'expected_vol': 'compress' if v2 < v1 else 'expand',
            'expected_heat': 'zero',
            'expected_law2': 'possible',
            'steps': [
                f'1) Expoente isentrópico: k = Cp0/Cv0 = {k:.4f}; T₁ = {T1_K:.2f} K.',
                f'2) Temperatura final: T₂ = T₁·(P₂/P₁)^((k−1)/k) = {T2_K:.2f} K ({T2_C:.2f} °C).',
                '3) Processo adiabático e reversível: Q = 0,00 kJ e Sger = 0,0000 kJ/K.',
                f'4) Trabalho isentrópico: W = m·R·(T₂ − T₁)/(1 − k) = {W:.2f} kJ.',
            ],
        }
    return prompt, solution


def _generate_pure_problem(opt, proc_type, mass, challenge=False):
    cfg = _PURE_PRESETS[opt]
    unit_t = cfg['unit_t']
    if proc_type in ('tcte', 'poli'):
        return _generate_ideal_gas_problem(proc_type, mass, challenge=challenge)

    for _ in range(15):
        try:
            P1 = random.choice(cfg['p_choices'])
            T1 = random.choice(cfg['t1_choices'])
            le, pg = [], []

            if proc_type == 'estado':
                # Generate saturated mixture or superheated vapor state
                if random.random() < 0.5:
                    x_pct = random.choice([25.0, 40.0, 55.0, 70.0, 80.0])
                    ctx = compute_single_state_context(opt, 1, 6, P1, x_pct, mass=mass)
                    T_val = float(ctx['temperatura'])
                    v_val = float(ctx['volume_especifico'])
                    h_val = float(ctx['entalpia_especifica'])
                    s_val = float(ctx['entropia_especifica'])
                    prompt = {
                        'substance': cfg['name'], 'process': 'estado', 'mass': mass, 'unit_t': unit_t,
                        'formula_hint': 'Região de saturação: y = y_l + x·(y_v − y_l), onde x é o título em fração decimal (0 a 1).',
                        'given': [
                            f'Substância: {cfg["name"]}', f'm = {mass} kg',
                            f'P = {P1} kPa', f'Título x = {x_pct}% (x = {x_pct/100:.2f})',
                        ],
                        'ask_fields': ['T2', 'h', 's'],
                        'is_state': True,
                    }
                    solution = {
                        'T2': round(T_val, 2), 'h': round(h_val, 2), 's': round(s_val, 4),
                        'expected_vol': 'const', 'expected_heat': 'zero', 'expected_law2': 'possible',
                        'steps': [
                            f'1) Na tabela de saturação em P = {P1} kPa: T_sat = {T_val:.2f} {unit_t}.',
                            f'2) Aplicando y = y_l + x·(y_v − y_l) com x = {x_pct/100:.2f}:',
                            f'3) v = {v_val:.6f} m³/kg; h = {h_val:.2f} kJ/kg; s = {s_val:.4f} kJ/kg·K.',
                        ],
                    }
                else:
                    T_sup = random.choice(cfg['t2_choices'])
                    ctx = compute_single_state_context(opt, 1, 0, P1, T_sup, mass=mass)
                    v_val = float(ctx['volume_especifico'])
                    h_val = float(ctx['entalpia_especifica'])
                    s_val = float(ctx['entropia_especifica'])
                    prompt = {
                        'substance': cfg['name'], 'process': 'estado', 'mass': mass, 'unit_t': unit_t,
                        'formula_hint': 'Compare T com T_sat(P): se T > T_sat, consulte a tabela de vapor superaquecido (interpolando se necessário).',
                        'given': [
                            f'Substância: {cfg["name"]}', f'm = {mass} kg',
                            f'P = {P1} kPa', f'T = {T_sup} {unit_t}',
                        ],
                        'ask_fields': ['v', 'h', 's'],
                        'is_state': True,
                    }
                    solution = {
                        'v': round(v_val, 5), 'h': round(h_val, 2), 's': round(s_val, 4),
                        'expected_vol': 'const', 'expected_heat': 'zero', 'expected_law2': 'possible',
                        'steps': [
                            f'1) Em P = {P1} kPa e T = {T_sup} {unit_t}, a substância encontra-se na região de vapor superaquecido.',
                            f'2) Consultando/interpolando a tabela de vapor superaquecido: v = {v_val:.5f} m³/kg, h = {h_val:.2f} kJ/kg, s = {s_val:.4f} kJ/kg·K.',
                        ],
                    }
                return prompt, solution

            if proc_type == 'pcte':
                T2_in = random.choice(cfg['t2_choices'])
                Tviz = random.choice(cfg['tviz_challenge'] if challenge else cfg['tviz_choices'])
                ctx, _, _ = compute_pcte_process_context(opt, (1, 0, P1, T1), 0, T2_in, Tviz, le, pg, mass=mass)
                W = float(ctx['Trabalho'])
                Q = float(ctx['Calor'])
                Sger = float(ctx['Sger'])
                v1 = float(ctx['volume_especifico'])
                v2 = float(ctx['volume_especifico2'])
                h1 = float(ctx['entalpia_especifica'])
                h2 = float(ctx['entalpia_especifica2'])
                s1 = float(ctx['entropia_especifica'])
                s2 = float(ctx['entropia_especifica2'])
                prompt = {
                    'substance': cfg['name'], 'process': 'pcte', 'mass': mass, 'unit_t': unit_t,
                    'formula_hint': 'Isobárico (P = cte): W = m·P·(v₂ − v₁); Q = m·(h₂ − h₁); Sger = m·(s₂ − s₁) − Q/T_viz(K).',
                    'given': [
                        f'Substância: {cfg["name"]}', f'm = {mass} kg',
                        f'P₁ = {P1} kPa', f'T₁ = {T1} {unit_t}',
                        f'T₂ = {T2_in} {unit_t} (P = constante)',
                        f'T_viz = {Tviz} {unit_t}',
                    ],
                    'ask_fields': ['W', 'Q', 'Sger'],
                    'is_state': False,
                }
                solution = {
                    'W': round(W, 2), 'Q': round(Q, 2), 'Sger': round(Sger, 4),
                    'expected_vol': 'expand' if v2 > v1 else ('compress' if v2 < v1 else 'const'),
                    'expected_heat': 'in' if Q > 0 else 'out',
                    'expected_law2': 'possible' if Sger >= -1e-6 else 'impossible',
                    'steps': [
                        f'1) Estado 1 (P₁={P1} kPa, T₁={T1} {unit_t}): v₁ = {v1:.6f} m³/kg, h₁ = {h1:.2f} kJ/kg, s₁ = {s1:.4f} kJ/kg·K.',
                        f'2) Estado 2 (P₂={P1} kPa, T₂={T2_in} {unit_t}): v₂ = {v2:.6f} m³/kg, h₂ = {h2:.2f} kJ/kg, s₂ = {s2:.4f} kJ/kg·K.',
                        f'3) Trabalho isobárico: W = m·P·(v₂ − v₁) = {mass} × {P1} × ({v2:.6f} − {v1:.6f}) = {W:.2f} kJ.',
                        f'4) Calor (1ª Lei): Q = m·(h₂ − h₁) = {mass} × ({h2:.2f} − {h1:.2f}) = {Q:.2f} kJ.',
                        f'5) Entropia gerada (2ª Lei): Sger = m·(s₂ − s₁) − Q/T_viz(K) = {Sger:.4f} kJ/K.',
                    ],
                }
                return prompt, solution

            elif proc_type == 'vcte':
                T2_in = random.choice(cfg['t2_choices'])
                Tviz = random.choice(cfg['tviz_challenge'] if challenge else cfg['tviz_choices'])
                ctx, _, _ = compute_vcte_process_context(opt, (1, 0, P1, T1), 0, T2_in, Tviz, le, pg, mass=mass)
                P2 = float(ctx['pressao2'])
                Q = float(ctx['Calor'])
                Sger = float(ctx['Sger'])
                u1 = float(ctx['energia_interna'])
                u2 = float(ctx['energia_interna2'])
                s1 = float(ctx['entropia_especifica'])
                s2 = float(ctx['entropia_especifica2'])
                prompt = {
                    'substance': cfg['name'], 'process': 'vcte', 'mass': mass, 'unit_t': unit_t,
                    'formula_hint': 'Isocórico (v = cte): W = 0; Q = m·(u₂ − u₁); Sger = m·(s₂ − s₁) − Q/T_viz(K).',
                    'given': [
                        f'Substância: {cfg["name"]}', f'm = {mass} kg',
                        f'P₁ = {P1} kPa', f'T₁ = {T1} {unit_t}',
                        f'T₂ = {T2_in} {unit_t} (v = constante)',
                        f'T_viz = {Tviz} {unit_t}',
                    ],
                    'ask_fields': ['P2', 'W', 'Q', 'Sger'],
                    'is_state': False,
                }
                solution = {
                    'P2': round(P2, 2), 'W': 0.0, 'Q': round(Q, 2), 'Sger': round(Sger, 4),
                    'expected_vol': 'const',
                    'expected_heat': 'in' if Q > 0 else 'out',
                    'expected_law2': 'possible' if Sger >= -1e-6 else 'impossible',
                    'steps': [
                        f'1) Estado 1: u₁ = {u1:.2f} kJ/kg, s₁ = {s1:.4f} kJ/kg·K.',
                        f'2) Estado 2 (v₂ = v₁, T₂ = {T2_in} {unit_t}): P₂ = {P2:.2f} kPa, u₂ = {u2:.2f} kJ/kg, s₂ = {s2:.4f} kJ/kg·K.',
                        '3) Trabalho isocórico: volume constante ⇒ W = 0,00 kJ.',
                        f'4) Calor (1ª Lei): Q = m·(u₂ − u₁) = {mass} × ({u2:.2f} − {u1:.2f}) = {Q:.2f} kJ.',
                        f'5) Entropia gerada (2ª Lei): Sger = m·(s₂ − s₁) − Q/T_viz(K) = {Sger:.4f} kJ/K.',
                    ],
                }
                return prompt, solution

            else:  # scte
                T1_s = random.choice(cfg['t2_choices'])
                P2_in = random.choice([p for p in cfg['p2_scte'] if p != P1] or cfg['p2_scte'])
                ctx, _, _ = compute_scte_process_context(opt, (1, 0, P1, T1_s), 1, P2_in, le, pg, mass=mass)
                T2 = float(ctx['temperatura2'])
                W = float(ctx['Trabalho'])
                v1 = float(ctx['volume_especifico'])
                v2 = float(ctx['volume_especifico2'])
                u1 = float(ctx['energia_interna'])
                u2 = float(ctx['energia_interna2'])
                s1 = float(ctx['entropia_especifica'])
                prompt = {
                    'substance': cfg['name'], 'process': 'scte', 'mass': mass, 'unit_t': unit_t,
                    'formula_hint': 'Isentrópico (adiabático e reversível): s₂ = s₁; Q = 0; Sger = 0; W = −m·(u₂ − u₁).',
                    'given': [
                        f'Substância: {cfg["name"]}', f'm = {mass} kg',
                        f'P₁ = {P1} kPa', f'T₁ = {T1_s} {unit_t}',
                        f'P₂ = {P2_in} kPa (adiabático e reversível)',
                    ],
                    'ask_fields': ['T2', 'W', 'Q'],
                    'is_state': False,
                }
                solution = {
                    'T2': round(T2, 2), 'W': round(W, 2), 'Q': 0.0,
                    'expected_vol': 'expand' if v2 > v1 else 'compress',
                    'expected_heat': 'zero',
                    'expected_law2': 'possible',
                    'steps': [
                        f'1) Estado 1: u₁ = {u1:.2f} kJ/kg, s₁ = {s1:.4f} kJ/kg·K.',
                        f'2) Condição isentrópica (s₂ = s₁ = {s1:.4f} kJ/kg·K, P₂ = {P2_in} kPa): T₂ = {T2:.2f} {unit_t}, u₂ = {u2:.2f} kJ/kg.',
                        '3) Processo adiabático e reversível: Q = 0,00 kJ e Sger = 0,0000 kJ/K.',
                        f'4) Trabalho (1ª Lei com Q = 0): W = −m·(u₂ − u₁) = −{mass} × ({u2:.2f} − {u1:.2f}) = {W:.2f} kJ.',
                    ],
                }
                return prompt, solution
        except Exception:
            continue
    return _generate_ideal_gas_problem(proc_type, mass, challenge=challenge)


@require_GET
def exercicios_poe_view(request):
    """Renderiza a página do Modo Exercício / Autoavaliação (POE)."""
    return render(request, 'exercicios.html', {
        'min_solve_seconds': MIN_SOLVE_SECONDS,
    })


@csrf_exempt
@require_POST
def api_exercicio_gerar_view(request):
    """Gera um exercício POE aleatório e guarda o gabarito APENAS na sessão do servidor."""
    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, UnicodeDecodeError):
        body = {}

    sub_key = str(body.get('substance', '1'))
    proc_type = str(body.get('process', 'pcte'))
    if proc_type not in ('estado', 'pcte', 'vcte', 'scte', 'tcte', 'poli'):
        proc_type = 'pcte'
    difficulty = str(body.get('difficulty', 'basic'))
    challenge = (difficulty == 'challenge')
    mass = 1.0 if difficulty == 'basic' else random.choice([1.5, 2.0, 2.5, 3.0])

    if sub_key == 'gas' or proc_type in ('tcte', 'poli'):
        prompt, solution = _generate_ideal_gas_problem(proc_type, mass, challenge=challenge)
    else:
        try:
            opt = int(sub_key)
            if opt not in _PURE_PRESETS:
                opt = 1
        except ValueError:
            opt = 1
        prompt, solution = _generate_pure_problem(opt, proc_type, mass, challenge=challenge)

    request.session['poe_exercise'] = {
        'prompt': prompt,
        'solution': solution,
        'created_at': time.time(),
        'attempts': 0,
        'last_answers': None,
        'unlocked': False,
    }
    request.session.modified = True

    return JsonResponse({
        'ok': True,
        'prompt': prompt,
        'min_seconds': MIN_SOLVE_SECONDS,
    })


def _is_close(user_val, truth_val):
    if abs(truth_val) < 1e-6:
        return abs(user_val) <= 0.5
    rel_err = abs(user_val - truth_val) / max(abs(truth_val), 1e-9)
    abs_err = abs(user_val - truth_val)
    return rel_err <= 0.03 or abs_err <= 0.5


def _hint_for(field, user_val, truth_val):
    if abs(truth_val) < 1e-6:
        return 'Revise as hipóteses do processo (esta grandeza é nula).'
    if (user_val > 0 > truth_val) or (user_val < 0 < truth_val):
        return 'Sinal invertido! Revise a convenção de sinais (Q > 0 entra, W > 0 realizado).'
    ratio = abs(user_val / truth_val) if abs(truth_val) > 1e-6 else 0
    if 0.85 <= ratio <= 1.15:
        return 'Valor próximo! Confira a interpolação nas tabelas ou a conversão para Kelvin.'
    return 'Valor distante do esperado — confira a fórmula aplicada e se multiplicou pela massa m.'


@csrf_exempt
@require_POST
def api_exercicio_corrigir_view(request):
    """Corrige as respostas do aluno com Trava Anti-Burla e só libera o Memorial após esforço genuíno."""
    ex = request.session.get('poe_exercise')
    if not ex:
        return JsonResponse({'ok': False, 'error': 'Gere um exercício antes de corrigir.'}, status=400)

    try:
        body = json.loads(request.body.decode('utf-8') or '{}')
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'error': 'JSON inválido.'}, status=400)

    # 1. Trava de tempo mínimo (evita cliques automáticos / spam para ver gabarito)
    elapsed = time.time() - float(ex.get('created_at', 0))
    if elapsed < MIN_SOLVE_SECONDS and not ex.get('unlocked'):
        remaining = int(math.ceil(MIN_SOLVE_SECONDS - elapsed))
        return JsonResponse({
            'ok': False,
            'blocked': True,
            'reason': 'min_time',
            'remaining_seconds': remaining,
            'message': f'Trava didática ativa: dedique pelo menos {MIN_SOLVE_SECONDS}s para calcular no caderno antes de enviar (faltam {remaining}s).',
        }, status=400)

    is_state = bool(ex['prompt'].get('is_state'))
    pred_vol = str(body.get('pred_vol', '')).strip()
    pred_heat = str(body.get('pred_heat', '')).strip()
    pred_law2 = str(body.get('pred_law2', '')).strip()
    justification = str(body.get('justification', '')).strip()

    if not is_state and (not pred_vol or not pred_heat or not pred_law2):
        return JsonResponse({
            'ok': False,
            'blocked': True,
            'reason': 'missing_poe',
            'message': 'Complete primeiro todas as previsões qualitativas (Etapa Prever - POE).',
        }, status=400)

    if len(justification) < 15 or len(set(justification.lower().replace(' ', ''))) < 5:
        return JsonResponse({
            'ok': False,
            'blocked': True,
            'reason': 'weak_justification',
            'message': 'Escreva uma justificativa física/equação válida (mínimo de 15 caracteres reais) explicando como chegou aos valores.',
        }, status=400)

    ask_fields = ex['prompt']['ask_fields']
    raw_answers = body.get('answers') or {}
    parsed = {}
    for f in ask_fields:
        val_raw = str(raw_answers.get(f, '')).replace(',', '.').strip()
        try:
            parsed[f] = float(val_raw)
        except ValueError:
            return JsonResponse({
                'ok': False,
                'blocked': True,
                'reason': 'invalid_number',
                'message': f'Preencha um valor numérico válido para {f}.',
            }, status=400)

    vals = list(parsed.values())
    if len(vals) >= 3 and len(set(vals)) == 1 and vals[0] != 0.0:
        return JsonResponse({
            'ok': False,
            'blocked': True,
            'reason': 'dummy_values',
            'message': 'Respostas idênticas detectadas em todos os campos. Realize os cálculos reais para desbloquear a correção.',
        }, status=400)

    if ex.get('last_answers') == parsed and not ex.get('unlocked'):
        return JsonResponse({
            'ok': False,
            'blocked': True,
            'reason': 'repeated_attempt',
            'message': 'Você enviou exatamente os mesmos números da tentativa anterior. Revise os cálculos com base nas dicas antes de tentar novamente.',
        }, status=400)

    sol = ex['solution']
    field_feedback = {}
    correct_count = 0
    for f in ask_fields:
        ok_f = _is_close(parsed[f], sol[f])
        if ok_f:
            correct_count += 1
        rel_err = None
        if abs(sol[f]) > 1e-6:
            rel_err = round(abs(parsed[f] - sol[f]) / abs(sol[f]) * 100.0, 2)
        else:
            rel_err = 0.0 if ok_f else round(abs(parsed[f]), 2)
        field_feedback[f] = {
            'correct': ok_f,
            'user_val': parsed[f],
            'rel_err': rel_err,
            'hint': 'Correto!' if ok_f else _hint_for(f, parsed[f], sol[f]),
        }

    poe_feedback = None if is_state else {
        'vol': pred_vol == sol['expected_vol'],
        'heat': pred_heat == sol['expected_heat'],
        'law2': pred_law2 == sol['expected_law2'],
    }

    score_pct = round((correct_count / max(len(ask_fields), 1)) * 100.0, 1)
    ex['attempts'] = int(ex.get('attempts', 0)) + 1
    ex['last_answers'] = parsed

    unlocked = (score_pct >= 75.0) or (ex['attempts'] >= 2)
    ex['unlocked'] = unlocked
    request.session['poe_exercise'] = ex
    request.session.modified = True

    if unlocked:
        idioma = str(body.get('idioma', 'pt-br')).strip()[:10] or 'pt-br'
        UsoSimulacao.objects.create(
            substancia=ex['prompt']['substance'][:50],
            tipo='Exercício POE',
            idioma=idioma,
        )

    resp = {
        'ok': True,
        'score_pct': score_pct,
        'attempts': ex['attempts'],
        'field_feedback': field_feedback,
        'poe_feedback': poe_feedback,
        'unlocked': unlocked,
    }
    if unlocked:
        resp['solution'] = {
            'values': {f: sol[f] for f in ask_fields},
            'steps': sol['steps'],
        }
    return JsonResponse(resp)

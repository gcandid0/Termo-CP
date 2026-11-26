# -*- coding: utf-8 -*-
"""
Suíte de Testes Automatizados do TERMO-CP (Item 4 - Confiabilidade Científica).
Cobre:
  1. Precisão científica do motor termodinâmico (7 substâncias puras + gás ideal)
  2. Processos termodinâmicos (Isobárico, Isentrópico, Isocórico) e busca binária no domo
  3. Imutabilidade e performance do cache singleton de tabelas (tabelas_termoprop)
  4. Isolamento de sessão entre múltiplas abas/fluxos concorrentes (request.session)
  5. Rotas legadas, rotas parametrizadas (/calc/...) e API JSON (/api/v1/estado/)
  6. Integridade de codificação UTF-8 (prevenção de Mojibake)
"""

import copy
import json
import pathlib
import re
from django.test import Client, TestCase
from django.urls import reverse

from . import tabelas_termoprop as tbs
from .thermo_engine import (
    BoundariesException,
    compute_ideal_gas_single_state,
    compute_pcte_process_context,
    compute_scte_process_context,
    compute_single_state_context,
    compute_vcte_process_context,
    resolve_ideal_gas_constants,
    subs_cls,
)


class ThermodynamicEngineTests(TestCase):
    """Valida a precisão numérica das interpolações nas Tabelas B.1 a B.7."""

    def test_water_saturated_mixture_by_temperature(self):
        # Água a T = 100 °C e título x = 50% (Tabela B.1.1: hl=419.02, hv=2676.05 -> h=1547.535)
        res = subs_cls(1, 0, 6, 100.0, 50.0).results
        self.assertEqual(res[0], 3)  # Fase 3: mistura saturada
        props = {p[1]: p[3] for p in res[2]}
        self.assertAlmostEqual(props['T'], 100.0, places=2)
        self.assertAlmostEqual(props['p'], 101.3, places=1)
        self.assertAlmostEqual(props['h'], 1547.535, places=2)
        self.assertAlmostEqual(props['s'], 4.3308, places=4)
        self.assertAlmostEqual(props['x'], 50.0, places=2)

    def test_water_saturated_mixture_by_pressure(self):
        # Água a p = 100 kPa e título x = 50% (Tabela B.1.2)
        res = subs_cls(1, 1, 6, 100.0, 50.0).results
        self.assertEqual(res[0], 3)
        props = {p[1]: p[3] for p in res[2]}
        self.assertAlmostEqual(props['T'], 99.62, places=2)
        self.assertAlmostEqual(props['p'], 100.0, places=2)

    def test_water_superheated_vapor_double_interpolation_symmetry(self):
        # Água superaquecida a T = 200 °C e p = 150 kPa (interpolação entre 100 e 200 kPa)
        r_tp = subs_cls(1, 0, 1, 200.0, 150.0).results
        r_pt = subs_cls(1, 1, 0, 150.0, 200.0).results
        self.assertEqual(r_tp[0], 2)  # Fase 2: vapor superaquecido
        self.assertEqual(r_pt[0], 2)
        for p1, p2 in zip(r_tp[2], r_pt[2]):
            self.assertAlmostEqual(p1[3], p2[3], places=6)

    def test_water_compressed_liquid(self):
        # Água líquido comprimido a p = 10000 kPa e T = 40 °C (Tabela B.1.4)
        res = subs_cls(1, 1, 0, 10000.0, 40.0).results
        self.assertEqual(res[0], 1)  # Fase 1: líquido comprimido
        props = {p[1]: p[3] for p in res[2]}
        self.assertAlmostEqual(props['v'], 0.001003, places=6)
        self.assertAlmostEqual(props['h'], 176.36, places=2)

    def test_all_seven_substances_saturation_states(self):
        # Testa cálculo de estado saturado nas 7 substâncias (Água, Amônia, CO2, R-410a, R-134a, N2, CH4)
        test_cases = [
            (1, 100.0, 50.0, 101.3),    # Água (100 °C)
            (2, 10.0, 60.0, 615.2),     # Amônia (10 °C)
            (3, 0.0, 40.0, 3485.1),     # CO2 (0 °C)
            (4, 10.0, 50.0, 1085.7),    # R-410a (10 °C)
            (5, 20.0, 75.0, 572.8),     # R-134a (20 °C)
            (6, 100.0, 50.0, 779.2),    # Nitrogênio (100 K)
            (7, 120.0, 50.0, 191.6),    # Metano (120 K)
        ]
        for opt, temp, qual, expected_p in test_cases:
            with self.subTest(opt=opt):
                ctx = compute_single_state_context(opt, 0, 6, temp, qual)
                self.assertEqual(ctx['fase'], 3)
                self.assertAlmostEqual(ctx['pressao'], expected_p, places=1)
                self.assertAlmostEqual(ctx['titulo'], qual, places=2)

    def test_out_of_bounds_raises_boundaries_exception(self):
        with self.assertRaises(BoundariesException):
            subs_cls(1, 0, 1, 5000.0, 100.0)  # T = 5000 °C fora da tabela
        with self.assertRaises(BoundariesException):
            subs_cls(2, 0, 6, 10.0, 150.0)    # Título x = 150% inválido


class ThermodynamicProcessesTests(TestCase):
    """Valida os cálculos de processos (Isobárico, Isentrópico, Isocórico e Gás Ideal)."""

    def test_isobaric_process_water(self):
        # Processo isobárico da água: Estado 1 (p=200 kPa, x=50%) -> Estado 2 (T=200 °C), Tviz=25 °C
        ctx, estados, grafico = compute_pcte_process_context(
            opt=1,
            state1_inputs=(1, 6, 200.0, 50.0),
            third_prop=0,
            third_val=200.0,
            temp_viz=25.0,
            lista_estados=[],
            pontos_grafico=[],
        )
        self.assertEqual(ctx['fase'], 3)
        self.assertEqual(ctx['fase2'], 2)
        self.assertEqual(ctx['pressao'], 200.0)
        self.assertEqual(ctx['pressao2'], 200.0)
        self.assertGreater(ctx['Calor'], 0)
        self.assertGreater(ctx['Trabalho'], 0)
        self.assertEqual(len(estados), 2)
        self.assertEqual(len(grafico), 1)
        self.assertGreater(len(grafico[0]), 50)

    def test_isentropic_process_dome_crossing(self):
        # Processo isentrópico da amônia cruzando o domo: Estado 1 (T=0 °C, x=95%) -> Estado 2 (p=1200 kPa)
        ctx, estados, grafico = compute_scte_process_context(
            opt=2,
            state1_inputs=(0, 6, 0.0, 95.0),
            third_prop=1,
            third_val=1200.0,
            lista_estados=[],
            pontos_grafico=[],
        )
        self.assertEqual(ctx['fase'], 3)
        self.assertEqual(ctx['fase2'], 2)
        self.assertAlmostEqual(ctx['entropia_especifica'], ctx['entropia_especifica2'], places=3)
        self.assertEqual(len(grafico[0]), 301)

    def test_isochoric_process_ammonia(self):
        # Processo isocórico da amônia: Estado 1 (T=0 °C, x=50%) -> Estado 2 (T=20 °C), Tviz=30 °C
        ctx, estados, grafico = compute_vcte_process_context(
            opt=2,
            state1_inputs=(0, 6, 0.0, 50.0),
            third_prop=0,
            third_val=20.0,
            temp_viz=30.0,
            lista_estados=[],
            pontos_grafico=[],
        )
        self.assertAlmostEqual(ctx['volume_especifico'], ctx['volume_especifico2'], places=5)
        self.assertGreater(ctx['Calor'], 0)

    def test_ideal_gas_constants_and_state_resolution(self):
        # Ar: Cp0 = 1.004, Cv0 = 0.717 -> R = 0.287, K = 1.4003
        Cv0, Cp0, R, K = resolve_ideal_gas_constants(11, 0.717, 12, 1.004)
        self.assertAlmostEqual(R, 0.287, places=4)
        self.assertAlmostEqual(K, 1.004 / 0.717, places=4)

        # Resolução a partir de R e K
        Cv2, Cp2, R2, K2 = resolve_ideal_gas_constants(13, 0.287, 14, 1.4)
        self.assertAlmostEqual(Cv2, 0.7175, places=4)
        self.assertAlmostEqual(Cp2, 1.0045, places=4)

        # Equação de estado p*v = R*T (T = 26.85 °C = 300 K, p = 100 kPa, R = 0.287 -> v = 0.861 m³/kg)
        T_c, p, v = compute_ideal_gas_single_state(0, 1, 26.85, 100.0, 0.287)
        self.assertAlmostEqual(v, 0.861, places=4)


class TablePerformanceAndImmutabilityTests(TestCase):
    """Garante que tabelas_cls é singleton e que interpolações não corrompem as tabelas em memória."""

    def test_tabelas_cls_is_singleton(self):
        t1 = tbs.tabelas_cls()
        t2 = tbs.tabelas_cls()
        self.assertIs(t1, t2)
        self.assertIs(t1, tbs.tabelas)

    def test_superheated_interpolation_does_not_mutate_tables(self):
        snapshot_b13 = copy.deepcopy(tbs.tabelas.B_1_3)
        snapshot_b22 = copy.deepcopy(tbs.tabelas.B_2_2)

        # Executa múltiplas interpolações com marcador == 1
        first_res = subs_cls(1, 0, 1, 200.0, 150.0).results
        for _ in range(10):
            again = subs_cls(1, 0, 1, 200.0, 150.0).results
            self.assertEqual(first_res[2], again[2])
            subs_cls(1, 0, 4, 250.0, 2950.0)
            subs_cls(2, 1, 0, 150.0, 50.0)

        self.assertEqual(tbs.tabelas.B_1_3, snapshot_b13)
        self.assertEqual(tbs.tabelas.B_2_2, snapshot_b22)


class SessionConcurrencyTests(TestCase):
    """Garante que múltiplas abas/fluxos na mesma sessão não sobrescrevam os dados uma da outra."""

    def setUp(self):
        self.client = Client()

    def test_concurrent_tabs_different_substances_do_not_collide(self):
        # Aba 1 inicia cálculo de Estado da Água (T = 100 °C)
        self.client.post(reverse('ask_known1'), {'property_choice': '0', 'value_input': '100'})

        # Aba 2 inicia cálculo de Estado da Amônia (p = 150 kPa) ANTES da Aba 1 terminar
        self.client.post(reverse('ask_known1_13'), {'property_choice': '1', 'value_input': '150'})

        # Aba 1 informa a 2ª propriedade da Água (x = 50%)
        self.client.post(reverse('ask_known2'), {'property_choice': '6', 'value_input': '50'})

        # Aba 2 informa a 2ª propriedade da Amônia (T = 50 °C)
        self.client.post(reverse('ask_known2_13'), {'property_choice': '0', 'value_input': '50'})

        # Aba 1 renderiza resultados da Água -> deve usar T=100 °C e x=50% (Pressão ~ 101.3 kPa)
        resp_agua = self.client.get(reverse('process_values'))
        self.assertEqual(resp_agua.status_code, 200)
        self.assertEqual(resp_agua.context['fase'], 3)
        self.assertAlmostEqual(resp_agua.context['temperatura'], 100.0, places=1)
        self.assertAlmostEqual(resp_agua.context['pressao'], 101.3, places=1)

        # Aba 2 renderiza resultados da Amônia -> deve usar p=150 kPa e T=50 °C (Fase 2: vapor superaquecido)
        resp_amonia = self.client.get(reverse('process_values_13'))
        self.assertEqual(resp_amonia.status_code, 200)
        self.assertEqual(resp_amonia.context['fase'], 2)
        self.assertAlmostEqual(resp_amonia.context['pressao'], 150.0, places=1)
        self.assertAlmostEqual(resp_amonia.context['temperatura'], 50.0, places=1)

    def test_concurrent_tabs_same_substance_with_calc_id(self):
        # Duas abas da MESMA substância identificadas por calc_id distintos
        self.client.post(reverse('ask_known1') + '?calc_id=tabA', {'property_choice': '0', 'value_input': '100'})
        self.client.post(reverse('ask_known1') + '?calc_id=tabB', {'property_choice': '0', 'value_input': '200'})

        self.client.post(reverse('ask_known2') + '?calc_id=tabA', {'property_choice': '6', 'value_input': '50'})
        self.client.post(reverse('ask_known2') + '?calc_id=tabB', {'property_choice': '1', 'value_input': '150'})

        resp_a = self.client.get(reverse('process_values') + '?calc_id=tabA')
        resp_b = self.client.get(reverse('process_values') + '?calc_id=tabB')

        self.assertAlmostEqual(resp_a.context['temperatura'], 100.0, places=1)
        self.assertAlmostEqual(resp_b.context['temperatura'], 200.0, places=1)

    def test_ideal_gas_multisession_stateless_isolation(self):
        from myapp.estados import get_gas_session
        client_a = Client()
        client_b = Client()

        # Usuário A inicia fluxo de Gás Ideal e salva um estado no seu contexto de sessão
        client_a.get(reverse('ask_known1_8'))
        session_a = client_a.session
        class MockReq: pass
        req_a = MockReq()
        req_a.session = session_a
        gas_a = get_gas_session(req_a)
        gas_a.salvar_estado(0.718, 1.005, 0.287, 1.4, 100.0, 20.0, 0.84)
        client_a.session.save()

        # Usuário B faz uma requisição concorrente limpando / iniciando seu próprio ciclo
        client_b.get(reverse('ask_known1_8'))
        session_b = client_b.session
        req_b = MockReq()
        req_b.session = session_b
        gas_b = get_gas_session(req_b)

        # Ciclo de B é limpo e isolado
        self.assertEqual(len(gas_b.lista_gas), 0)
        self.assertFalse(gas_b.tem_estado_valido())

        # Ciclo de A permanece íntegro e sem contaminação pelo usuário B
        self.assertEqual(len(gas_a.lista_gas), 1)
        self.assertTrue(gas_a.tem_estado_valido())
        self.assertEqual(gas_a.ultimo_estado()[4], 100.0)


class RoutingAndViewsIntegrationTests(TestCase):
    """Testa as rotas parametrizadas, rotas legadas e o endpoint da API JSON."""

    def setUp(self):
        self.client = Client()

    def test_parameterized_state_routes(self):
        r1 = self.client.get(reverse('param_state_step', kwargs={'substance': 'co2', 'mode': 'estado', 'step': 1}))
        self.assertEqual(r1.status_code, 200)

        self.client.post(
            reverse('param_state_step', kwargs={'substance': 'co2', 'mode': 'estado', 'step': 1}),
            {'property_choice': '0', 'value_input': '0'},
        )
        self.client.post(
            reverse('param_state_step', kwargs={'substance': 'co2', 'mode': 'estado', 'step': 2}),
            {'property_choice': '6', 'value_input': '50'},
        )
        res = self.client.get(reverse('param_state_results', kwargs={'substance': 'co2', 'mode': 'estado'}))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.context['fase'], 3)
        self.assertAlmostEqual(res.context['pressao'], 3485.1, places=1)

    def test_api_calculate_state_endpoint(self):
        resp = self.client.get(
            reverse('api_calculate_state'),
            {'substance': 'agua', 'prop1': 0, 'val1': 100, 'prop2': 6, 'val2': 50, 'mass': 2.5},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['substance'], 'agua')
        self.assertEqual(data['fase'], 3)
        self.assertAlmostEqual(data['massa'], 2.5, places=2)
        self.assertAlmostEqual(data['pressao'], 101.3, places=1)

    def test_header_and_help_modal_ui_enhancements(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Title must be pure text without logo
        self.assertIn('<h1>TERMO-CP</h1>', content)
        self.assertNotIn('Logo TERMO-CP', content)
        # Dark mode toggle button must NOT be present
        self.assertNotIn('id="theme-toggle-btn"', content)
        # Help button and modal must be present
        self.assertIn('id="page-help-btn"', content)
        self.assertIn('id="page-help-modal"', content)
        # Header nav has standard items only (no Ajuda tab in nav)
        nav_html = content.split('<nav>')[1].split('</nav>')[0]
        self.assertNotIn('/ajuda/', nav_html)

        # Test that Ajuda page loads cleanly
        resp_ajuda = self.client.get(reverse('ajuda'))
        self.assertEqual(resp_ajuda.status_code, 200)
        ajuda_content = resp_ajuda.content.decode('utf-8')
        self.assertNotIn('id="theme-toggle-btn"', ajuda_content)
        self.assertIn('Central de Ajuda', ajuda_content)


class MassScalingAndSpecificVolumeScaleTests(TestCase):
    """Valida a entrada de massa personalizada (m != 1 kg), escalonamento de grandezas extensivas e escala do cilindro."""

    def setUp(self):
        self.client = Client()

    def test_single_state_mass_scaling_and_specific_liquid_volume(self):
        ctx_1kg = compute_single_state_context(1, 0, 6, 100.0, 50.0, mass=1.0)
        ctx_25kg = compute_single_state_context(1, 0, 6, 100.0, 50.0, mass=2.5)

        # Propriedades intensivas e VolumeL_esp permanecem idênticas
        self.assertEqual(ctx_1kg['volume_especifico'], ctx_25kg['volume_especifico'])
        self.assertEqual(ctx_1kg['VolumeL_esp'], ctx_25kg['VolumeL_esp'])

        # Volumes extensivos de líquido e vapor escalam com a massa m = 2.5 kg
        self.assertAlmostEqual(ctx_25kg['VolumeL'], ctx_1kg['VolumeL'] * 2.5, places=6)
        self.assertAlmostEqual(ctx_25kg['VolumeV'], ctx_1kg['VolumeV'] * 2.5, places=6)
        self.assertEqual(ctx_25kg['massa'], 2.5)
        self.assertEqual(ctx_25kg['massa_float'], 2.5)

    def test_isobaric_isentropic_isochoric_processes_scale_with_mass(self):
        # 1. Isobárico (Água)
        c1_p, _, _ = compute_pcte_process_context(1, (1, 6, 200.0, 50.0), 0, 200.0, 25.0, [], [], mass=1.0)
        c25_p, _, _ = compute_pcte_process_context(1, (1, 6, 200.0, 50.0), 0, 200.0, 25.0, [], [], mass=2.5)
        self.assertAlmostEqual(c25_p['Calor'], round(c1_p['Calor'] * 2.5, 2), places=1)
        self.assertAlmostEqual(c25_p['Trabalho'], round(c1_p['Trabalho'] * 2.5, 2), places=1)
        self.assertAlmostEqual(c25_p['Sger'], round(c1_p['Sger'] * 2.5, 5), places=3)

        # 2. Isentrópico (Amônia)
        c1_s, _, _ = compute_scte_process_context(2, (0, 6, 0.0, 95.0), 1, 1200.0, [], [], mass=1.0)
        c25_s, _, _ = compute_scte_process_context(2, (0, 6, 0.0, 95.0), 1, 1200.0, [], [], mass=3.0)
        self.assertAlmostEqual(c25_s['Trabalho'], round(c1_s['Trabalho'] * 3.0, 2), places=1)

        # 3. Isocórico (Amônia)
        c1_v, _, _ = compute_vcte_process_context(2, (0, 6, 0.0, 50.0), 0, 20.0, 30.0, [], [], mass=1.0)
        c25_v, _, _ = compute_vcte_process_context(2, (0, 6, 0.0, 50.0), 0, 20.0, 30.0, [], [], mass=2.0)
        self.assertAlmostEqual(c25_v['Calor'], round(c1_v['Calor'] * 2.0, 2), places=1)
        self.assertAlmostEqual(c25_v['Sger'], round(c1_v['Sger'] * 2.0, 5), places=3)

    def test_end_to_end_form_submission_with_custom_mass_renders_specific_volume_scale(self):
        # 1º Formulário: Página separada de Massa (/massa/agua_estado/) -> redireciona para ask_known1
        mass_url = reverse('ask_mass', kwargs={'flow_key': 'agua_estado'})
        r_mass_get = self.client.get(mass_url)
        self.assertEqual(r_mass_get.status_code, 200)
        self.assertIn('Massa do sistema', r_mass_get.content.decode('utf-8'))

        r0 = self.client.post(mass_url, {'mass_input': '2.5'})
        self.assertEqual(r0.status_code, 302)
        self.assertEqual(r0.url, reverse('ask_known1'))

        # 2º Formulário: 1ª propriedade (T = 100 °C) -> redireciona para ask_known2
        r1 = self.client.post(
            reverse('ask_known1'),
            {'property_choice': '0', 'value_input': '100'},
        )
        self.assertEqual(r1.status_code, 302)
        self.assertEqual(r1.url, reverse('ask_known2'))

        # 3º Formulário: 2ª propriedade (x = 50%) -> redireciona para process_values
        r2 = self.client.post(
            reverse('ask_known2'),
            {'property_choice': '6', 'value_input': '50'},
        )
        self.assertEqual(r2.status_code, 302)
        self.assertEqual(r2.url, reverse('process_values'))

        resp = self.client.get(reverse('process_values'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['massa'], 2.5)
        self.assertEqual(resp.context['massa_float'], 2.5)
        html = resp.content.decode('utf-8')
        self.assertIn('2,5 kg', html)
        self.assertIn('Volume esp. [m³/kg]', html)

    def test_process_flow_has_mass_first_and_ambient_temperature_last(self):
        # 1º Formulário: Massa (m = 2.0 kg)
        r0 = self.client.post(reverse('ask_mass', kwargs={'flow_key': 'agua_pcte'}), {'mass_input': '2.0'})
        self.assertEqual(r0.url, reverse('ask_known1_3'))

        # 2º Formulário: 1ª prop Estado 1 (p = 200 kPa)
        r1 = self.client.post(reverse('ask_known1_3'), {'property_choice': '1', 'value_input': '200'})
        self.assertEqual(r1.url, reverse('ask_known2_3'))

        # 3º Formulário: 2ª prop Estado 1 (x = 50%)
        r2 = self.client.post(reverse('ask_known2_3'), {'property_choice': '6', 'value_input': '50'})
        self.assertEqual(r2.url, reverse('ask_known3_3'))

        # 4º Formulário: Propriedade no estado final (T2 = 200 °C)
        r3_get = self.client.get(reverse('ask_known3_3'))
        self.assertIn('propriedade no estado final', r3_get.content.decode('utf-8').lower())
        r3 = self.client.post(reverse('ask_known3_3'), {'property_choice': '0', 'value_input': '200'})
        self.assertEqual(r3.url, reverse('ask_known4_3'))

        # 5º Formulário (ÚLTIMO): Temperatura da vizinhança (Tviz = 25 °C)
        r4_get = self.client.get(reverse('ask_known4_3'))
        self.assertIn('Temperatura da vizinhança', r4_get.content.decode('utf-8'))
        r4 = self.client.post(reverse('ask_known4_3'), {'property_choice': '7', 'value_input': '25'})
        self.assertEqual(r4.url, reverse('process_values_3'))

        resp = self.client.get(reverse('process_values_3'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['massa'], 2.0)
        self.assertEqual(resp.context['TempViz'], 25.0)

    def test_ideal_gas_cylinder_state_renders_without_template_errors(self):
        self.client.post(reverse('ask_mass', kwargs={'flow_key': 'gas_cilindro'}), {'mass_input': '1.5'})
        self.client.post(reverse('ask_known3_7'), {'property_choice': '7', 'R_value_input': '0.287'})
        self.client.post(reverse('ask_known1_7'), {'property_choice': '0', 'value_input': '10'})
        self.client.post(reverse('ask_known2_7'), {'property_choice': '1', 'value_input': '100'})
        resp = self.client.get(reverse('process_values_7'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['massa'], 1.5)
        self.assertIn('1,5 kg', resp.content.decode('utf-8'))


class EncodingIntegrityTests(TestCase):
    """Garante que todos os arquivos do projeto estão em UTF-8 limpo (sem BOM e sem Mojibake)."""

    def test_all_source_and_template_files_are_valid_utf8_without_mojibake(self):
        root = pathlib.Path(__file__).resolve().parent.parent
        mojibake_re = re.compile(r'\xc3[\xa1\xa3\xa2\xaa\xa9\xb3\xb5\xba\xa7\x80-\xbf]|\ufffd|[\u0100-\u024f]')

        for p in list((root / 'myapp').rglob('*')) + list((root / 'termocp').rglob('*')):
            if not p.is_file() or p.suffix not in ('.py', '.html', '.css', '.js'):
                continue
            with self.subTest(file=str(p.relative_to(root))):
                raw = p.read_bytes()
                self.assertFalse(raw.startswith(b'\xef\xbb\xbf'), f'UTF-8 BOM encontrado em {p}')
                text = raw.decode('utf-8')
                matches = mojibake_re.findall(text)
                self.assertEqual(matches, [], f'Sequência Mojibake encontrada em {p}: {matches}')



class ReliabilityAndThermoFeaturesTests(TestCase):
    """Testa correções de erro genérico, persistência de contato, título (x) em fração e balanço de ciclos."""

    def setUp(self):
        self.client = Client()

    def test_erro_generico_displays_message_context(self):
        # Força um erro de limite de tabela termodinâmica para garantir que a mensagem real é exibida
        self.client.post(
            reverse('param_state_step', kwargs={'substance': 'agua', 'mode': 'estado', 'step': 1}),
            {'property_choice': '0', 'value_input': '99999'},
        )
        self.client.post(
            reverse('param_state_step', kwargs={'substance': 'agua', 'mode': 'estado', 'step': 2}),
            {'property_choice': '1', 'value_input': '100'},
        )
        resp = self.client.get(reverse('param_state_results', kwargs={'substance': 'agua', 'mode': 'estado'}))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('limites das tabelas termodinâmicas', resp.content.decode('utf-8'))

    def test_contato_persists_message_to_database(self):
        from .models import MensagemContato

        resp = self.client.post(
            reverse('contato'),
            {'nome': 'Aluno Teste', 'email': 'aluno@ufr.edu.br', 'mensagem': 'Excelente simulador!'},
        )
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(MensagemContato.objects.count(), 1)
        msg = MensagemContato.objects.first()
        self.assertEqual(msg.nome, 'Aluno Teste')
        self.assertEqual(msg.email, 'aluno@ufr.edu.br')
        self.assertEqual(msg.mensagem, 'Excelente simulador!')

    def test_quality_fraction_formatting_and_api(self):
        from .thermo_engine import format_quality_fraction

        self.assertEqual(format_quality_fraction(50.0), '0.5000')
        self.assertEqual(format_quality_fraction('45,25'), '0.4525')
        self.assertIsNone(format_quality_fraction(None))

        resp = self.client.get(
            reverse('api_calculate_state'),
            {'substance': 'agua', 'prop1': 0, 'val1': 100, 'prop2': 6, 'val2': 50},
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['titulo_fracao'], '0.5000')

        # Verifica exibição em % e fração no HTML renderizado
        self.client.post(
            reverse('param_state_step', kwargs={'substance': 'agua', 'mode': 'estado', 'step': 1}),
            {'property_choice': '0', 'value_input': '100'},
        )
        self.client.post(
            reverse('param_state_step', kwargs={'substance': 'agua', 'mode': 'estado', 'step': 2}),
            {'property_choice': '6', 'value_input': '50'},
        )
        res = self.client.get(reverse('param_state_results', kwargs={'substance': 'agua', 'mode': 'estado'}))
        self.assertEqual(res.status_code, 200)
        self.assertIn('(x = 0.5000)', res.content.decode('utf-8'))

    def test_cycle_balance_power_and_refrigeration(self):
        from .thermo_engine import compute_cycle_balance

        # Ciclo de potência: Q_H = 1000 kJ, Q_L = 600 kJ, W_liq = 400 kJ -> η = 40.0%
        power = compute_cycle_balance([
            {'Q': 1000.0, 'W': 0.0, 'Sger': 0.05},
            {'Q': 0.0, 'W': 500.0, 'Sger': 0.02},
            {'Q': -600.0, 'W': 0.0, 'Sger': 0.03},
            {'Q': 0.0, 'W': -100.0, 'Sger': 0.01},
        ])
        self.assertAlmostEqual(power['W_liq'], 400.0, places=3)
        self.assertAlmostEqual(power['Q_H'], 1000.0, places=3)
        self.assertAlmostEqual(power['Q_L'], 600.0, places=3)
        self.assertAlmostEqual(power['eficiencia_termica'], 40.0, places=2)
        self.assertIsNone(power['cop_refrigeracao'])

        # Ciclo de refrigeração: Q_H (evaporador) = 300 kJ, W_liq = -100 kJ -> COP_R = 3.0
        refrig = compute_cycle_balance([
            {'Q': 300.0, 'W': 0.0, 'Sger': 0.01},
            {'Q': -400.0, 'W': -100.0, 'Sger': 0.02},
        ])
        self.assertAlmostEqual(refrig['W_liq'], -100.0, places=3)
        self.assertAlmostEqual(refrig['cop_refrigeracao'], 3.0, places=3)
        self.assertAlmostEqual(refrig['cop_bomba_calor'], 4.0, places=3)
        self.assertIsNone(refrig['eficiencia_termica'])


class ExtrasFeaturesTests(TestCase):
    """Testes para Favicon (0 404s), Estatísticas Anônimas, Link Compartilhável e Exercício POE."""

    def test_favicon_root_and_subpaths_redirect_without_404(self):
        for url in ('/favicon.ico', '/favicon.png', '/agua/agua-estado-1/favicon.png', '/processos/favicon.png'):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, f'Expected 302 for {url}')
            self.assertIn('/static/myapp/img/favicon.png', resp['Location'])

    def test_anonymous_usage_logging(self):
        from myapp.models import UsoSimulacao
        resp = self.client.post(
            '/api/log-uso/',
            data=json.dumps({'substancia': 'Água', 'tipo': 'Isobárico', 'idioma': 'pt-br'}),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json()['ok'])
        self.assertEqual(UsoSimulacao.objects.filter(substancia='Água', tipo='Isobárico').count(), 1)

    def test_shareable_simulation_link(self):
        resp = self.client.post(
            '/api/compartilhar/',
            data=json.dumps({
                'titulo': 'Água — Isobárico',
                'substancia': 'Água',
                'tipo': 'Isobárico',
                'source_path': '/agua/agua-estado-resultados/',
                'payload': {
                    'states': [{'title': 'Estado 1', 'rows': [{'label': 'P:', 'value': '100 kPa'}]}],
                    'process': [{'label': 'W', 'value': '96,86 kJ'}],
                },
            }),
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data['ok'])
        page = self.client.get(f"/s/{data['codigo']}/")
        self.assertEqual(page.status_code, 200)
        self.assertContains(page, '100 kPa')
        self.assertContains(page, '96,86 kJ')
        opened = self.client.get(f"/s/{data['codigo']}/abrir/")
        self.assertEqual(opened.status_code, 302)
        self.assertEqual(opened['Location'], '/agua/agua-estado-resultados/')

    def test_poe_exercise_anti_cheating_and_unlock(self):
        # 1. Página carrega
        self.assertEqual(self.client.get('/exercicios/').status_code, 200)

        # 2. Gera exercício sem vazar gabarito na resposta
        gen = self.client.post(
            '/api/exercicios/gerar/',
            data=json.dumps({'substance': 'gas', 'process': 'pcte', 'difficulty': 'basic'}),
            content_type='application/json',
        )
        self.assertEqual(gen.status_code, 200)
        gdata = gen.json()
        self.assertTrue(gdata['ok'])
        self.assertNotIn('solution', gdata)

        # 3. Envio imediato (< 25s) é bloqueado pela trava anti-burla
        fast = self.client.post(
            '/api/exercicios/corrigir/',
            data=json.dumps({
                'pred_vol': 'expand', 'pred_heat': 'in', 'pred_law2': 'possible',
                'justification': 'Apliquei W = m*P*(v2 - v1) e Q = m*Cp0*(T2 - T1).',
                'answers': {'W': 10, 'Q': 20, 'Sger': 0.1},
            }),
            content_type='application/json',
        )
        self.assertEqual(fast.status_code, 400)
        self.assertEqual(fast.json()['reason'], 'min_time')

        # 4. Simula passagem de 30s e envia respostas corretas do gabarito de sessão -> desbloqueia Memorial
        session = self.client.session
        ex = session['poe_exercise']
        ex['created_at'] -= 30
        sol = ex['solution']
        session['poe_exercise'] = ex
        session.save()

        ok_resp = self.client.post(
            '/api/exercicios/corrigir/',
            data=json.dumps({
                'pred_vol': sol['expected_vol'],
                'pred_heat': sol['expected_heat'],
                'pred_law2': sol['expected_law2'],
                'justification': 'Utilizei a 1a e 2a Leis para gas ideal com massa constante.',
                'answers': {f: sol[f] for f in ex['prompt']['ask_fields']},
            }),
            content_type='application/json',
        )
        self.assertEqual(ok_resp.status_code, 200)
        odata = ok_resp.json()
        self.assertTrue(odata['unlocked'])
        self.assertEqual(odata['score_pct'], 100.0)
        self.assertIn('steps', odata['solution'])
        self.assertTrue(str(odata.get('receipt_code', '')).startswith('POE-'))
        from myapp.models import TentativaExercicio
        self.assertEqual(TentativaExercicio.objects.filter(codigo=odata['receipt_code']).count(), 1)

    def test_share_process_reopens_exact_process_not_zeroed(self):
        # Executa processo isobárico da Água (p=200 kPa, x=50% -> T2=200 °C, Tviz=25 °C)
        self.client.post(reverse('ask_mass', kwargs={'flow_key': 'agua_pcte'}), {'mass_input': '1.0'})
        self.client.post(reverse('ask_known1_3'), {'property_choice': '1', 'value_input': '200'})
        self.client.post(reverse('ask_known2_3'), {'property_choice': '6', 'value_input': '50'})
        self.client.post(reverse('ask_known3_3'), {'property_choice': '0', 'value_input': '200'})
        self.client.post(reverse('ask_known4_3'), {'property_choice': '7', 'value_input': '25'})

        res_url = reverse('process_values_3')
        orig = self.client.get(res_url)
        self.assertEqual(orig.status_code, 200)
        orig_work = orig.context['Trabalho']
        orig_heat = orig.context['Calor']
        self.assertNotEqual(orig_work, 0.0)
        self.assertNotEqual(orig_heat, 0.0)

        # Compartilha o processo
        share_resp = self.client.post(
            '/api/compartilhar/',
            data=json.dumps({
                'substancia': 'Água',
                'tipo': 'Isobárico',
                'titulo': 'Água — Isobárico',
                'payload': {
                    'source_path': res_url,
                    'cards': [],
                    'summary': [],
                },
            }),
            content_type='application/json',
        )
        self.assertEqual(share_resp.status_code, 200)
        codigo = share_resp.json()['codigo']

        # Um aluno (sessão limpa) clica em "Simular no TERMO-CP" (/s/<codigo>/abrir/)
        visitor = Client()
        open_resp = visitor.get(f'/s/{codigo}/abrir/', follow=True)
        self.assertEqual(open_resp.status_code, 200)
        self.assertEqual(open_resp.context['Trabalho'], orig_work)
        self.assertEqual(open_resp.context['Calor'], orig_heat)

    def test_security_csrf_enforced_and_payload_sanitized(self):
        # 1. CSRF deve ser exigido em /api/compartilhar/
        csrf_client = Client(enforce_csrf_checks=True)
        r_no_csrf = csrf_client.post(
            '/api/compartilhar/',
            data=json.dumps({'titulo': 'X', 'substancia': 'Água', 'tipo': 'Estado', 'payload': {}}),
            content_type='application/json',
        )
        self.assertEqual(r_no_csrf.status_code, 403)

        # 2. Payload acima de 600 KB é rejeitado (413)
        big = 'A' * (650 * 1024)
        r_big = self.client.post(
            '/api/compartilhar/',
            data=json.dumps({'titulo': 'Big', 'substancia': 'Água', 'tipo': 'Estado', 'payload': {'big': big}}),
            content_type='application/json',
        )
        self.assertEqual(r_big.status_code, 413)

        # 3. cylinder_img malicioso e source_path proibido (/admin/) são descartados na sanitização
        r_san = self.client.post(
            '/api/compartilhar/',
            data=json.dumps({
                'titulo': 'Teste San',
                'substancia': 'Água',
                'tipo': 'Estado',
                'source_path': '/admin/',
                'payload': {
                    'source_path': '//evil.example.com',
                    'cylinder_img': 'javascript:alert(1)',
                    'cards': [{'title': 'OK', 'rows': [{'label': 'T', 'value': '100'}]}],
                },
            }),
            content_type='application/json',
        )
        self.assertEqual(r_san.status_code, 200)
        from myapp.models import SimulacaoCompartilhada
        sim = SimulacaoCompartilhada.objects.get(codigo=r_san.json()['codigo'])
        saved = json.loads(sim.payload_json)
        self.assertNotIn('cylinder_img', saved)
        self.assertNotIn('source_path', saved)

        # 4. Honeypot em /contato/ bloqueia spam silenciosamente sem gravar no banco
        from myapp.models import MensagemContato
        before = MensagemContato.objects.count()
        r_bot = self.client.post('/contato/', {
            'nome': 'Bot', 'email': 'bot@spam.test', 'mensagem': 'spam', 'website': 'http://spam.test',
        })
        self.assertEqual(r_bot.status_code, 302)
        self.assertEqual(MensagemContato.objects.count(), before)

    def test_admin_scientific_dashboard_and_csv_export(self):
        from django.contrib.auth import get_user_model
        from myapp.models import UsoSimulacao
        UsoSimulacao.objects.create(substancia='Água', tipo='Isobárico', idioma='pt-br')
        UsoSimulacao.objects.create(substancia='Amônia', tipo='Isentrópico', idioma='en')

        # Anônimo não acessa exportação CSV do artigo
        anon = self.client.get('/admin/exportar-estatisticas-artigo/')
        self.assertEqual(anon.status_code, 302)

        User = get_user_model()
        su = User.objects.create_superuser('admin_test', 'admin@test.local', 'StrongPass123!')
        self.client.force_login(su)

        dash = self.client.get('/admin/?periodo=30')
        self.assertEqual(dash.status_code, 200)
        self.assertContains(dash, 'Painel de Métricas Científicas')
        self.assertContains(dash, 'chartBySub')

        csv_resp = self.client.get('/admin/exportar-estatisticas-artigo/?periodo=all')
        self.assertEqual(csv_resp.status_code, 200)
        self.assertIn('text/csv', csv_resp['Content-Type'])
        self.assertIn('SIMULAÇÕES POR SUBSTÂNCIA', csv_resp.content.decode('utf-8'))

# -*- coding: utf-8 -*-
"""
Views Unificadas e Parametrizadas do TERMO-CP (Item 2 - De 911 funções para ~10 views).
Fornece:
  1. Views parametrizadas por (<slug:substance>, <slug:process_type>, <int:step>)
  2. Fábricas de views para manter 100% de retrocompatibilidade com todas as rotas legadas
  3. Isolamento de sessão por substância/aba (evitando colisão de request.session entre abas)
  4. Endpoint JSON para consulta programática de propriedades
"""

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.mail import BadHeaderError, EmailMessage
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from . import estados as std
from .forms import (
    MassForm,
    PropertyForm,
    SecondPropertyForm,
    TempForm,
    ThirdPropertyForm3,
)
from .thermo_engine import (
    BoundariesException,
    CalculationTypeError,
    SUBSTANCE_BY_SLUG,
    SUBSTANCE_CONFIG,
    TituloException,
    agua_cls,
    clear_flow_cycle,
    compute_pcte_process_context,
    compute_scte_process_context,
    compute_single_state_context,
    compute_vcte_process_context,
    get_flow_cycle,
    get_flow_val,
    has_flow_keys,
    save_flow_cycle,
    set_flow_data,
    subs_cls,
)

if not hasattr(std, 'instancia_estados'):
    std.instancia_estados = std.estados_cls()


# ==============================================================================
# 1. VIEWS INSTITUCIONAIS E DE NAVEGAÇÃO
# ==============================================================================

def homepage_view(request):
    return render(request, 'Inicio.html')


def estado_view(request):
    return render(request, 'estado.html')


def sobre_view(request):
    return render(request, 'sobre.html')


def ajuda_view(request):
    return render(request, 'ajuda.html')


def processo_view(request):
    return render(request, 'processo.html')


def erro_generico_view(request):
    return render(request, 'erro_generico.html')


def contato_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()

        if not nome or not email or not mensagem:
            messages.error(request, 'Por favor, preencha todos os campos.')
            return redirect('contato')

        from .models import MensagemContato
        registro = MensagemContato.objects.create(
            nome=nome,
            email=email,
            mensagem=mensagem,
            enviado_por_email=False,
        )

        assunto = f'[TERMO-CP] Nova mensagem de {nome}'
        corpo = f'Nome: {nome}\nE-mail: {email}\n\nMensagem:\n{mensagem}'

        if settings.EMAIL_HOST_USER and settings.CONTACT_EMAIL_DESTINATION:
            try:
                email_msg = EmailMessage(
                    subject=assunto,
                    body=corpo,
                    from_email=settings.EMAIL_HOST_USER,
                    to=[settings.CONTACT_EMAIL_DESTINATION],
                    reply_to=[email],
                )
                email_msg.send(fail_silently=False)
                registro.enviado_por_email = True
                registro.save(update_fields=['enviado_por_email'])
                messages.success(request, 'Mensagem enviada com sucesso!')
            except BadHeaderError:
                messages.error(request, 'Cabeçalho inválido detectado.')
            except Exception as e:
                print(f'Erro ao enviar e-mail: {e}')
                messages.success(request, 'Mensagem registrada com sucesso! Nossa equipe responderá em breve.')
        else:
            messages.success(request, 'Mensagem registrada com sucesso! Nossa equipe responderá em breve.')

        return redirect('contato')

    return render(request, 'contato.html')


# ==============================================================================
# 2. FÁBRICAS DE VIEWS PARAMETRIZADAS (ESTADO / PROPRIEDADE / PCTE / SCTE / VCTE)
# ==============================================================================

def _get_step_template(opt, kind, step):
    cfg = SUBSTANCE_CONFIG[opt]
    folder = cfg['folder']
    prefix = cfg.get('step_prefix', cfg['file_prefix'])
    return f"{folder}/{prefix}-{kind}-{step}.html"


def _get_results_template(opt, kind, step):
    cfg = SUBSTANCE_CONFIG[opt]
    folder = cfg['folder']
    file_prefix = cfg['file_prefix']
    return f"{folder}/results-{file_prefix}-{kind}-{step}.html"


def _redirect_preserving_calc_id(request, url_or_name, **kwargs):
    target_url = reverse(url_or_name, kwargs=kwargs) if kwargs else reverse(url_or_name)
    calc_id = request.GET.get('calc_id')
    if calc_id:
        target_url = f"{target_url}?calc_id={calc_id}"
    return redirect(target_url)


def make_single_state_views(opt, kind='estado', suffix='', error_route='error_type_7'):
    """
    Gera as views de cálculo de estado único ('estado' ou 'propriedade')
    para qualquer substância pura (opt 1..7) com sessão isolada por fluxo.
    """
    cfg = SUBSTANCE_CONFIG[opt]
    scope = f"{cfg['slug']}_{kind}"
    route_step1 = f"ask_known1_{suffix}" if suffix else "ask_known1"
    route_step2 = f"ask_known2_{suffix}" if suffix else "ask_known2"
    route_results = f"process_values_{suffix}" if suffix else "process_values"
    tpl_step1 = _get_step_template(opt, kind, 1)
    tpl_step2 = _get_step_template(opt, kind, 2)
    tpl_results = _get_results_template(opt, kind, 3)

    def ask_known1(request):
        if request.method == 'POST':
            form = PropertyForm(request.POST)
            if form.is_valid():
                property_choice = form.cleaned_data['property_choice']
                value_input = form.cleaned_data['value_input']
                data_to_save = {
                    'property_choice': property_choice,
                    'value_input': value_input,
                }
                if 'mass_input' in request.POST and form.cleaned_data.get('mass_input') is not None:
                    data_to_save['mass_input'] = float(form.cleaned_data['mass_input'])
                set_flow_data(request, scope, data_to_save)
                return _redirect_preserving_calc_id(request, route_step2)
        else:
            form = PropertyForm()
        return render(request, tpl_step1, {'form': form})

    def ask_known2(request):
        prop1 = int(get_flow_val(request, scope, 'property_choice', 0))
        excluded_properties = [prop1]
        if request.method == 'POST':
            form = SecondPropertyForm(request.POST, excluded_properties=excluded_properties)
            if form.is_valid():
                property_choice = form.cleaned_data['property_choice']
                value_input = form.cleaned_data['value_input']
                set_flow_data(request, scope, {
                    'second_property_choice': property_choice,
                    'second_value_input': value_input,
                })
                return _redirect_preserving_calc_id(request, route_results)
        else:
            form = SecondPropertyForm(excluded_properties=excluded_properties)
        return render(request, tpl_step2, {'form': form})

    def process_values(request):
        if not has_flow_keys(request, scope, ('property_choice', 'second_property_choice')):
            return redirect(route_step1)
        try:
            prop1 = int(get_flow_val(request, scope, 'property_choice'))
            prop2 = int(get_flow_val(request, scope, 'second_property_choice'))
            val1 = float(get_flow_val(request, scope, 'value_input'))
            val2 = float(get_flow_val(request, scope, 'second_value_input'))
            mass_val = float(get_flow_val(request, scope, 'mass_input', 1.0) or 1.0)
            ctx = compute_single_state_context(opt, prop1, prop2, val1, val2, mass=mass_val)
            return render(request, tpl_results, ctx)
        except CalculationTypeError:
            return redirect(error_route)
        except ValidationError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except BoundariesException:
            return render(request, 'erro_generico.html', {
                'message': 'Os valores fornecidos (ou calculados) estão fora dos limites das tabelas termodinâmicas'
            })
        except TypeError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except IndexError:
            return render(request, 'erro_generico.html', {
                'message': 'Ocorreu um erro ao acessar as tabelas termodinâmicas (valores fora do alcance esperado).'
            })

    return ask_known1, ask_known2, process_values, erro_generico_view, erro_generico_view


def make_pcte_views(opt, suffix, error_route=None):
    """
    Gera as views de processo isobárico (Pressão Constante)
    para qualquer substância pura (opt 1..7) com sessão isolada por substância.
    """
    cfg = SUBSTANCE_CONFIG[opt]
    scope = f"{cfg['slug']}_cycle"
    err_target = error_route or f"error_type_{suffix}"
    route_step1 = f"ask_known1_{suffix}"
    route_step2 = f"ask_known2_{suffix}"
    route_step3 = f"ask_known3_{suffix}"
    route_step4 = f"ask_known4_{suffix}"
    route_results = f"process_values_{suffix}"

    tpl_step1 = _get_step_template(opt, 'pcte', 1)
    tpl_step2 = _get_step_template(opt, 'pcte', 2)
    tpl_step_tviz = _get_step_template(opt, 'pcte', 3)
    tpl_step_prop2 = _get_step_template(opt, 'pcte', 4)
    tpl_results = _get_results_template(opt, 'pcte', 5)

    def ask_known1(request):
        clear_flow_cycle(request, scope, std.instancia_estados)
        if request.method == 'POST':
            form = PropertyForm(request.POST)
            if form.is_valid():
                property_choice = form.cleaned_data['property_choice']
                value_input = form.cleaned_data['value_input']
                data_to_save = {
                    'property_choice': property_choice,
                    'value_input': value_input,
                    'excluded_properties': [int(property_choice)],
                }
                if 'mass_input' in request.POST and form.cleaned_data.get('mass_input') is not None:
                    data_to_save['mass_input'] = float(form.cleaned_data['mass_input'])
                set_flow_data(request, scope, data_to_save)
                return _redirect_preserving_calc_id(request, route_step2)
        else:
            form = PropertyForm()
        return render(request, tpl_step1, {'form': form})

    def ask_known2(request):
        excluded = list(get_flow_val(request, scope, 'excluded_properties', []))
        if request.method == 'POST':
            form = SecondPropertyForm(request.POST, excluded_properties=excluded)
            if form.is_valid():
                second_prop = form.cleaned_data['property_choice']
                second_val = form.cleaned_data['value_input']
                excluded.append(int(second_prop))
                set_flow_data(request, scope, {
                    'second_property_choice': second_prop,
                    'second_value_input': second_val,
                    'excluded_properties': excluded,
                })
                return _redirect_preserving_calc_id(request, route_step3)
        else:
            form = SecondPropertyForm(excluded_properties=excluded)
        return render(request, tpl_step2, {'form': form})

    def ask_known3(request):
        # Penúltimo passo: Propriedade do estado final (ou Calor transferido)
        if request.method == 'POST':
            form = ThirdPropertyForm3(request.POST)
            if form.is_valid():
                third_prop = form.cleaned_data['property_choice']
                third_val = form.cleaned_data['value_input']
                set_flow_data(request, scope, {
                    'third_property_choice': third_prop,
                    'third_value_input': third_val,
                    'excluded_properties': [int(third_prop)],
                })
                return _redirect_preserving_calc_id(request, route_step4)
        else:
            form = ThirdPropertyForm3()
        return render(request, tpl_step_prop2, {'form': form})

    def ask_known4(request):
        # Último passo: Temperatura da vizinhança
        if request.method == 'POST':
            form = TempForm(request.POST)
            if form.is_valid():
                temp_val = form.cleaned_data['value_input']
                set_flow_data(request, scope, {'temp_value_input': temp_val})
                return _redirect_preserving_calc_id(request, route_results)
        else:
            form = TempForm()
        return render(request, tpl_step_tviz, {'form': form})

    def process_values(request):
        if not has_flow_keys(request, scope, ('property_choice', 'second_property_choice')):
            return redirect(route_step1)
        try:
            third_prop = int(get_flow_val(request, scope, 'third_property_choice'))
            third_val = float(get_flow_val(request, scope, 'third_value_input'))
            temp_viz = float(get_flow_val(request, scope, 'temp_value_input'))
            lista_estados, pontos_grafico = get_flow_cycle(request, scope, std.instancia_estados)

            state1_inputs = None
            if not lista_estados:
                state1_inputs = (
                    int(get_flow_val(request, scope, 'property_choice')),
                    int(get_flow_val(request, scope, 'second_property_choice')),
                    float(get_flow_val(request, scope, 'value_input')),
                    float(get_flow_val(request, scope, 'second_value_input')),
                )

            mass_val = float(get_flow_val(request, scope, 'mass_input', 1.0) or 1.0)
            ctx, lista_estados, pontos_grafico = compute_pcte_process_context(
                opt, state1_inputs, third_prop, third_val, temp_viz, lista_estados, pontos_grafico, mass=mass_val
            )
            save_flow_cycle(request, scope, lista_estados, pontos_grafico, std.instancia_estados)
            return render(request, tpl_results, ctx)
        except CalculationTypeError:
            return redirect(err_target)
        except ValidationError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except BoundariesException:
            return render(request, 'erro_generico.html', {
                'message': 'Os valores fornecidos (ou calculados) estão fora dos limites das tabelas termodinâmicas'
            })
        except TypeError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except IndexError:
            return render(request, 'erro_generico.html', {
                'message': 'Ocorreu um erro ao acessar as tabelas termodinâmicas (valores fora do alcance esperado).'
            })

    return homepage_view, ask_known1, ask_known2, ask_known3, ask_known4, process_values, erro_generico_view, erro_generico_view


def make_scte_views(opt, suffix, error_route=None):
    """
    Gera as views de processo isentrópico (Entropia Constante / Adiabático Reversível)
    para qualquer substância pura (opt 1..7) com sessão isolada por substância.
    """
    cfg = SUBSTANCE_CONFIG[opt]
    scope = f"{cfg['slug']}_cycle"
    err_target = error_route or f"error_type_{suffix}"
    route_step1 = f"ask_known1_{suffix}"
    route_step2 = f"ask_known2_{suffix}"
    route_step3 = f"ask_known3_{suffix}"
    route_results = f"process_values_{suffix}"

    tpl_step1 = _get_step_template(opt, 'scte', 1)
    tpl_step2 = _get_step_template(opt, 'scte', 2)
    tpl_step3 = _get_step_template(opt, 'scte', 3)
    tpl_results = _get_results_template(opt, 'scte', 4)

    def ask_known1(request):
        clear_flow_cycle(request, scope, std.instancia_estados)
        if request.method == 'POST':
            form = PropertyForm(request.POST)
            if form.is_valid():
                property_choice = form.cleaned_data['property_choice']
                value_input = form.cleaned_data['value_input']
                data_to_save = {
                    'property_choice': property_choice,
                    'value_input': value_input,
                    'excluded_properties': [int(property_choice)],
                }
                if 'mass_input' in request.POST and form.cleaned_data.get('mass_input') is not None:
                    data_to_save['mass_input'] = float(form.cleaned_data['mass_input'])
                set_flow_data(request, scope, data_to_save)
                return _redirect_preserving_calc_id(request, route_step2)
        else:
            form = PropertyForm()
        return render(request, tpl_step1, {'form': form})

    def ask_known2(request):
        excluded = list(get_flow_val(request, scope, 'excluded_properties', []))
        if request.method == 'POST':
            form = SecondPropertyForm(request.POST, excluded_properties=excluded)
            if form.is_valid():
                second_prop = form.cleaned_data['property_choice']
                second_val = form.cleaned_data['value_input']
                excluded.append(int(second_prop))
                set_flow_data(request, scope, {
                    'second_property_choice': second_prop,
                    'second_value_input': second_val,
                    'excluded_properties': excluded,
                })
                return _redirect_preserving_calc_id(request, route_step3)
        else:
            form = SecondPropertyForm(excluded_properties=excluded)
        return render(request, tpl_step2, {'form': form})

    def ask_known3(request):
        if request.method == 'POST':
            form = PropertyForm(request.POST)
            if form.is_valid():
                third_prop = form.cleaned_data['property_choice']
                third_val = form.cleaned_data['value_input']
                set_flow_data(request, scope, {
                    'third_property_choice': third_prop,
                    'third_value_input': third_val,
                    'excluded_properties': [int(third_prop)],
                })
                return redirect(route_results)
        else:
            form = PropertyForm()
        return render(request, tpl_step3, {'form': form})

    def process_values(request):
        if not has_flow_keys(request, scope, ('property_choice', 'second_property_choice')):
            return redirect(route_step1)
        try:
            third_prop = int(get_flow_val(request, scope, 'third_property_choice'))
            third_val = float(get_flow_val(request, scope, 'third_value_input'))
            lista_estados, pontos_grafico = get_flow_cycle(request, scope, std.instancia_estados)

            state1_inputs = None
            if not lista_estados:
                state1_inputs = (
                    int(get_flow_val(request, scope, 'property_choice')),
                    int(get_flow_val(request, scope, 'second_property_choice')),
                    float(get_flow_val(request, scope, 'value_input')),
                    float(get_flow_val(request, scope, 'second_value_input')),
                )

            mass_val = float(get_flow_val(request, scope, 'mass_input', 1.0) or 1.0)
            ctx, lista_estados, pontos_grafico = compute_scte_process_context(
                opt, state1_inputs, third_prop, third_val, lista_estados, pontos_grafico, mass=mass_val
            )
            save_flow_cycle(request, scope, lista_estados, pontos_grafico, std.instancia_estados)
            return render(request, tpl_results, ctx)
        except CalculationTypeError:
            return redirect(err_target)
        except ValidationError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except BoundariesException:
            return render(request, 'erro_generico.html', {
                'message': 'Os valores fornecidos (ou calculados) estão fora dos limites das tabelas termodinâmicas'
            })
        except TypeError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except IndexError:
            return render(request, 'erro_generico.html', {
                'message': 'Ocorreu um erro ao acessar as tabelas termodinâmicas (valores fora do alcance esperado).'
            })

    return homepage_view, ask_known1, ask_known2, ask_known3, process_values, erro_generico_view, erro_generico_view


def make_vcte_views(opt, suffix, error_route=None):
    """
    Gera as views de processo isocórico (Volume Constante)
    para qualquer substância pura (opt 1..7) com sessão isolada por substância.
    """
    cfg = SUBSTANCE_CONFIG[opt]
    scope = f"{cfg['slug']}_cycle"
    err_target = error_route or f"error_type_{suffix}"
    route_step1 = f"ask_known1_{suffix}"
    route_step2 = f"ask_known2_{suffix}"
    route_step3 = f"ask_known3_{suffix}"
    route_step4 = f"ask_known4_{suffix}"
    route_results = f"process_values_{suffix}"

    tpl_step1 = _get_step_template(opt, 'vcte', 1)
    tpl_step2 = _get_step_template(opt, 'vcte', 2)
    tpl_step_tviz = _get_step_template(opt, 'vcte', 3)
    tpl_step_prop2 = _get_step_template(opt, 'vcte', 4)
    tpl_results = _get_results_template(opt, 'vcte', 5)

    def ask_known1(request):
        clear_flow_cycle(request, scope, std.instancia_estados)
        if request.method == 'POST':
            form = PropertyForm(request.POST)
            if form.is_valid():
                property_choice = form.cleaned_data['property_choice']
                value_input = form.cleaned_data['value_input']
                data_to_save = {
                    'property_choice': property_choice,
                    'value_input': value_input,
                    'excluded_properties': [int(property_choice)],
                }
                if 'mass_input' in request.POST and form.cleaned_data.get('mass_input') is not None:
                    data_to_save['mass_input'] = float(form.cleaned_data['mass_input'])
                set_flow_data(request, scope, data_to_save)
                return _redirect_preserving_calc_id(request, route_step2)
        else:
            form = PropertyForm()
        return render(request, tpl_step1, {'form': form})

    def ask_known2(request):
        excluded = list(get_flow_val(request, scope, 'excluded_properties', []))
        if request.method == 'POST':
            form = SecondPropertyForm(request.POST, excluded_properties=excluded)
            if form.is_valid():
                second_prop = form.cleaned_data['property_choice']
                second_val = form.cleaned_data['value_input']
                excluded.append(int(second_prop))
                set_flow_data(request, scope, {
                    'second_property_choice': second_prop,
                    'second_value_input': second_val,
                    'excluded_properties': excluded,
                })
                return _redirect_preserving_calc_id(request, route_step3)
        else:
            form = SecondPropertyForm(excluded_properties=excluded)
        return render(request, tpl_step2, {'form': form})

    def ask_known3(request):
        # Penúltimo passo: Propriedade do estado final (ou Calor transferido)
        if request.method == 'POST':
            form = PropertyForm(request.POST)
            if form.is_valid():
                third_prop = form.cleaned_data['property_choice']
                third_val = form.cleaned_data['value_input']
                set_flow_data(request, scope, {
                    'third_property_choice': third_prop,
                    'third_value_input': third_val,
                    'excluded_properties': [int(third_prop)],
                })
                return _redirect_preserving_calc_id(request, route_step4)
        else:
            form = PropertyForm()
        return render(request, tpl_step_prop2, {'form': form})

    def ask_known4(request):
        # Último passo: Temperatura da vizinhança
        if request.method == 'POST':
            form = TempForm(request.POST)
            if form.is_valid():
                temp_val = form.cleaned_data['value_input']
                set_flow_data(request, scope, {'temp_value_input': temp_val})
                return _redirect_preserving_calc_id(request, route_results)
        else:
            form = TempForm()
        return render(request, tpl_step_tviz, {'form': form})

    def process_values(request):
        if not has_flow_keys(request, scope, ('property_choice', 'second_property_choice')):
            return redirect(route_step1)
        try:
            third_prop = int(get_flow_val(request, scope, 'third_property_choice'))
            third_val = float(get_flow_val(request, scope, 'third_value_input'))
            temp_viz = float(get_flow_val(request, scope, 'temp_value_input'))
            lista_estados, pontos_grafico = get_flow_cycle(request, scope, std.instancia_estados)

            state1_inputs = None
            if not lista_estados:
                state1_inputs = (
                    int(get_flow_val(request, scope, 'property_choice')),
                    int(get_flow_val(request, scope, 'second_property_choice')),
                    float(get_flow_val(request, scope, 'value_input')),
                    float(get_flow_val(request, scope, 'second_value_input')),
                )

            mass_val = float(get_flow_val(request, scope, 'mass_input', 1.0) or 1.0)
            ctx, lista_estados, pontos_grafico = compute_vcte_process_context(
                opt, state1_inputs, third_prop, third_val, temp_viz, lista_estados, pontos_grafico, mass=mass_val
            )
            save_flow_cycle(request, scope, lista_estados, pontos_grafico, std.instancia_estados)
            return render(request, tpl_results, ctx)
        except CalculationTypeError:
            return redirect(err_target)
        except ValidationError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except BoundariesException:
            return render(request, 'erro_generico.html', {
                'message': 'Os valores fornecidos (ou calculados) estão fora dos limites das tabelas termodinâmicas'
            })
        except TypeError as e:
            return render(request, 'erro_generico.html', {'message': str(e)})
        except IndexError:
            return render(request, 'erro_generico.html', {
                'message': 'Ocorreu um erro ao acessar as tabelas termodinâmicas (valores fora do alcance esperado).'
            })

    return homepage_view, ask_known1, ask_known2, ask_known3, ask_known4, process_values, erro_generico_view, erro_generico_view


# ==============================================================================
# 3. REGISTRO CENTRAL DE VIEWS POR SUBSTÂNCIA E PROCESSO (Item 2)
# ==============================================================================

# Mapeamento (opt, kind) -> sufixo legado das rotas
_LEGACY_SUFFIX_MAP = {
    (1, 'estado'): ('', 'error_type7'),
    (1, 'pcte'): ('3', 'error_type_3'),
    (1, 'scte'): ('4', 'error_type_4'),
    (1, 'vcte'): ('5', 'error_type_5'),

    (2, 'estado'): ('13', 'error_type_7'),
    (2, 'propriedade'): ('14', 'error_type_7'),
    (2, 'pcte'): ('15', 'error_type_15'),
    (2, 'scte'): ('16', 'error_type_16'),
    (2, 'vcte'): ('17', 'error_type_17'),

    (3, 'estado'): ('18', 'error_type_7'),
    (3, 'propriedade'): ('19', 'error_type_7'),
    (3, 'pcte'): ('20', 'error_type_20'),
    (3, 'scte'): ('21', 'error_type_21'),
    (3, 'vcte'): ('22', 'error_type_22'),

    (4, 'estado'): ('23', 'error_type_7'),
    (4, 'propriedade'): ('24', 'error_type_7'),
    (4, 'pcte'): ('25', 'error_type_25'),
    (4, 'scte'): ('26', 'error_type_26'),
    (4, 'vcte'): ('27', 'error_type_27'),

    (5, 'estado'): ('28', 'error_type_7'),
    (5, 'propriedade'): ('29', 'error_type_7'),
    (5, 'pcte'): ('30', 'error_type_30'),
    (5, 'scte'): ('31', 'error_type_31'),
    (5, 'vcte'): ('32', 'error_type_32'),

    (6, 'estado'): ('33', 'error_type_7'),
    (6, 'propriedade'): ('34', 'error_type_7'),
    (6, 'pcte'): ('35', 'error_type_35'),
    (6, 'scte'): ('36', 'error_type_36'),
    (6, 'vcte'): ('37', 'error_type_37'),

    (7, 'estado'): ('38', 'error_type_7'),
    (7, 'propriedade'): ('39', 'error_type_7'),
    (7, 'pcte'): ('40', 'error_type_40'),
    (7, 'scte'): ('41', 'error_type_41'),
    (7, 'vcte'): ('42', 'error_type_42'),
}

_VIEW_REGISTRY = {}
for (opt_id, kind_key), (suf, err_rt) in _LEGACY_SUFFIX_MAP.items():
    if kind_key in ('estado', 'propriedade'):
        _VIEW_REGISTRY[(opt_id, kind_key)] = make_single_state_views(opt_id, kind_key, suf, err_rt)
    elif kind_key == 'pcte':
        _VIEW_REGISTRY[(opt_id, kind_key)] = make_pcte_views(opt_id, suf, err_rt)
    elif kind_key == 'scte':
        _VIEW_REGISTRY[(opt_id, kind_key)] = make_scte_views(opt_id, suf, err_rt)
    elif kind_key == 'vcte':
        _VIEW_REGISTRY[(opt_id, kind_key)] = make_vcte_views(opt_id, suf, err_rt)


def get_registered_views(opt, kind):
    return _VIEW_REGISTRY[(opt, kind)]


_SUBSTANCE_I18N_NAMES = {
    1: ('Água', 'Water', 'Agua'),
    2: ('Amônia', 'Ammonia', 'Amoníaco'),
    3: ('CO₂', 'CO₂', 'CO₂'),
    4: ('R-410A', 'R-410A', 'R-410A'),
    5: ('R-134A', 'R-134A', 'R-134A'),
    6: ('Nitrogênio', 'Nitrogen', 'Nitrógeno'),
    7: ('Metano', 'Methane', 'Metano'),
}

_MASS_FLOW_REGISTRY = {
    'gas_prop': {
        'session_scope': 'gas_prop',
        'next_route': 'ask_known3_6',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': False,
    },
    'gas_cilindro': {
        'session_scope': 'gas_cilindro',
        'next_route': 'ask_known3_7',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': False,
    },
    'gas_pcte': {
        'session_scope': 'gas_pcte',
        'next_route': 'ask_known1_8',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': True,
    },
    'gas_vcte': {
        'session_scope': 'gas_vcte',
        'next_route': 'ask_known1_9',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': True,
    },
    'gas_tcte': {
        'session_scope': 'gas_tcte',
        'next_route': 'ask_known1_10',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': True,
    },
    'gas_poli': {
        'session_scope': 'gas_poli',
        'next_route': 'ask_known1_11',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': True,
    },
    'gas_scte': {
        'session_scope': 'gas_scte',
        'next_route': 'ask_known1_12',
        'is_final_step': False,
        'names': ('Gás Ideal', 'Ideal Gas', 'Gas Ideal'),
        'is_gas_process': True,
    },
}

for (_opt_id, _kind_key), (_suf, _err_rt) in _LEGACY_SUFFIX_MAP.items():
    _slug = SUBSTANCE_CONFIG[_opt_id]['slug']
    _fk = f"{_slug}_{_kind_key}"
    _first_step_route = f"ask_known1_{_suf}" if _suf else "ask_known1"
    if _kind_key in ('estado', 'propriedade'):
        _MASS_FLOW_REGISTRY[_fk] = {
            'session_scope': _fk,
            'next_route': _first_step_route,
            'is_final_step': False,
            'names': _SUBSTANCE_I18N_NAMES[_opt_id],
            'is_gas_process': False,
        }
    else:
        _MASS_FLOW_REGISTRY[_fk] = {
            'session_scope': f"{_slug}_cycle",
            'next_route': _first_step_route,
            'is_final_step': False,
            'names': _SUBSTANCE_I18N_NAMES[_opt_id],
            'is_gas_process': False,
        }


def ask_mass_view(request, flow_key):
    """View única para a página separada de entrada de Massa do sistema (kg)."""
    meta = _MASS_FLOW_REGISTRY.get(flow_key)
    if not meta:
        raise Http404("Fluxo de cálculo inválido para definição de massa.")

    if request.method == 'POST':
        form = MassForm(request.POST)
        if form.is_valid():
            mass_val = float(form.cleaned_data['mass_input'] or 1.0)
            set_flow_data(request, meta['session_scope'], {'mass_input': mass_val})
            if meta.get('is_gas_process'):
                request.session['mass_input'] = mass_val
                request.session.modified = True
            return _redirect_preserving_calc_id(request, meta['next_route'])
    else:
        form = MassForm()

    name_pt, name_en, name_es = meta['names']
    return render(request, 'massa_step.html', {
        'form': form,
        'name_pt': name_pt,
        'name_en': name_en,
        'name_es': name_es,
        'is_final_step': meta['is_final_step'],
    })


# ==============================================================================
# 4. ROTAS PARAMETRIZADAS MODERNAS (Item 2: /calc/<substance>/<kind>/...)
# ==============================================================================

def parameterized_state_step_view(request, substance, mode='estado', step=1):
    """View única parametrizada para os passos 1 e 2 de Estado/Propriedade de qualquer substância."""
    cfg = SUBSTANCE_BY_SLUG.get(substance)
    if not cfg or mode not in ('estado', 'propriedade'):
        raise Http404("Substância ou modo inválido.")
    opt = cfg['opt']
    if opt == 1 and mode == 'propriedade':
        mode = 'estado'
    views_tuple = get_registered_views(opt, mode)
    if step == 1:
        return views_tuple[0](request)
    elif step == 2:
        return views_tuple[1](request)
    raise Http404("Passo inválido.")


def parameterized_state_results_view(request, substance, mode='estado'):
    """View única parametrizada para resultados de Estado/Propriedade de qualquer substância."""
    cfg = SUBSTANCE_BY_SLUG.get(substance)
    if not cfg or mode not in ('estado', 'propriedade'):
        raise Http404("Substância ou modo inválido.")
    opt = cfg['opt']
    if opt == 1 and mode == 'propriedade':
        mode = 'estado'
    views_tuple = get_registered_views(opt, mode)
    return views_tuple[2](request)


def parameterized_process_step_view(request, substance, process_type, step=1):
    """View única parametrizada para os passos 1..4 de Processos (pcte, scte, vcte) de qualquer substância."""
    cfg = SUBSTANCE_BY_SLUG.get(substance)
    if not cfg or process_type not in ('pcte', 'scte', 'vcte'):
        raise Http404("Substância ou tipo de processo inválido.")
    opt = cfg['opt']
    views_tuple = get_registered_views(opt, process_type)
    # views_tuple: (homepage, ask1, ask2, ask3, [ask4], process_values, err_val, err_type)
    max_step = 3 if process_type == 'scte' else 4
    if 1 <= step <= max_step:
        return views_tuple[step](request)
    raise Http404("Passo inválido para este processo.")


def parameterized_process_results_view(request, substance, process_type):
    """View única parametrizada para resultados de Processos (pcte, scte, vcte) de qualquer substância."""
    cfg = SUBSTANCE_BY_SLUG.get(substance)
    if not cfg or process_type not in ('pcte', 'scte', 'vcte'):
        raise Http404("Substância ou tipo de processo inválido.")
    opt = cfg['opt']
    views_tuple = get_registered_views(opt, process_type)
    results_fn = views_tuple[4] if process_type == 'scte' else views_tuple[5]
    return results_fn(request)


def api_calculate_state_view(request):
    """
    Endpoint JSON para consulta direta e desacoplada de propriedades termodinâmicas:
    GET/POST /api/v1/estado/?substance=agua&prop1=0&val1=100&prop2=6&val2=50
    """
    data = request.GET if request.method == 'GET' else request.POST
    substance = data.get('substance', 'agua')
    cfg = SUBSTANCE_BY_SLUG.get(substance)
    if not cfg:
        return JsonResponse({'error': f'Substância desconhecida: {substance}'}, status=400)
    try:
        prop1 = int(data.get('prop1'))
        prop2 = int(data.get('prop2'))
        val1 = float(data.get('val1'))
        val2 = float(data.get('val2'))
        mass_val = float(data.get('mass', 1.0) or 1.0)
        ctx = compute_single_state_context(cfg['opt'], prop1, prop2, val1, val2, mass=mass_val)
        return JsonResponse({
            'substance': cfg['slug'],
            'massa': ctx['massa_float'],
            'fase': ctx['fase'],
            'temperatura': ctx['temperatura'],
            'pressao': ctx['pressao'],
            'volume_especifico': ctx['volume_especifico'],
            'energia_interna': ctx['energia_interna'],
            'entalpia_especifica': ctx['entalpia_especifica'],
            'entropia_especifica': ctx['entropia_especifica'],
            'titulo': ctx['titulo'],
            'titulo_fracao': ctx['titulo_fracao'],
        })
    except BoundariesException:
        return JsonResponse({'error': 'Valores fora dos limites das tabelas termodinâmicas.'}, status=422)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

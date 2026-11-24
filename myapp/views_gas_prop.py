# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .forms import PropertyGasIdeal1, RGasIdeal1, SecondPropertyGasIdeal1
from .thermo_engine import (
    compute_ideal_gas_single_state,
    format_mass_display,
    get_flow_val,
    has_flow_keys,
    set_flow_data,
)

SCOPE = 'gas_prop'


def homepage_view(request):
    return render(request, 'Inicio.html')


def processo_view(request):
    return render(request, 'processo.html')


def processosgasideal_view(request):
    return render(request, 'processos2.html')


def ask_known3_view6(request):
    if request.method == 'POST':
        form = RGasIdeal1(request.POST)
        if form.is_valid():
            R_value_input = form.cleaned_data.get('R_value_input')
            if R_value_input is not None:
                set_flow_data(request, SCOPE, {'R_value_input': R_value_input})
                return redirect('ask_known1_6')
            form.add_error(None, "Erro ao processar o valor de R. Por favor, preencha corretamente.")
    else:
        form = RGasIdeal1()
    return render(request, 'gas/ask_known3_6.html', {'form': form})


def ask_known1_view6(request):
    if request.method == 'POST':
        form = PropertyGasIdeal1(request.POST)
        if form.is_valid():
            property_choice = form.cleaned_data['property_choice']
            value_input = form.cleaned_data['value_input']
            data_to_save = {
                'property_choice': property_choice,
                'value_input': value_input,
            }
            if 'mass_input' in request.POST and form.cleaned_data.get('mass_input') is not None:
                data_to_save['mass_input'] = float(form.cleaned_data['mass_input'])
            set_flow_data(request, SCOPE, data_to_save)
            return redirect('ask_known2_6')
    else:
        form = PropertyGasIdeal1()
    return render(request, 'gas/ask_known1_6.html', {'form': form})


def ask_known2_view6(request):
    excluded_properties = [int(get_flow_val(request, SCOPE, 'property_choice', 0))]
    if request.method == 'POST':
        form = SecondPropertyGasIdeal1(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            property_choice = form.cleaned_data['property_choice']
            value_input = form.cleaned_data['value_input']
            set_flow_data(request, SCOPE, {
                'second_property_choice': property_choice,
                'second_value_input': value_input,
            })
            return redirect('process_values_6')
    else:
        form = SecondPropertyGasIdeal1(excluded_properties=excluded_properties)
    return render(request, 'gas/ask_known2_6.html', {'form': form})


def process_values_view6(request):
    if not has_flow_keys(request, SCOPE, ('property_choice', 'second_property_choice')):
        return redirect('ask_known1_6')

    try:
        prop1 = int(get_flow_val(request, SCOPE, 'property_choice'))
        prop2 = int(get_flow_val(request, SCOPE, 'second_property_choice'))
        val1 = float(get_flow_val(request, SCOPE, 'value_input'))
        val2 = float(get_flow_val(request, SCOPE, 'second_value_input'))
        R_val = float(get_flow_val(request, SCOPE, 'R_value_input'))
        mass_val = float(get_flow_val(request, SCOPE, 'mass_input', 1.0))

        temperatura_c, pressao, volume = compute_ideal_gas_single_state(prop1, prop2, val1, val2, R_val)

        return render(request, 'gas/results_6.html', {
            'temperatura': round(temperatura_c, 3),
            'pressao': round(pressao, 6),
            'volume': round(volume, 6),
            'R': R_val,
            'massa': format_mass_display(mass_val),
            'massa_float': mass_val,
        })
    except ValidationError as e:
        return render(request, 'erro_generico.html', {'message': str(e)})

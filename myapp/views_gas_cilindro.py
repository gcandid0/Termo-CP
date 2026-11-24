# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .forms import PropertyGasIdeal2, RGasIdeal2, SecondPropertyGasIdeal2
from .thermo_engine import (
    compute_ideal_gas_single_state,
    format_mass_display,
    get_flow_val,
    has_flow_keys,
    set_flow_data,
)

SCOPE = 'gas_cilindro'


def ask_known3_view7(request):
    if request.method == 'POST':
        form = RGasIdeal2(request.POST)
        if form.is_valid():
            R_value_input = form.cleaned_data.get('R_value_input')
            if R_value_input is not None:
                set_flow_data(request, SCOPE, {'R_value_input': R_value_input})
                return redirect('ask_known1_7')
            form.add_error(None, "Erro ao processar o valor de R. Por favor, preencha corretamente.")
    else:
        form = RGasIdeal2()
    return render(request, 'gas/ask_known3_7.html', {'form': form})


def ask_known1_view7(request):
    if request.method == 'POST':
        form = PropertyGasIdeal2(request.POST)
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
            return redirect('ask_known2_7')
    else:
        form = PropertyGasIdeal2()
    return render(request, 'gas/ask_known1_7.html', {'form': form})


def ask_known2_view7(request):
    excluded_properties = [int(get_flow_val(request, SCOPE, 'property_choice', 0))]
    if request.method == 'POST':
        form = SecondPropertyGasIdeal2(request.POST, excluded_properties=excluded_properties)
        if form.is_valid():
            property_choice = form.cleaned_data['property_choice']
            value_input = form.cleaned_data['value_input']
            set_flow_data(request, SCOPE, {
                'second_property_choice': property_choice,
                'second_value_input': value_input,
            })
            return redirect('process_values_7')
    else:
        form = SecondPropertyGasIdeal2(excluded_properties=excluded_properties)
    return render(request, 'gas/ask_known2_7.html', {'form': form})


def process_values_view7(request):
    if not has_flow_keys(request, SCOPE, ('property_choice', 'second_property_choice')):
        return redirect('ask_known1_7')

    try:
        prop1 = int(get_flow_val(request, SCOPE, 'property_choice'))
        prop2 = int(get_flow_val(request, SCOPE, 'second_property_choice'))
        val1 = float(get_flow_val(request, SCOPE, 'value_input'))
        val2 = float(get_flow_val(request, SCOPE, 'second_value_input'))
        R_val = float(get_flow_val(request, SCOPE, 'R_value_input'))
        mass_val = float(get_flow_val(request, SCOPE, 'mass_input', 1.0))

        temperatura_c, pressao, volume = compute_ideal_gas_single_state(prop1, prop2, val1, val2, R_val)

        if pressao < 0.0001 or volume < 0.0001 or volume > 1000:
            return redirect('error_type7')

        return render(request, 'gas/results_7.html', {
            'temperatura': round(temperatura_c, 3),
            'pressao': round(pressao, 6),
            'volume': round(volume, 6),
            'R': R_val,
            'massa': format_mass_display(mass_val),
            'massa_float': mass_val,
        })
    except ValidationError as e:
        return render(request, 'erro_generico.html', {'message': str(e)})


def error_type_view7(request):
    return render(request, 'erro_generico.html')

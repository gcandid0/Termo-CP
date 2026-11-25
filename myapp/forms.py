# -*- coding: utf-8 -*-
"""
Formulários do TERMO-CP (Refatorados segundo o princípio DRY).
Define as classes base parametrizadas e mantém aliases retrocompatíveis para todas as views.
"""

from django import forms
from django.utils.safestring import mark_safe


def t_html(pt, en, es, fr=None):
    """
    Gera a tag HTML traduzível identificada pelo JavaScript de internacionalização.
    """
    fr_val = fr if fr is not None else en
    html_string = f'<span class="lang-text" data-pt-br="{pt}" data-en="{en}" data-es="{es}" data-fr="{fr_val}">{pt}</span>'
    return mark_safe(html_string)


# --- VARIÁVEIS CONSTANTES DE TEXTO TRADUZIDO ---
LBL_SEL_PROP = t_html("Selecione a propriedade conhecida", "Select the known property", "Seleccione la propiedad conocida", "Sélectionnez la propriété connue")
LBL_SEL_OUTRA_PROP = t_html("Selecione a outra propriedade conhecida", "Select the other known property", "Seleccione la otra propiedad conocida", "Sélectionnez l'autre propriété connue")
LBL_DIGITE_VALOR = t_html("Digite o valor", "Enter the value", "Introduzca el valor", "Entrez la valeur")

# --- LISTAS DE PROPRIEDADES TRADUZIDAS ---
P_TEMP = t_html('Temperatura (T)', 'Temperature (T)', 'Temperatura (T)', 'Température (T)')
P_PRESS = t_html('Pressão (p)', 'Pressure (p)', 'Presión (p)', 'Pression (p)')
P_VOL = t_html('Volume específico (v)', 'Specific volume (v)', 'Volumen específico (v)', 'Volume spécifique (v)')
P_ENER = t_html('Energia interna (u)', 'Internal energy (u)', 'Energía interna (u)', 'Énergie interne (u)')
P_ENTAL = t_html('Entalpia (h)', 'Enthalpy (h)', 'Entalpía (h)', 'Enthalpie (h)')
P_ENTRO = t_html('Entropia (s)', 'Entropy (s)', 'Entropía (s)', 'Entropie (s)')
P_TIT = t_html('Título (x)', 'Quality (x)', 'Calidad (x)', 'Titre (x)')
P_CALOR = t_html('Calor transferido (Q)', 'Transferred heat (Q)', 'Calor transferido (Q)', 'Chaleur transférée (Q)')

C_CV = t_html('Cv0', 'Cv0', 'Cv0')
C_CP = t_html('Cp0', 'Cp0', 'Cp0')
C_R = t_html('R', 'R', 'R')
C_K = t_html('K', 'K', 'K')


# ==============================================================================
# CLASSES BASE DE FORMULÁRIOS (SUBSTÂNCIAS PURAS)
# ==============================================================================

class Processos(forms.Form):
    PROCESSOS_CHOICES = [
        (100, t_html('Aquecimento/Resfriamento à pressão constante', 'Heating/Cooling at constant pressure', 'Calentamiento/Enfriamiento a presión constante')),
        (101, t_html('Aquecimento/Resfriamento à volume constante', 'Heating/Cooling at constant volume', 'Calentamiento/Enfriamiento a volumen constante')),
        (102, t_html('Compressão/Expansão adiabática e reversível', 'Reversible adiabatic compression/expansion', 'Compresión/Expansión adiabática y reversible')),
    ]


class PropertyForm(forms.Form):
    """Seleção da 1ª propriedade (T ou p) e massa opcional para substâncias puras."""
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)
    mass_input = forms.FloatField(required=False, initial=1.0, min_value=0.0001)


class SecondPropertyForm(forms.Form):
    """Seleção da 2ª propriedade (T, p, v, u, h, s, x) excluindo a 1ª."""
    ALL_PROPERTIES = [
        (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
        (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
    ]

    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)
        filtered = [(num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP,
        )

    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)


class TempForm(forms.Form):
    """Entrada de temperatura da vizinhança para processos de substâncias puras."""
    property_choice = forms.IntegerField(widget=forms.HiddenInput(), initial=7)
    value_input = forms.CharField(
        label=t_html(
            "Digite o valor da Temperatura da Vizinhança",
            "Enter the Surroundings Temperature value",
            "Introduzca el valor de la Temperatura del Entorno",
        ),
        required=True,
    )


class MassForm(forms.Form):
    """Entrada de massa do sistema (kg) em página separada."""
    mass_input = forms.FloatField(
        label=t_html(
            "Digite o valor da Massa do sistema (kg):",
            "Enter the System Mass value (kg):",
            "Introduzca el valor de la Masa del sistema (kg):",
        ),
        initial=1.0,
        min_value=0.0001,
        required=True,
    )


class ThirdPropertyForm3(forms.Form):
    """Seleção da propriedade do Estado 2 para processos isobáricos (T, v, u, h, s, x, Q)."""
    ALL_PROPERTIES = [
        (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
        (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
    ]

    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)
        filtered = [(num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP,
        )

    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)


# ==============================================================================
# CLASSES BASE DE FORMULÁRIOS (GÁS IDEAL)
# ==============================================================================

class PropertyGasIdeal1(forms.Form):
    PROPERTY_CHOICES = [(0, P_TEMP), (1, P_PRESS), (2, P_VOL)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)
    mass_input = forms.FloatField(required=False, initial=1.0, min_value=0.0001)


class SecondPropertyGasIdeal1(forms.Form):
    ALL_PROPERTIES = [(0, P_TEMP), (1, P_PRESS), (2, P_VOL)]

    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)
        filtered = [(num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP,
        )

    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)


class RGasIdeal1(forms.Form):
    property_choice = forms.IntegerField(widget=forms.HiddenInput(), initial=7)
    R_value_input = forms.CharField(
        label=t_html('Digite o valor do R', 'Enter the value of R', 'Introduzca el valor de R'),
        required=True,
    )


class ConstantesPCte8(forms.Form):
    PROPERTY_CHOICES = [('11', C_CV), ('12', C_CP), ('13', C_R), ('14', C_K)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class ConstantesPCte8_2(forms.Form):
    ALL_PROPERTIES = [('11', C_CV), ('12', C_CP), ('13', C_R), ('14', C_K)]

    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)
        excluded_set = {str(x) for x in (excluded_properties or []) if x is not None}
        filtered = [(num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_set]
        if not filtered:
            filtered = self.ALL_PROPERTIES
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP,
        )

    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class Prop1PCte8(forms.Form):
    """Primeira propriedade do Estado 1 em processos de gás ideal (T, p ou v)."""
    PROPERTY_CHOICES = [('0', P_TEMP), ('1', P_PRESS), ('2', P_VOL)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)
    mass_input = forms.FloatField(required=False, initial=1.0, min_value=0.0001)


class Prop1PCte8_2(forms.Form):
    """Segunda propriedade do Estado 1 em processos de gás ideal (exclui a 1ª)."""
    ALL_PROPERTIES = [('0', P_TEMP), ('1', P_PRESS), ('2', P_VOL)]

    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)
        excluded_set = {str(x) for x in (excluded_properties or []) if x is not None}
        filtered = [(num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_set]
        if not filtered:
            filtered = self.ALL_PROPERTIES
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP,
        )

    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class Prop2PCte8(forms.Form):
    PROPERTY_CHOICES = [('0', P_TEMP), ('2', P_VOL), ('8', P_CALOR)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class Prop2VCte9(forms.Form):
    PROPERTY_CHOICES = [('0', P_TEMP), ('1', P_PRESS), ('8', P_CALOR)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class Prop2TCte10(forms.Form):
    PROPERTY_CHOICES = [('1', P_PRESS), ('2', P_VOL), ('8', P_CALOR)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class Prop2TCte11(forms.Form):
    PROPERTY_CHOICES = [('0', P_TEMP), ('1', P_PRESS), ('2', P_VOL), ('8', P_CALOR)]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP,
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class TvizGasIdeal8(forms.Form):
    Tviz_value_input = forms.FloatField(
        label=t_html(
            'Digite o valor da Temperatura da Vizinhança',
            'Enter the Surroundings Temperature value',
            'Introduzca el valor de la Temperatura del Entorno',
        ),
        required=True,
    )


class NGasIdeal11(forms.Form):
    N_value_input = forms.FloatField(
        label=t_html('Digite o valor de n', 'Enter the value of n', 'Introduzca el valor de n'),
        required=True,
    )


# ==============================================================================
# ALIASES DE RETROCOMPATIBILIDADE (MANTÉM TODOS OS 115 NOMES IMPORTÁVEIS)
# ==============================================================================

# Grupo 2 -> PropertyForm
PropertyForm3 = PropertyForm
PropertyIso = PropertyForm
ThirdPropertyIso = PropertyForm
PropertyForm5 = PropertyForm
ThirdPropertyForm5 = PropertyForm
PropertyFormAmoniaEst1 = PropertyForm
PcteAmonia = PropertyForm
ScteAmonia = PropertyForm
ScteAmonia3 = PropertyForm
vcteAmonia = PropertyForm
vcteAmonia4 = PropertyForm
PropertyFormCO2Est1 = PropertyForm
PcteCO2 = PropertyForm
ScteCO2 = PropertyForm
ScteCO23 = PropertyForm
vcteCO2 = PropertyForm
vcteCO24 = PropertyForm
PropertyFormR410AEst1 = PropertyForm
PcteR410A = PropertyForm
ScteR410A = PropertyForm
ScteR410A3 = PropertyForm
vcteR410A = PropertyForm
vcteR410A4 = PropertyForm
PropertyFormR134AEst1 = PropertyForm
PcteR134A = PropertyForm
ScteR134A = PropertyForm
ScteR134A3 = PropertyForm
vcteR134A = PropertyForm
vcteR134A4 = PropertyForm
PropertyFormKelvinEst1 = PropertyForm
PcteKelvin = PropertyForm
ScteKelvin = PropertyForm
ScteKelvin3 = PropertyForm
vcteKelvin = PropertyForm
vcteKelvin4 = PropertyForm

# Grupo 3 -> SecondPropertyForm
SecondPropertyForm3 = SecondPropertyForm
SecondPropertyIso = SecondPropertyForm
SecondPropertyForm5 = SecondPropertyForm
SecondPropertyFormAmoniaEst1 = SecondPropertyForm
PcteAmonia2 = SecondPropertyForm
ScteAmonia2 = SecondPropertyForm
vcteAmonia2 = SecondPropertyForm
SecondPropertyFormCO2Est1 = SecondPropertyForm
PcteCO22 = SecondPropertyForm
ScteCO22 = SecondPropertyForm
vcteCO22 = SecondPropertyForm
SecondPropertyFormR410AEst1 = SecondPropertyForm
PcteR410A2 = SecondPropertyForm
ScteR410A2 = SecondPropertyForm
vcteR410A2 = SecondPropertyForm
SecondPropertyFormR134AEst1 = SecondPropertyForm
PcteR134A2 = SecondPropertyForm
ScteR134A2 = SecondPropertyForm
vcteR134A2 = SecondPropertyForm
SecondPropertyFormKelvinEst1 = SecondPropertyForm
PcteKelvin2 = SecondPropertyForm
ScteKelvin2 = SecondPropertyForm
vcteKelvin2 = SecondPropertyForm

# Grupo 4 -> TempForm
TempForm2 = TempForm
PcteAmonia3 = TempForm
vcteAmonia3 = TempForm
PcteCO23 = TempForm
vcteCO23 = TempForm
PcteR410A3 = TempForm
vcteR410A3 = TempForm
PcteR134A3 = TempForm
vcteR134A3 = TempForm
PcteKelvin3 = TempForm
vcteKelvin3 = TempForm

# Grupo 5 -> ThirdPropertyForm3
PcteAmonia4 = ThirdPropertyForm3
PcteCO24 = ThirdPropertyForm3
PcteR410A4 = ThirdPropertyForm3
PcteR134A4 = ThirdPropertyForm3
PcteKelvin4 = ThirdPropertyForm3

# Gás Ideal Aliases
PropertyGasIdeal2 = PropertyGasIdeal1
SecondPropertyGasIdeal2 = SecondPropertyGasIdeal1
RGasIdeal2 = RGasIdeal1

ConstantesVCte9 = ConstantesPCte8
ConstantesTCte10 = ConstantesPCte8
ConstantesPoli11 = ConstantesPCte8
ConstantesPoli12 = ConstantesPCte8

ConstantesVCte9_2 = ConstantesPCte8_2
ConstantesTCte10_2 = ConstantesPCte8_2
ConstantesPoli11_2 = ConstantesPCte8_2
ConstantesPoli12_2 = ConstantesPCte8_2

Prop1VCte9 = Prop1PCte8
Prop1TCte10 = Prop1PCte8
Prop1Poli11 = Prop1PCte8
Prop1_12 = Prop1PCte8
Prop2_12 = Prop1PCte8

Prop1VCte9_2 = Prop1PCte8_2
Prop1TCte10_2 = Prop1PCte8_2
Prop1Poli11_2 = Prop1PCte8_2
Prop1_2_12 = Prop1PCte8_2

TvizGasIdeal9 = TvizGasIdeal8
TvizGasIdeal10 = TvizGasIdeal8
TvizGasIdeal11 = TvizGasIdeal8

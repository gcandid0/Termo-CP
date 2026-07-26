from django import forms
from django.utils.safestring import mark_safe

# --- FUNÇÃO AUXILIAR PARA GERAR O HTML TRADUZÍVEL ---
def t_html(pt, en, es):
    """
    Gera a tag HTML que o JavaScript do base2.html irá identificar
    e traduzir automaticamente no lado do cliente.
    """
    html_string = f'<span class="lang-text" data-pt-br="{pt}" data-en="{en}" data-es="{es}">{pt}</span>'
    return mark_safe(html_string)

# --- VARIÁVEIS CONSTANTES DE TEXTO TRADUZIDO ---
# (Criadas para evitar digitação repetitiva e manter a consistência)
LBL_SEL_PROP = t_html("Selecione a propriedade conhecida", "Select the known property", "Seleccione la propiedad conocida")
LBL_SEL_OUTRA_PROP = t_html("Selecione a outra propriedade conhecida", "Select the other known property", "Seleccione la otra propiedad conocida")
LBL_DIGITE_VALOR = t_html("Digite o valor", "Enter the value", "Introduzca el valor")

# --- LISTAS DE PROPRIEDADES TRADUZIDAS ---
P_TEMP = t_html('Temperatura (T)', 'Temperature (T)', 'Temperatura (T)')
P_PRESS = t_html('Pressão (p)', 'Pressure (p)', 'Presión (p)')
P_VOL = t_html('Volume específico (v)', 'Specific volume (v)', 'Volumen específico (v)')
P_ENER = t_html('Energia interna (u)', 'Internal energy (u)', 'Energía interna (u)')
P_ENTAL = t_html('Entalpia (h)', 'Enthalpy (h)', 'Entalpía (h)')
P_ENTRO = t_html('Entropia (s)', 'Entropy (s)', 'Entropía (s)')
P_TIT = t_html('Título (x)', 'Quality (x)', 'Calidad (x)')
P_CALOR = t_html('Calor transferido (Q)', 'Transferred heat (Q)', 'Calor transferido (Q)')

C_CV = t_html('Cv0', 'Cv0', 'Cv0')
C_CP = t_html('Cp0', 'Cp0', 'Cp0')
C_R = t_html('R', 'R', 'R')
C_K = t_html('K', 'K', 'K')


class Processos(forms.Form):
    PROCESSOS_CHOICES = [
        (100, t_html('Aquecimento/Resfriamento à pressão constante', 'Heating/Cooling at constant pressure', 'Calentamiento/Enfriamiento a presión constante')),
        (101, t_html('Aquecimento/Resfriamento à volume constante', 'Heating/Cooling at constant volume', 'Calentamiento/Enfriamiento a volumen constante')),
        (102, t_html('Compressão/Expansão adiabática e reversível', 'Reversible adiabatic compression/expansion', 'Compresión/Expansión adiabática y reversible')),
    ]

class PropertyForm(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PropertyForm3(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyForm3(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class TempForm(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class ThirdPropertyForm3(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
            (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PropertyIso(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyIso(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ThirdPropertyIso(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)


class PropertyForm5(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyForm5(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class TempForm2(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class ThirdPropertyForm5(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

###############################################################################################

class PropertyGasIdeal1(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
        (2, P_VOL)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyGasIdeal1(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP),
            (1, P_PRESS),
            (2, P_VOL),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class RGasIdeal1(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    R_value_input = forms.CharField(
        label=t_html("Digite o valor do R", "Enter the value of R", "Introduzca el valor de R"), 
        required=True
    )

###############################################################################################

class PropertyGasIdeal2(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
        (2, P_VOL)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyGasIdeal2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP),
            (1, P_PRESS),
            (2, P_VOL),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class RGasIdeal2(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    R_value_input = forms.CharField(
        label=t_html("Digite o valor do R", "Enter the value of R", "Introduzca el valor de R"), 
        required=True
    )

###############################################################################################

class ConstantesPCte8(forms.Form):
    PROPERTY_CHOICES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class ConstantesPCte8_2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            ('11', C_CV),
            ('12', C_CP),
            ('13', C_R),
            ('14', C_K)
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


class Prop1PCte8(forms.Form):
    """Primeira propriedade do Estado 1 (livre escolha entre T, p ou v)."""
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1PCte8_2(forms.Form):
    """Segunda propriedade do Estado 1 (exclui a já escolhida em Prop1PCte8)."""
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            ('0', P_TEMP),
            ('1', P_PRESS),
            ('2', P_VOL),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop2PCte8(forms.Form):

    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('2', P_VOL),
        ('8', P_CALOR),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class TvizGasIdeal8(forms.Form):
    Tviz_value_input = forms.FloatField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

###############################################################################################

class ConstantesVCte9(forms.Form):
    PROPERTY_CHOICES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class ConstantesVCte9_2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            ('11', C_CV),
            ('12', C_CP),
            ('13', C_R),
            ('14', C_K)
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1VCte9(forms.Form):
    """Primeira propriedade do Estado 1 (livre escolha entre T, p ou v)."""
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1VCte9_2(forms.Form):
    """Segunda propriedade do Estado 1 (exclui a já escolhida em Prop1VCte9)."""
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            ('0', P_TEMP),
            ('1', P_PRESS),
            ('2', P_VOL),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop2VCte9(forms.Form):
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('8', P_CALOR),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class TvizGasIdeal9(forms.Form):
    Tviz_value_input = forms.FloatField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

###############################################################################################

class ConstantesTCte10(forms.Form):
    PROPERTY_CHOICES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class ConstantesTCte10_2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            ('11', C_CV),
            ('12', C_CP),
            ('13', C_R),
            ('14', C_K)
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1TCte10(forms.Form):
    """Primeira propriedade do Estado 1 (livre escolha entre T, p ou v)."""
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1TCte10_2(forms.Form):
    """Segunda propriedade do Estado 1 (exclui a já escolhida em Prop1TCte10)."""
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            ('0', P_TEMP),
            ('1', P_PRESS),
            ('2', P_VOL),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop2TCte10(forms.Form):
    PROPERTY_CHOICES = [
        ('1', P_PRESS),
        ('2', P_VOL),
        ('8', P_CALOR),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class TvizGasIdeal10(forms.Form):
    Tviz_value_input = forms.FloatField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

###############################################################################################

class ConstantesPoli11(forms.Form):
    PROPERTY_CHOICES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class ConstantesPoli11_2(forms.Form):
    ALL_PROPERTIES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]

    def __init__(self, *args, excluded_properties=None, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_set = {str(x) for x in (excluded_properties or []) if x is not None}
        filtered_properties = [
            (num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_set
        ]
        if not filtered_properties:
            filtered_properties = self.ALL_PROPERTIES
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1Poli11(forms.Form):
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1Poli11_2(forms.Form):
    ALL_PROPERTIES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]

    def __init__(self, *args, excluded_properties=None, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_set = {str(x) for x in (excluded_properties or []) if x is not None}
        filtered_properties = [
            (num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_set
        ]
        if not filtered_properties:
            filtered_properties = self.ALL_PROPERTIES
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop2TCte11(forms.Form):
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
        ('8', P_CALOR),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class NGasIdeal11(forms.Form):
    N_value_input = forms.FloatField(
        label=t_html("Digite o valor de n", "Enter the value of n", "Introduzca el valor de n"), 
        required=True
    )

class TvizGasIdeal11(forms.Form):
    Tviz_value_input = forms.FloatField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

###############################################################################################

class ConstantesPoli12(forms.Form):
    PROPERTY_CHOICES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class ConstantesPoli12_2(forms.Form):
    ALL_PROPERTIES = [
        ('11', C_CV),
        ('12', C_CP),
        ('13', C_R),
        ('14', C_K)
    ]

    def __init__(self, *args, excluded_properties=None, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_set = {str(x) for x in (excluded_properties or []) if x is not None}
        filtered_properties = [
            (num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_set
        ]
        if not filtered_properties:
            filtered_properties = self.ALL_PROPERTIES
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1_12(forms.Form):
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop1_2_12(forms.Form):
    ALL_PROPERTIES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]

    def __init__(self, *args, excluded_properties=None, **kwargs):
        super().__init__(*args, **kwargs)
        excluded_set = {str(x) for x in (excluded_properties or []) if x is not None}
        filtered_properties = [
            (num, name) for num, name in self.ALL_PROPERTIES if num not in excluded_set
        ]
        if not filtered_properties:
            filtered_properties = self.ALL_PROPERTIES
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)

class Prop2_12(forms.Form):
    PROPERTY_CHOICES = [
        ('0', P_TEMP),
        ('1', P_PRESS),
        ('2', P_VOL),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.FloatField(label=LBL_DIGITE_VALOR, required=True)


# --- AMONIA ---

class PropertyFormAmoniaEst1(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyFormAmoniaEst1(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- AMONIA (P = cte) ---

class PcteAmonia(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteAmonia2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteAmonia3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class PcteAmonia4(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
            (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- AMONIA (S = cte) ---

class ScteAmonia(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteAmonia2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteAmonia3(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- AMONIA (v = cte) ---

class vcteAmonia(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteAmonia2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteAmonia3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class vcteAmonia4(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- CO2 ---

class PropertyFormCO2Est1(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyFormCO2Est1(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- CO2 (P = cte) ---

class PcteCO2(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteCO22(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteCO23(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class PcteCO24(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
            (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- CO2 (S = cte) ---

class ScteCO2(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteCO22(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteCO23(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- CO2 (v = cte) ---

class vcteCO2(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteCO22(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteCO23(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class vcteCO24(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R410A ---

class PropertyFormR410AEst1(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyFormR410AEst1(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R410A (P = cte) ---

class PcteR410A(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteR410A2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteR410A3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class PcteR410A4(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
            (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R410A (S = cte) ---

class ScteR410A(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteR410A2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteR410A3(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R410A (v = cte) ---

class vcteR410A(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteR410A2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteR410A3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class vcteR410A4(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R134A ---

class PropertyFormR134AEst1(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyFormR134AEst1(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R134A (P = cte) ---

class PcteR134A(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteR134A2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteR134A3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class PcteR134A4(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
            (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R134A (S = cte) ---

class ScteR134A(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteR134A2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteR134A3(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- R134A (v = cte) ---

class vcteR134A(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteR134A2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteR134A3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class vcteR134A4(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- Kelvin ---

class PropertyFormKelvinEst1(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class SecondPropertyFormKelvinEst1(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- Kelvin (P = cte) ---

class PcteKelvin(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteKelvin2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class PcteKelvin3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class PcteKelvin4(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (2, P_VOL), (3, P_ENER), (4, P_ENTAL),
            (5, P_ENTRO), (6, P_TIT), (8, P_CALOR),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- Kelvin (S = cte) ---

class ScteKelvin(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteKelvin2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class ScteKelvin3(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

# --- Kelvin (v = cte) ---

class vcteKelvin(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteKelvin2(forms.Form):
    def __init__(self, *args, **kwargs):
        excluded_properties = kwargs.pop('excluded_properties', [])
        super().__init__(*args, **kwargs)

        all_properties = [
            (0, P_TEMP), (1, P_PRESS), (2, P_VOL), (3, P_ENER),
            (4, P_ENTAL), (5, P_ENTRO), (6, P_TIT),
        ]
        filtered_properties = [(num, name) for num, name in all_properties if num not in excluded_properties]
        self.fields['property_choice'] = forms.ChoiceField(
            choices=filtered_properties,
            widget=forms.RadioSelect,
            label=LBL_SEL_OUTRA_PROP
        )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)

class vcteKelvin3(forms.Form):
    property_choice = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=7
    )
    value_input = forms.CharField(
        label=t_html("Digite o valor da Temperatura da Vizinhança", "Enter the Surroundings Temperature value", "Introduzca el valor de la Temperatura del Entorno"), 
        required=True
    )

class vcteKelvin4(forms.Form):
    PROPERTY_CHOICES = [
        (0, P_TEMP),
        (1, P_PRESS),
    ]
    property_choice = forms.ChoiceField(
        choices=PROPERTY_CHOICES,
        widget=forms.RadioSelect,
        label=LBL_SEL_PROP
    )
    value_input = forms.CharField(label=LBL_DIGITE_VALOR, required=True)
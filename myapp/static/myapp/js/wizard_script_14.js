function updateLabel() {
        var selectedRadio = document.querySelector('input[name="property_choice"]:checked');
        var inputField = document.getElementById('value_input_field');

        if (!selectedRadio) {
            inputField.style.display = 'none';
            return;
        }

        var labelElement = document.getElementById('value-label');
        var numberInput = document.getElementById('value_input');
        var selectedValue = selectedRadio.value;

        // Recupera o idioma salvo, padronizando o português se não houver
        var lang = localStorage.getItem('preferredLang') || 'pt-br';

        // Dicionário completo e traduzido de todas as propriedades suportadas
        var dict = {
            '0': { icon: 'fas fa-temperature-high', min: -250, max: 3000,
                   'pt-br': 'Digite o valor da Temperatura (°C):',
                   'en': 'Enter the Temperature value (°C):',
                   'es': 'Ingrese el valor de la Temperatura (°C):' },
            '1': { icon: 'fas fa-tachometer-alt', min: 0.1, max: 50000,
                   'pt-br': 'Digite o valor da Pressão (kPa):',
                   'en': 'Enter the Pressure value (kPa):',
                   'es': 'Ingrese el valor de la Presión (kPa):' },
            '2': { icon: 'fas fa-cube', min: 0.0001, max: 1000,
                   'pt-br': 'Digite o valor do Volume Específico (m³/kg):',
                   'en': 'Enter the Specific Volume value (m³/kg):',
                   'es': 'Ingrese el valor del Volumen Específico (m³/kg):' },
            '3': { icon: 'fas fa-bolt', min: 0, max: 10000,
                   'pt-br': 'Digite o valor da Energia Interna (kJ/kg):',
                   'en': 'Enter the Internal Energy value (kJ/kg):',
                   'es': 'Ingrese el valor de la Energía Interna (kJ/kg):' },
            '4': { icon: 'fas fa-fire', min: 0, max: 10000,
                   'pt-br': 'Digite o valor da Entalpia (kJ/kg):',
                   'en': 'Enter the Enthalpy value (kJ/kg):',
                   'es': 'Ingrese el valor de la Entalpía (kJ/kg):' },
            '5': { icon: 'fas fa-random', min: 0, max: 100,
                   'pt-br': 'Digite o valor da Entropia (kJ/kg·K):',
                   'en': 'Enter the Entropy value (kJ/kg·K):',
                   'es': 'Ingrese el valor de la Entropía (kJ/kg·K):' },
            '6': { icon: 'fas fa-percentage', min: 0, max: 100,
                   'pt-br': 'Digite o valor do Título (%):',
                   'en': 'Enter the Quality value (%):',
                   'es': 'Ingrese el valor del Título (%):' },
            '8': { icon: 'fas fa-fire-alt', min: -100000, max: 100000,
                   'pt-br': 'Digite o valor do Calor Transferido (kJ):',
                   'en': 'Enter the Transferred Heat value (kJ):',
                   'es': 'Ingrese el valor del Calor Transferido (kJ):' },
            '11': { icon: 'fas fa-compress-arrows-alt', min: 0.1, max: 15,
                    'pt-br': 'Digite o valor de Cv0 (kJ/(kg·K)):',
                    'en': 'Enter the Cv0 value (kJ/(kg·K)):',
                    'es': 'Ingrese el valor de Cv0 (kJ/(kg·K)):' },
            '12': { icon: 'fas fa-expand-arrows-alt', min: 0.1, max: 20,
                    'pt-br': 'Digite o valor de Cp0 (kJ/(kg·K)):',
                    'en': 'Enter the Cp0 value (kJ/(kg·K)):',
                    'es': 'Ingrese el valor de Cp0 (kJ/(kg·K)):' },
            '13': { icon: 'fas fa-registered', min: 0.05, max: 5,
                    'pt-br': 'Digite o valor de R (kJ/(kg·K)):',
                    'en': 'Enter the R value (kJ/(kg·K)):',
                    'es': 'Ingrese el valor de R (kJ/(kg·K)):' },
            '14': { icon: 'fas fa-divide', min: 1.01, max: 2.0,
                    'pt-br': 'Digite o valor de K:',
                    'en': 'Enter the K value:',
                    'es': 'Ingrese el valor de K:' }
        };

        var placeholders = {
            'pt-br': 'Digite o valor',
            'en': 'Enter the value',
            'es': 'Ingrese el valor'
        };

        var propInfo = dict[selectedValue];

        if (propInfo) {
            labelElement.innerHTML = `<i class="${propInfo.icon}"></i> ${propInfo[lang]}`;
            numberInput.setAttribute('min', propInfo.min);
            numberInput.setAttribute('max', propInfo.max);
        } else {
            // Fallback de segurança
            var fallback = {
                'pt-br': 'Digite o valor da propriedade selecionada:',
                'en': 'Enter the value of the selected property:',
                'es': 'Ingrese el valor de la propiedad seleccionada:'
            };
            labelElement.innerHTML = `<i class="fas fa-pen"></i> ${fallback[lang]}`;
            numberInput.removeAttribute('min');
            numberInput.removeAttribute('max');
        }

        numberInput.placeholder = placeholders[lang];
        inputField.style.display = 'block';
    }

    document.addEventListener('DOMContentLoaded', function() {
        var radios = document.querySelectorAll('input[name="property_choice"]');
        radios.forEach(function(radio) {
            radio.addEventListener('change', updateLabel);
        });
        
        // Executa na carga inicial da página
        updateLabel();

        // Atualiza os inputs dinâmicos se o usuário trocar a língua com um rádio já selecionado
        var langOptions = document.querySelectorAll('.lang-option');
        langOptions.forEach(function(btn) {
            btn.addEventListener('click', function() {
                setTimeout(updateLabel, 50); // Aguarda o localStorage atualizar no script do base.html
            });
        });
    });

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

        // Dicionário completo e traduzido
        var dict = {
            '0': { icon: 'fas fa-temperature-high', min: -250, max: 3000,
                   'pt-br': 'Digite o valor da Temperatura (°C):',
                   'en': 'Enter the Temperature value (°C):',
                   'es': 'Ingrese el valor de la Temperatura (°C):',
                   'fr': 'Entrez la valeur de la Température (°C) :' },
            '1': { icon: 'fas fa-tachometer-alt', min: 0.1, max: 50000,
                   'pt-br': 'Digite o valor da Pressão (kPa):',
                   'en': 'Enter the Pressure value (kPa):',
                   'es': 'Ingrese el valor de la Presión (kPa):',
                   'fr': 'Entrez la valeur de la Pression (kPa) :' },
            '2': { icon: 'fas fa-cube', min: 0.0001, max: 1000,
                   'pt-br': 'Digite o valor do Volume (m³/kg):',
                   'en': 'Enter the Volume value (m³/kg):',
                   'es': 'Ingrese el valor del Volumen (m³/kg):',
                   'fr': 'Entrez la valeur du Volume (m³/kg) :' }
        };

        var placeholders = {
            'pt-br': 'Digite o valor',
            'en': 'Enter the value',
            'es': 'Ingrese el valor',
            'fr': 'Entrez la valeur'
        };

        var propInfo = dict[selectedValue];

        if (propInfo) {
            labelElement.innerHTML = `<i class="${propInfo.icon}"></i> ${(propInfo[lang] || propInfo['en'] || propInfo['pt-br'])}`;
            numberInput.setAttribute('min', propInfo.min);
            numberInput.setAttribute('max', propInfo.max);
        } else {
            // Fallback de segurança para propriedades não mapeadas acima
            var fallback = {
                'pt-br': 'Digite o valor da propriedade selecionada:',
                'en': 'Enter the value of the selected property:',
                'es': 'Ingrese el valor de la propiedad seleccionada:',
                'fr': 'Entrez la valeur de la propriété sélectionnée :'
            };
            labelElement.innerHTML = `<i class="fas fa-pen"></i> ${(fallback[lang] || fallback['en'] || fallback['pt-br'])}`;
            numberInput.removeAttribute('min');
            numberInput.removeAttribute('max');
        }

        numberInput.placeholder = (placeholders[lang] || placeholders['en'] || placeholders['pt-br']);
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
                setTimeout(updateLabel, 50); // Aguarda o localStorage atualizar
            });
        });
    });

function updateLabel() {
        var selectedRadio = document.querySelector('input[name="property_choice"]:checked');
        if (!selectedRadio) {
            document.getElementById('value_input_field').style.display = 'none';
            return;
        }

        var selectedValue = selectedRadio.value;
        var label = document.getElementById('value-label');
        var inputField = document.getElementById('value_input_field');
        var numberInput = document.getElementById('value_input');

        let currentLang = localStorage.getItem('preferredLang') || 'pt-br';

        let phStr = {
            'pt-br': 'Digite o valor',
            'en': 'Enter the value',
            'es': 'Introduzca el valor'
        };

        // Mapeamento expandido adaptado para o sistema de idiomas dinâmico
        var info = {
            '0': { icon: 'fas fa-temperature-high', min: 90.7, max: 575.0, 
                pt: 'Digite o valor da Temperatura (K)', en: 'Enter the Temperature value (K)', es: 'Introduzca el valor de la Temperatura (K)'},
            '1': { icon: 'fas fa-tachometer-alt', min: 11.7, max: 8000, 
                pt: 'Digite o valor da Pressão (kPa)', en: 'Enter the Pressure value (kPa)', es: 'Introduzca el valor de la Presión (kPa)'},
            '2': { icon: 'fas fa-cube', min: 0.002215, max: 3.98163, 
                pt: 'Digite o valor do Volume Específico (m³/kg)', en: 'Enter the Specific Volume value (m³/kg)', es: 'Introduzca el valor del Volumen Específico (m³/kg)'},
            '3': { icon: 'fas fa-bolt', min: -358.1, max: 1053.98, 
                pt: 'Digite o valor da Energia Interna (kJ/kg)', en: 'Enter the Internal Energy value (kJ/kg)', es: 'Introduzca el valor de la Energía Interna (kJ/kg)'},
            '4': { icon: 'fas fa-fire', min: -358.07, max: 1353.77, 
                pt: 'Digite o valor da Entalpia (kJ/kg)', en: 'Enter the Enthalpy value (kJ/kg)', es: 'Introduzca el valor de la Entalpía (kJ/kg)'},
            '5': { icon: 'fas fa-random', min: 4.2264, max: 12.4661, 
                pt: 'Digite o valor da Entropia (kJ/kg·K)', en: 'Enter the Entropy value (kJ/kg·K)', es: 'Introduzca el valor de la Entropía (kJ/kg·K)'},
            '6': { icon: 'fas fa-percentage', min: 0, max: 100, 
                pt: 'Digite o valor do Título (%)', en: 'Enter the Quality value (%)', es: 'Introduzca el valor del Título (%)'}
        };

        var prop = info[selectedValue];

        if (prop) {
            label.innerHTML = `<i class="${prop.icon}"></i> <span class="lang-text" data-pt-br="${prop.pt}" data-en="${prop.en}" data-es="${prop.es}">${prop.pt}</span>`;
            numberInput.setAttribute('min', prop.min);
            numberInput.setAttribute('max', prop.max);
        } else {
            // Comportamento padrão de segurança
            label.innerHTML = `<i class="fas fa-pencil-alt"></i> <span class="lang-text" data-pt-br="Digite o valor da propriedade selecionada:" data-en="Enter the selected property value:" data-es="Introduzca el valor de la propiedad seleccionada:">Digite o valor da propriedade selecionada:</span>`;
            numberInput.removeAttribute('min');
            numberInput.removeAttribute('max');
        }

        numberInput.placeholder = phStr[currentLang];
        inputField.style.display = 'block';

        // Dispara a tradução para formatar o label que acabou de ser injetado (caso não esteja em pt-br)
        if(currentLang !== 'pt-br') {
             const elements = document.querySelectorAll('.lang-text');
             elements.forEach(el => {
                 const newText = el.getAttribute('data-' + currentLang);
                 if (newText) el.textContent = newText;
             });
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        var radios = document.querySelectorAll('input[name="property_choice"]');
        radios.forEach(function(radio) {
            radio.addEventListener('change', updateLabel);
        });
        updateLabel();

        // Escuta cliques no idioma para atualizar o placeholder dinamicamente
        document.addEventListener('click', function(e) {
            if (e.target.closest('.lang-option')) {
                setTimeout(updateLabel, 50);
            }
        });
    });

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

        // Pega o idioma selecionado no navegador (definido no base.html)
        var lang = localStorage.getItem('preferredLang') || 'pt-br';

        // Definição das constantes e seus limites
        var info = {
            '11': { text: 'Cv0', min: 0.1, max: 15 },
            '12': { text: 'Cp0', min: 0.1, max: 20 },
            '13': { text: 'R', min: 0.05, max: 5 },
            '14': { text: 'K', min: 1.01, max: 2.0 }
        };

        // Dicionário de traduções dinâmicas para o JavaScript
        var dict = {
            'pt-br': { label: 'Digite o valor de', placeholder: 'Digite o valor' },
            'en': { label: 'Enter the value for', placeholder: 'Enter the value' },
            'es': { label: 'Ingrese el valor de', placeholder: 'Ingrese el valor' },
            'fr': { label: 'Entrez la valeur de', placeholder: 'Entrez la valeur' }
        };

        if (info[selectedValue]) {
            // Atualiza o texto mesclando o dicionário de idioma com o nome da constante
            label.innerHTML = `<i class="fas fa-ruler-combined"></i> ${(dict[lang] || dict['en'] || dict['pt-br']).label} ${info[selectedValue].text}`;
            numberInput.setAttribute('min', info[selectedValue].min);
            numberInput.setAttribute('max', info[selectedValue].max);
            numberInput.placeholder = (dict[lang] || dict['en'] || dict['pt-br']).placeholder;
            inputField.style.display = 'block';
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Escuta os cliques nas opções de rádio
        var radios = document.querySelectorAll('input[name="property_choice"]');
        radios.forEach(function(radio) {
            radio.addEventListener('change', updateLabel);
        });

        // Atualiza os inputs dinâmicos se o usuário trocar a língua com um rádio já selecionado
        var langOptions = document.querySelectorAll('.lang-option');
        langOptions.forEach(function(btn) {
            btn.addEventListener('click', function() {
                setTimeout(updateLabel, 50); // Aguarda o localStorage atualizar no base.html
            });
        });
    });

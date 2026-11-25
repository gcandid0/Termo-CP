function updateLabel() {
        var selectedRadio = document.querySelector('input[name="property_choice"]:checked');
        if (!selectedRadio) return;

        var selectedValue = selectedRadio.value;
        var label = document.getElementById('value-label');
        var inputField = document.getElementById('value_input_field');
        var numberInput = document.getElementById('value_input');

        // Pega o idioma salvo no localStorage
        let currentLang = localStorage.getItem('preferredLang') || 'pt-br';

        // Dicionários para Placeholders
        let phStr = {
            'pt-br': 'Digite o valor',
            'en': 'Enter the value',
            'es': 'Introduzca el valor',
            'fr': 'Entrez la valeur',
            'zh': '输入数值'
        };

        // Lógica de Label e Limites, injetando as classes .lang-text para funcionar com o seu base.html
        if (selectedValue == '0') {
            label.innerHTML = '<i class="fas fa-temperature-high"></i> ' +
                              '<span class="lang-text" ' +
                              'data-pt-br="Digite o valor da Temperatura (°C)" ' +
                              'data-en="Enter the Temperature value (°C)" ' +
                              'data-es="Introduzca el valor de la Temperatura (°C)">' +
                              'Digite o valor da Temperatura (°C)</span>';
            
            numberInput.setAttribute('min', '0');
            numberInput.setAttribute('max', '1300');
            numberInput.placeholder = (phStr[currentLang] || phStr['en'] || phStr['pt-br']);

        } else if (selectedValue == '1') {
            label.innerHTML = '<i class="fas fa-tachometer-alt"></i> ' +
                              '<span class="lang-text" ' +
                              'data-pt-br="Digite o valor da Pressão (kPa)" ' +
                              'data-en="Enter the Pressure value (kPa)" ' +
                              'data-es="Introduzca el valor de la Presión (kPa)">' +
                              'Digite o valor da Pressão (kPa)</span>';
            
            numberInput.setAttribute('min', '0.6113');
            numberInput.setAttribute('max', '50000');
            numberInput.placeholder = (phStr[currentLang] || phStr['en'] || phStr['pt-br']);
        }

        inputField.style.display = 'block';

        // Dispara a tradução novamente para formatar o label que acabou de ser injetado (caso não esteja em pt-br)
        if(currentLang !== 'pt-br') {
             // Reutiliza os nós do lang-text e traduz sem mover o slider (pq ja está no lugar)
             const elements = document.querySelectorAll('.lang-text');
             elements.forEach(el => {
                 const newText = el.getAttribute('data-' + currentLang) || (currentLang !== 'pt-br' ? el.getAttribute('data-en') : null);
                 if (newText) el.textContent = newText;
             });
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Escuta as trocas de rádio
        var radios = document.querySelectorAll('input[name="property_choice"]');
        radios.forEach(function(radio) {
            radio.addEventListener('change', updateLabel);
        });

        // Escuta cliques na opção de idioma para atualizar o placeholder dinamicamente se o input estiver aberto
        document.addEventListener('click', function(e) {
            if (e.target.closest('.lang-option')) {
                setTimeout(updateLabel, 50); // Recalcula os placeholders e labels de acordo com o novo idioma
            }
        });
    });

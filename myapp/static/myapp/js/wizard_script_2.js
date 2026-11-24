function updatePlaceholder() {
        let currentLang = localStorage.getItem('preferredLang') || 'pt-br';
        let numberInput = document.getElementById('value_input');

        let phStr = {
            'pt-br': 'Digite o valor',
            'en': 'Enter the value',
            'es': 'Introduzca el valor'
        };

        if(numberInput) {
            numberInput.placeholder = phStr[currentLang] || phStr['pt-br'];
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Atualiza no carregamento da página
        updatePlaceholder();

        // Escuta os cliques nas bandeiras para atualizar o placeholder dinamicamente
        document.addEventListener('click', function(e) {
            if (e.target.closest('.lang-option')) {
                // Pequeno delay para garantir que a língua já foi atualizada no localStorage
                setTimeout(updatePlaceholder, 50);
            }
        });
    });

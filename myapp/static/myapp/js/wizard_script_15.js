function updatePlaceholder() {
        var input = document.getElementById('Tviz_value_input');
        var lang = localStorage.getItem('preferredLang') || 'pt-br';
        
        var placeholders = {
            'pt-br': 'Digite o valor',
            'en': 'Enter the value',
            'es': 'Ingrese el valor',
            'fr': 'Entrez la valeur',
            'zh': '输入数值'
        };
        
        if(input) {
            input.placeholder = (placeholders[lang] || placeholders['en'] || placeholders['pt-br']);
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        // Inicializa o placeholder com a linguagem correta
        updatePlaceholder();

        // Atualiza o placeholder automaticamente se o usuário trocar de idioma pelo header
        var langOptions = document.querySelectorAll('.lang-option');
        langOptions.forEach(function(btn) {
            btn.addEventListener('click', function() {
                setTimeout(updatePlaceholder, 50); // Dá um tempinho pro localStorage atualizar no script do base.html
            });
        });
    });

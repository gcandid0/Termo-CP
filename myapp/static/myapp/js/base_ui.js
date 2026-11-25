// Limpa qualquer preferência residual de tema
try {
    localStorage.removeItem('thermo_theme');
    document.documentElement.removeAttribute('data-theme');
} catch (e) {}

// Reinicia o histórico de comparação de cálculos sempre que qualquer
        // botão/link do cabeçalho (nav) for clicado, antes de navegar para a página.
        document.addEventListener("DOMContentLoaded", function() {
            document.querySelectorAll('header nav a').forEach(function(link) {
                link.addEventListener('click', function() {
                    localStorage.removeItem('thermoCalcHistory_v1');
                });
            });
        });

        // Executa assim que o HTML da página (incluindo o que vem do block content) estiver carregado
        document.addEventListener("DOMContentLoaded", function() {
            // Busca se o usuário já escolheu um idioma antes. Se não, o padrão é 'pt-br'
            let savedLang = localStorage.getItem('preferredLang') || 'pt-br';

            // Define o índice da bolinha branca baseado no idioma salvo
            let index = 0;
            if (savedLang === 'en') index = 1;
            if (savedLang === 'es') index = 2;
            if (savedLang === 'fr') index = 3;
            if (savedLang === 'zh') index = 4;

            // Aplica a tradução e posiciona a bolinha imediatamente
            changeLanguage(index, savedLang);
        });

        // Função chamada quando você clica numa bandeira
        function changeLanguage(index, langCode) {
            // 1. Move a bolinha
            const slider = document.getElementById('lang-slider');
            if(slider) {
                slider.style.transform = `translateX(${index * 100}%)`;
            }

            // 2. Salva a preferência no navegador do usuário
            localStorage.setItem('preferredLang', langCode);

            // 3. Pega todos os elementos que têm a classe 'lang-text' na tela
            const elements = document.querySelectorAll('.lang-text');

            // 4. Para cada elemento, pega o texto correspondente ao idioma e substitui
            elements.forEach(el => {
                const newText = el.getAttribute('data-' + langCode) || (langCode !== 'pt-br' ? el.getAttribute('data-en') : null);
                if (newText) {
                    el.textContent = newText;
                }
            });

            // Dispara evento global para gráficos/componentes filhos
            document.dispatchEvent(new CustomEvent("languageChanged", { detail: { language: langCode } }));

            // 5. Elementos com listas/HTML interno (ex: passos de ajuda) usam 'lang-html',
            // que substitui o conteúdo via innerHTML em vez de texto puro
            const htmlElements = document.querySelectorAll('.lang-html');
            htmlElements.forEach(el => {
                const newHtml = el.getAttribute('data-' + langCode) || (langCode !== 'pt-br' ? el.getAttribute('data-en') : null);
                if (newHtml) {
                    el.innerHTML = newHtml;
                }
            });
        }

// Abre/fecha o modal de ajuda contextual de cada página
        document.addEventListener('DOMContentLoaded', function() {
            var btn = document.getElementById('page-help-btn');
            var overlay = document.getElementById('page-help-overlay');
            var closeBtn = document.getElementById('page-help-close');

            function openHelp() { overlay.classList.add('open'); }
            function closeHelp() { overlay.classList.remove('open'); }

            if (btn) btn.addEventListener('click', openHelp);
            if (closeBtn) closeBtn.addEventListener('click', closeHelp);
            if (overlay) {
                overlay.addEventListener('click', function(e) {
                    if (e.target === overlay) closeHelp();
                });
            }
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape') closeHelp();
            });
        });

// ============ TOUR GUIADO DOS BOTÕES (BALÃO + TELA ESCURA) ============
        document.addEventListener('DOMContentLoaded', function () {
            var overlay = document.getElementById('page-tour-overlay');
            var dim = document.getElementById('page-tour-dim');
            var highlightBox = document.getElementById('tour-highlight-box');
            var balloon = document.getElementById('tour-balloon');
            var arrow = document.getElementById('tour-arrow');
            var titleText = document.getElementById('tour-balloon-title-text');
            var bodyText = document.getElementById('tour-balloon-text');
            var stepCount = document.getElementById('tour-step-count');
            var prevBtn = document.getElementById('tour-prev-btn');
            var nextBtn = document.getElementById('tour-next-btn');
            var closeBtn = document.getElementById('tour-close-btn');
            var triggerBtn = document.getElementById('page-tour-trigger');
            var helpOverlay = document.getElementById('page-help-overlay');

            var steps = [];
            var currentStep = 0;

            // Descrições de "o que o botão faz", por id do elemento (prioridade)
            // e, em seguida, pelo texto do rótulo (fallback), nos 3 idiomas.
            var descById = {
                'btnDidactic': { 'pt-br': 'Mostra o memorial de cálculo: o passo a passo e as fórmulas usadas para chegar ao resultado.', 'en': 'Shows the calculation memorial: the step-by-step and formulas used to reach the result.', 'es': 'Muestra la memoria de cálculo: el paso a paso y las fórmulas usadas para llegar al resultado.' },
                'btnCurrentDiagram': { 'pt-br': 'Abre o diagrama termodinâmico (T-s, P-v, etc.) do processo calculado.', 'en': 'Opens the thermodynamic diagram (T-s, P-v, etc.) of the calculated process.', 'es': 'Abre el diagrama termodinámico (T-s, P-v, etc.) del proceso calculado.' },
                'btnFinalReport': { 'pt-br': 'Gera um relatório final com os resultados, pronto para exportar como imagem.', 'en': 'Generates a final report with the results, ready to export as an image.', 'es': 'Genera un informe final con los resultados, listo para exportar como imagen.' },
                'btnHistory': { 'pt-br': 'Mostra o histórico dos cálculos feitos nesta sessão, para comparar resultados.', 'en': 'Shows the history of calculations made in this session, to compare results.', 'es': 'Muestra el historial de los cálculos hechos en esta sesión, para comparar resultados.' },
                'openModalBtn': { 'pt-br': 'Avança para a próxima etapa, informando o segundo estado do processo.', 'en': 'Moves to the next step, entering the second state of the process.', 'es': 'Avanza a la siguiente etapa, ingresando el segundo estado del proceso.' },
                'page-help-btn': { 'pt-br': 'Abre a ajuda contextual desta página.', 'en': 'Opens the contextual help for this page.', 'es': 'Abre la ayuda contextual de esta página.' },
                'btnToggleFullCycle': { 'pt-br': 'Alterna entre ver só este processo e ver todos os processos do ciclo juntos no diagrama.', 'en': 'Switches between showing only this process and all the cycle processes together on the diagram.', 'es': 'Alterna entre ver solo este proceso y todos los procesos del ciclo juntos en el diagrama.' },
                'btnCompareSelected': { 'pt-br': 'Compara lado a lado os cálculos marcados no histórico.', 'en': 'Compares side by side the calculations ticked in the history.', 'es': 'Compara lado a lado los cálculos marcados en el historial.' },
                'btnClearHistory': { 'pt-br': 'Apaga todos os cálculos guardados no histórico desta sessão.', 'en': "Deletes all calculations stored in this session's history.", 'es': 'Borra todos los cálculos guardados en el historial de esta sesión.' },
                'btnStateDiagram': { 'pt-br': 'Abre o diagrama termodinâmico do estado calculado.', 'en': 'Opens the thermodynamic diagram of the calculated state.', 'es': 'Abre el diagrama termodinámico del estado calculado.' },
                'volumeSlider': { 'pt-br': 'Arraste para ver como o pistão e o volume do cilindro mudam entre o estado inicial e o final.', 'en': 'Drag to see how the piston and cylinder volume change between the initial and final states.', 'es': 'Arrastre para ver cómo cambian el pistón y el volumen del cilindro entre el estado inicial y el final.' },
                'chartTypeSelector': { 'pt-br': 'Escolhe o par de propriedades (P-v, T-s, h-s…) em que o processo é desenhado.', 'en': 'Chooses the property pair (P-v, T-s, h-s…) in which the process is drawn.', 'es': 'Elige el par de propiedades (P-v, T-s, h-s…) en que se dibuja el proceso.' }
            };

            var descByLabel = {
                'imprimir': { 'pt-br': 'Imprime (ou salva em PDF) a tela de resultados.', 'en': 'Prints (or saves as PDF) the results screen.', 'es': 'Imprime (o guarda en PDF) la pantalla de resultados.' },
                'print': { 'pt-br': 'Imprime (ou salva em PDF) a tela de resultados.', 'en': 'Prints (or saves as PDF) the results screen.', 'es': 'Imprime (o guarda en PDF) la pantalla de resultados.' },
                'voltar': { 'pt-br': 'Volta para a etapa anterior, sem perder os dados já informados.', 'en': 'Goes back to the previous step, without losing the data already entered.', 'es': 'Vuelve a la etapa anterior, sin perder los datos ya ingresados.' },
                'go back': { 'pt-br': 'Volta para a etapa anterior, sem perder os dados já informados.', 'en': 'Goes back to the previous step, without losing the data already entered.', 'es': 'Vuelve a la etapa anterior, sin perder los datos ya ingresados.' },
                'volver': { 'pt-br': 'Volta para a etapa anterior, sem perder os dados já informados.', 'en': 'Goes back to the previous step, without losing the data already entered.', 'es': 'Vuelve a la etapa anterior, sin perder los datos ya ingresados.' },
                'novo cálculo': { 'pt-br': 'Limpa os campos e inicia um novo cálculo do zero.', 'en': 'Clears the fields and starts a new calculation from scratch.', 'es': 'Limpia los campos e inicia un nuevo cálculo desde cero.' },
                'new calculation': { 'pt-br': 'Limpa os campos e inicia um novo cálculo do zero.', 'en': 'Clears the fields and starts a new calculation from scratch.', 'es': 'Limpia los campos e inicia un nuevo cálculo desde cero.' },
                'nuevo cálculo': { 'pt-br': 'Limpa os campos e inicia um novo cálculo do zero.', 'en': 'Clears the fields and starts a new calculation from scratch.', 'es': 'Limpia los campos e inicia un nuevo cálculo desde cero.' },
                'continuar': { 'pt-br': 'Envia os dados informados e avança para a próxima tela.', 'en': 'Submits the entered data and moves to the next screen.', 'es': 'Envía los datos ingresados y avanza a la siguiente pantalla.' },
                'continue': { 'pt-br': 'Envia os dados informados e avança para a próxima tela.', 'en': 'Submits the entered data and moves to the next screen.', 'es': 'Envía los datos ingresados y avanza a la siguiente pantalla.' },
                'tela inicial': { 'pt-br': 'Volta para a tela inicial do TERMO-CP.', 'en': 'Returns to the TERMO-CP home screen.', 'es': 'Vuelve a la pantalla de inicio de TERMO-CP.' },
                'home screen': { 'pt-br': 'Volta para a tela inicial do TERMO-CP.', 'en': 'Returns to the TERMO-CP home screen.', 'es': 'Vuelve a la pantalla de inicio de TERMO-CP.' },
                'pantalla de inicio': { 'pt-br': 'Volta para a tela inicial do TERMO-CP.', 'en': 'Returns to the TERMO-CP home screen.', 'es': 'Vuelve a la pantalla de inicio de TERMO-CP.' },
                'calcular': { 'pt-br': 'Calcula as propriedades a partir dos valores informados.', 'en': 'Calculates the properties from the entered values.', 'es': 'Calcula las propiedades a partir de los valores ingresados.' },

                // ---- Resultados calculados (linhas de dados dos estados e do processo) ----
                'fase:': { 'pt-br': 'Indica o estado físico da substância no ponto calculado: líquido comprimido, mistura saturada (líquido+vapor) ou vapor superaquecido.', 'en': 'Indicates the physical state of the substance at the calculated point: compressed liquid, saturated mixture (liquid+vapor) or superheated vapor.', 'es': 'Indica el estado físico de la sustancia en el punto calculado: líquido comprimido, mezcla saturada (líquido+vapor) o vapor sobrecalentado.' },
                'phase:': { 'pt-br': 'Indica o estado físico da substância no ponto calculado: líquido comprimido, mistura saturada (líquido+vapor) ou vapor superaquecido.', 'en': 'Indicates the physical state of the substance at the calculated point: compressed liquid, saturated mixture (liquid+vapor) or superheated vapor.', 'es': 'Indica el estado físico de la sustancia en el punto calculado: líquido comprimido, mezcla saturada (líquido+vapor) o vapor sobrecalentado.' },
                'massa (m):': { 'pt-br': 'Massa da substância considerada no cálculo.', 'en': 'Mass of the substance used in the calculation.', 'es': 'Masa de la sustancia considerada en el cálculo.' },
                'mass (m):': { 'pt-br': 'Massa da substância considerada no cálculo.', 'en': 'Mass of the substance used in the calculation.', 'es': 'Masa de la sustancia considerada en el cálculo.' },
                'masa (m):': { 'pt-br': 'Massa da substância considerada no cálculo.', 'en': 'Mass of the substance used in the calculation.', 'es': 'Masa de la sustancia considerada en el cálculo.' },
                'temperatura (t):': { 'pt-br': 'Temperatura da substância neste estado.', 'en': 'Temperature of the substance at this state.', 'es': 'Temperatura de la sustancia en este estado.' },
                'temperature (t):': { 'pt-br': 'Temperatura da substância neste estado.', 'en': 'Temperature of the substance at this state.', 'es': 'Temperatura de la sustancia en este estado.' },
                'pressão (p):': { 'pt-br': 'Pressão da substância neste estado.', 'en': 'Pressure of the substance at this state.', 'es': 'Presión de la sustancia en este estado.' },
                'pressure (p):': { 'pt-br': 'Pressão da substância neste estado.', 'en': 'Pressure of the substance at this state.', 'es': 'Presión de la sustancia en este estado.' },
                'presión (p):': { 'pt-br': 'Pressão da substância neste estado.', 'en': 'Pressure of the substance at this state.', 'es': 'Presión de la sustancia en este estado.' },
                'volume específico (v):': { 'pt-br': 'Volume ocupado pela substância por unidade de massa.', 'en': 'Volume occupied by the substance per unit of mass.', 'es': 'Volumen ocupado por la sustancia por unidad de masa.' },
                'specific volume (v):': { 'pt-br': 'Volume ocupado pela substância por unidade de massa.', 'en': 'Volume occupied by the substance per unit of mass.', 'es': 'Volumen ocupado por la sustancia por unidad de masa.' },
                'volumen específico (v):': { 'pt-br': 'Volume ocupado pela substância por unidade de massa.', 'en': 'Volume occupied by the substance per unit of mass.', 'es': 'Volumen ocupado por la sustancia por unidad de masa.' },
                'energia interna (u):': { 'pt-br': 'Energia associada ao movimento e às interações das moléculas da substância.', 'en': 'Energy associated with the motion and interactions of the substance\'s molecules.', 'es': 'Energía asociada al movimiento e interacciones de las moléculas de la sustancia.' },
                'internal energy (u):': { 'pt-br': 'Energia associada ao movimento e às interações das moléculas da substância.', 'en': 'Energy associated with the motion and interactions of the substance\'s molecules.', 'es': 'Energía asociada al movimiento e interacciones de las moléculas de la sustancia.' },
                'energía interna (u):': { 'pt-br': 'Energia associada ao movimento e às interações das moléculas da substância.', 'en': 'Energy associated with the motion and interactions of the substance\'s molecules.', 'es': 'Energía asociada al movimiento e interacciones de las moléculas de la sustancia.' },
                'entalpia (h):': { 'pt-br': 'Soma da energia interna com o produto pressão-volume (h = u + p·v); muito usada em processos com escoamento.', 'en': 'Sum of the internal energy and the pressure-volume product (h = u + p·v); widely used in flow processes.', 'es': 'Suma de la energía interna con el producto presión-volumen (h = u + p·v); muy usada en procesos con flujo.' },
                'enthalpy (h):': { 'pt-br': 'Soma da energia interna com o produto pressão-volume (h = u + p·v); muito usada em processos com escoamento.', 'en': 'Sum of the internal energy and the pressure-volume product (h = u + p·v); widely used in flow processes.', 'es': 'Suma de la energía interna con el producto presión-volumen (h = u + p·v); muy usada en procesos con flujo.' },
                'entalpía (h):': { 'pt-br': 'Soma da energia interna com o produto pressão-volume (h = u + p·v); muito usada em processos com escoamento.', 'en': 'Sum of the internal energy and the pressure-volume product (h = u + p·v); widely used in flow processes.', 'es': 'Suma de la energía interna con el producto presión-volumen (h = u + p·v); muy usada en procesos con flujo.' },
                'entropia (s):': { 'pt-br': 'Medida da desordem molecular e da irreversibilidade associada ao estado da substância.', 'en': 'Measure of molecular disorder and the irreversibility associated with the substance\'s state.', 'es': 'Medida del desorden molecular y de la irreversibilidad asociada al estado de la sustancia.' },
                'entropy (s):': { 'pt-br': 'Medida da desordem molecular e da irreversibilidade associada ao estado da substância.', 'en': 'Measure of molecular disorder and the irreversibility associated with the substance\'s state.', 'es': 'Medida del desorden molecular y de la irreversibilidad asociada al estado de la sustancia.' },
                'entropía (s):': { 'pt-br': 'Medida da desordem molecular e da irreversibilidade associada ao estado da substância.', 'en': 'Measure of molecular disorder and the irreversibility associated with the substance\'s state.', 'es': 'Medida del desorden molecular y de la irreversibilidad asociada al estado de la sustancia.' },
                'título (x):': { 'pt-br': 'Fração de vapor presente na mistura líquido-vapor saturada (0% = líquido saturado, 100% = vapor saturado).', 'en': 'Fraction of vapor present in the saturated liquid-vapor mixture (0% = saturated liquid, 100% = saturated vapor).', 'es': 'Fracción de vapor presente en la mezcla líquido-vapor saturada (0% = líquido saturado, 100% = vapor saturado).' },
                'quality (x):': { 'pt-br': 'Fração de vapor presente na mistura líquido-vapor saturada (0% = líquido saturado, 100% = vapor saturado).', 'en': 'Fraction of vapor present in the saturated liquid-vapor mixture (0% = saturated liquid, 100% = saturated vapor).', 'es': 'Fracción de vapor presente en la mezcla líquido-vapor saturada (0% = líquido saturado, 100% = vapor saturado).' },
                'calidad (x):': { 'pt-br': 'Fração de vapor presente na mistura líquido-vapor saturada (0% = líquido saturado, 100% = vapor saturado).', 'en': 'Fraction of vapor present in the saturated liquid-vapor mixture (0% = saturated liquid, 100% = saturated vapor).', 'es': 'Fracción de vapor presente en la mezcla líquido-vapor saturada (0% = líquido saturado, 100% = vapor saturado).' },
                'volume líquido (vl):': { 'pt-br': 'Volume ocupado pela fase líquida dentro da mistura saturada.', 'en': 'Volume occupied by the liquid phase within the saturated mixture.', 'es': 'Volumen ocupado por la fase líquida dentro de la mezcla saturada.' },
                'liquid volume (vl):': { 'pt-br': 'Volume ocupado pela fase líquida dentro da mistura saturada.', 'en': 'Volume occupied by the liquid phase within the saturated mixture.', 'es': 'Volumen ocupado por la fase líquida dentro de la mezcla saturada.' },
                'volumen líquido (vl):': { 'pt-br': 'Volume ocupado pela fase líquida dentro da mistura saturada.', 'en': 'Volume occupied by the liquid phase within the saturated mixture.', 'es': 'Volumen ocupado por la fase líquida dentro de la mezcla saturada.' },
                'volume vapor (vv):': { 'pt-br': 'Volume ocupado pela fase de vapor dentro da mistura saturada.', 'en': 'Volume occupied by the vapor phase within the saturated mixture.', 'es': 'Volumen ocupado por la fase de vapor dentro de la mezcla saturada.' },
                'vapor volume (vv):': { 'pt-br': 'Volume ocupado pela fase de vapor dentro da mistura saturada.', 'en': 'Volume occupied by the vapor phase within the saturated mixture.', 'es': 'Volumen ocupado por la fase de vapor dentro de la mezcla saturada.' },
                'volumen vapor (vv):': { 'pt-br': 'Volume ocupado pela fase de vapor dentro da mistura saturada.', 'en': 'Volume occupied by the vapor phase within the saturated mixture.', 'es': 'Volumen ocupado por la fase de vapor dentro de la mezcla saturada.' },
                'constante r:': { 'pt-br': 'Constante particular do gás (R = Ru / M), usada nas equações de gás ideal.', 'en': 'Particular gas constant (R = Ru / M), used in the ideal-gas equations.', 'es': 'Constante particular del gas (R = Ru / M), usada en las ecuaciones de gas ideal.' },
                'r constant:': { 'pt-br': 'Constante particular do gás (R = Ru / M), usada nas equações de gás ideal.', 'en': 'Particular gas constant (R = Ru / M), used in the ideal-gas equations.', 'es': 'Constante particular del gas (R = Ru / M), usada en las ecuaciones de gas ideal.' },
                'cp0:': { 'pt-br': 'Calor específico a pressão constante do gás ideal (base para os cálculos de entalpia e entropia).', 'en': 'Ideal-gas specific heat at constant pressure (basis for the enthalpy and entropy calculations).', 'es': 'Calor específico a presión constante del gas ideal (base para los cálculos de entalpía y entropía).' },
                'cv0:': { 'pt-br': 'Calor específico a volume constante do gás ideal (base para os cálculos de energia interna e entropia).', 'en': 'Ideal-gas specific heat at constant volume (basis for the internal-energy and entropy calculations).', 'es': 'Calor específico a volumen constante del gas ideal (base para los cálculos de energía interna y entropía).' },
                'expoente (n):': { 'pt-br': 'Expoente politrópico que caracteriza o tipo de processo (p·v^n = constante).', 'en': 'Polytropic exponent that characterizes the type of process (p·v^n = constant).', 'es': 'Exponente politrópico que caracteriza el tipo de proceso (p·v^n = constante).' },
                'exponent (n):': { 'pt-br': 'Expoente politrópico que caracteriza o tipo de processo (p·v^n = constante).', 'en': 'Polytropic exponent that characterizes the type of process (p·v^n = constant).', 'es': 'Exponente politrópico que caracteriza el tipo de proceso (p·v^n = constante).' },
                'expoente isentrópico (k):': { 'pt-br': 'Razão entre os calores específicos (cp/cv) do gás, usada nos processos isentrópicos.', 'en': 'Ratio between the specific heats (cp/cv) of the gas, used in isentropic processes.', 'es': 'Razón entre los calores específicos (cp/cv) del gas, usada en los procesos isentrópicos.' },
                'isentropic exponent (k):': { 'pt-br': 'Razão entre os calores específicos (cp/cv) do gás, usada nos processos isentrópicos.', 'en': 'Ratio between the specific heats (cp/cv) of the gas, used in isentropic processes.', 'es': 'Razón entre los calores específicos (cp/cv) del gas, usada en los procesos isentrópicos.' },
                'razão (k):': { 'pt-br': 'Razão entre os calores específicos (cp/cv) do gás.', 'en': 'Ratio between the gas\'s specific heats (cp/cv).', 'es': 'Razón entre los calores específicos (cp/cv) del gas.' },
                'ratio (k):': { 'pt-br': 'Razão entre os calores específicos (cp/cv) do gás.', 'en': 'Ratio between the gas\'s specific heats (cp/cv).', 'es': 'Razón entre los calores específicos (cp/cv) del gas.' },
                'razón (k):': { 'pt-br': 'Razão entre os calores específicos (cp/cv) do gás.', 'en': 'Ratio between the gas\'s specific heats (cp/cv).', 'es': 'Razón entre los calores específicos (cp/cv) del gas.' },
                'trabalho (w)': { 'pt-br': 'Trabalho realizado pelo sistema (ou sobre ele) ao longo do processo.', 'en': 'Work done by the system (or on it) throughout the process.', 'es': 'Trabajo realizado por el sistema (o sobre él) a lo largo del proceso.' },
                'work (w)': { 'pt-br': 'Trabalho realizado pelo sistema (ou sobre ele) ao longo do processo.', 'en': 'Work done by the system (or on it) throughout the process.', 'es': 'Trabajo realizado por el sistema (o sobre él) a lo largo del proceso.' },
                'trabajo (w)': { 'pt-br': 'Trabalho realizado pelo sistema (ou sobre ele) ao longo do processo.', 'en': 'Work done by the system (or on it) throughout the process.', 'es': 'Trabajo realizado por el sistema (o sobre él) a lo largo del proceso.' },
                'calor (q)': { 'pt-br': 'Quantidade de calor trocada entre o sistema e a vizinhança durante o processo.', 'en': 'Amount of heat exchanged between the system and the surroundings during the process.', 'es': 'Cantidad de calor intercambiada entre el sistema y el entorno durante el proceso.' },
                'heat (q)': { 'pt-br': 'Quantidade de calor trocada entre o sistema e a vizinhança durante o processo.', 'en': 'Amount of heat exchanged between the system and the surroundings during the process.', 'es': 'Cantidad de calor intercambiada entre el sistema y el entorno durante el proceso.' },
                'entropia gerada (sger)': { 'pt-br': 'Entropia gerada pelas irreversibilidades do processo; pela 2ª Lei da Termodinâmica, deve ser sempre ≥ 0.', 'en': 'Entropy generated by the irreversibilities of the process; by the 2nd Law of Thermodynamics, it must always be ≥ 0.', 'es': 'Entropía generada por las irreversibilidades del proceso; por la 2ª Ley de la Termodinámica, debe ser siempre ≥ 0.' },
                'generated entropy (sger)': { 'pt-br': 'Entropia gerada pelas irreversibilidades do processo; pela 2ª Lei da Termodinâmica, deve ser sempre ≥ 0.', 'en': 'Entropy generated by the irreversibilities of the process; by the 2nd Law of Thermodynamics, it must always be ≥ 0.', 'es': 'Entropía generada por las irreversibilidades del proceso; por la 2ª Ley de la Termodinámica, debe ser siempre ≥ 0.' },
                'entropía generada (sger)': { 'pt-br': 'Entropia gerada pelas irreversibilidades do processo; pela 2ª Lei da Termodinâmica, deve ser sempre ≥ 0.', 'en': 'Entropy generated by the irreversibilities of the process; by the 2nd Law of Thermodynamics, it must always be ≥ 0.', 'es': 'Entropía generada por las irreversibilidades del proceso; por la 2ª Ley de la Termodinámica, debe ser siempre ≥ 0.' },
                'temp. da vizinhança': { 'pt-br': 'Temperatura do ambiente externo, usada para calcular a troca de calor e a entropia gerada.', 'en': 'Temperature of the external surroundings, used to calculate the heat exchange and the generated entropy.', 'es': 'Temperatura del ambiente externo, usada para calcular el intercambio de calor y la entropía generada.' },
                'temperatura da vizinhança': { 'pt-br': 'Temperatura do ambiente externo, usada para calcular a troca de calor e a entropia gerada.', 'en': 'Temperature of the external surroundings, used to calculate the heat exchange and the generated entropy.', 'es': 'Temperatura del ambiente externo, usada para calcular el intercambio de calor y la entropía generada.' },
                'surroundings temp': { 'pt-br': 'Temperatura do ambiente externo, usada para calcular a troca de calor e a entropia gerada.', 'en': 'Temperature of the external surroundings, used to calculate the heat exchange and the generated entropy.', 'es': 'Temperatura del ambiente externo, usada para calcular el intercambio de calor y la entropía generada.' },
                'temp. del entorno': { 'pt-br': 'Temperatura do ambiente externo, usada para calcular a troca de calor e a entropia gerada.', 'en': 'Temperature of the external surroundings, used to calculate the heat exchange and the generated entropy.', 'es': 'Temperatura del ambiente externo, usada para calcular el intercambio de calor y la entropía generada.' }
            };

            function getDescription(el, label) {
                var lang = localStorage.getItem('preferredLang') || 'pt-br';
                var own = el.getAttribute('data-tour-' + lang) || el.getAttribute('data-tour-pt-br');
                if (own) return own;
                var byId = el.id && descById[el.id];
                if (byId) return byId[lang] || byId['pt-br'];
                var byLabel = descByLabel[label.trim().toLowerCase()];
                if (byLabel) return byLabel[lang] || byLabel['pt-br'];
                return '';
            }

            // Extrai um rótulo/texto legível de um botão da tela (tooltip do ícone,
            // texto visível, aria-label ou title, nessa ordem de preferência).
            function getLabel(el) {
                var lang0 = localStorage.getItem('preferredLang') || 'pt-br';
                var custom = el.getAttribute('data-tour-label-' + lang0) || el.getAttribute('data-tour-label-pt-br');
                if (custom) return custom;
                var tooltip = el.querySelector('.icon-tooltip');
                if (tooltip && tooltip.textContent.trim()) return tooltip.textContent.trim();
                var clone = el.cloneNode(true);
                clone.querySelectorAll('i').forEach(function (i) { i.remove(); });
                var text = clone.textContent.replace(/\s+/g, ' ').trim();
                if (text) return text;
                if (el.getAttribute('aria-label')) return el.getAttribute('aria-label');
                if (el.getAttribute('title')) return el.getAttribute('title');
                return '';
            }

            // Extrai o rótulo (nome da grandeza) e o valor calculado de uma
            // linha de resultado (.data-row de .results-card/.state-card, ou
            // .process-item do resumo do processo: Trabalho, Calor, etc.)
            function getRowLabelAndValue(el) {
                var labelEl = el.querySelector('.data-label') || el.querySelector('.lang-text');
                var label = labelEl ? labelEl.textContent.replace(/\s+/g, ' ').trim() : '';
                var valueEl = el.querySelector('.data-value') || el.querySelector('strong');
                var value = valueEl ? valueEl.textContent.replace(/\s+/g, ' ').trim() : '';
                return { label: label, value: value };
            }

            // Monta a lista de passos do tour a partir dos elementos visíveis da
            // tela: tanto os botões de ação quanto as linhas de resultado
            // (estados calculados e resumo do processo: W, Q, Sger etc.)
            function buildSteps() {
                steps = [];
                var candidates = document.querySelectorAll(
                    '.icon-btn, .btn, .process-button, .tab-btn, .btn-submit, #page-help-btn, ' +
                    '.option-card, #value_input_field, [data-tour-label-pt-br], ' +
                    '.results-card .data-row, .state-card .data-row, .process-results .process-item'
                );
                candidates.forEach(function (el) {
                    if (el.offsetParent === null) return; // ignora elementos ocultos
                    var isResultRow = el.classList.contains('data-row') || el.classList.contains('process-item');
                    if (isResultRow) {
                        var info = getRowLabelAndValue(el);
                        if (!info.label) return;
                        steps.push({ el: el, label: info.label, value: info.value, isResult: true });
                    } else {
                        var label = getLabel(el);
                        if (!label) return;
                        steps.push({ el: el, label: label, isResult: false });
                    }
                });
            }

            // Mostra/oculta o botão "Mostrar o que cada botão faz" conforme a página
            function refreshTriggerVisibility() {
                buildSteps();
                if (triggerBtn) {
                    triggerBtn.style.display = steps.length > 1 ? 'flex' : 'none';
                }
            }

            function positionStep() {
                if (!steps.length) return;
                var target = steps[currentStep].el;
                var rect = target.getBoundingClientRect();
                var pad = 8;

                highlightBox.style.top = (rect.top - pad) + 'px';
                highlightBox.style.left = (rect.left - pad) + 'px';
                highlightBox.style.width = (rect.width + pad * 2) + 'px';
                highlightBox.style.height = (rect.height + pad * 2) + 'px';

                titleText.textContent = steps[currentStep].label;
                var stepDesc = getDescription(target, steps[currentStep].label);
                if (steps[currentStep].isResult && steps[currentStep].value) {
                    var savedLangVal = localStorage.getItem('preferredLang') || 'pt-br';
                    var calcValueLabel = { 'pt-br': 'Valor calculado', 'en': 'Calculated value', 'es': 'Valor calculado', 'fr': 'Valeur calculée', 'zh': '计算值' };
                    var calcValueText = calcValueLabel[savedLangVal] || calcValueLabel['pt-br'];
                    stepDesc = (stepDesc ? stepDesc + ' ' : '') + '\u2192 ' + calcValueText + ': ' + steps[currentStep].value;
                }
                bodyText.textContent = stepDesc;
                stepCount.textContent = (currentStep + 1) + ' / ' + steps.length;
                prevBtn.style.visibility = currentStep === 0 ? 'hidden' : 'visible';

                var nextLabelSpan = nextBtn.querySelector('span');
                if (currentStep === steps.length - 1) {
                    nextLabelSpan.setAttribute('data-pt-br', 'Concluir');
                    nextLabelSpan.setAttribute('data-en', 'Finish');
                    nextLabelSpan.setAttribute('data-es', 'Finalizar');
                    nextLabelSpan.setAttribute('data-fr', 'Terminer');
                    nextLabelSpan.setAttribute('data-zh', '完成');
                } else {
                    nextLabelSpan.setAttribute('data-pt-br', 'Próximo');
                    nextLabelSpan.setAttribute('data-en', 'Next');
                    nextLabelSpan.setAttribute('data-es', 'Siguiente');
                    nextLabelSpan.setAttribute('data-fr', 'Suivant');
                    nextLabelSpan.setAttribute('data-zh', '下一步');
                }
                var savedLang = localStorage.getItem('preferredLang') || 'pt-br';
                var newText = nextLabelSpan.getAttribute('data-' + savedLang);
                if (newText) nextLabelSpan.textContent = newText;

                // Posiciona o balão embaixo do botão; se não couber, posiciona acima
                var balloonWidth = balloon.offsetWidth || 260;
                var balloonHeight = balloon.offsetHeight || 100;
                var spaceBelow = window.innerHeight - rect.bottom;
                var top, showBelow;

                if (spaceBelow > balloonHeight + 30) {
                    top = rect.bottom + 18;
                    showBelow = true;
                } else {
                    top = rect.top - balloonHeight - 18;
                    showBelow = false;
                }
                top = Math.max(10, Math.min(top, window.innerHeight - balloonHeight - 10));

                var left = rect.left + rect.width / 2 - balloonWidth / 2;
                left = Math.max(10, Math.min(left, window.innerWidth - balloonWidth - 10));

                balloon.style.top = top + 'px';
                balloon.style.left = left + 'px';

                // Posiciona a setinha do balão apontando para o botão
                var arrowLeft = Math.min(
                    Math.max(rect.left + rect.width / 2 - left - 8, 12),
                    balloonWidth - 28
                );
                arrow.style.left = arrowLeft + 'px';
                if (showBelow) {
                    arrow.style.top = '-8px';
                    arrow.style.bottom = '';
                } else {
                    arrow.style.top = '';
                    arrow.style.bottom = '-8px';
                }

                target.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }

            function openTour() {
                buildSteps();
                if (!steps.length) return;
                currentStep = 0;
                overlay.classList.add('open');
                document.body.style.overflow = 'hidden';
                setTimeout(positionStep, 50);
            }

            function closeTour() {
                overlay.classList.remove('open');
                document.body.style.overflow = '';
            }

            function nextStep() {
                if (currentStep < steps.length - 1) {
                    currentStep++;
                    positionStep();
                } else {
                    closeTour();
                }
            }

            function prevStep() {
                if (currentStep > 0) {
                    currentStep--;
                    positionStep();
                }
            }

            if (triggerBtn) {
                triggerBtn.addEventListener('click', function () {
                    if (helpOverlay) helpOverlay.classList.remove('open');
                    openTour();
                });
            }
            if (closeBtn) closeBtn.addEventListener('click', closeTour);
            if (dim) dim.addEventListener('click', closeTour);
            if (nextBtn) nextBtn.addEventListener('click', nextStep);
            if (prevBtn) prevBtn.addEventListener('click', prevStep);

            document.addEventListener('keydown', function (e) {
                if (!overlay.classList.contains('open')) return;
                if (e.key === 'Escape') closeTour();
                if (e.key === 'ArrowRight' || e.key === 'Enter') nextStep();
                if (e.key === 'ArrowLeft') prevStep();
            });

            window.addEventListener('resize', function () {
                if (overlay.classList.contains('open')) positionStep();
            });

                        refreshTriggerVisibility();
        });


// ============ EXIBIÇÃO PRÉVIA DOS LIMITES VÁLIDOS (HELPER TEXT) ============
document.addEventListener('DOMContentLoaded', function () {
    function formatBound(val, lang) {
        if (val === null || val === undefined || val === '') return '';
        var str = String(val).trim();
        if (lang === 'en') return str.replace(',', '.');
        return str.replace('.', ',');
    }

    function extractUnit(input) {
        var label = null;
        if (input.id) {
            label = document.querySelector('label[for="' + input.id + '"]');
        }
        if (!label && input.previousElementSibling && input.previousElementSibling.tagName === 'LABEL') {
            label = input.previousElementSibling;
        }
        if (!label) return '';
        var text = label.textContent.trim();
        var match = text.match(/\(([^()]+)\)\s*:?\s*$/);
        return match ? ' ' + match[1].trim() : '';
    }

    function updateInputHelper(input) {
        var helper = input._rangeHelper;
        if (!helper) {
            helper = document.createElement('small');
            helper.className = 'input-range-helper';
            helper.setAttribute('role', 'status');
            input.insertAdjacentElement('afterend', helper);
            input._rangeHelper = helper;
        }

        var minAttr = input.getAttribute('min');
        var maxAttr = input.getAttribute('max');
        var hasMin = minAttr !== null && minAttr !== '';
        var hasMax = maxAttr !== null && maxAttr !== '';

        if (!hasMin && !hasMax) {
            helper.style.display = 'none';
            return;
        }

        var lang = localStorage.getItem('preferredLang') || 'pt-br';
        var unit = extractUnit(input);
        var minStr = formatBound(minAttr, lang);
        var maxStr = formatBound(maxAttr, lang);
        var msg = '';

        if (hasMin && hasMax) {
            if (lang === 'en') msg = 'Valid range: ' + minStr + ' to ' + maxStr + unit;
            else if (lang === 'es') msg = 'Rango válido: ' + minStr + ' a ' + maxStr + unit;
            else if (lang === 'fr') msg = 'Plage valide : ' + minStr + ' à ' + maxStr + unit;
            else if (lang === 'zh') msg = '有效范围：' + minStr + ' 至 ' + maxStr + unit;
            else msg = 'Faixa válida: ' + minStr + ' a ' + maxStr + unit;
        } else if (hasMin) {
            if (lang === 'en') msg = 'Minimum value: ' + minStr + unit;
            else if (lang === 'es') msg = 'Valor mínimo: ' + minStr + unit;
            else if (lang === 'fr') msg = 'Valeur minimale : ' + minStr + unit;
            else if (lang === 'zh') msg = '最小值：' + minStr + unit;
            else msg = 'Valor mínimo: ' + minStr + unit;
        } else if (hasMax) {
            if (lang === 'en') msg = 'Maximum value: ' + maxStr + unit;
            else if (lang === 'es') msg = 'Valor máximo: ' + maxStr + unit;
            else if (lang === 'fr') msg = 'Valeur maximale : ' + maxStr + unit;
            else if (lang === 'zh') msg = '最大值：' + maxStr + unit;
            else msg = 'Valor máximo: ' + maxStr + unit;
        }

        var rawVal = input.value;
        var outOfRange = false;
        if (rawVal !== '') {
            var numVal = parseFloat(rawVal);
            if (!isNaN(numVal)) {
                if (hasMin && numVal < parseFloat(minAttr)) outOfRange = true;
                if (hasMax && numVal > parseFloat(maxAttr)) outOfRange = true;
            }
        }

        helper.classList.toggle('out-of-range', outOfRange);
        var iconClass = outOfRange ? 'fas fa-exclamation-triangle' : 'fas fa-info-circle';
        helper.innerHTML = '<i class="' + iconClass + '"></i><span>' + msg + '</span>';
        helper.style.display = 'flex';
    }

    function attachAllNumberInputs() {
        var inputs = document.querySelectorAll('input[type="number"]');
        inputs.forEach(function (input) {
            if (input._rangeObserverAttached) {
                updateInputHelper(input);
                return;
            }
            input._rangeObserverAttached = true;

            var observer = new MutationObserver(function () {
                updateInputHelper(input);
            });
            observer.observe(input, { attributes: true, attributeFilter: ['min', 'max'] });

            input.addEventListener('input', function () {
                updateInputHelper(input);
            });

            updateInputHelper(input);
        });
    }

    attachAllNumberInputs();

    document.addEventListener('languageChanged', function () {
        setTimeout(attachAllNumberInputs, 60);
    });
});

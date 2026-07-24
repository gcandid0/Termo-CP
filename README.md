# TERMO-CP

**TERMO-CP** é uma plataforma web interativa para **cálculo, simulação e visualização de estados e processos termodinâmicos** em um **sistema fechado do tipo cilindro-pistão**, contendo 1,0 kg de **água pura** (substância pura) ou de um **gás ideal**.

O projeto é desenvolvido no âmbito da **Universidade Federal de Rondonópolis (UFR)** e tem como objetivo oferecer uma ferramenta gratuita, acessível e didática que substitua a consulta manual a tabelas termodinâmicas e a resolução repetitiva de interpolações, apoiando o ensino e a aprendizagem de Termodinâmica em cursos de Engenharia.

> 📌 **Aviso de propriedade intelectual:** o TERMO-CP está em processo de **registro junto ao INPI (Instituto Nacional da Propriedade Industrial)**. Consulte a seção [Propriedade Intelectual e Registro no INPI](#-propriedade-intelectual-e-registro-no-inpi) antes de reutilizar, redistribuir ou derivar este software.

## 👥 Autores

- **Gabriel Candido Messias dos Santos** — [gabrielcandidomds@gmail.com](mailto:gabrielcandidomds@gmail.com)
- **Fábio Basaglia Fonseca** — [fabio.fonseca@ufr.edu.br](mailto:fabio.fonseca@ufr.edu.br)
- **Shaider Alberico Irineu Feitosa** (colaborador do projeto TERMOPROP, base do TERMO-CP)

Instituto de Ciências Agrárias e Tecnológicas, Universidade Federal de Rondonópolis (UFR), Av. dos Estudantes, 5055, Sagrada Família, Rondonópolis – MT, Brasil.

## 📋 Sobre o projeto

O TERMO-CP simula, de forma gráfica e interativa, os estados de **líquido comprimido**, **vapor superaquecido** e a **região de mistura líquido-vapor (saturação)** da água, além do comportamento de **gases ideais**, dentro de um conjunto cilindro-pistão. O usuário informa propriedades termodinâmicas conhecidas (temperatura, pressão, volume específico, energia interna, entalpia, entropia ou título) e a plataforma determina automaticamente o estado termodinâmico correspondente e as demais propriedades, indicando também a posição do pistão e a fase da substância.

Além da determinação de estados isolados, o TERMO-CP permite **simular processos termodinâmicos completos**, calculando grandezas como calor transferido (*Q*), trabalho realizado (*W*) e entropia gerada (*S*ger) entre um estado inicial e um estado final, com base na Primeira e na Segunda Leis da Termodinâmica.

O projeto é derivado do **TERMOPROP**, programa mais amplo desenvolvido pelo mesmo grupo de pesquisa para cálculo de propriedades termodinâmicas de diversas substâncias e misturas.

### 🎯 Objetivos

- Tornar os cálculos termodinâmicos mais acessíveis, intuitivos e integrados a um único ambiente web, sem necessidade de instalação de software.
- Reduzir o tempo e o erro associados à consulta manual de tabelas e à interpolação de propriedades.
- Oferecer uma representação gráfica dinâmica (cilindro-pistão) que correlacione diretamente os resultados numéricos com o comportamento físico do sistema.
- Servir como ferramenta de apoio ao ensino, à resolução de exercícios, à elaboração de avaliações e a análises preliminares de engenharia térmica.

## ⚙️ Funcionalidades

### Substância pura (água)

- Determinação do estado termodinâmico a partir de **duas propriedades conhecidas** (temperatura, pressão, volume específico, energia interna, entalpia, entropia ou título), identificando automaticamente a fase: líquido comprimido, líquido saturado, mistura líquido-vapor ou vapor superaquecido.
- Simulação de processos:
  - **Isobárico** (pressão constante)
  - **Isocórico / isovolumétrico** (volume constante)
  - **Isentrópico** (adiabático e reversível)
- Cálculo de calor transferido, trabalho realizado e entropia gerada em cada processo, considerando a temperatura da vizinhança informada pelo usuário.
- Continuidade entre estados: o estado final de um processo pode ser usado automaticamente como estado inicial do processo seguinte (armazenamento temporário em sessão), possibilitando a montagem sequencial de ciclos termodinâmicos.
- Interpolação linear sobre tabelas termodinâmicas estruturadas (baseadas em Borgnakke e Sonntag) para determinação de propriedades intermediárias.

### Gases ideais

- Determinação de propriedades a partir da Equação de Estado do Gás Ideal (*PV = mRT*), informando três das quatro propriedades (pressão, volume específico, temperatura, constante do gás).
- Simulação de processos **isobáricos, isocóricos, isotérmicos e politrópicos**, além de processos isentrópicos.
- Cálculo de energia interna, entalpia e entropia específicas considerando calores específicos constantes (*c*v0, *c*p0).

### Interface gráfica

- Visualização dinâmica, em tempo real, do sistema cilindro-pistão, com atualização da posição do pistão conforme o volume calculado.
- Diferenciação visual das fases da água por coloração (azul claro para líquido, azul escuro para vapor), com escala logarítmica de volume.
- Formulários com validação automática de dados, impedindo a inserção de valores fora dos limites das tabelas de referência.
- Exibição comparativa entre estado inicial e estado final de cada processo simulado.

> 💡 O escopo desta plataforma abrange os estados entre líquido comprimido e vapor superaquecido da água (fase sólida não incluída). Uma expansão em desenvolvimento (ver [Roadmap](#-roadmap)) contempla também amônia, dióxido de carbono, R-410a, R-134a, nitrogênio e metano.

## 🧮 Fundamentação termodinâmica

Os cálculos da plataforma baseiam-se na Primeira e na Segunda Leis da Termodinâmica aplicadas a sistemas fechados, e na definição de trabalho de deslocamento de fronteira:

**Primeira Lei da Termodinâmica** (sistema fechado, entre os estados 1 e 2):

```
m(u2 − u1) = Q − W
```

**Segunda Lei da Termodinâmica:**

```
m(s2 − s1) = Q / Tviz + Sger
```

**Trabalho de deslocamento da fronteira:**

```
W = ∫ p dV   (de 1 a 2)
```

**Casos particulares por tipo de processo:**

| Processo | Simplificação |
|---|---|
| Isobárico | W = p(V2 − V1) |
| Isocórico | W = 0 |
| Adiabático | Q = 0 |
| Reversível | Sger = 0 |

Onde *m* é a massa do sistema (kg), *u* a energia interna específica (kJ/kg), *Q* o calor transferido (kJ), *W* o trabalho realizado (kJ), *s* a entropia específica (kJ/kg·K), *T*viz a temperatura da vizinhança (K) e *S*ger a entropia gerada (kJ/K).

Para a região de saturação, o título (*x*) e as propriedades médias são obtidos por:

```
x = (y − yl) / (yv − yl)
y = yl + x(yv − yl)
```

Para valores fora dos pontos tabelados, aplica-se **interpolação linear**:

```
y = y1 + [(X − X1) / (X2 − X1)] · (y2 − y1)
```

Para gases ideais, aplica-se a Equação de Estado do Gás Ideal e os modelos de calor específico constante:

```
PV = mRT
u2 − u1 = cv0(T2 − T1)
h2 − h1 = cp0(T2 − T1)
s2 − s1 = cp0·ln(T2/T1) − R·ln(P2/P1)
```

## 🚀 Tecnologias

- **[Python](https://www.python.org/)** — linguagem do núcleo computacional (determinação de estado, interpolação de propriedades, cálculo de processos).
- **[Django](https://www.djangoproject.com/)** — framework de backend responsável pelo roteamento, formulários, gerenciamento de sessão e persistência temporária de estados.
- **JavaScript + HTML**, com a biblioteca **[Processing.js / p5.js](https://p5js.org/)** — camada de frontend responsável pela visualização gráfica dinâmica do cilindro-pistão.

## 🏗️ Arquitetura

O sistema segue o princípio de **separação funcional** entre três camadas:

1. **Processamento numérico (backend/Python):** algoritmos de determinação de fase, interpolação linear sobre tabelas termodinâmicas estruturadas e aplicação da Primeira e da Segunda Leis da Termodinâmica.
2. **Gerenciamento web (Django):** roteamento de requisições, formulários, validação de dados de entrada e armazenamento temporário de estados em sessão — permitindo que o estado final de um processo seja reaproveitado como estado inicial do processo seguinte.
3. **Visualização gráfica (JavaScript/Processing.js):** renderização em tempo real do sistema cilindro-pistão, sincronizada com os resultados numéricos calculados no backend.

## 📁 Estrutura do projeto

```
Termo-CP/
├── myapp/          # aplicação Django com a lógica de simulação termodinâmica
├── termocp/         # configurações do projeto Django (settings, urls, wsgi)
├── manage.py        # utilitário de linha de comando do Django
└── .gitignore
```

## 🔧 Instalação e execução local

Pré-requisitos: Python 3.10+ e pip.

```bash
git clone https://github.com/gcandid0/Termo-CP.git
cd Termo-CP

python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

Acesse em [http://127.0.0.1:8000](http://127.0.0.1:8000).

> Se o repositório ainda não possuir um `requirements.txt`, gere um com `pip freeze > requirements.txt` após instalar Django e demais dependências utilizadas no projeto.

## 🗺️ Roadmap

Conforme apresentado nas publicações do grupo de pesquisa, os próximos passos previstos para o TERMO-CP incluem:

- Incorporação de novas substâncias puras e fluidos refrigerantes: **amônia, dióxido de carbono, R-410a, R-134a, nitrogênio e metano**.
- Ampliação dos recursos gráficos de visualização.
- Implementação de módulos para simulação de **ciclos termodinâmicos completos** (ex.: Ciclo Rankine).
- Avaliações educacionais sistemáticas do impacto da ferramenta no processo de ensino-aprendizagem.

## 📚 Publicações relacionadas

Este software é resultado de pesquisa acadêmica e está descrito nos seguintes trabalhos:

- SANTOS, G. C. M.; FONSECA, F. B. **Software for simulating thermodynamic states of water in a cylinder-piston system**. In: *Proceedings of the XLVI Ibero-Latin-American Congress on Computational Methods in Engineering (CILAMCE)*, Vitória, ES, Brasil, 2025.
- SANTOS, G. C. M.; FONSECA, F. B. **Modelagem e Análise Termodinâmica de Processos em Sistema Fechado com Água**. In: *XIII Congresso Brasileiro de Termodinâmica / IX Escola de Termodinâmica*, Brasília, DF, Brasil, 2026.
- SANTOS, G. C. M.; FONSECA, F. B. **Desenvolvimento de uma simulação interativa de cilindro-pistão para o ensino de Termodinâmica**. In: *XII Congreso Internacional de Ingeniería Mecánica, Mecatrónica y Automatización (CIMM)*, 2025.
- SANTOS, G. C. M.; FONSECA, F. B. **TERMO-CP: uma plataforma interativa para cálculo e visualização de processos e estados termodinâmicos**. CONEM2026-1510. In: *13º Congresso Nacional de Engenharia Mecânica (CONEM)*, São Luís, MA, Brasil, 2026.
- SANTOS, G. C. M.; FONSECA, F. B. **Expansão da Plataforma TERMO-CP: Integração de Diferentes Substâncias Puras para Simulação de Processos Termodinâmicos**. *XIII Congresso Brasileiro de Termodinâmica*, 2026.
- FONSECA, F. B.; SANTOS, G. C. M.; FEITOSA, S. A. I. Capítulo: **TERMOPROP e TERMO-CP: ferramentas computacionais de livre acesso para determinação e aplicação de propriedades termodinâmicas**. In: Livro (capítulo), 2025.

### Referências bibliográficas centrais

- BORGNAKKE, C.; SONNTAG, R. E. **Fundamentos da Termodinâmica**. 2ª/8ª ed. São Paulo: Editora Blucher, 2018.
- ÇENGEL, Y. A.; BOLES, M. A. **Termodinâmica**. 7ª ed. Porto Alegre: Bookman, 2013.

## 🔒 Propriedade Intelectual e Registro no INPI

O software **TERMO-CP** é fruto de pesquisa desenvolvida na Universidade Federal de Rondonópolis (UFR) e **encontra-se em processo de registro de programa de computador junto ao INPI (Instituto Nacional da Propriedade Industrial)**, nos termos da Lei nº 9.609/1998 (Lei do Software) e da Lei nº 9.610/1998 (Lei de Direitos Autorais).

Em função disso:

- Todos os direitos sobre o código-fonte, algoritmos, interface e demais materiais deste repositório são reservados aos autores e à instituição vinculada, até definição formal dos termos de licenciamento pós-registro.
- **Este repositório não deve ser considerado, até segunda ordem, como software de código aberto para fins de redistribuição, uso comercial ou criação de obras derivadas**, salvo autorização expressa dos autores.
- Consulte o arquivo [LICENSE](LICENSE) para os termos atuais de uso.
- Dúvidas sobre licenciamento, colaboração acadêmica ou uso institucional podem ser encaminhadas diretamente aos autores pelos e-mails informados na seção [Autores](#-autores).

## 🤝 Contribuindo

Contribuições da comunidade acadêmica são bem-vindas para fins de revisão, testes e sugestões, respeitando as condições descritas em [Propriedade Intelectual e Registro no INPI](#-propriedade-intelectual-e-registro-no-inpi). Veja o arquivo [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 🙏 Agradecimentos

Os autores agradecem à **Universidade Federal de Rondonópolis (UFR)** e à **Pró-Reitoria de Ensino de Pós-Graduação e Pesquisa** pelo apoio institucional ao desenvolvimento e à divulgação deste trabalho.

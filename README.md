<p align="center">
  <a href="https://gcandid0.pythonanywhere.com/">
    <img src="./assets/logo.png" alt="TERMO-CP Logo" width="120">
  </a>
</p>

<div align="center">

# TERMO-CP

### Plataforma web para simulação de estados e processos termodinâmicos em sistemas cilindro-pistão.

<br/>

<a href="https://gcandid0.pythonanywhere.com/"><img src="https://img.shields.io/badge/Acessar-gcandid0.pythonanywhere.com-2b9246?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Acessar plataforma"></a>
<a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-6.0.5-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python%203-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
<a href="https://p5js.org/"><img src="https://img.shields.io/badge/P5.js-ED225D?style=for-the-badge&logo=p5dotjs&logoColor=white" alt="P5.js">
<img src="https://img.shields.io/badge/Licen%C3%A7a-Todos%20os%20direitos%20reservados-b91c1c?style=for-the-badge" alt="Licença">

<br/>

<a href="http://lattes.cnpq.br/6696786236047929"><img src="https://img.shields.io/badge/Lattes-Curr%C3%ADculo-1a5fb4?style=for-the-badge&logo=googlescholar&logoColor=white" alt="Lattes"></a>
<a href="https://www.linkedin.com/in/gabriel-candido-235637226/"><img src="https://img.shields.io/badge/LinkedIn-Gabriel%20Candido-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
<a href="https://github.com/gcandid0/Termo-CP"><img src="https://img.shields.io/badge/GitHub-Termo--CP-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>

</div>

<p align="center"><sub>Desenvolvido no âmbito de pesquisa acadêmica da <strong>Universidade Federal de Rondonópolis (UFR)</strong> · em processo de registro junto ao INPI</sub></p>

## Índice

- [Sobre o TERMO-CP](#sobre-o-termo-cp)
- [Idiomas](#-idiomas)
- [Substâncias suportadas](#substâncias-suportadas)
- [Como usar](#-como-usar)
- [Funcionalidades](#-funcionalidades)
- [Stack Tecnológica](#️-stack-tecnológica)
- [Roadmap](#️-roadmap)
- [Contato](#-contato)
- [Autores](#-autores)
- [Licença](#-licença)
- [Como citar](#-como-citar)
- [Contribuindo](#-contribuindo)

---

## Sobre o TERMO-CP

O **TERMO-CP** é uma plataforma computacional desenvolvida para a simulação de **estados** e **processos termodinâmicos**, aplicada a substâncias puras e a gases ideais em sistemas fechados do tipo cilindro-pistão.

O projeto tem foco educacional, voltado a estudantes, professores e engenheiros que precisam calcular propriedades termodinâmicas e visualizar transformações de forma rápida, interativa e visual.

**Principais recursos:**

- **Cálculo de estados termodinâmicos** - determinação de propriedades (P, T, v, u, h, s, x) a partir de pares de variáveis conhecidas
- **Simulação de processos** - condições iniciais e finais para transformações completas (isobáricas, isocóricas, isotérmicas, adiabáticas, entre outras)
- **Visualização 3D interativa** - animação do cilindro-pistão em P5.js (WEBGL) para cada resultado
- **Relatórios exportáveis** - captura dos resultados via html2canvas
- **Múltiplas substâncias** - água, amônia, CO₂, R-410a, R-134a, nitrogênio, metano e gás ideal

<br>

<div align="center">
  <a href="https://gcandid0.pythonanywhere.com/">
    <img src="./assets/screenshot-home.png" alt="Tela inicial do TERMO-CP" width="900" style="border-radius: 12px;">
  </a>
</div>

## 🌐 Idiomas

A plataforma está disponível em três idiomas, selecionáveis diretamente no menu superior:

🇧🇷 Português &nbsp;|&nbsp; 🇺🇸 English &nbsp;|&nbsp; 🇪🇸 Español

## Substâncias suportadas

| Substância | Estados | Processos |
|---|---|---|
| Gás Ideal | ✅ | ✅ |
| Água | ✅ | ✅ |
| Amônia | ✅ | ✅ |
| CO₂ | ✅ | ✅ |
| R-410a | ✅ | ✅ |
| R-134a | ✅ | ✅ |
| Nitrogênio | ✅ | ✅ |
| Metano | ✅ | ✅ |

## 🚀 Como usar

> [!IMPORTANT]
> O código-fonte está disponível neste repositório apenas para **visualização e estudo acadêmico**, conforme a [licença](#-licença) vigente. Para rodar localmente com fins de pesquisa/avaliação:

**Pré-requisitos:**
- Python 3
- pip

### Instalação local

```bash
# Clone o repositório
git clone https://github.com/gcandid0/Termo-CP.git
cd Termo-CP

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente (.env)
# crie um arquivo .env na raiz com:
# SECRET_KEY=<sua-chave>
# DEBUG=True

# Rode as migrações e o servidor
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

**Dependências principais** (`requirements.txt`):

| Pacote | Versão |
|---|---|
| Django | 6.0.5 |
| asgiref | 3.11.1 |
| python-dotenv | 1.2.2 |
| sqlparse | 0.5.5 |
| tzdata | 2026.2 |

### Uso online

Não é necessário instalar nada - acesse diretamente a versão publicada:

**[gcandid0.pythonanywhere.com →](https://gcandid0.pythonanywhere.com/)**

---

## ✨ Funcionalidades

### Simulação de Estados

Informe duas propriedades conhecidas de uma substância (pressão, temperatura, volume específico, título, etc.) e o TERMO-CP calcula automaticamente as demais propriedades termodinâmicas com base nas tabelas de referência (ex.: tabelas B.x para água).

### Simulação de Processos

Defina o estado inicial e o tipo de processo (isobárico, isocórico, isotérmico, adiabático, politrópico) para obter o estado final e as trocas de energia (trabalho e calor) envolvidas.

### Visualização do Cilindro-Pistão

Cada resultado é acompanhado de uma animação 3D em P5.js que representa o comportamento do pistão durante o processo, facilitando a compreensão visual do fenômeno.

### Relatórios

Os resultados podem ser exportados como imagem/relatório diretamente da página, usando html2canvas.

---

## 🛠️ Stack Tecnológica

- **Backend:** Python 3 + Django
- **Frontend:** HTML5, JavaScript, P5.js
- **Deploy:** PythonAnywhere
- **Configuração:** python-dotenv (`.env` com `SECRET_KEY` e `DEBUG`)

---

## 🗺️ Roadmap

<!-- Marque o que já está pronto e o que está planejado -->
- [x] Cálculo de estados para 8 substâncias
- [x] Simulação de processos com animação do pistão
- [x] Exportação de relatório
- [x] Suporte a PT/EN/ES

---

## 📬 Contato

Dúvidas, sugestões ou relatos de problemas podem ser enviados pelo [formulário de contato](https://gcandid0.pythonanywhere.com/) da plataforma, por [issues no GitHub](https://github.com/gcandid0/Termo-CP/issues) ou diretamente pelos e-mails abaixo.

## 👤 Autores

Projeto desenvolvido no âmbito de pesquisa acadêmica da **Universidade Federal de Rondonópolis (UFR)**:

- **Gabriel Candido Messias dos Santos** — [gabrielcandidomds@gmail.com](mailto:gabrielcandidomds@gmail.com) · [Lattes](http://lattes.cnpq.br/6696786236047929) · [LinkedIn](https://www.linkedin.com/in/gabriel-candido-235637226/)
- **Fábio Basaglia Fonseca** — [fabio.fonseca@ufr.edu.br](mailto:fabio.fonseca@ufr.edu.br)

## 📄 Licença

O TERMO-CP está em **processo de registro junto ao INPI** (Lei nº 9.609/1998 e Lei nº 9.610/1998) e seus direitos autorais são reservados aos autores e à UFR.

Até a conclusão do registro e definição formal dos termos de licenciamento:

- ✅ É permitida a **visualização e o estudo** do código-fonte para fins acadêmicos, de pesquisa e avaliação, sem fins comerciais.
- ❌ **Não é permitida**, sem autorização expressa e por escrito dos autores: reprodução, distribuição, modificação, criação de obras derivadas, uso comercial, sublicença ou cessão de direitos.

O software é fornecido "no estado em que se encontra", sem garantias de qualquer tipo. Veja o texto completo em [LICENSE](LICENSE).

## 📚 Como citar

Se o TERMO-CP for utilizado em trabalhos acadêmicos, você pode citá-lo como:

```
SANTOS, G. C. M. dos; FONSECA, F. B. TERMO-CP: plataforma computacional para
simulação de estados e processos termodinâmicos. Universidade Federal de
Rondonópolis (UFR), <ano>. Disponível em:
https://gcandid0.pythonanywhere.com/. Acesso em: <data>.
```

## 🤝 Contribuindo

Contribuições são bem-vindas, respeitando os termos da [licença](#-licença) — em especial, entre em contato com os autores antes de propor alterações de código. Veja o guia completo em [CONTRIBUTING.md](CONTRIBUTING.md).

---

> [!WARNING]
> O TERMO-CP tem finalidade educacional e os resultados devem ser validados antes de aplicações de engenharia críticas. O software encontra-se em processo de registro no INPI e é distribuído sob termos restritivos — consulte a [Licença](#-licença) antes de qualquer uso além de visualização e estudo.
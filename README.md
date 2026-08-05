<p align="center">
  <a href="https://gcandid0.pythonanywhere.com/">
    <img src="https://img.shields.io/badge/TERMO--CP-Simula%C3%A7%C3%A3o%20Termodin%C3%A2mica-2b6cb0?style=for-the-badge" alt="TERMO-CP Banner" width="100%">
  </a>
</p>

<div align="center">

# TERMO-CP

### Plataforma web para simulação de estados e processos termodinâmicos em sistemas cilindro-pistão.

<br/>

<a href="https://gcandid0.pythonanywhere.com/"><img src="https://img.shields.io/badge/Acessar-gcandid0.pythonanywhere.com-2b9246?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Acessar plataforma"></a>
<img src="https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django">
<img src="https://img.shields.io/badge/Python%203-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
<img src="https://img.shields.io/badge/P5.js-ED225D?style=for-the-badge&logo=p5dotjs&logoColor=white" alt="P5.js">

</div>

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
    <img src="https://img.shields.io/badge/Interface-TERMO--CP-1a1a2e?style=for-the-badge" alt="TERMO-CP Interface" width="600">
  </a>
</div>

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

**Pré-requisitos:**
- Python 3
- Django

### Instalação local

```bash
# Clone o repositório
git clone https://github.com/<seu-usuario>/termo-cp.git
cd termo-cp

# Crie e ative um ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente (.env)
cp .env.example .env
# defina SECRET_KEY e DEBUG

# Rode as migrações e o servidor
python manage.py migrate
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` no navegador.

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

## 📬 Contato

Dúvidas, sugestões ou relatos de problemas podem ser enviados pelo [formulário de contato](https://gcandid0.pythonanywhere.com/) da plataforma.

## Responsáveis

Projeto desenvolvido por **Gabriel Candido** e **Fábio Fonseca**.

---

> [!WARNING]
> O TERMO-CP tem finalidade educacional. Resultados devem ser validados antes de aplicações de engenharia críticas.
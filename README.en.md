<a name="top"></a>
<p align="center">
  <a href="https://gcandid0.pythonanywhere.com/">
    <img src="./assets/logo.png" alt="TERMO-CP Logo" width="120">
  </a>
</p>

<div align="center">

# TERMO-CP

### Web platform for simulating thermodynamic states and processes in piston-cylinder systems.

<sub><a href="./README.md">🇧🇷 Português</a> &nbsp;|&nbsp; 🇺🇸 English &nbsp;|&nbsp; <a href="./README.es.md">🇪🇸 Español</a></sub>

<br/>

<a href="https://gcandid0.pythonanywhere.com/"><img src="https://img.shields.io/badge/Live-gcandid0.pythonanywhere.com-2b9246?style=for-the-badge&logo=googlechrome&logoColor=white" alt="Live platform"></a>
<a href="https://www.djangoproject.com/"><img src="https://img.shields.io/badge/Django-6.0.5-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django"></a>
<a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python%203-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3"></a>
<a href="https://p5js.org/"><img src="https://img.shields.io/badge/P5.js-ED225D?style=for-the-badge&logo=p5dotjs&logoColor=white" alt="P5.js"></a>
<a href="https://github.com/gcandid0/Termo-CP/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-All%20rights%20reserved-b91c1c?style=for-the-badge" alt="License"></a>

<br/>

<a href="https://github.com/gcandid0/Termo-CP/stargazers"><img src="https://img.shields.io/github/stars/gcandid0/Termo-CP?style=flat-square&color=f0b429&label=stars" alt="GitHub stars"></a>
<a href="https://github.com/gcandid0/Termo-CP/commits/main"><img src="https://img.shields.io/github/last-commit/gcandid0/Termo-CP?style=flat-square&color=2b9246&label=last%20commit" alt="Last commit"></a>
<a href="https://github.com/gcandid0/Termo-CP"><img src="https://img.shields.io/github/repo-size/gcandid0/Termo-CP?style=flat-square&color=1a5fb4&label=size" alt="Repo size"></a>
<a href="https://github.com/gcandid0/Termo-CP/issues"><img src="https://img.shields.io/github/issues/gcandid0/Termo-CP?style=flat-square&color=b91c1c&label=issues" alt="Issues"></a>

<br/><br/>

<a href="http://lattes.cnpq.br/6696786236047929"><img src="https://img.shields.io/badge/Lattes-CV-1a5fb4?style=for-the-badge&logo=googlescholar&logoColor=white" alt="Lattes"></a>
<a href="https://www.linkedin.com/in/gabriel-candido-235637226/"><img src="https://img.shields.io/badge/LinkedIn-Gabriel%20Candido-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn"></a>
<a href="https://github.com/gcandid0/Termo-CP"><img src="https://img.shields.io/badge/GitHub-Termo--CP-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>

</div>

<p align="center"><sub>Developed as part of academic research at <strong>Universidade Federal de Rondonópolis (UFR)</strong>, Brazil · patent registration in progress with INPI</sub></p>

## Table of Contents

- [About TERMO-CP](#about-termo-cp)
- [Languages](#languages)
- [Supported substances](#supported-substances)
- [Getting started](#getting-started)
- [Features](#features)
- [Tech stack](#tech-stack)
- [Roadmap](#roadmap)
- [Contact](#contact)
- [Authors](#authors)
- [License](#license)
- [How to cite](#how-to-cite)
- [Contributing](#contributing)

---

## About TERMO-CP

**TERMO-CP** is a computational platform for simulating thermodynamic **states** and **processes**, applied to pure substances and ideal gases in closed piston-cylinder systems.

The project is education-focused, built for students, teachers, and engineers who need to compute thermodynamic properties and visualize transformations quickly and interactively.

**Key features:**

- **Thermodynamic state calculation** - determines properties (P, T, v, u, h, s, x) from known variable pairs
- **Process simulation** - initial and final conditions for complete transformations (isobaric, isochoric, isothermal, adiabatic, and more)
- **Interactive 3D visualization** - piston-cylinder animation in P5.js (WEBGL) for every result
- **Exportable reports** - result capture via html2canvas
- **Multiple substances** - water, ammonia, CO₂, R-410a, R-134a, nitrogen, methane, and ideal gas

<br>

<div align="center">
  <a href="https://gcandid0.pythonanywhere.com/">
    <img src="./assets/screenshot-home.png" alt="TERMO-CP home screen" width="900" style="border-radius: 12px;">
  </a>
</div>

<p align="right"><a href="#top">↑ back to top</a></p>

## Languages

The platform is available in three languages, selectable from the top menu:

🇧🇷 Português &nbsp;|&nbsp; 🇺🇸 English &nbsp;|&nbsp; 🇪🇸 Español

<p align="right"><a href="#top">↑ back to top</a></p>

## Supported substances

| Substance | States | Processes |
|---|---|---|
| Ideal gas | ✅ | ✅ |
| Water | ✅ | ✅ |
| Ammonia | ✅ | ✅ |
| CO₂ | ✅ | ✅ |
| R-410a | ✅ | ✅ |
| R-134a | ✅ | ✅ |
| Nitrogen | ✅ | ✅ |
| Methane | ✅ | ✅ |

<p align="right"><a href="#top">↑ back to top</a></p>

## Getting started

> [!IMPORTANT]
> The source code in this repository is available for **viewing and academic study only**, per the current [license](#license). To run it locally for research/evaluation purposes:

**Requirements:**
- Python 3
- pip

### Local installation

```bash
# Clone the repository
git clone https://github.com/gcandid0/Termo-CP.git
cd Termo-CP

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables (.env)
# create a .env file at the root with:
# SECRET_KEY=<your-key>
# DEBUG=True

# Run migrations and start the server
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

**Main dependencies** (`requirements.txt`):

| Package | Version |
|---|---|
| Django | 6.0.5 |
| asgiref | 3.11.1 |
| python-dotenv | 1.2.2 |
| sqlparse | 0.5.5 |
| tzdata | 2026.2 |

### Online use

No installation needed - use the published version directly:

**[gcandid0.pythonanywhere.com →](https://gcandid0.pythonanywhere.com/)**

<p align="right"><a href="#top">↑ back to top</a></p>

---

## Features

### State simulation

Enter two known properties of a substance (pressure, temperature, specific volume, quality, etc.) and TERMO-CP automatically computes the remaining thermodynamic properties based on reference tables (e.g., B.x tables for water).

### Process simulation

Define the initial state and process type (isobaric, isochoric, isothermal, adiabatic, polytropic) to obtain the final state and the energy exchanges (work and heat) involved.

### Piston-cylinder visualization

Every result comes with a 3D P5.js animation representing the piston's behavior during the process, making the phenomenon easier to understand visually.

### Reports

Results can be exported as an image/report directly from the page, using html2canvas.

<p align="right"><a href="#top">↑ back to top</a></p>

---

## Tech stack

- **Backend:** Python 3 + Django
- **Frontend:** HTML5, JavaScript, P5.js
- **Deployment:** PythonAnywhere
- **Configuration:** python-dotenv (`.env` with `SECRET_KEY` and `DEBUG`)

<p align="right"><a href="#top">↑ back to top</a></p>

---

## Roadmap

- [x] State calculation for 8 substances
- [x] Process simulation with piston animation
- [x] Report export
- [x] PT/EN/ES support

<p align="right"><a href="#top">↑ back to top</a></p>

---

## Contact

Questions, suggestions, or bug reports can be sent through the platform's [contact form](https://gcandid0.pythonanywhere.com/), via [GitHub issues](https://github.com/gcandid0/Termo-CP/issues), or directly by email below.

## Authors

Developed as part of academic research at **Universidade Federal de Rondonópolis (UFR)**, Brazil:

- **Gabriel Candido Messias dos Santos** — [gabrielcandidomds@gmail.com](mailto:gabrielcandidomds@gmail.com) · [Lattes](http://lattes.cnpq.br/6696786236047929) · [LinkedIn](https://www.linkedin.com/in/gabriel-candido-235637226/)
- **Fábio Basaglia Fonseca** — [fabio.fonseca@ufr.edu.br](mailto:fabio.fonseca@ufr.edu.br)

## License

TERMO-CP is currently undergoing **patent/software registration with INPI** (Brazilian IP office), under Law No. 9,609/1998 and Law No. 9,610/1998. Copyright is reserved to the authors and UFR.

Until registration is complete and formal licensing terms are defined:

- ✅ **Viewing and studying** the source code is permitted for academic, research, and evaluation purposes, non-commercially.
- ❌ **Not permitted** without express written authorization from the authors: reproduction, distribution, modification, derivative works, commercial use, sublicensing, or transfer of rights.

The software is provided "as is", without warranties of any kind. See the full text in [LICENSE](LICENSE).

## How to cite

If TERMO-CP is used in academic work, you may cite it as:

```
SANTOS, G. C. M. dos; FONSECA, F. B. TERMO-CP: computational platform for
simulating thermodynamic states and processes. Universidade Federal de
Rondonópolis (UFR), <year>. Available at:
https://gcandid0.pythonanywhere.com/. Accessed on: <date>.
```

## Contributing

Contributions are welcome, subject to the terms of the [license](#license) — in particular, please contact the authors before proposing code changes. See the full guide in [CONTRIBUTING.md](CONTRIBUTING.md).

<p align="right"><a href="#top">↑ back to top</a></p>

---

> [!WARNING]
> TERMO-CP is intended for educational purposes; results should be validated before use in critical engineering applications. The software is undergoing INPI registration and is distributed under restrictive terms — see the [License](#license) before any use beyond viewing and study.

<br>

<div align="center">
  <img src="./assets/logo.png" alt="TERMO-CP" width="48">
  <br>
  <sub>
    <strong>TERMO-CP</strong> · developed at <a href="https://www.ufr.edu.br/">Universidade Federal de Rondonópolis (UFR)</a><br>
    <a href="https://gcandid0.pythonanywhere.com/">Platform</a> ·
    <a href="https://github.com/gcandid0/Termo-CP">GitHub</a> ·
    <a href="http://lattes.cnpq.br/6696786236047929">Lattes</a> ·
    <a href="https://www.linkedin.com/in/gabriel-candido-235637226/">LinkedIn</a> ·
    <a href="mailto:gabrielcandidomds@gmail.com">Contact</a>
  </sub>
</div>
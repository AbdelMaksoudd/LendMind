

# 💳 LendMind: Aprobación de Préstamos y Evaluación de Riesgos con IA

**LendMind** es una plataforma de aprendizaje automático integral diseñada para automatizar y optimizar el proceso de solicitud de préstamos. Aprovechando datos financieros históricos, el sistema predice la probabilidad de aprobación de préstamos y sugiere límites de crédito apropiados.

---

## 🏗️ Arquitectura del Proyecto

El repositorio está organizado en una estructura de **Monorepo**, lo que garantiza una separación clara entre experimentos de ciencia de datos, lógica del backend e interfaces de usuario:

- **`notebooks/`**: Contiene cuadernos Jupyter documentados para ingeniería de datos y evaluación de modelos.
  - `01_data_preparation.ipynb`: Limpieza de datos y EDA (Análisis Exploratorio de Datos).
  - `02_build_and_evaluate_models.ipynb`: Entrenamiento de modelos y métricas de rendimiento.
- **`server/`**: Servidor web SSR construido con **FastAPI**.
- **`docs/`**: Documentación técnica y el archivo `LCDataDictionary.xlsx`.
- **`saved_models/`**: Modelos serializados y listos para producción (archivos `.pkl`).
- **`data/`**: (Solo local) Directorio para conjuntos de datos sin procesar.

---

## 🧠 Aspectos Destacados de Ingeniería de IA

Este proyecto implementa una canalización rigurosa de ingeniería de datos en múltiples etapas para garantizar la fiabilidad de los modelos y su preparación para producción:

*   **Preprocesamiento Integral de Datos**: Gestionado y limpiado un **conjunto de datos de 1.2 GB**, manejando **Valores Faltantes** complejos y asegurando la consistencia de los datos en más de 150 variables sin procesar.
*   **Prevención de Fugas de Datos**: Identificado y eliminado sistemáticamente más de 10 **Variables Post-Origen** (p. ej., `late fees`, `recoveries`) que no estarían disponibles en el momento de la solicitud, evitando el sesgo de "look-ahead".
*   **Ingeniería Inteligente de Características**: Se llevó a cabo un proceso de selección multicapa:
    - **Filtrado de Multicolinealidad**: Uso de matrices de correlación y VIF para eliminar características redundantes.
    - **Importancia Basada en Modelos**: Aprovechamiento de **Random Forest** para identificar las **15 "Características Doradas"** con mayor poder predictivo.
*   **Validación Robusta del Sistema**: Implementación de **Esquemas Pydantic** en el backend de FastAPI para imponer validación y tipado estrictos de datos, asegurando que el sistema se mantenga estable bajo diversos escenarios de entrada. (aún no)

---

## 📊 Configuración del Conjunto de Datos

El sistema se entrena con un masivo conjunto de datos histórico de préstamos (1.2 GB). Debido a los límites de tamaño de archivo de GitHub, `loan.csv` está excluido del repositorio.

### Opción 1: Descarga Automatizada (API de Kaggle)

Si tienes la CLI de Kaggle instalada, ejecuta los siguientes comandos en tu terminal:

```bash
mkdir data
kaggle datasets download -d [KA-KA-shi/Lending Club Loan Data] -p data/ --unzip
```

### Opción 2: Configuración Manual

1. Descarga el Conjunto de Datos desde [https://www.kaggle.com/datasets/adarshsng/lending-club-loan-data-csv].
2. Crea una carpeta llamada `DataSet/` en la raíz del proyecto.
3. Extrae y coloca `loan.csv` dentro de la carpeta `data/`.

---

## 🚀 Primeros Pasos

### 1. Configuración del Entorno

```bash
cd server
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Ejecutar el Servidor de Producción

```bash
python ./src/main.py
```

---

## 🛠️ Tecnologías Utilizadas

- **IA/ML**: Pandas, Scikit-Learn, Numpy, Joblib.
- **Backend**: FastAPI, WebSockets, Jinja2, SQLAlchemy, SQLite.
- **Control de Versiones**: Git & GitHub.
- **Herramientas**: VS Code, Jupyter Notebooks.


---

## 👥 El Equipo de Ingeniería

- **Mohamed Ahmed AbdelMaksoud** - Arquitectura de IA y Backend
  - [GitHub](https://github.com/AbdelMaksoudd) | [LinkedIn](https://www.linkedin.com/in/abdelmaksoudd)

- **Muhammad Lutfi** - Desarrollo Full-Stack
  - [GitHub](https://github.com/muhammadlutf1) | [LinkedIn](https://www.linkedin.com/in/muhammadlutf1)

---

© 2026 Proyecto LendMind - Dedicado a decisiones financieras más inteligentes.

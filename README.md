# 📊 Proyecto Final - Análisis Financiero con Ray, FastAPI y React

## Tabla de Contenidos

- [📋 Descripción del Proyecto](#-descripción-del-proyecto)
- [⚙️ Tecnologías utilizadas](#️-tecnologías-utilizadas)
- [🧪 Requisitos](#-requisitos)
- [🖼️ Vista previa](#️-vista-previa)
- [🔌 Endpoints Principales](#-endpoints-principales)
- [🐳 Ejecución con Docker](#-ejecución-con-docker)
- [💻 Instalación local](#-instalación-local)
- [🚀 Ejecución local](#-ejecución-local)
- [👨‍💻 Desarrolladores](#️-desarrolladores)

---

## 📋 Descripción del Proyecto
Este proyecto implementa dos estrategias de inversión financiera:

- **Estrategia de Sentimiento:** Construcción de portafolios mensuales basada en análisis de engagement de Twitter.
- **Estrategia Intradía:** Generación de señales de trading combinando modelos GARCH con indicadores técnicos (RSI + Bandas de Bollinger).

Está desarrollado con una arquitectura de microservicios, procesamiento paralelo con **Ray**, APIs con **FastAPI**, frontend en **React + TailwindCSS**, y completamente contenerizado con **Docker**, y desplegado en **AWS EC2**.

---

## ⚙️ Tecnologías utilizadas

- 🔄 **Ray & Ray Serve** – Paralelización y microservicios
- ⚡ **FastAPI** – backend de alto rendimiento
- 📈 **Pandas / Arch / TA** – Procesamiento de datos financieros
- 💻 **React + TailwindCSS** – Frontend moderno y responsivo
- 🐳 **Docker** – Contenerización y despliegue
- ☁️ **AWS EC2** – Instancia de nube para producción

---

## 🧪 Requisitos

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Cuenta en AWS (opcional para despliegue)

---

## 🖼️ Vista previa
![image](https://res.cloudinary.com/dprzfeoj8/image/upload/v1753935042/app-preview_ddq49a.png)


---

## 🔌 Endpoints Principales

### 📈 sentiment – Estrategia de sentimiento

- **GET /sentiment/returns/dates**  ➡️ Fechas disponibles para el análisis
- **GET /sentiment/returns/filter** ➡️  Retorna por rango de fechas
- **GET /sentiment/returns/filter/csv**   ➡️  Descarga retornos filtrados por fecha en formato csv
- **POST /sentiment/recalculate**    ➡️ Recalcula portafolio con criterio dinamico
- **GET /sentiment/compare**    ➡️ Compara rendimiento secuencial vs paralelo

### ⚡ intraday – Estrategia intradía

- **POST /intradaily/run-strategy**  ➡️ Ejecuta estrategia
- **GET /intradaily/dates** ➡️  Fechas disponibles para el análisis
- **GET /intradaily/returns** ➡️  Retorno acumulado
- **GET /intradaily/daily** ➡️  Retorno diario
- **GET /intradaily/returns/download**    ➡️  Descarga CSV del retorno actual
- **GET /intradaily/compare**    ➡️ Compara rendimiento secuencial vs paralelo

---

## 🐳 Ejecución con Docker

Asegurarse de tener docker instalado y encendido.

```bash
docker -v
```

Si no la tienes instalada descargala aquí.

https://www.docker.com/products/docker-desktop/

Inciar la aplicación
```bash
docker compose up --build
```

---

## 🚀 Accede a la app

Una vez levantados los contenedores, abre en tu navegador:

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend (API): [http://localhost:8000/docs](http://localhost:8000/docs) – Documentación automática de FastAPI


---

## 💻 Instalación local - Si no quieres usar Docker

### 1. Clona el repositorio

```bash
git clone https://github.com/DylanFarkas/proyecto-final-ml.git
```

```bash
cd proyecto-final-ml
```

### 2. Backend 
Asegurarse de tener python 3.10 instalado.

Creamos entorno virtual.

```bash
py -3.10 -m venv venv
```

Activamos entorno virtual.
- #### En Windows

```bash
venv/scripts/activate
```

- #### En Linux / Mac

```bash
source venv/bin/activate
```

Instalamos dependencias.

```bash
pip install -r requirements.txt
```

### 3. Frontend
Asegurarse de tener node Instalado.

```bash
node -v
```

Si no está instalado, instalalo aquí.

https://nodejs.org/en/download


Ingresar a la carpeta.
```bash
cd Client
```

Instalar dependencias.
```bash
npm install
```
---

## 🚀 Ejecución local

### 1. Inicia el backend

Desde la raiz del proyecto

```bash
python -m api.main
```

### 2. Inicia el Frontend

Desde la carpeta Client

```bash
npm run dev
```

Ingresa a las siguientes urls.

- Frontend: [http://localhost:5173](http://localhost:5173)
- Backend (API): [http://localhost:8000/docs](http://localhost:8000/docs) – Documentación automática de FastAPI

---

## 👨‍💻 Desarrolladores

Este proyecto fue desarrollado como parte del curso de **Infraestructuras Paralelas y Distribuidas de la Universidad del Valle**.

|         Nombre      |            GitHub               |
|---------------------|---------------------------------|
| Juan Manuel García  | https://github.com/jgarcia9300  |
| Esteban Espinosa    | https://github.com/Esteban93040 |
| Dylan Farkas        | https://github.com/DylanFarkas  |

---
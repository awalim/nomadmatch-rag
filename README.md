# 🌍 NomadMatch · Encuentra tu ciudad europea ideal

![Version](https://img.shields.io/badge/version-5.0.0-blueviolet?style=for-the-badge)
![Stack](https://img.shields.io/badge/stack-RAG%20%7C%20ChromaDB%20%7C%20FastAPI-6E56CF?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**✨ Sistema de recomendación de ciudades para nómadas digitales con IA y matching semántico ✨**

*🇪🇸 Español · [English](#-english)*

---

## 🎯 ¿Qué es NomadMatch?

**NomadMatch** es un sistema RAG (Retrieval-Augmented Generation) que ayuda a nómadas digitales a encontrar su ciudad europea ideal.

Los usuarios seleccionan sus preferencias (presupuesto, clima, internet, visa, ambiente) y el sistema encuentra **las 3 ciudades con mejor matching** usando embeddings semánticos y búsqueda por similitud vectorial.

---

## ✨ Características

| Feature | Descripción |
|---------|-------------|
| 🎨 **Diseño Premium** | Interfaz moderna con gradientes, glows y modo oscuro |
| 🔍 **Matching Semántico** | Embeddings de OpenAI (`text-embedding-3-small`) + ChromaDB |
| 🏙️ **50+ Ciudades** | Dataset completo de ciudades europeas con +90 atributos |
| 🖼️ **Fotos Reales** | Thumbnails por ciudad |
| 📱 **Responsive** | Funciona en móvil, tablet y desktop |
| 🔐 **Autenticación JWT** | Registro, login, perfil y upgrade a premium |
| 💎 **Tier Premium** | Datos exclusivos de visados y fiscalidad por ciudad |
| ❤️ **Match / Skip** | Sistema de favoritos tipo Tinder con persistencia en BD |
| 📂 **Auto-ingesta** | Los CSVs se cargan automáticamente al levantar Docker |
| 🐳 **Full Docker** | Un solo `docker-compose up` y listo |

---

## 🏗️ Arquitectura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│  ChromaDB   │
│  Nginx      │     │   FastAPI   │     │  Vectores   │
│  Port 3000  │◀────│  Port 8000  │◀────│  Embeddings │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   SQLite    │     ┌─────────────┐
                    │  Users DB   │     │   OpenAI    │
                    └─────────────┘     │  Embeddings │
                                        └─────────────┘
```

**Stack técnico:**
- **Frontend:** Vanilla JS + CSS (servido por Nginx)
- **Backend:** FastAPI + Uvicorn
- **Base de datos vectorial:** ChromaDB (persistente)
- **Base de datos usuarios:** SQLite + SQLAlchemy
- **Embeddings:** OpenAI `text-embedding-3-small` (1536 dims)
- **Autenticación:** JWT (python-jose + bcrypt)
- **Contenedores:** Docker Compose

---

## 🚀 Instalación rápida (3 minutos)

### Prerrequisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y ejecutándose
- [Git](https://git-scm.com/)
- [OpenAI API Key](https://platform.openai.com/api-keys)

### 1. Clonar el repositorio

```bash
git clone https://github.com/awalim/nomadmatch-rag.git
cd nomadmatch-rag
git checkout feature/prototipo-5
```

### 2. Configurar la API Key de OpenAI

**Windows (CMD):**
```bash
set OPENAI_API_KEY=sk-proj-TU_CLAVE_AQUI
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-TU_CLAVE_AQUI"
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY=sk-proj-TU_CLAVE_AQUI
```

### 3. Levantar el sistema

```bash
docker-compose up --build -d
```

### 4. ¡Listo!

| Servicio | URL |
|----------|-----|
| 🌐 **Frontend** | http://localhost:3000 |
| ⚙️ **Backend API** | http://localhost:8000 |
| 📖 **Documentación API** | http://localhost:8000/docs |

> **Nota:** Los datos se ingestarán automáticamente en ChromaDB al arrancar. Verifica con: `docker-compose logs -f backend`

---

## 📁 Estructura del proyecto

```
nomadmatch-rag/
├── 📁 backend/                    # FastAPI + ChromaDB + Auth
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── auth.py           # Autenticación JWT (register/login/upgrade)
│   │   │   ├── deps.py           # Dependencias compartidas (get_db, get_current_user)
│   │   │   └── routes.py         # Endpoints REST (query, upload, preferences, premium)
│   │   ├── 📁 core/
│   │   │   └── config.py         # Configuración (CORS, API keys)
│   │   ├── 📁 models/
│   │   │   ├── schemas.py        # Schemas Pydantic
│   │   │   └── user.py           # Modelos SQLAlchemy (User, CityPreference)
│   │   ├── 📁 utils/
│   │   │   ├── chroma_utils.py   # ChromaManager (ingesta, búsqueda, scoring)
│   │   │   ├── llm_utils.py      # Generación de respuestas con OpenAI
│   │   │   └── scoring.py        # Scoring fiscal y de visados
│   │   └── main.py               # Punto de entrada + auto-ingesta
│   ├── 📁 data/
│   │   └── cities.csv            # Dataset interno (50 ciudades)
│   ├── Dockerfile
│   └── requirements.txt
├── 📁 data/                       # Datasets externos (montados en Docker)
│   ├── city_general_free.csv     # 50 ciudades · 91 columnas · Tier FREE
│   ├── city_tax_premium.csv      # 47 ciudades · 17 columnas · Tier PREMIUM (fiscalidad)
│   └── city_visa_premium.csv     # 47 ciudades · 18 columnas · Tier PREMIUM (visados)
├── 📁 frontend/
│   ├── 📁 public/
│   │   ├── index.html            # HTML principal
│   │   ├── app.js                # Lógica JS (auth, búsqueda, Match/Skip, Favs)
│   │   ├── styles.css            # Estilos principales
│   │   ├── premium-styles.css    # Estilos premium
│   │   ├── city-images.json      # Mapeo ciudad → imagen
│   │   └── 📁 thumbnails/       # 50 fotos de ciudades
│   └── Dockerfile                # Nginx Alpine
├── 📁 langflow/                   # Flow export (opcional)
├── docker-compose.yml             # Orquestación Docker
└── README.md                      # Este archivo
```

---

## 🔧 API Endpoints

### Públicos (sin autenticación)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | Estado del sistema y ChromaDB |
| `GET` | `/api/v1/collections` | Info de colecciones y documentos |
| `POST` | `/api/v1/upload` | Subir e ingestar un CSV |
| `POST` | `/api/v1/query` | Búsqueda semántica + ranking |
| `POST` | `/api/v1/chat` | Chat con recomendaciones |

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Crear cuenta |
| `POST` | `/api/v1/auth/login` | Iniciar sesión → JWT token |
| `GET` | `/api/v1/auth/me` | Perfil del usuario actual |
| `PUT` | `/api/v1/auth/preferences` | Actualizar preferencias |
| `POST` | `/api/v1/auth/upgrade` | Upgrade a Premium |

### Preferencias de ciudades (requiere login)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/preferences/city` | Guardar Match (like) o Skip (dislike) |
| `GET` | `/api/v1/preferences/cities` | Obtener likes y dislikes |
| `DELETE` | `/api/v1/preferences/city/{name}` | Eliminar preferencia |

### Premium (requiere login + premium)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/premium/advice` | Datos de visados y fiscalidad |

> 📖 Documentación interactiva completa en: http://localhost:8000/docs

---

## 📊 Datasets

El proyecto incluye **3 CSVs** con datos de 50 ciudades eur

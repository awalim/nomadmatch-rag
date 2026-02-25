<div align="center">
  <img src="https://github.com/awalim/nomadmatch-rag/blob/prototipo-5/frontend/public/logo-nomadmatch-darkbg-trans.png?raw=true" alt="NomadMatch Logo" width="250"/>
  <h1>Encuentra tu Ciudad Europea Ideal</h1>
</div>

![Version](https://img.shields.io/badge/version-5.0.0-blueviolet?style=for-the-badge)
![Stack](https://img.shields.io/badge/stack-RAG%20%7C%20ChromaDB%20%7C%20FastAPI-6E56CF?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## 🇪🇸 Español <a name="spanish"></a>
*🇪🇸 Español · [🇬🇧 English](#english)*

**✨ Sistema de recomendación de ciudades para nómadas digitales con IA y matching semántico ✨**

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
git checkout prototipo-5
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
├── 📁 data/                      # Datasets externos (montados en Docker)
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
│   │   └── 📁 thumbnails/        # 50 fotos de ciudades
│   └── Dockerfile                # Nginx Alpine
├── 📁 langflow/                  # Flow export (opcional)
├── docker-compose.yml            # Orquestación Docker
└── README.md                     # Este archivo
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

El proyecto incluye **3 CSVs** con datos de 50 ciudades europeas:

### `city_general_free.csv` (91 columnas)
Datos generales accesibles para todos los usuarios:
- 💰 **Costos:** Alquiler (studio, 1BR, 2BR, 3BR), presupuesto mensual, coworking
- 📶 **Internet:** Velocidad (Mbps), fiabilidad
- 🌡️ **Clima:** Temperatura por estación, horas de sol, lluvia, humedad
- 🏥 **Vida:** Seguridad, sanidad, transporte, bici, walkability
- 👥 **Comunidad:** Tamaño expat, escena nómada, nivel de inglés
- 🎨 **Vibes:** Nightlife, dating, familia, startup, outdoor, arte, LGBTQ+

### `city_visa_premium.csv` (18 columnas)
Datos exclusivos premium sobre visados nómada digital:
- 🛂 Tipo de visa, duración, elegibilidad
- 💶 Requisito de ingresos mínimos
- 📅 Estancia mínima/máxima
- 🇪🇺 Zona Schengen

### `city_tax_premium.csv` (17 columnas)
Datos exclusivos premium sobre fiscalidad:
- 📊 Tasa impositiva estándar y especial
- 🏛️ Regímenes especiales (NHR, Beckham Law, IP Box, etc.)
- ⏰ Años de beneficio fiscal
- 🏆 Scoring fiscal y global

---

## ❤️ Sistema Match / Skip

Los usuarios registrados pueden interactuar con las ciudades:

- **❤️ Match:** Marca la ciudad como favorita (botón rojo). La tarjeta permanece visible.
- **✖️ Skip:** Descarta la ciudad (animación slide-out). Se oculta del feed.
- **📋 Pestaña Favs:** Lista de Matches y Skips. Se puede cambiar de opinión o eliminar.
- **🔄 Cambio de opinión:** Mover de Skip a Match (o viceversa) actualiza el feed automáticamente.

---

## 🧑‍💻 Flujo de trabajo para el equipo

### Ramas

| Rama | Uso |
|------|-----|
| `main` | Producción, siempre estable |
| `develop` | Integración de features |
| `feature/*` | Features nuevas (ej: `feature/prototipo-5`) |

### Convención de commits

```
feat:     Nueva funcionalidad
fix:      Corrección de bug
style:    Cambios de formato, CSS
refactor: Refactorización de código
docs:     Documentación
chore:    Cambios en build, docker, etc.
```

### Para añadir una feature

```bash
git checkout -b feature/nueva-funcionalidad
# ... trabajar ...
git add .
git commit -m "feat: descripción de la feature"
git push origin feature/nueva-funcionalidad
# → Crear Pull Request en GitHub
```

---

## 🐛 Troubleshooting

### Docker Desktop no está corriendo
```
open //./pipe/dockerDesktopLinuxEngine: El sistema no puede encontrar el archivo especificado
```
→ Abre Docker Desktop y espera a que esté listo antes de `docker-compose up`.

### Puerto ya ocupado
```
Bind for 0.0.0.0:3000 failed: port is already allocated
```
→ Ejecuta `docker ps --filter "publish=3000"`, para el contenedor que lo usa, o cambia el puerto en `docker-compose.yml`.

### API Key inválida (error 401 en ingesta)
```
Incorrect API key provided: sk-tu-cl****aqui
```
→ Configura tu API key real: `set OPENAI_API_KEY=sk-proj-TU_CLAVE_REAL` y haz `docker-compose down && docker-compose up --build -d`.

### ChromaDB vacío después de reiniciar
→ Los datos se persisten en un volumen Docker (`chroma_data`). Si eliminaste el volumen (`docker-compose down -v`), la auto-ingesta los recargará al siguiente arranque.

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'feat: add amazing feature'`)
4. Push (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

---

## 👥 Creadores

- **Jana Liscakova**
- **Aitor Laskurain González**
- **Andrea de la Dehesa Demaría**

---

## 📄 Licencia

MIT © 2026 NomadMatch Team

---

## 🇬🇧 English <a name="english"></a>
*[🇪🇸 Español](#spanish) · [🇬🇧 English](#english)*

<div align="center">
  <img src="https://github.com/awalim/nomadmatch-rag/blob/prototipo-5/frontend/public/logo-nomadmatch-darkbg-trans.png?raw=true" alt="NomadMatch Logo" width="250"/>
  <h1>Find Your Perfect European City</h1>
</div>

![Version](https://img.shields.io/badge/version-5.0.0-blueviolet?style=for-the-badge)
![Stack](https://img.shields.io/badge/stack-RAG%20%7C%20ChromaDB%20%7C%20FastAPI-6E56CF?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**✨ City matching system for digital nomads with AI and semantic matching ✨**


---

## 🎯 ¿What is NomadMatch?

**NomadMatch** is a RAG (Retrieval-Augmented Generation) system that helps digital nomads find their ideal European city.

Users select their preferences (budget, climate, visa, atmosphere) and the system finds **the 3 best-matching cities** using semantic embeddings and vector similarity search.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎨 **Premium Design** | Modern interface with gradients, glows, and dark mode |
| 🔍 **Semantic Matching** | OpenAI embeddings (`text-embedding-3-small`) + ChromaDB |
| 🏙️ **50+ Cities** | Complete dataset of European cities with +90 attributes |
| 🖼️ **Real Photos** | Thumbnails per city |
| 📱 **Responsive** | Works on mobile, tablet, and desktop |
| 🔐 **JWT Authentication** | Registration, login, profile, and upgrade to premium |
| 💎 **Premium Tier** | Exclusive visa and tax data by city |
| ❤️ **Match / Skip** | Tinder-style favorites system with persistence in DB |
| 📂 **Auto-ingestion** | CSVs are automatically loaded when Docker is launched |
| 🐳 **Full Docker** | Just one `docker-compose up` and you're ready to go |


---

## 🏗️ Arquitecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│  ChromaDB   │
│  Nginx      │     │   FastAPI   │     │  Vectors   │
│  Port 3000  │◀────│  Port 8000  │◀────│  Embeddings │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    │   SQLite    │     ┌─────────────┐
                    │  Users DB   │     │   OpenAI    │
                    └─────────────┘     │  Embeddings │
                                        └─────────────┘
```

**Technical stack:**
- **Frontend:** Vanilla JS + CSS (served by Nginx)
- **Backend:** FastAPI + Uvicorn
- **Vector database:** ChromaDB (persistent)
- **User database:** SQLite + SQLAlchemy
- **Embeddings:** OpenAI `text-embedding-3-small` (1536 dims)
- **Authentication:** JWT (python-jose + bcrypt)
- **Containers:** Docker Compose

---

## 🚀 Quick Installation (3 minutes)

### Prerrequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y ejecutándose
- [Git](https://git-scm.com/)
- [OpenAI API Key](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/awalim/nomadmatch-rag.git
cd nomadmatch-rag
git checkout prototype-5
```

### 2. Configure the OpenAI API Key

**Windows (CMD):**
```bash
set OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY=“sk-proj-YOUR_KEY_HERE”
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

### 3. Build up the system

```bash
docker-compose up --build -d
```

### 4. Done!

| Service | URL |
|----------|-----|
| 🌐 **Frontend** | http://localhost:3000 |
| ⚙️ **Backend API** | http://localhost:8000 |
| 📖 **API Documentation** | http://localhost:8000/docs |

> **Note:** Data will be automatically ingested into ChromaDB upon startup. Verify with: `docker-compose logs -f backend`

---

## 📁 Project structure

```
nomadmatch-rag/
├── 📁 backend/                   # FastAPI + ChromaDB + Auth
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── auth.py           # JWT authentication (register/login/upgrade)
│   │   │   ├── deps.py           # Shared dependencies (get_db, get_current_user)
│   │   │   └── routes.py         # REST endpoints (query, upload, preferences, premium)
│   │   ├── 📁 core/
│   │   │   └── config.py         # Configuration (CORS, API keys)
│   │   ├── 📁 models/
│   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   └── user.py           # SQLAlchemy models (User, CityPreference)
│   │   ├── 📁 utils/
│   │   │   ├── chroma_utils.py   # ChromaManager (ingestion, search, scoring)
│   │   │   ├── llm_utils.py      # Response generation with OpenAI
│   │   │   └── scoring.py        # Tax and visa scoring
│   │   └── main.py               # Entry point + auto-ingest
│   ├── 📁 data/
│   │   └── cities.csv            # Internal dataset (50 cities)
│   ├── Dockerfile
│   └── requirements.txt
├── 📁 data/                      # External datasets (mounted in Docker)
│   ├── city_general_free.csv     # 50 cities · 91 columns · FREE Tier
│   ├── city_tax_premium.csv      # 47 cities · 17 columns · PREMIUM Tier (taxation)
│   └── city_visa_premium.csv     # 47 cities · 18 columns · PREMIUM Tier (visas)
├── 📁 frontend/
│   ├── 📁 public/
│   │   ├── index.html            # Main HTML
│   │   ├── app.js                # JS logic (auth, search, Match/Skip, Favs)
│   │   ├── styles.css            # Main styles
│   │   ├── premium-styles.css    # Premium styles
│   │   ├── city-images.json      # City → image mapping
│   │   └── 📁 thumbnails/        # 50 city photos
│   └── Dockerfile                # Nginx Alpine
├── 📁 langflow/                  # Flow export (optional)
├── docker-compose.yml            # Docker orchestration
└── README.md                     # This file

```

---

## 🔧 API Endpoints

### Public (no authentication required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health` | System status and ChromaDB |
| `GET` | `/api/v1/collections` | Collection and document info |
| `POST` | `/api/v1/upload` | Upload and ingest a CSV |
| `POST` | `/api/v1/query` | Semantic search + ranking |
| `POST` | `/api/v1/chat` | Chat with recommendations |

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/auth/register` | Create account |
| `POST` | `/api/v1/auth/login` | Log in → JWT token |
| `GET` | `/api/v1/auth/me` | Current user profile |
| `PUT` | `/api/v1/auth/preferences` | Update preferences |
| `POST` | `/api/v1/auth/upgrade` | Upgrade to Premium |

### City preferences (requires login)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/preferences/city` | Save Match (like) or Skip (dislike) |
| `GET` | `/api/v1/preferences/cities` | Get likes and dislikes |
| `DELETE` | `/api/v1/preferences/city/{name}` | Delete preference |

### Premium (requires login + premium)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/premium/advice` | Visa and tax data |

> 📖 Complete interactive documentation at: http://localhost:8000/docs

---


## 📊 Datasets

The project includes **3 CSVs** with data from 50 European cities:

### `city_general_free.csv` (91 columns)
General data accessible to all users:
- 💰 **Costs:** Rent (studio, 1BR, 2BR, 3BR), monthly budget, coworking
- 📶 **Internet:** Speed (Mbps), reliability
- 🌡️ **Climate:** Temperature by season, hours of sunshine, rainfall, humidity
- 🏥 **Life:** Safety, healthcare, transportation, biking, walkability
- 👥 **Community:** Expat size, nomad scene, English level
- 🎨 **Vibes:** Nightlife, dating, family, startups, outdoors, art, LGBTQ+

### `city_visa_premium.csv` (18 columns)
Exclusive premium data on digital nomad visas:
- 🛂 Visa type, duration, eligibility
- 💶 Minimum income requirement
- 📅 Minimum/maximum stay
- 🇪🇺 Schengen area

### `city_tax_premium.csv` (17 columns)
Exclusive premium data on taxation:
- 📊 Standard and special tax rates
- 🏛️ Special regimes (NHR, Beckham Law, IP Box, etc.)
- ⏰ Years of tax benefits
- 🏆 Tax and global scoring

---

### ❤️ Match/Skip System

Registered users can interact with cities:

- ❤️ Match: Mark the city as a favourite (red button). The card remains visible.
- **✖️ Skip:** Discard the city (slide-out animation). It is hidden from the feed.
- **📋 Favs tab:** List of Matches and Skips. You can change your mind or delete.
- **🔄 Change of mind:** Moving from Skip to Match (or vice versa) automatically updates the feed.

---

## 🧑‍💻 Workflow for the team

### Branches

| Branch | Use |
|------|-----|
| `main` | Production, always stable |
| `develop` | Feature integration |
| `feature/*` | New features (e.g., `feature/prototype-5`) |

### Commit convention

```
feat:     New functionality
fix:      Bug fix
style:    Formatting changes, CSS
refactor: Code refactoring
docs:     Documentation
chore:    Changes to build, docker, etc.
```

### To add a feature

```bash
git checkout -b feature/new-functionality
# ... work ...
git add .
git commit -m “feat: feature description”
git push origin feature/new-functionality
# → Create Pull Request on GitHub
```

---

## 🐛 Troubleshooting

### Docker Desktop is not running
```
open //./pipe/dockerDesktopLinuxEngine: The system cannot find the specified file
```
→ Open Docker Desktop and wait for it to be ready before running `docker-compose up`.

### Port already in use
```
Bind for 0.0.0.0:3000 failed: port is already allocated
```
→ Run `docker ps --filter “publish=3000”`, stop the container that is using it, or change the port in `docker-compose.yml`.

### Invalid API Key (error 401 on ingestion)
```
Incorrect API key provided: sk-tu-cl****here
```
→ Set your real API key: `set OPENAI_API_KEY=sk-proj-YOUR_REAL_KEY` and run `docker-compose down && docker-compose up --build -d`.

### ChromaDB empty after restarting
→ Data is persisted in a Docker volume (`chroma_data`). If you deleted the volume (`docker-compose down -v`), auto-ingest will reload it on the next startup.

---

## 🤝 Contribute

1. Fork the project
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m ‘feat: add amazing feature’`)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 👥 Creators

- **Jana Liscakova**
- **Aitor Laskurain González**
- **Andrea de la Dehesa Demaría**

---

## 📄 Licence

MIT © 2026 NomadMatch Team

---




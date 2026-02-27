## :es: Español <a name="spanish"></a>
*:es: Español · [:gb: English](#english)*

<div align="center">
  <img src="https://github.com/awalim/nomadmatch-rag/blob/prototipo-5/frontend/public/logo_nomadmatch_banner.png?raw=true" alt="NomadMatch Logo" width="750"/>
  <h1>Encuentra tu Ciudad Europea Ideal</h1>
</div>

![Version](https://img.shields.io/badge/version-5.2.0-blueviolet?style=for-the-badge)
![Stack](https://img.shields.io/badge/stack-RAG%20%7C%20ChromaDB%20%7C%20Langflow%20%7C%20FastAPI-6E56CF?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**✨ Sistema de recomendación de ciudades para nómadas digitales con IA conversacional, aprendizaje por swipes y lógica de tier free/premium ✨**

---

## 🎯 ¿Qué es NomadMatch?

**NomadMatch** es un sistema RAG (Retrieval-Augmented Generation) que ayuda a nómadas digitales a encontrar su ciudad europea ideal.

El usuario selecciona sus preferencias en un onboarding visual (presupuesto, clima, visa nómada, ambiente) y el sistema devuelve **5 tarjetas swipeables** con el porcentaje de match, descripción personalizada y desglose de costes. Cada swipe enseña al sistema cuáles ciudades le gustan al usuario — las siguientes recomendaciones mejoran automáticamente con cada interacción.

---

## ✨ Características

| Feature | Descripción |
|---------|-------------|
| 🧠 **RAG + LLM** | ChromaDB recupera candidatos → GPT-4o-mini razona, puntúa y genera respuestas personalizadas |
| 🃏 **Output card/detail** | Cada ciudad tiene una tarjeta swipeable (card) y un panel expandible con datos completos (detail) |
| 📈 **Aprendizaje por swipes** | El sistema detecta patrones entre ciudades con MATCHED/SKIPPED y ajusta las siguientes recomendaciones |
| 🔒 **Tier free/premium** | Visa, fiscalidad y consejo fiscal bloqueados hasta upgrade. Desbloqueados con `tier:premium` |
| 🗺️ **50+ Ciudades** | Dataset con 91 atributos por ciudad (costes, clima, seguridad, comunidad nómada, vibes) |
| 🌡️ **Pre-filtros duros** | Clima y presupuesto son filtros obligatorios antes del scoring — nunca aparecen ciudades que los violen |
| 💬 **Memoria conversacional** | Langflow Message History almacena el historial de la sesión y lo pasa al LLM en cada llamada |
| 🔐 **Autenticación JWT** | Registro, login, upgrade a premium. Swipes persistidos en SQLite por usuario |
| 📂 **Auto-ingesta** | Los CSVs se cargan automáticamente al levantar Docker |
| 🐳 **Full Docker** | Un solo `docker-compose up --build -d` y listo |
| 🔄 **Flows exportados** | Los flows de Langflow (Load + Retrieve) están en `/flows` listos para importar |

---

## 🏗️ Arquitectura

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│    Frontend      │─────▶│    Backend       │─────▶│    ChromaDB      │
│  Vanilla JS/CSS  │      │    FastAPI       │      │   50 ciudades    │
│    Port 3000     │◀─────│    Port 8000     │◀─────│   Embeddings     │
└──────────────────┘      └────────┬─────────┘      └──────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
             ┌──────▼──────┐             ┌────────▼────────┐
             │   SQLite    │             │    Langflow     │
             │  Users +    │             │  Retrieve Flow  │
             │  Swipes DB  │             │  GPT-4o-mini    │
             └─────────────┘             └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │   OpenAI API    │
                                         │  Embeddings +   │
                                         │  Chat           │
                                         └─────────────────┘
```

**Stack técnico:**
- **Frontend:** Vanilla JS + CSS (servido por Nginx)
- **Backend:** FastAPI + Uvicorn
- **RAG engine:** Langflow + ChromaDB
- **LLM:** GPT-4o-mini (recomendaciones) + `text-embedding-3-small` (embeddings, 1536 dims)
- **Base de datos usuarios:** SQLite + SQLAlchemy
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
git checkout prototype-5-v2
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
│   │   │   ├── auth.py            # Autenticación JWT (register/login/upgrade)
│   │   │   ├── deps.py            # Dependencias compartidas (get_db, get_current_user)
│   │   │   └── routes.py          # Endpoints REST (query, upload, preferences, premium)
│   │   ├── 📁 core/
│   │   │   ├── config.py          # Configuración (CORS, API keys)
│   │   │   └── langflow_client.py # Cliente HTTP para llamar a Langflow
│   │   ├── 📁 models/
│   │   │   ├── schemas.py         # Schemas Pydantic
│   │   │   └── user.py            # Modelos SQLAlchemy (User, CityPreference)
│   │   ├── 📁 utils/
│   │   │   ├── chroma_utils.py    # ChromaManager (ingesta, búsqueda, scoring)
│   │   │   ├── llm_utils.py       # Generación de respuestas con OpenAI
│   │   │   └── scoring.py         # Scoring fiscal y de visados
│   │   └── main.py                # Punto de entrada + auto-ingesta
│   ├── 📁 data/
│   │   └── cities.csv             # Dataset interno (50 ciudades)
│   ├── Dockerfile
│   └── requirements.txt
├── 📁 data/                       # Datasets externos (montados en Docker)
│   ├── city_general_free.csv      # 50 ciudades · 91 columnas · Tier FREE
│   ├── city_tax_premium.csv       # 47 ciudades · 17 columnas · Tier PREMIUM (fiscalidad)
│   └── city_visa_premium.csv      # 47 ciudades · 18 columnas · Tier PREMIUM (visados)
├── 📁 flows/                          # ⭐ NUEVO en prototype-5-v2
│   ├── nomadmatch_load_flow.json      # Flow de ingesta: CSVs → ChromaDB
│   └── nomadmatch_retrieve_flow.json  # Flow de recomendación: query → LLM → JSON
├── 📁 langflow/                   # Flow legacy (referencia)
│   └── nomadmatch_langflow.json
├── 📁 frontend/
│   ├── 📁 public/
│   │   ├── index.html             # HTML principal
│   │   ├── app.js                 # Lógica JS (auth, búsqueda, Match/Skip, Favs)
│   │   ├── styles.css             # Estilos principales
│   │   ├── premium-styles.css     # Estilos premium
│   │   ├── city-images.json       # Mapeo ciudad → imagen
│   │   └── 📁 thumbnails/         # 50 fotos de ciudades
│   └── Dockerfile                 # Nginx Alpine
├── docker-compose.yml             # Orquestación Docker
└── README.md                      # Este archivo
```

---

## 🔄 Cómo funciona el sistema RAG

### Flujo completo de una recomendación

```
1. Usuario completa onboarding en el frontend
        ↓
2. Frontend envía PROFILE al endpoint de Langflow
   PROFILE: tier:free|budget_range:900-1200|climate:warm|
            visa_needed:true|vibes:beach,historical,tech_hub|
            nationality:US|tax_optimization:false
        ↓
3. ChromaDB recupera los 20 candidatos más similares
        ↓
4. Langflow Prompt (8 pasos) ejecuta:
   - STEP 1: Detecta tipo de input (PROFILE / MATCHED / SKIPPED)
   - STEP 2: Extrae perfil del usuario
   - STEP 3: Lee historial de swipes y detecta patrones
   - STEP 4: Pre-filtro duro de clima y presupuesto
   - STEP 5: Construye lista de exclusión (ciudades ya vistas)
   - STEP 6: Scoring interno 0-100 por ciudad
   - STEP 7: Aplica reglas de tier (free → locked_premium)
   - STEP 8: Devuelve JSON card/detail
        ↓
5. Frontend renderiza 5 tarjetas swipeables
        ↓
6. Usuario swipea → MATCHED/SKIPPED enviado a Langflow
        ↓
7. Message History Store guarda respuesta del LLM
        ↓
8. Next call: LLM lee historial → excluye ciudades vistas
              → detecta patrones → mejora recomendaciones
```

### Formato de mensajes al RAG

**Primera llamada (onboarding):**
```
PROFILE: tier:free|budget_range:900-1200|climate:warm|visa_needed:true|vibes:beach,historical,tech_hub|nationality:US|tax_optimization:false
```

| Campo | Opciones |
|-------|----------|
| `tier` | `free`, `premium` |
| `budget_range` | `<900`, `900-1200`, `1200-1600`, `1600-2000` |
| `climate` | `warm`, `cool`, `cold` |
| `visa_needed` | `true`, `false` |
| `vibes` | `beach`, `nightlife`, `historical`, `nature`, `tech_hub`, `foodie`, `art`, `sports` |
| `nationality` | nombre o código de país |
| `tax_optimization` | `true`, `false` |

**Swipe derecha:** `MATCHED: Seville`

**Swipe izquierda:** `SKIPPED: Barcelona`

### Payload Langflow

```json
{
  "input_value": "PROFILE: tier:free|budget_range:900-1200|climate:warm|visa_needed:true|vibes:beach,historical,tech_hub|nationality:US|tax_optimization:false",
  "session_id": "user_abc123",
  "input_type": "chat",
  "output_type": "chat"
}
```

> El `session_id` debe ser el ID del usuario — constante durante toda la sesión para que el historial persista.

---

## 📊 Estructura del JSON de output

```json
{
  "revealed_preferences": "User prefers warm affordable Spanish cities with beach and cultural vibes",
  "show_upgrade_prompt": true,
  "cities": [
    {
      "card": {
        "city": "Seville",
        "country": "Spain",
        "match_percentage": 85,
        "monthly_cost_eur": 1100,
        "vibe_tags": ["Flamenco", "Sunny", "Historical", "Tapas"],
        "hero_description": "La capital andaluza donde la cultura y el sol se fusionan con un coste de vida imbatible.",
        "top_reasons": [
          "You will enjoy a warm Mediterranean climate year-round.",
          "You can access the Spanish Digital Nomad Visa programme.",
          "You will find affordable coworking spaces in a vibrant cultural scene."
        ]
      },
      "detail": {
        "about": "Seville combines stunning Moorish architecture with a passionate local culture...",
        "climate": "Hot Mediterranean summers averaging 35°C, mild winters around 12°C.",
        "internet": 100,
        "community": "medium",
        "safety": "Safe",
        "cost_breakdown": {
          "rent_monthly_eur": 650,
          "food_monthly_eur": 300,
          "transport_monthly_eur": 50,
          "coworking_monthly_eur": 100
        },
        "best_neighbourhoods": ["Santa Cruz", "Triana"],
        "coworking_spaces": ["Coco Sevilla", "Espacio Open"],
        "nomad_events": "Regular meetups and networking events throughout the year.",
        "visa_section": "locked_premium",
        "tax_section": "locked_premium",
        "fiscal_tip": "locked_premium"
      }
    }
  ]
}
```

**Campos por tier:**

| Campo | Free | Premium |
|-------|------|---------|
| `card.*` | ✅ completo | ✅ completo |
| `detail.cost_breakdown` | ✅ visible | ✅ visible |
| `detail.visa_section` | 🔒 `locked_premium` | ✅ datos reales |
| `detail.tax_section` | 🔒 `locked_premium` | ✅ datos reales |
| `detail.fiscal_tip` | 🔒 `locked_premium` | ✅ consejo accionable |
| `show_upgrade_prompt` | `true` | `false` |

---

## 📊 Datasets

El proyecto incluye **3 CSVs** con datos de 50 ciudades europeas:

### `city_general_free.csv` (91 columnas)
Datos generales accesibles para todos los usuarios:
- 💰 **Costos:** Alquiler (studio, 1BR, 2BR, 3BR), presupuesto mensual, coworking
- 🌡️ **Clima:** Temperatura por estación, horas de sol, lluvia, humedad
- 🏥 **Vida:** Seguridad, sanidad, transporte, bici, walkability
- 👥 **Comunidad:** Tamaño expat, escena nómada, Nomad List Rating, nivel de inglés
- 🎨 **Vibes:** Nightlife, dating, familia, startup, outdoor, arte, LGBTQ+

### `city_visa_premium.csv` (18 columnas)
Datos exclusivos premium sobre visados nómada digital:
- 🛂 Tipo de visa, duración, elegibilidad por nacionalidad
- 💶 Requisito de ingresos mínimos en EUR
- 📅 Estancia mínima/máxima
- 🇪🇺 Zona Schengen

### `city_tax_premium.csv` (17 columnas)
Datos exclusivos premium sobre fiscalidad:
- 📊 Tasa impositiva estándar y especial
- 🏛️ Regímenes especiales (NHR, Beckham Law, IP Box, etc.)
- ⏰ Años de beneficio fiscal
- 🏆 Scoring fiscal y global

---

## ⚙️ Scoring del RAG

El prompt ejecuta un scoring interno de 0 a 100 para cada ciudad. El usuario solo ve el `match_percentage` final.

| Dimensión | Pts máx | Descripción |
|-----------|---------|-------------|
| Budget fit | 25 | Ciudad dentro del rango declarado = 25 pts |
| Vibe match | 15 | 3 pts por cada vibe del usuario que coincide con la ciudad |
| Climate match | 15 | Exacto=15, adyacente=10, opuesto=0 |
| Visa match | 10 | DNV disponible para la nacionalidad = 10 pts |
| Nomad community | 10 | Nomad List Rating ≥ 4.0 = 10 pts |
| Safety | 5 | Safety Index ≥ 70 = 5 pts |
| Revealed preference bonus | +20 | Aplicado tras 2+ swipes con patrón detectado |
| Tax regime *(solo premium)* | +10 | NHR, Beckham Law, IP Box, flat tax = 10 pts |

**Pre-filtros duros (antes del scoring):**
- `climate:warm` → eliminadas todas las ciudades del norte y centro de Europa
- Budget ceiling: `900-1200` → máximo €1.380 (+15%), `1200-1600` → máximo €1.840, etc.
- Ciudades ya vistas en la sesión → excluidas permanentemente

---

## ❤️ Sistema Match / Skip

Los usuarios registrados pueden interactuar con las ciudades:

- **❤️ Match:** Marca la ciudad como favorita. La tarjeta permanece visible.
- **✖️ Skip:** Descarta la ciudad (animación slide-out). Se oculta del feed.
- **📋 Pestaña Favs:** Lista de Matches y Skips. Se puede cambiar de opinión o eliminar.
- **🔄 Cambio de opinión:** Mover de Skip a Match (o viceversa) actualiza el feed automáticamente.

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

## 🔁 Importar los flows de Langflow

Los flows están en la carpeta `/flows`:

1. Abre Langflow en http://localhost:7860 (o tu instancia)
2. Importa `flows/nomadmatch_load_flow.json` → ejecútalo para ingestar los CSVs en ChromaDB
3. Importa `flows/nomadmatch_retrieve_flow.json` → configura tu `OPENAI_API_KEY` en el componente LLM
4. Verifica que la colección de ChromaDB se llama `nomadmatch_cities` en ambos flows
5. Copia el Flow ID del Retrieve Flow → configura `LANGFLOW_FLOW_ID` en `docker-compose.yml`

---

## 🧑‍💻 Flujo de trabajo para el equipo

### Ramas

| Rama | Uso |
|------|-----|
| `main` | Producción, siempre estable |
| `develop` | Integración de features |
| `prototype-5-v2` | Rama activa actual |
| `feature/*` | Features nuevas |

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

### El LLM devuelve ciudades frías con `climate:warm`
→ Verifica que el prompt del Retrieve Flow contiene el Step 4 con el pre-filtro de clima. El texto clave que debe estar: `Tallinn, Warsaw, Vilnius, Prague, Budapest...are NOT warm climate cities and must be removed`.

### `revealed_preferences` es null después de varios swipes
→ Verifica que el componente Message History (modo Store) está conectado al output del Language Model en el canvas de Langflow. Sin esa conexión las respuestas del LLM no se guardan en el historial.

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
*[🇪🇸 Español](#spanish) · 🇬🇧 English*

<div align="center">
  <img src="https://github.com/awalim/nomadmatch-rag/blob/prototipo-5/frontend/public/logo_nomadmatch_banner.png?raw=true" alt="NomadMatch Logo" width="750"/>
  <h1>Find Your Perfect European City</h1>
</div>

![Version](https://img.shields.io/badge/version-5.2.0-blueviolet?style=for-the-badge)
![Stack](https://img.shields.io/badge/stack-RAG%20%7C%20ChromaDB%20%7C%20Langflow%20%7C%20FastAPI-6E56CF?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Docker](https://img.shields.io/badge/docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)

**✨ City matching system for digital nomads with conversational AI, swipe learning, and free/premium tier logic ✨**

---

## 🎯 What is NomadMatch?

**NomadMatch** is a RAG (Retrieval-Augmented Generation) system that helps digital nomads find their ideal European city.

Users select their preferences in a visual onboarding (budget, climate, digital nomad visa, vibe) and the system returns **5 swipeable cards** with match percentage, personalized description, and cost breakdown. Each swipe teaches the system which cities the user likes — subsequent recommendations improve automatically with each interaction.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **RAG + LLM** | ChromaDB retrieves candidates → GPT-4o-mini reasons, scores, and generates personalized responses |
| 🃏 **Card/detail output** | Each city has a swipeable card and an expandable panel with full data |
| 📈 **Swipe learning** | System detects patterns across MATCHED/SKIPPED cities and adjusts subsequent recommendations |
| 🔒 **Free/premium tiers** | Visa, tax, and fiscal tip locked until upgrade. Unlocked with `tier:premium` |
| 🗺️ **50+ Cities** | Dataset with 91 attributes per city (costs, climate, safety, nomad community, vibes) |
| 🌡️ **Hard pre-filters** | Climate and budget are mandatory filters before scoring — cities that violate them never appear |
| 💬 **Conversational memory** | Langflow Message History stores session history and passes it to the LLM on each call |
| 🔐 **JWT Auth** | Registration, login, premium upgrade. Swipes persisted per user in SQLite |
| 📂 **Auto-ingestion** | CSVs are automatically loaded when Docker is launched |
| 🐳 **Full Docker** | Just one `docker-compose up --build -d` and you're ready to go |
| 🔄 **Exported flows** | Langflow flows (Load + Retrieve) are in `/flows` ready to import |

---

## 🏗️ Architecture

```
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│    Frontend      │─────▶│    Backend       │─────▶│    ChromaDB      │
│  Vanilla JS/CSS  │      │    FastAPI       │      │    50 cities     │
│    Port 3000     │◀─────│    Port 8000     │◀─────│    Embeddings    │
└──────────────────┘      └────────┬─────────┘      └──────────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
             ┌──────▼──────┐             ┌────────▼────────┐
             │   SQLite    │             │    Langflow     │
             │  Users +    │             │  Retrieve Flow  │
             │  Swipes DB  │             │  GPT-4o-mini    │
             └─────────────┘             └────────┬────────┘
                                                  │
                                         ┌────────▼────────┐
                                         │   OpenAI API    │
                                         │  Embeddings +   │
                                         │  Chat           │
                                         └─────────────────┘
```

**Technical stack:**
- **Frontend:** Vanilla JS + CSS (served by Nginx)
- **Backend:** FastAPI + Uvicorn
- **RAG engine:** Langflow + ChromaDB
- **LLM:** GPT-4o-mini (recommendations) + `text-embedding-3-small` (embeddings, 1536 dims)
- **User database:** SQLite + SQLAlchemy
- **Authentication:** JWT (python-jose + bcrypt)
- **Containers:** Docker Compose

---

## 🚀 Quick Installation (3 minutes)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/)
- [OpenAI API Key](https://platform.openai.com/api-keys)

### 1. Clone the repository

```bash
git clone https://github.com/awalim/nomadmatch-rag.git
cd nomadmatch-rag
git checkout prototype-5-v2
```

### 2. Configure the OpenAI API Key

**Windows (CMD):**
```bash
set OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-proj-YOUR_KEY_HERE"
```

**Mac/Linux:**
```bash
export OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

### 3. Start the system

```bash
docker-compose up --build -d
```

### 4. Done!

| Service | URL |
|---------|-----|
| 🌐 **Frontend** | http://localhost:3000 |
| ⚙️ **Backend API** | http://localhost:8000 |
| 📖 **API Documentation** | http://localhost:8000/docs |

> **Note:** Data will be automatically ingested into ChromaDB upon startup. Verify with: `docker-compose logs -f backend`

---

## 📁 Project structure

```
nomadmatch-rag/
├── 📁 backend/                    # FastAPI + ChromaDB + Auth
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── auth.py           # JWT authentication (register/login/upgrade)
│   │   │   ├── deps.py           # Shared dependencies (get_db, get_current_user)
│   │   │   └── routes.py         # REST endpoints (query, upload, preferences, premium)
│   │   ├── 📁 core/
│   │   │   ├── config.py         # Configuration (CORS, API keys)
│   │   │   └── langflow_client.py # HTTP client to call Langflow
│   │   ├── 📁 models/
│   │   │   ├── schemas.py        # Pydantic schemas
│   │   │   └── user.py           # SQLAlchemy models (User, CityPreference)
│   │   ├── 📁 utils/
│   │   │   ├── chroma_utils.py    # ChromaManager (ingestion, search, scoring)
│   │   │   ├── llm_utils.py       # Response generation with OpenAI
│   │   │   └── scoring.py         # Tax and visa scoring
│   │   └── main.py                # Entry point + auto-ingest
│   ├── 📁 data/
│   │   └── cities.csv             # Internal dataset (50 cities)
│   ├── Dockerfile
│   └── requirements.txt
├── 📁 data/                       # External datasets (mounted in Docker)
│   ├── city_general_free.csv      # 50 cities · 91 columns · FREE Tier
│   ├── city_tax_premium.csv       # 47 cities · 17 columns · PREMIUM Tier (taxation)
│   └── city_visa_premium.csv      # 47 cities · 18 columns · PREMIUM Tier (visas)
├── 📁 flows/                          # ⭐ NEW in prototype-5-v2
│   ├── nomadmatch_load_flow.json      # Ingestion flow: CSVs → ChromaDB
│   └── nomadmatch_retrieve_flow.json  # Recommendation flow: query → LLM → JSON
├── 📁 langflow/                   # Legacy flow (reference)
│   └── nomadmatch_langflow.json
├── 📁 frontend/
│   ├── 📁 public/
│   │   ├── index.html             # Main HTML
│   │   ├── app.js                 # JS logic (auth, search, Match/Skip, Favs)
│   │   ├── styles.css             # Main styles
│   │   ├── premium-styles.css     # Premium styles
│   │   ├── city-images.json       # City → image mapping
│   │   └── 📁 thumbnails/         # 50 city photos
│   └── Dockerfile                 # Nginx Alpine
├── docker-compose.yml             # Docker orchestration
└── README.md                      # This file
```

---

## 🔄 How the RAG system works

### Full recommendation flow

```
1. User completes onboarding on the frontend
        ↓
2. Frontend sends PROFILE to the Langflow endpoint
   PROFILE: tier:free|budget_range:900-1200|climate:warm|
            visa_needed:true|vibes:beach,historical,tech_hub|
            nationality:US|tax_optimization:false
        ↓
3. ChromaDB retrieves the 20 most similar candidates
        ↓
4. Langflow Prompt (8 steps) executes:
   - STEP 1: Detect input type (PROFILE / MATCHED / SKIPPED)
   - STEP 2: Extract user profile
   - STEP 3: Read swipe history and detect patterns
   - STEP 4: Hard pre-filter for climate and budget
   - STEP 5: Build exclusion list (already-seen cities)
   - STEP 6: Internal scoring 0-100 per city
   - STEP 7: Apply tier rules (free → locked_premium)
   - STEP 8: Return card/detail JSON
        ↓
5. Frontend renders 5 swipeable cards
        ↓
6. User swipes → MATCHED/SKIPPED sent to Langflow
        ↓
7. Message History Store saves LLM response
        ↓
8. Next call: LLM reads history → excludes seen cities
              → detects patterns → improves recommendations
```

### Message format

**First call (onboarding):**
```
PROFILE: tier:free|budget_range:900-1200|climate:warm|visa_needed:true|vibes:beach,historical,tech_hub|nationality:US|tax_optimization:false
```

| Field | Options |
|-------|---------|
| `tier` | `free`, `premium` |
| `budget_range` | `<900`, `900-1200`, `1200-1600`, `1600-2000` |
| `climate` | `warm`, `cool`, `cold` |
| `visa_needed` | `true`, `false` |
| `vibes` | `beach`, `nightlife`, `historical`, `nature`, `tech_hub`, `foodie`, `art`, `sports` |
| `nationality` | country name or code |
| `tax_optimization` | `true`, `false` |

**Swipe right:** `MATCHED: Seville`

**Swipe left:** `SKIPPED: Barcelona`

---

## 📊 Datasets

The project includes **3 CSVs** with data from 50 European cities:

### `city_general_free.csv` (91 columns)
General data accessible to all users:
- 💰 **Costs:** Rent (studio, 1BR, 2BR, 3BR), monthly budget, coworking
- 🌡️ **Climate:** Temperature by season, hours of sunshine, rainfall, humidity
- 🏥 **Life:** Safety, healthcare, transportation, biking, walkability
- 👥 **Community:** Expat size, nomad scene, Nomad List Rating, English level
- 🎨 **Vibes:** Nightlife, dating, family, startups, outdoors, art, LGBTQ+

### `city_visa_premium.csv` (18 columns)
Exclusive premium data on digital nomad visas:
- 🛂 Visa type, duration, eligibility by nationality
- 💶 Minimum income requirement in EUR
- 📅 Minimum/maximum stay
- 🇪🇺 Schengen area

### `city_tax_premium.csv` (17 columns)
Exclusive premium data on taxation:
- 📊 Standard and special tax rates
- 🏛️ Special regimes (NHR, Beckham Law, IP Box, etc.)
- ⏰ Years of tax benefits
- 🏆 Tax and global scoring

---

## ⚙️ RAG Scoring

The prompt runs an internal scoring of 0 to 100 per city. Users only see the final `match_percentage`.

| Dimension | Max pts | Description |
|-----------|---------|-------------|
| Budget fit | 25 | City within declared range = 25 pts |
| Vibe match | 15 | 3 pts per user vibe that matches the city |
| Climate match | 15 | Exact=15, adjacent=10, opposite=0 |
| Visa match | 10 | DNV available for the nationality = 10 pts |
| Nomad community | 10 | Nomad List Rating ≥ 4.0 = 10 pts |
| Safety | 5 | Safety Index ≥ 70 = 5 pts |
| Revealed preference bonus | +20 | Applied after 2+ swipes with detected pattern |
| Tax regime *(premium only)* | +10 | NHR, Beckham Law, IP Box, flat tax = 10 pts |

**Hard pre-filters (before scoring):**
- `climate:warm` → all Northern and Central European cities removed
- Budget ceiling: `900-1200` → max €1,380 (+15%), `1200-1600` → max €1,840, etc.
- Already-seen cities in the session → permanently excluded

---

## ❤️ Match / Skip System

Registered users can interact with cities:

- **❤️ Match:** Mark the city as a favourite. The card remains visible.
- **✖️ Skip:** Discard the city (slide-out animation). Hidden from the feed.
- **📋 Favs tab:** List of Matches and Skips. You can change your mind or delete.
- **🔄 Change of mind:** Moving from Skip to Match (or vice versa) automatically updates the feed.

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

## 🔁 Importing the Langflow flows

The flows are in the `/flows` folder:

1. Open Langflow at http://localhost:7860 (or your instance)
2. Import `flows/nomadmatch_load_flow.json` → run it to ingest the CSVs into ChromaDB
3. Import `flows/nomadmatch_retrieve_flow.json` → configure your `OPENAI_API_KEY` in the LLM component
4. Verify the ChromaDB collection is named `nomadmatch_cities` in both flows
5. Copy the Retrieve Flow ID → configure `LANGFLOW_FLOW_ID` in `docker-compose.yml`

---

## 🧑‍💻 Workflow for the team

### Branches

| Branch | Use |
|--------|-----|
| `main` | Production, always stable |
| `develop` | Feature integration |
| `prototype-5-v2` | Current active branch |
| `feature/*` | New features |

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
git commit -m "feat: feature description"
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
→ Run `docker ps --filter "publish=3000"`, stop the container using it, or change the port in `docker-compose.yml`.

### Invalid API Key (error 401 on ingestion)
```
Incorrect API key provided: sk-tu-cl****here
```
→ Set your real API key: `set OPENAI_API_KEY=sk-proj-YOUR_REAL_KEY` and run `docker-compose down && docker-compose up --build -d`.

### ChromaDB empty after restarting
→ Data is persisted in a Docker volume (`chroma_data`). If you deleted the volume (`docker-compose down -v`), auto-ingest will reload it on the next startup.

### LLM returns cold-climate cities with `climate:warm`
→ Verify the Retrieve Flow prompt contains the Step 4 climate pre-filter. The key text that must be present: `Tallinn, Warsaw, Vilnius, Prague, Budapest...are NOT warm climate cities and must be removed`.

### `revealed_preferences` is null after several swipes
→ Verify the Message History component (Store mode) is connected to the Language Model output in the Langflow canvas. Without this connection, LLM responses are not saved to history.

---

## 🤝 Contribute

1. Fork the project
2. Create your branch (`git checkout -b feature/amazing-feature`)
3. Commit (`git commit -m 'feat: add amazing feature'`)
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

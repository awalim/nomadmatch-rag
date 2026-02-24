# 🌍 NomadMatch · Encuentra tu ciudad europea ideal

<p align="center">
  <img src="https://img.shields.io/badge/version-1.0.0-blueviolet?style=for-the-badge" alt="Version">
  <img src="https://img.shields.io/badge/stack-RAG%20%7C%20ChromaDB%20%7C%20FastAPI-6E56CF?style=for-the-badge" alt="Stack">
  <img src="https://img.shields.io/badge/license-MIT-green?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>✨ Sistema de recomendación de ciudades para nómadas digitales con IA y matching semántico ✨</b>
</p>

<p align="center">
  <i>🇪🇸 Español · <a href="#english">English</a></i>
</p>

---

## 🎯 ¿Qué es NomadMatch?

**NomadMatch** es un sistema RAG (Retrieval-Augmented Generation) que ayuda a nómadas digitales a encontrar su ciudad europea ideal. 

Los usuarios seleccionan sus preferencias (presupuesto, clima, internet, visa, ambiente) y el sistema encuentra **las 3 ciudades con mejor matching** usando embeddings semánticos y búsqueda por similitud vectorial.

### ✨ Características

| | |
|---|---|
| 🎨 **Diseño Premium** | Interfaz moderna con gradientes, glows y modo oscuro |
| 🌍 **Bilingüe** | Toggle ES/EN completamente funcional |
| 🔍 **Matching Semántico** | Embeddings de OpenAI + ChromaDB |
| 🏙️ **50+ Ciudades** | Dataset completo de ciudades europeas |
| 🖼️ **Fotos Reales** | Imágenes de Unsplash por ciudad |
| 📱 **Responsive** | Funciona en móvil, tablet y desktop |
| 🔒 **Premium Ready** | Estructura preparada para contenido de pago |

---

## 🏗️ Arquitectura
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Frontend │────▶│ Backend │────▶│ ChromaDB │
│ Live │ │ FastAPI │ │ Vectores │
│ Server │◀────│ REST │◀────│ Embeddings │
└─────────────┘ └─────────────┘ └─────────────┘
│
▼
┌─────────────┐
│ OpenAI │
│ Embeddings │
└─────────────┘


---

## 🚀 Instalación para el equipo (5 minutos)

### Prerrequisitos

- Docker y Docker Compose
- Git
- OpenAI API Key ([obtener aquí](https://platform.openai.com/api-keys))

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/nomadmatch-rag.git
cd nomadmatch-rag

## 2. CONFIGURAR VARIABLES PARA EL ENTORNO:
cp backend/.env.example backend/.env
nano backend/.env
# Añade tu OPENAI_API_KEY

### 3. LEVANTAR EL SISTEMA:
docker-compose up --build -d
sleep 10  # Esperar a que el backend inicie

## 4. CARGAR LOS DATOS:
# Subir dataset de 50 ciudades
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@./data/nomadmatch_european_cities.csv"

### 5. ¡Usar!
Frontend: http://localhost:3000

Backend API: http://localhost:8000

Documentación API: http://localhost:8000/docs


### ESTRUCTURA DEL PROYECTO
nomadmatch-rag/
├── 📁 backend/               # FastAPI + ChromaDB
│   ├── 📁 app/
│   │   ├── 📁 api/          # Endpoints REST
│   │   ├── 📁 core/         # Configuración
│   │   ├── 📁 models/       # Schemas Pydantic
│   │   └── 📁 utils/        # ChromaManager
│   ├── .env.example         # Variables de entorno
│   └── requirements.txt     # Dependencias
├── 📁 frontend/             # Vanilla JS + CSS
│   ├── 📁 public/           # HTML, CSS, JS, imágenes
│   ├── Dockerfile          # Node + live-server
│   └── package.json        # Dependencias frontend
├── 📁 data/                # Datasets (gitignorados)
│   ├── sample_cities.csv   # 🔹 MUESTRA (10 ciudades)
│   └── README.md           # Documentación de datos
├── 📁 langflow/            # Flow export (opcional)
├── docker-compose.yml      # Orquestación
└── README.md              # Este archivo



### 🧑‍💻 Flujo de trabajo para el equipo
1. Cada desarrollador clona
bash
git clone https://github.com/tu-usuario/nomadmatch-rag.git
cd nomadmatch-rag
cp backend/.env.example backend/.env

# Cada uno pone su propia OpenAI API Key
docker-compose up --build -d
2. Rama principal (main) siempre estable
main → Producción, siempre funcionando

develop → Integración de features

feature/* → Features nuevas

3. Para añadir una feature
bash
git checkout -b feature/nueva-funcionalidad

# ... trabajar ...
git add .
git commit -m "feat: añadida nueva funcionalidad"
git push origin feature/nueva-funcionalidad

# Crear Pull Request en GitHub
4. Convención de commits
text
feat:     Nueva funcionalidad
fix:      Corrección de bug
style:    Cambios de formato, CSS
refactor: Refactorización de código
docs:     Documentación
chore:    Cambios en build, docker, etc.
🔧 API Endpoints
Método	Endpoint	Descripción
GET	/api/v1/health	Estado del sistema
GET	/api/v1/collections	Info de ChromaDB
POST	/api/v1/upload	Subir CSV
POST	/api/v1/query	Búsqueda semántica
POST	/api/v1/chat	Obtener matches
Ver documentación completa →

### 📊 Dataset
El proyecto incluye 50 ciudades europeas con +70 atributos cada una:

💰 Costos: Alquiler, presupuesto mensual

📶 Internet: Velocidad, fiabilidad

🌡️ Clima: Temperatura verano/invierno, horas de sol

🛂 Visa: Disponibilidad, duración, tipo

💼 Tax: NHR, Beckham Law, IP Box, etc.

🎨 Vibes: Playas, vida nocturna, tech hub, etc.

⚠️ IMPORTANTE: El dataset completo (nomadmatch_european_cities.csv) NO se sube a GitHub. Cada desarrollador debe cargarlo localmente con el comando curl proporcionado. Solo se sube sample_cities.csv para pruebas.

### 🤝 Contribuir
Fork el proyecto

Crea tu rama (git checkout -b feature/amazing-feature)

Commit (git commit -m 'feat: add amazing feature')

Push (git push origin feature/amazing-feature)

Abre un Pull Request



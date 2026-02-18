// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
let cityImages = {};

// Estado Global de Usuario
let currentUser = {
    isLoggedIn: false,
    isPremium: false,
    email: null,
    library: []
};

// Carga de imágenes de ciudades
fetch('/city-images.json')
    .then(response => response.ok ? response.json() : {})
    .then(data => {
        cityImages = data;
        console.log('✅ Imágenes cargadas:', Object.keys(cityImages).length);
    })
    .catch(error => {
        console.warn('⚠️ No se encontró city-images.json, se usará generación dinámica.');
    });

function getCityImage(cityName) {
    if (!cityName) return '/thumbnails/default.jpg';
    if (cityImages[cityName]) return cityImages[cityName];
    
    const cleanName = cityName.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/\s+/g, '');
        
    return `/thumbnails/${cleanName}.jpg`;
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 NomadMatch iniciado');
    checkHealth();
    setupEventListeners();
    checkCollections();
});

function setupEventListeners() {
    // 1. Botón de Búsqueda
    const matchButton = document.getElementById('matchButton');
    if (matchButton) {
        matchButton.addEventListener('click', findMatches);
    }

    // 2. Control de Modales (Auth y Premium)
    const btnSignup = document.querySelector('.btn-primary'); // Botón Registrarse
    const btnLogin = document.querySelector('.btn-outline');  // Botón Iniciar Sesión
    const btnPremium = document.querySelector('.premium-badge'); // Banner naranja
    
    const authModal = document.getElementById('authModal');
    const premiumModal = document.getElementById('premiumModal');

    if (btnSignup) btnSignup.onclick = () => openAuthModal('signup');
    if (btnLogin) btnLogin.onclick = () => openAuthModal('login');
    if (btnPremium) btnPremium.onclick = () => premiumModal.style.display = "block";

    // 3. Cerrar Modales
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.onclick = () => {
            authModal.style.display = "none";
            premiumModal.style.display = "none";
        };
    });

    window.onclick = (event) => {
        if (event.target.className === 'modal-wrapper') {
            authModal.style.display = "none";
            premiumModal.style.display = "none";
        }
    };

    // 4. Lógica del Formulario de Registro
    const authForm = document.getElementById('authForm');
    if (authForm) {
        authForm.onsubmit = (e) => {
            e.preventDefault();
            handleAuth();
        };
    }

    // 5. Botón de Upgrade Premium
    const upgradeBtn = document.getElementById('upgradeBtn');
    if (upgradeBtn) {
        upgradeBtn.onclick = () => {
            currentUser.isPremium = true;
            alert("✨ ¡Ahora eres Premium! Tienes acceso a tier_premium.csv");
            premiumModal.style.display = "none";
        };
    }
}

// Funciones de Interfaz de Usuario
function openAuthModal(type) {
    const title = document.getElementById('authTitle');
    const modal = document.getElementById('authModal');
    title.innerText = type === 'login' ? 'Iniciar Sesión' : 'Crear cuenta';
    modal.style.display = "block";
}

function handleAuth() {
    const email = document.getElementById('userEmail').value;
    currentUser.isLoggedIn = true;
    currentUser.email = email;
    
    // Actualizar UI del Navbar
    document.querySelector('.nav-links').innerHTML = `
        <span style="color: var(--text-secondary)">Hola, ${email.split('@')[0]}</span>
        <button class="btn-outline" onclick="location.reload()">Salir</button>
    `;
    
    document.getElementById('authModal').style.display = "none";
    console.log('👤 Usuario registrado:', currentUser);
}

// Conexión con el Backend
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        const statusDot = document.querySelector('.status-dot');
        const dbStatus = document.getElementById('dbStatus');
        
        if (response.ok && data.status === 'healthy') {
            statusDot.className = 'status-dot connected';
            if (dbStatus) dbStatus.innerText = 'Conectado';
        }
    } catch (error) {
        console.error('❌ Error API:', error);
    }
}

async function checkCollections() {
    try {
        const response = await fetch(`${API_BASE_URL}/collections`);
        const data = await response.json();
        const info = document.getElementById('collectionInfo');
        if (info && data.collections) {
            info.innerHTML = `
                <div class="status-item">
                    <span class="status-dot connected"></span>
                    <span>Base de datos: <strong>${data.collections[0] || 'Vectores'}</strong></span>
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Error collections:', error);
    }
}

async function findMatches() {
    const resultsContainer = document.getElementById('resultsContainer');
    resultsContainer.innerHTML = '<div class="loading-message">🔍 Buscando tus ciudades ideales...</div>';

    const preferences = {
        budget: document.querySelector('input[name="budget"]:checked')?.value || 'moderate',
        climate: document.querySelector('input[name="climate"]:checked')?.value || 'warm',
        visa: document.querySelector('input[name="visa"]:checked')?.value === 'yes',
        vibes: Array.from(document.querySelectorAll('input[name="vibe"]:checked')).map(cb => cb.value)
    };

    try {
        const query = buildQuery(preferences);
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, num_results: 15 })
        });

        const data = await response.json();
        if (!data.results) throw new Error('No hay resultados');

        const matches = rankCities(data.results, preferences);
        displayMatches(matches.slice(0, 3));
    } catch (error) {
        resultsContainer.innerHTML = `<div class="loading-message">❌ Error: ${error.message}</div>`;
    }
}

function buildQuery(p) {
    let q = `European city for nomads. Budget: ${p.budget}, Climate: ${p.climate}.`;
    if (p.visa) q += " Needs digital nomad visa.";
    q += ` Vibes: ${p.vibes.join(', ')}`;
    return q;
}

function rankCities(results, p) {
    return results.map(r => {
        let score = r.similarity_score || 0.5;
        const m = r.metadata || {};
        if (p.visa && m.Digital_Nomad_Visa === 'Yes') score += 0.3;
        return { ...r, score };
    }).sort((a, b) => b.score - a.score);
}

function displayMatches(cities) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = cities.map((city, i) => {
        const m = city.metadata || {};
        const name = m.city || 'Ciudad';
        return `
            <div class="city-card">
                <img class="city-image" src="${getCityImage(name)}" alt="${name}" onerror="this.src='/thumbnails/default.jpg'">
                <div class="city-info">
                    <div class="city-header">
                        <div><span class="city-name">${name}</span><span class="city-country">${m.country || ''}</span></div>
                        <span class="city-score">#${i + 1}</span>
                    </div>
                    <div class="city-details">
                        <div class="city-detail"><span class="detail-label">💰 Presupuesto</span><span class="detail-value">${m.Monthly_Budget_Single || 'Moderate'}</span></div>
                        <div class="city-detail"><span class="detail-label">🌡️ Clima</span><span class="detail-value">${m.Summer_Temperature || 'Warm'}</span></div>
                        <div class="city-detail"><span class="detail-label">📶 Internet</span><span class="detail-value">${m.Internet_Reliability_Score || 'Good'}</span></div>
                        <div class="city-detail"><span class="detail-label">🛂 Visa</span><span class="detail-value">${m.Digital_Nomad_Visa === 'Yes' ? '✅ Sí' : '❌ No'}</span></div>
                    </div>
                    <div class="city-tags">
                        ${(m.Vibe_Tags || 'Europe').split(',').slice(0, 3).map(t => `<span class="city-tag">${t}</span>`).join('')}
                    </div>
                </div>
            </div>`;
    }).join('');
}

setInterval(checkHealth, 30000);

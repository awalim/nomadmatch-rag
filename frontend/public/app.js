// ============================================
// NOMADMATCH · APP PRINCIPAL
// Versión con autenticación real y sección premium
// ============================================

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
let cityImages = {};

// Estado Global de Usuario
let currentUser = {
    isLoggedIn: false,
    isPremium: false,
    email: null,
    token: null
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
    loadCollections();
    checkLoginStatus(); // Verificar si hay token guardado
});

// ============================================
// CONFIGURACIÓN DE EVENTOS
// ============================================
function setupEventListeners() {
    // Botón de Búsqueda
    const matchButton = document.getElementById('matchButton');
    if (matchButton) {
        matchButton.addEventListener('click', findMatches);
    }

    // Botones de autenticación
    const btnSignup = document.querySelector('.btn-primary:not(#matchButton)'); // Registrarse
    const btnLogin = document.querySelector('.btn-outline'); // Iniciar Sesión
    const btnPremium = document.querySelector('.premium-badge'); // Banner naranja

    if (btnSignup) btnSignup.addEventListener('click', () => openAuthModal('register'));
    if (btnLogin) btnLogin.addEventListener('click', () => openAuthModal('login'));
    if (btnPremium) btnPremium.addEventListener('click', () => openPremiumModal());

    // Modales
    const authModal = document.getElementById('authModal');
    const premiumModal = document.getElementById('premiumModal');

    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            authModal.style.display = 'none';
            premiumModal.style.display = 'none';
        });
    });

    window.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal-wrapper')) {
            authModal.style.display = 'none';
            premiumModal.style.display = 'none';
        }
    });

    // Formulario de autenticación
    const authForm = document.getElementById('authForm');
    if (authForm) {
        authForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleAuth();
        });
    }

    // Botón de upgrade premium (dentro del modal premium)
    const upgradeBtn = document.getElementById('upgradeBtn');
    if (upgradeBtn) {
        upgradeBtn.addEventListener('click', upgradeToPremium);
    }

    // Pestañas free/premium
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', handleTabClick);
    });
}

// ============================================
// AUTENTICACIÓN REAL CON BACKEND
// ============================================
let currentAuthMode = 'login'; // 'login' o 'register'

function openAuthModal(mode) {
    currentAuthMode = mode;
    const title = document.getElementById('authTitle');
    const subtitle = document.getElementById('authSubtitle');
    const modal = document.getElementById('authModal');
    
    if (mode === 'login') {
        title.innerText = 'Iniciar Sesión';
        subtitle.innerText = 'Accede a tu cuenta';
    } else {
        title.innerText = 'Crear cuenta';
        subtitle.innerText = 'Únete a la comunidad de nómadas';
    }
    modal.style.display = 'block';
}

async function handleAuth() {
    const email = document.getElementById('userEmail').value;
    const password = document.getElementById('userPass').value;
    const endpoint = currentAuthMode === 'login' ? '/auth/login' : '/auth/register';

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Error en autenticación');
        }

        const data = await response.json();
        // Guardar token y estado
        localStorage.setItem('token', data.access_token);
        currentUser = {
            isLoggedIn: true,
            isPremium: data.is_premium,
            email: email,
            token: data.access_token
        };

        // Actualizar UI del navbar
        updateNavbar();
        document.getElementById('authModal').style.display = 'none';
        console.log('✅ Usuario autenticado:', currentUser);
    } catch (error) {
        alert(`❌ ${error.message}`);
    }
}

function updateNavbar() {
    const navLinks = document.querySelector('.nav-links');
    if (currentUser.isLoggedIn) {
        navLinks.innerHTML = `
            <span style="color: var(--text-secondary)">Hola, ${currentUser.email.split('@')[0]}</span>
            ${currentUser.isPremium ? '<span class="premium-badge-mini">⭐ Premium</span>' : ''}
            <button class="btn-outline" onclick="logout()">Salir</button>
        `;
    } else {
        navLinks.innerHTML = `
            <button class="lang-toggle">
                <span class="lang-es">ES</span>
                <span class="lang-separator">/</span>
                <span class="lang-en">EN</span>
            </button>
            <button class="btn-outline" onclick="openAuthModal('login')">Iniciar sesión</button>
            <button class="btn-primary" onclick="openAuthModal('register')">Registrarse</button>
        `;
    }
}

function logout() {
    localStorage.removeItem('token');
    currentUser = { isLoggedIn: false, isPremium: false, email: null, token: null };
    updateNavbar();
    // Volver a la pestaña free
    document.querySelector('[data-tab="free"]').click();
}

function checkLoginStatus() {
    const token = localStorage.getItem('token');
    if (token) {
        // Verificar token con el backend
        fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(res => res.json())
        .then(user => {
            currentUser = {
                isLoggedIn: true,
                isPremium: user.is_premium,
                email: user.email,
                token: token
            };
            updateNavbar();
        })
        .catch(() => {
            localStorage.removeItem('token');
        });
    }
}

// ============================================
// FUNCIONES PREMIUM
// ============================================
function openPremiumModal() {
    if (!currentUser.isLoggedIn) {
        alert('Debes iniciar sesión primero');
        openAuthModal('login');
        return;
    }
    document.getElementById('premiumModal').style.display = 'block';
}

async function upgradeToPremium() {
    // Aquí iría la lógica de pago real (Stripe, etc.)
    // Por ahora, simulamos que el usuario se hace premium
    const token = currentUser.token;
    if (!token) return;

    try {
        // Llamada a un endpoint que haga premium al usuario (debes crearlo en el backend)
        // O simplemente actualizamos en la base de datos manualmente como antes
        // Por simplicidad, haremos la actualización directa con una llamada al backend
        const response = await fetch(`${API_BASE_URL}/auth/upgrade`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            currentUser.isPremium = true;
            updateNavbar();
            document.getElementById('premiumModal').style.display = 'none';
            alert('✨ ¡Ahora eres Premium!');
            // Recargar datos premium si la pestaña está activa
            if (document.querySelector('[data-tab="premium"].active')) {
                loadPremiumAdvice();
            }
        } else {
            alert('Error al actualizar');
        }
    } catch (error) {
        console.error(error);
    }
}

// Manejo de pestañas
function handleTabClick(e) {
    const tab = e.target.dataset.tab;
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    e.target.classList.add('active');
    
    document.getElementById('freeResults').style.display = tab === 'free' ? 'block' : 'none';
    document.getElementById('premiumResults').style.display = tab === 'premium' ? 'block' : 'none';

    if (tab === 'premium') {
        if (currentUser.isLoggedIn && currentUser.isPremium) {
            loadPremiumAdvice();
        } else {
            showPremiumLocked();
        }
    }
}

function showPremiumLocked() {
    const container = document.getElementById('premiumResults');
    container.innerHTML = `
        <div class="empty-state premium-empty">
            <div class="empty-illustration"><span class="empty-emoji">🔒</span></div>
            <h3>Contenido exclusivo para usuarios premium</h3>
            <p>${!currentUser.isLoggedIn ? 'Inicia sesión y actualiza tu cuenta' : 'Actualiza tu cuenta'} para acceder a guías de visados e impuestos.</p>
            <button class="btn-primary" id="premiumUpgradeBtn">${!currentUser.isLoggedIn ? 'Iniciar sesión' : 'Actualizar a Premium'}</button>
        </div>
    `;
    document.getElementById('premiumUpgradeBtn').addEventListener('click', () => {
        if (!currentUser.isLoggedIn) {
            openAuthModal('login');
        } else {
            openPremiumModal();
        }
    });
}

function loadPremiumAdvice() {
    const container = document.getElementById('premiumResults');
    container.innerHTML = `<div class="empty-state"><div class="empty-illustration"><span class="empty-emoji">🔍</span></div><h3>Cargando información premium...</h3></div>`;

    fetch(`${API_BASE_URL}/premium/advice`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${currentUser.token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            query: "información de visados e impuestos",
            num_results: 5
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.results && data.results.length > 0) {
            let html = '';
            data.results.forEach(city => {
                const meta = city.metadata;
                html += `
                    <div class="city-card premium-card">
                        <div class="city-info">
                            <div class="city-header">
                                <span class="city-name">${meta.city}</span>
                                <span class="city-score">Overall: ${meta.overall_score}</span>
                            </div>
                            <div class="city-details">
                                <div class="city-detail"><span class="detail-label">💰 Ingreso mínimo</span><span class="detail-value">${meta.monthly_income_requirement_eur}€</span></div>
                                <div class="city-detail"><span class="detail-label">🛂 Visa</span><span class="detail-value">${meta.visa == '1' ? 'Sí' : 'No'}</span></div>
                                <div class="city-detail"><span class="detail-label">🌍 Elegibilidad</span><span class="detail-value">${interpretEU(meta.eu_noneu_intl)}</span></div>
                                <div class="city-detail"><span class="detail-label">📅 Estancia máx</span><span class="detail-value">${meta.max_stay_months} meses</span></div>
                            </div>
                            <div class="city-tags">
                                <span class="city-tag">Tax score: ${meta.tax_score}</span>
                                <span class="city-tag">Visa score: ${meta.visa_score}</span>
                            </div>
                        </div>
                    </div>
                `;
            });
            html += `<div class="premium-advice">${data.advice}</div>`;
            container.innerHTML = html;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-illustration"><span class="empty-emoji">📊</span></div>
                    <h3>No hay datos premium disponibles</h3>
                </div>
            `;
        }
    })
    .catch(err => {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-illustration"><span class="empty-emoji">❌</span></div>
                <h3>Error al cargar datos premium</h3>
            </div>
        `;
    });
}

function interpretEU(val) {
    const map = {0:'Solo UE', 1:'UE y no UE', 2:'Todos', 3:'Solo no UE'};
    return map[val] || 'Desconocido';
}

// ============================================
// FUNCIONES DE CONEXIÓN CON BACKEND (FREE TIER)
// ============================================
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

async function loadCollections() {
    try {
        const response = await fetch(`${API_BASE_URL}/collections`);
        const data = await response.json();
        const info = document.getElementById('collectionInfo');
        if (info && data.collections) {
            info.innerHTML = `
                <div class="status-item">
                    <span class="status-dot connected"></span>
                    <span>Base de datos: <strong>${data.collections[0] || 'Vectores'}</strong> (${data.stats.total_documents} docs)</span>
                </div>
            `;
        }
    } catch (error) {
        console.error('❌ Error collections:', error);
    }
}

async function findMatches() {
    const resultsContainer = document.getElementById('freeResults');
    if (!resultsContainer) {
        console.error('❌ No se encontró el contenedor freeResults');
        return;
    }
    resultsContainer.innerHTML = '<div class="loading-message">🔍 Buscando tus ciudades ideales...</div>';

    const preferences = {
        budget: document.querySelector('input[name="budget"]:checked')?.value || 'moderate',
        climate: document.querySelector('input[name="climate"]:checked')?.value || 'warm',
        visa: document.querySelector('input[name="visa"]:checked')?.value === 'yes',
        vibes: Array.from(document.querySelectorAll('input[name="vibe"]:checked')).map(cb => cb.value)
    };
    console.log('Preferencias:', preferences);

    try {
        const query = buildQuery(preferences);
        console.log('Query enviada:', query);
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: query, num_results: 15 })
        });

        const data = await response.json();
        console.log('Datos recibidos:', data);

        if (!data.results || data.results.length === 0) {
            resultsContainer.innerHTML = '<div class="loading-message">No se encontraron ciudades con esas preferencias. Intenta con otras opciones.</div>';
            return;
        }

        const matches = rankCities(data.results, preferences);
        displayMatches(matches.slice(0, 3));
    } catch (error) {
        console.error('Error en búsqueda:', error);
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
    console.log('displayMatches llamada con', cities.length, 'ciudades');
    const container = document.getElementById('freeResults');
    if (!container) {
        console.error('❌ freeResults no encontrado en displayMatches');
        return;
    }

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
                        <div class="city-detail"><span class="detail-label">💰 Presupuesto</span><span class="detail-value">${m.budget || 'Moderate'}</span></div>
                        <div class="city-detail"><span class="detail-label">🌡️ Clima</span><span class="detail-value">${m.climate || 'Warm'}</span></div>
                        <div class="city-detail"><span class="detail-label">📶 Internet</span><span class="detail-value">${m.internet || 'Good'}</span></div>
                        <div class="city-detail"><span class="detail-label">🛂 Visa</span><span class="detail-value">${m.visa === 'Yes' || m.visa === '1' ? '✅ Sí' : '❌ No'}</span></div>
                    </div>
                    <div class="city-tags">
                        ${(m.vibe || '').split(',').slice(0, 3).map(t => `<span class="city-tag">${t}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

setInterval(checkHealth, 30000);
setInterval(loadCollections, 60000);

// ============================================
// NOMADMATCH · VERSIÓN FINAL ABSOLUTA
// ============================================

const API_BASE_URL = 'http://localhost:8000/api/v1';
let cityImages = {};
let userPreferences = {};
let hiddenCities = new Set();
let allRankedCities = [];
let lastPreferences = null;
let currentUser = {
    isLoggedIn: false,
    isPremium: false,
    email: null,
    token: null
};

// Mapeo de nombres de ciudades para imágenes
const cityImageMap = {
    "cluj-napoca": "cluj",
    "naples": "napoles",
    "thessaloniki": "thessaloniki",
    "wroclaw": "wroclaw",
    "gdansk": "gdansk",
    "ljubljana": "ljubljana",
    "bratislava": "bratislava",
    "nicosia": "nicosia",
    "groningen": "groningen",
    "innsbruck": "innsbruck",
    "aarhus": "aarhus",
    "cork": "cork",
    "edinburgh": "edinburgh",
    "dublin": "dublin",
    "munich": "munich",
    "vienna": "vienna",
    "malta": "malta",
    "malaga": "malaga",
    "nice": "nice",
    "sarajevo": "sarajevo",
    "tirana": "tirana",
    "brno": "brno",
    "plovdiv": "plovdiv",
    "funchal": "funchal",
    "las palmas": "laspalmas",
    "coimbra": "coimbra",
    "timisoara": "timisoara",
    "krakow": "krakow",
    "prague": "prague",
    "budapest": "budapest",
    "warsaw": "warsaw",
    "lisbon": "lisbon",
    "barcelona": "barcelona",
    "berlin": "berlin",
    "amsterdam": "amsterdam",
    "copenhagen": "copenhagen",
    "stockholm": "stockholm",
    "helsinki": "helsinki", 
    "oslo": "oslo"
};

fetch('/city-images.json')
    .then(response => response.ok ? response.json() : {})
    .then(data => {
        cityImages = data;
        console.log('✅ Imágenes cargadas:', Object.keys(cityImages).length);
    })
    .catch(() => console.warn('⚠️ city-images.json no encontrado'));

function getCityImage(cityName) {
    if (!cityName) return 'https://via.placeholder.com/300x200?text=No+Image';
    if (cityImages[cityName]) return cityImages[cityName];
    let cleanName = cityName.toLowerCase()
        .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
        .replace(/\s+/g, '');
    // Aplicar mapeo especial
    if (cityImageMap[cleanName]) cleanName = cityImageMap[cleanName];
    return `/thumbnails/${cleanName}.jpg`;
}

document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 NomadMatch iniciado');
    checkHealth();
    setupEventListeners();
    checkLoginStatus();
});

// ============================================
// CONFIGURACIÓN DE EVENTOS
// ============================================
function setupEventListeners() {
    const matchButton = document.getElementById('matchButton');
    if (matchButton) matchButton.addEventListener('click', findMatches);

    const btnSignup = document.querySelector('.btn-primary:not(#matchButton)');
    const btnLogin = document.querySelector('.btn-outline');
    const btnPremium = document.querySelector('.premium-badge');

    if (btnSignup) btnSignup.addEventListener('click', () => openAuthModal('register'));
    if (btnLogin) btnLogin.addEventListener('click', () => openAuthModal('login'));
    if (btnPremium) btnPremium.addEventListener('click', () => openPremiumModal());

    const authModal = document.getElementById('authModal');
    const premiumModal = document.getElementById('premiumModal');
    document.querySelectorAll('.close-modal').forEach(btn => {
        btn.addEventListener('click', () => {
            authModal.style.display = 'none';
            premiumModal.style.display = 'none';
        });
    });
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal-wrapper')) {
            authModal.style.display = 'none';
            premiumModal.style.display = 'none';
        }
    });

    const authForm = document.getElementById('authForm');
    if (authForm) authForm.addEventListener('submit', (e) => { e.preventDefault(); handleAuth(); });

    const upgradeBtn = document.getElementById('upgradeBtn');
    if (upgradeBtn) upgradeBtn.addEventListener('click', upgradeToPremium);

    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.addEventListener('click', handleTabClick);
    });
}

// ============================================
// AUTENTICACIÓN
// ============================================
let currentAuthMode = 'login';

function openAuthModal(mode) {
    currentAuthMode = mode;
    const title = document.getElementById('authTitle');
    const subtitle = document.getElementById('authSubtitle');
    title.innerText = mode === 'login' ? 'Iniciar Sesión' : 'Crear cuenta';
    subtitle.innerText = mode === 'login' ? 'Accede a tu cuenta' : 'Únete a la comunidad';
    document.getElementById('authModal').style.display = 'block';
}

async function handleAuth() {
    const email = document.getElementById('userEmail').value;
    const password = document.getElementById('userPass').value;
    const endpoint = currentAuthMode === 'login' ? '/auth/login' : '/auth/register';

    try {
        const res = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        if (!res.ok) throw new Error((await res.json()).detail || 'Error');
        const data = await res.json();
        localStorage.setItem('token', data.access_token);
        currentUser = {
            isLoggedIn: true,
            isPremium: data.is_premium,
            email,
            token: data.access_token
        };
        updateNavbar();
        document.getElementById('authModal').style.display = 'none';
        console.log('✅ Usuario autenticado:', currentUser);
        loadUserPreferences();
    } catch (err) {
        alert(`❌ ${err.message}`);
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
            <button class="lang-toggle"><span class="lang-es">ES</span><span class="lang-separator">/</span><span class="lang-en">EN</span></button>
            <button class="btn-outline" onclick="openAuthModal('login')">Iniciar sesión</button>
            <button class="btn-primary" onclick="openAuthModal('register')">Registrarse</button>
        `;
    }
}

function logout() {
    localStorage.removeItem('token');
    currentUser = { isLoggedIn: false, isPremium: false, email: null, token: null };
    updateNavbar();
    document.querySelector('[data-tab="free"]').click();
}

function checkLoginStatus() {
    const token = localStorage.getItem('token');
    if (!token) return;
    fetch(`${API_BASE_URL}/auth/me`, { headers: { 'Authorization': `Bearer ${token}` } })
        .then(res => res.json())
        .then(user => {
            currentUser = { isLoggedIn: true, isPremium: user.is_premium, email: user.email, token };
            updateNavbar();
            loadUserPreferences();
        })
        .catch(() => localStorage.removeItem('token'));
}

// ============================================
// FUNCIONES PREMIUM
// ============================================
function openPremiumModal() {
    if (!currentUser.isLoggedIn) {
        alert('Inicia sesión primero');
        openAuthModal('login');
        return;
    }
    document.getElementById('premiumModal').style.display = 'block';
}

async function upgradeToPremium() {
    const token = currentUser.token;
    if (!token) return;
    try {
        const res = await fetch(`${API_BASE_URL}/auth/upgrade`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            currentUser.isPremium = true;
            updateNavbar();
            document.getElementById('premiumModal').style.display = 'none';
            alert('✨ ¡Ahora eres Premium!');
            if (document.querySelector('[data-tab="premium"].active')) loadPremiumAdvice();
        } else alert('Error al actualizar');
    } catch (err) { console.error(err); }
}

function handleTabClick(e) {
    const tab = e.target.dataset.tab;
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    e.target.classList.add('active');

    document.getElementById('freeResults').style.display = tab === 'free' ? 'block' : 'none';
    document.getElementById('premiumResults').style.display = tab === 'premium' ? 'block' : 'none';
    document.getElementById('favsResults').style.display = tab === 'favs' ? 'block' : 'none';

    if (tab === 'premium') {
        if (currentUser.isLoggedIn) loadPremiumAdvice();
        else showPremiumLocked();
    } else if (tab === 'favs') {
        loadFavs();
    }
}

function showPremiumLocked() {
    document.getElementById('premiumResults').innerHTML = `
        <div class="empty-state premium-empty">
            <div class="empty-illustration"><span class="empty-emoji">🔒</span></div>
            <h3>Contenido exclusivo para usuarios premium</h3>
            <p>${!currentUser.isLoggedIn ? 'Inicia sesión' : 'Actualiza tu cuenta'} para acceder.</p>
            <button class="btn-primary" id="premiumUpgradeBtn">${!currentUser.isLoggedIn ? 'Iniciar sesión' : 'Actualizar a Premium'}</button>
        </div>
    `;
    document.getElementById('premiumUpgradeBtn').addEventListener('click', () => {
        if (!currentUser.isLoggedIn) openAuthModal('login');
        else openPremiumModal();
    });
}

// ============================================
// BÚSQUEDA Y RANKING (FREE TIER)
// ============================================
async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE_URL}/health`);
        const data = await res.json();
        const statusDot = document.querySelector('.status-dot');
        const dbStatus = document.getElementById('dbStatus');
        if (res.ok && data.status === 'healthy') {
            statusDot.className = 'status-dot connected';
            if (dbStatus) dbStatus.innerText = 'Conectado';
        }
    } catch (err) { console.error('❌ Error API:', err); }
}

async function findMatches() {
    const resultsContainer = document.getElementById('freeResults');
    if (!resultsContainer) return console.error('❌ freeResults no encontrado');
    resultsContainer.innerHTML = '<div class="loading-message">🔍 Buscando...</div>';

    const preferences = {
        budget: document.querySelector('input[name="budget"]:checked')?.value || 'moderate',
        climate: document.querySelector('input[name="climate"]:checked')?.value || 'warm',
        visa: document.querySelector('input[name="visa"]:checked')?.value === 'yes',
        vibes: Array.from(document.querySelectorAll('input[name="vibe"]:checked')).map(cb => cb.value)
    };
    console.log('Preferencias:', preferences);
    lastPreferences = preferences;

    try {
        const query = buildQuery(preferences);
        console.log('Query enviada:', query);
        const res = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, num_results: 30 })
        });
        const data = await res.json();
        console.log('Datos recibidos:', data);
        
        let citiesForRanking = data.results;
        
        if (!citiesForRanking || citiesForRanking.length < 5) {
            console.warn('⚠️ Pocos resultados del backend, usando datos de respaldo (50 ciudades)');
            citiesForRanking = window.fallbackCities;
        }
        
        allRankedCities = rankCities(citiesForRanking, preferences);

        if (allRankedCities.length === 0) {
            resultsContainer.innerHTML = '<div class="loading-message">No se encontraron ciudades</div>';
            return;
        }

        displayMatches();
    } catch (err) {
        console.error('Error:', err);
        console.warn('⚠️ Error en API, usando datos de respaldo');
        allRankedCities = rankCities(window.fallbackCities, preferences);
        displayMatches();
    }
}

function buildQuery(p) {
    let q = `European city for digital nomads. Budget: ${p.budget}, Climate: ${p.climate}.`;
    if (p.visa) q += " Needs digital nomad visa.";
    if (p.vibes.length) q += ` Vibes: ${p.vibes.join(', ')}.`;
    return q;
}

function rankCities(results, p) {
    const scored = results.map(r => {
        const m = r.metadata || {};
        let score = r.score_pct !== undefined ? r.score_pct : (r.similarity_score || 0.5) * 100;
        
        // Clima: multiplicadores más agresivos
        const summer = (m.summer_temp || '').toLowerCase();
        const region = (m.region || '').toLowerCase();
        
        if (p.climate === 'warm') {
            if (summer.includes('warm') || summer.includes('hot') || region.includes('southern')) {
                score = score * 2.0; // DUPLICAR para ciudades cálidas
            } else if (summer.includes('mild')) {
                score = score * 0.8;
            } else {
                score = score * 0.3; // Penalizar fuertemente
            }
        } else if (p.climate === 'mild') {
            if (summer.includes('mild') || region.includes('central')) {
                score = score * 1.5;
            } else {
                score = score * 0.5;
            }
        } else if (p.climate === 'cool') {
            if (summer.includes('cool') || summer.includes('cold') || region.includes('northern')) {
                score = score * 1.5;
            } else {
                score = score * 0.5;
            }
        }
        
        // Visa
        if (p.visa) {
            if (m.visa === 'Yes' || m.Digital_Nomad_Visa === 'Yes') {
                score = score * 1.3;
            } else {
                score = score * 0.6;
            }
        }
        
        // Vibes
        if (p.vibes.length && m.vibe_tags) {
            const tags = m.vibe_tags.toLowerCase();
            p.vibes.forEach(v => {
                if (tags.includes(v.toLowerCase())) score = score * 1.1;
            });
        }
        
        score = Math.min(100, Math.round(score));
        return { ...r, display_score: score, metadata: m };
    });

    // Separar por clima
    const goodClimate = [];
    const badClimate = [];
    
    scored.forEach(item => {
        const m = item.metadata;
        const summer = (m.summer_temp || '').toLowerCase();
        const region = (m.region || '').toLowerCase();
        let meetsClimate = false;
        
        if (p.climate === 'warm') {
            meetsClimate = summer.includes('warm') || summer.includes('hot') || region.includes('southern');
        } else if (p.climate === 'mild') {
            meetsClimate = summer.includes('mild') || region.includes('central');
        } else if (p.climate === 'cool') {
            meetsClimate = summer.includes('cool') || summer.includes('cold') || region.includes('northern');
        }
        
        if (meetsClimate) goodClimate.push(item);
        else badClimate.push(item);
    });
    
    goodClimate.sort((a, b) => b.display_score - a.display_score);
    badClimate.sort((a, b) => b.display_score - a.display_score);
    
    return [...goodClimate, ...badClimate];
}

function displayMatches() {
    console.log('displayMatches llamada');
    const container = document.getElementById('freeResults');
    if (!container) return;

    // Filtrar primero por clima según las preferencias
    let climateFiltered = allRankedCities;
    if (lastPreferences) {
        climateFiltered = allRankedCities.filter(c => {
            const m = c.metadata || {};
            const summer = (m.summer_temp || '').toLowerCase();
            const region = (m.region || '').toLowerCase();
            if (lastPreferences.climate === 'warm') {
                return summer.includes('warm') || summer.includes('hot') || region.includes('southern');
            } else if (lastPreferences.climate === 'mild') {
                return summer.includes('mild') || region.includes('central');
            } else if (lastPreferences.climate === 'cool') {
                return summer.includes('cool') || summer.includes('cold') || region.includes('northern');
            }
            return true; // si no hay preferencia, mostrar todas
        });
    }

    // Luego filtrar las ocultas
    const visible = climateFiltered.filter(c => {
        const name = c.metadata?.city || c.city || '';
        return !hiddenCities.has(name);
    });

    if (visible.length === 0) {
        container.innerHTML = '<div class="empty-state"><h3>No hay ciudades disponibles</h3><p>Prueba con otras preferencias o revisa tus skips en Favs</p></div>';
        return;
    }

    const top3 = visible.slice(0, 3);
    
    container.innerHTML = top3.map((city, idx) => {
        const m = city.metadata || {};
        const name = m.city || city.city || '';
        const country = m.country || city.country || '';
        
        const budgetEur = m.budget_eur || 'N/A';
        const budgetLabel = m.budget || 'Moderate';
        const budgetDisplay = budgetEur !== 'N/A' ? `${budgetEur} EUR (${budgetLabel})` : budgetLabel;

        const winter = m.winter_temp || m.Winter_Temperature || 'N/A';
        const summer = m.summer_temp || m.Summer_Temperature || 'N/A';
        const climateDisplay = (winter !== 'N/A' || summer !== 'N/A') ? `${winter} - ${summer}` : (m.climate || 'N/A');

        const internet = m.internet || m.Internet_Reliability_Score || 'Good';
        const mbps = m.internet_mbps || m.Internet_Avg_Mbps || '';
        const internetDisplay = mbps ? `${internet} (${mbps} Mbps)` : internet;

        const visaOk = m.visa === 'Yes' || m.Digital_Nomad_Visa === 'Yes' || m.visa === '1';
        const visaDisplay = visaOk ? '✅ Sí' : '❌ No';

        let vibeTags = [];
        if (m.vibe_tags) vibeTags = m.vibe_tags.split(',').map(t => t.trim());
        else if (m.Vibe_Tags) vibeTags = m.Vibe_Tags.split(',').map(t => t.trim());
        else if (m.vibe) vibeTags = m.vibe.split(',').map(t => t.trim());
        const topVibes = vibeTags.slice(0, 3);

        const score = city.display_score || 0;
        const scoreDisplay = score ? `${score}%` : 'N/A';

        return `
            <div class="city-card" data-city="${name}">
                <img class="city-image" src="${getCityImage(name)}" alt="${name}" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
                <div class="city-info">
                    <div class="city-header">
                        <div><span class="city-name">${name}</span><span class="city-country">${country}</span></div>
                        <span class="city-score">#${idx+1} · ${scoreDisplay}</span>
                    </div>
                    <div class="city-details">
                        <div class="city-detail">
                            <span class="detail-label">💰 Budget</span>
                            <span class="detail-value">${budgetDisplay}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">🌡️ Clima</span>
                            <span class="detail-value">${climateDisplay}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">📶 Internet</span>
                            <span class="detail-value">${internetDisplay}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">🛂 Visa</span>
                            <span class="detail-value">${visaDisplay}</span>
                        </div>
                    </div>
                    <div class="city-tags">${topVibes.map(t => `<span class="city-tag">${t}</span>`).join('')}</div>
                    ${currentUser.isLoggedIn ? `
                    <div class="city-actions">
                        <button class="btn-match ${userPreferences[name] === 'like' ? 'active' : ''}" onclick="setCityPreference('${name.replace(/'/g, "\\'")}', 'like', this)" title="Match"><span class="action-icon">❤️</span><span class="action-text">Match</span></button>
                        <button class="btn-skip ${userPreferences[name] === 'dislike' ? 'active' : ''}" onclick="setCityPreference('${name.replace(/'/g, "\\'")}', 'dislike', this)" title="Skip"><span class="action-icon">✖️</span><span class="action-text">Skip</span></button>
                    </div>` : ''}
                </div>
            </div>
        `;
    }).join('');
}
// ============================================
// PREFERENCIAS DE CIUDAD (MATCH/SKIP)
// ============================================
async function loadUserPreferences() {
    if (!currentUser.isLoggedIn) return;
    try {
        const res = await fetch(`${API_BASE_URL}/preferences/cities`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (res.ok) {
            const data = await res.json();
            userPreferences = {};
            hiddenCities.clear();
            (data.preferences || []).forEach(p => {
                userPreferences[p.city_name] = p.action;
                if (p.action === 'dislike') hiddenCities.add(p.city_name);
            });
            console.log('✅ Preferencias cargadas:', Object.keys(userPreferences).length);
        }
    } catch (err) { console.warn('⚠️ Error cargando preferencias:', err); }
}

async function setCityPreference(cityName, action, btn) {
    if (!currentUser.token) return;
    if (userPreferences[cityName] === action) {
        try {
            const res = await fetch(`${API_BASE_URL}/preferences/city/${encodeURIComponent(cityName)}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${currentUser.token}` }
            });
            if (res.ok) {
                delete userPreferences[cityName];
                if (action === 'dislike') hiddenCities.delete(cityName);
                updatePreferenceButtons(cityName);
                showToast(`Preferencia eliminada`, 'info');
                refreshFeed();
            }
        } catch (err) { console.error(err); }
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/preferences/city`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${currentUser.token}`, 'Content-Type': 'application/json' },
            body: JSON.stringify({ city_name: cityName, action })
        });
        if (res.ok) {
            userPreferences[cityName] = action;
            if (action === 'dislike') hiddenCities.add(cityName);
            else hiddenCities.delete(cityName);
            updatePreferenceButtons(cityName);
            showToast(action === 'like' ? `❤️ ${cityName} añadida` : `✖️ ${cityName} ocultada`, action === 'like' ? 'success' : 'warning');
            if (action === 'dislike' && btn) {
                const card = btn.closest('.city-card');
                if (card) {
                    card.style.transition = 'opacity 0.5s, transform 0.5s';
                    card.style.opacity = '0';
                    card.style.transform = 'translateX(100px)';
                    setTimeout(() => card.remove(), 500);
                }
            }
            refreshFeed();
        }
    } catch (err) { console.error(err); showToast('Error', 'error'); }
}

function updatePreferenceButtons(cityName) {
    document.querySelectorAll('.city-card').forEach(card => {
        const nameEl = card.querySelector('.city-name');
        if (nameEl && nameEl.textContent === cityName) {
            const match = card.querySelector('.btn-match');
            const skip = card.querySelector('.btn-skip');
            if (match) match.classList.toggle('active', userPreferences[cityName] === 'like');
            if (skip) skip.classList.toggle('active', userPreferences[cityName] === 'dislike');
        }
    });
}

function showToast(msg, type = 'info') {
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();
    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.textContent = msg;
    document.body.appendChild(toast);
    requestAnimationFrame(() => toast.classList.add('show'));
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function refreshFeed() {
    if (document.querySelector('[data-tab="free"].active') && allRankedCities.length) {
        displayMatches();
    }
}

// ============================================
// PESTAÑA PREMIUM (AHORA COHERENTE CON FREE)
// ============================================
async function loadPremiumAdvice() {
    console.log('🔷 loadPremiumAdvice ejecutada');
    const container = document.getElementById('premiumResults');
    if (!container) return;

    if (!allRankedCities || allRankedCities.length === 0 || !lastPreferences) {
        container.innerHTML = '<div class="empty-state">Primero realiza una búsqueda en la pestaña Free</div>';
        return;
    }

    // Aplicar el mismo filtro climático que en displayMatches
    let climateFiltered = allRankedCities;
    if (lastPreferences) {
        climateFiltered = allRankedCities.filter(c => {
            const m = c.metadata || {};
            const summer = (m.summer_temp || '').toLowerCase();
            const region = (m.region || '').toLowerCase();
            if (lastPreferences.climate === 'warm') {
                return summer.includes('warm') || summer.includes('hot') || region.includes('southern');
            } else if (lastPreferences.climate === 'mild') {
                return summer.includes('mild') || region.includes('central');
            } else if (lastPreferences.climate === 'cool') {
                return summer.includes('cool') || summer.includes('cold') || region.includes('northern');
            }
            return true;
        });
    }

    // Filtrar también las ocultas (aunque en Premium quizá no sea necesario, pero por consistencia)
    const visible = climateFiltered.filter(c => {
        const name = c.metadata?.city || c.city || '';
        return !hiddenCities.has(name);
    });

    if (visible.length === 0) {
        container.innerHTML = '<div class="empty-state">No hay ciudades disponibles</div>';
        return;
    }

    // Mostrar las 3 primeras (igual que en Free)
    const top3 = visible.slice(0, 3);
    
    let html = '';
    for (const city of top3) {
        const m = city.metadata || {};
        const cityName = m.city || 'Ciudad';
        const country = m.country || '';
        
        const visaAvailable = m.visa === 'Yes' ? '✅ Sí' : '❌ No';
        const visaType = m.visa_type || 'N/A';
        const visaScore = m.visa_score || 'N/A';
        const taxRate = m.tax_rate || 'N/A';
        const taxRegime = m.tax_regime || 'N/A';
        const taxScore = m.tax_score || 'N/A';

        html += `
            <div class="city-card premium-card">
                <img class="city-image" src="${getCityImage(cityName)}" alt="${cityName}" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
                <div class="city-info">
                    <div class="city-header">
                        <span class="city-name">${cityName}</span>
                        <span class="city-country">${country}</span>
                    </div>
                    
                    <div class="premium-detail-section">
                        <h4>🛂 Visa</h4>
                        <div class="city-details">
                            <div class="city-detail">
                                <span class="detail-label">Disponible</span>
                                <span class="detail-value">${visaAvailable}</span>
                            </div>
                            <div class="city-detail">
                                <span class="detail-label">Tipo</span>
                                <span class="detail-value">${visaType}</span>
                            </div>
                            <div class="city-detail">
                                <span class="detail-label">Visa Score</span>
                                <span class="detail-value">${visaScore}</span>
                            </div>
                        </div>
                    </div>
                    
                    <div class="premium-detail-section">
                        <h4>💰 Fiscalidad</h4>
                        <div class="city-details">
                            <div class="city-detail">
                                <span class="detail-label">Tasa estándar</span>
                                <span class="detail-value">${taxRate}%</span>
                            </div>
                            <div class="city-detail">
                                <span class="detail-label">Régimen especial</span>
                                <span class="detail-value">${taxRegime}</span>
                            </div>
                            <div class="city-detail">
                                <span class="detail-label">Tax Score</span>
                                <span class="detail-value">${taxScore}</span>
                            </div>
                        </div>
                    </div>
                    
                    ${currentUser.isLoggedIn ? `
                    <div class="city-actions">
                        <button class="btn-match ${userPreferences[cityName] === 'like' ? 'active' : ''}" onclick="setCityPreference('${cityName.replace(/'/g, "\\'")}', 'like', this)" title="Match"><span class="action-icon">❤️</span><span class="action-text">Match</span></button>
                        <button class="btn-skip ${userPreferences[cityName] === 'dislike' ? 'active' : ''}" onclick="setCityPreference('${cityName.replace(/'/g, "\\'")}', 'dislike', this)" title="Skip"><span class="action-icon">✖️</span><span class="action-text">Skip</span></button>
                    </div>` : ''}
                </div>
            </div>
        `;
    }
    
    // Añadir análisis LLM simulado
    const analysis = generatePremiumAnalysis(top3);
    html += `<div class="premium-analysis">${analysis}</div>`;
    
    container.innerHTML = html;
    console.log('✅ Premium HTML generado');
}

// Simulación de análisis LLM
function generatePremiumAnalysis(top3) {
    if (top3.length === 0) return '';
    const cities = top3.map(c => c.metadata?.city).join(', ');
    return `
        <div class="llm-analysis">
            <h4>🤖 Análisis de IA</h4>
            <p>Basado en tus preferencias, las ciudades que mejor se ajustan son <strong>${cities}</strong>.</p>
            <p>${top3[0].metadata?.city} destaca por su excelente puntuación fiscal y disponibilidad de visa nómada. ${top3[1]?.metadata?.city} ofrece un equilibrio entre costo y calidad de vida. ${top3[2]?.metadata?.city} es ideal si priorizas la comunidad tecnológica.</p>
            <p>Recuerda que los requisitos de visa pueden cambiar; consulta fuentes oficiales antes de planificar tu mudanza.</p>
        </div>
    `;
}

// ============================================
// FAVS
// ============================================
async function loadFavs() {
    const container = document.getElementById('favsResults');
    if (!container) return;
    if (!currentUser.isLoggedIn) {
        container.innerHTML = `<div class="empty-state"><h3>Inicia sesión para ver favoritos</h3><button class="btn-primary" onclick="openAuthModal('login')">Iniciar sesión</button></div>`;
        return;
    }
    try {
        const res = await fetch(`${API_BASE_URL}/preferences/cities`, {
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (!res.ok) throw new Error();
        const data = await res.json();
        const likes = data.likes || [];
        const dislikes = data.dislikes || [];
        let html = '<div class="favs-container">';
        html += '<div class="favs-section"><h3>❤️ Matches</h3>';
        if (likes.length === 0) html += '<p class="empty-message">No tienes matches aún</p>';
        else likes.forEach(c => html += createFavCard(c, 'like'));
        html += '</div><div class="favs-section"><h3>✖️ Skips</h3>';
        if (dislikes.length === 0) html += '<p class="empty-message">No tienes skips aún</p>';
        else dislikes.forEach(c => html += createFavCard(c, 'dislike'));
        html += '</div></div>';
        container.innerHTML = html;
    } catch (err) { container.innerHTML = '<div class="empty-state">Error cargando favoritos</div>'; }
}

function createFavCard(cityName, action) {
    const other = action === 'like' ? 'dislike' : 'like';
    const otherText = action === 'like' ? 'Mover a Skip' : 'Mover a Match';
    const otherIcon = action === 'like' ? '✖️' : '❤️';
    return `
        <div class="city-card fav-card" data-city="${cityName}">
            <img class="city-image" src="${getCityImage(cityName)}" alt="${cityName}" onerror="this.src='https://via.placeholder.com/300x200?text=No+Image'">
            <div class="city-info">
                <div class="city-header"><span class="city-name">${cityName}</span></div>
                <div class="city-actions">
                    <button class="btn-outline" onclick="changeFavPreference('${cityName}', '${other}')"><span class="action-icon">${otherIcon}</span> ${otherText}</button>
                    <button class="btn-outline" onclick="deleteFavPreference('${cityName}')"><span class="action-icon">🗑️</span> Eliminar</button>
                </div>
            </div>
        </div>
    `;
}

async function changeFavPreference(cityName, newAction) {
    await setCityPreference(cityName, newAction, null);
    loadFavs();
    refreshFeed();
}

async function deleteFavPreference(cityName) {
    if (!currentUser.token) return;
    try {
        const res = await fetch(`${API_BASE_URL}/preferences/city/${encodeURIComponent(cityName)}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${currentUser.token}` }
        });
        if (res.ok) {
            delete userPreferences[cityName];
            if (hiddenCities.has(cityName)) hiddenCities.delete(cityName);
            loadFavs();
            refreshFeed();
            showToast('Preferencia eliminada', 'info');
        }
    } catch (err) { console.error(err); }
}

// Health check automático
setInterval(checkHealth, 30000);

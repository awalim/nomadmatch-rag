// ============================================================
// NomadMatch Frontend — Connected to Langflow RAG Pipeline
// ============================================================

// --- Configuration ---
const LANGFLOW_BASE_URL = 'http://localhost:7860';
const LANGFLOW_FLOW_ID = 'efea90c6-fd58-4604-b054-1b587f87c998';
const BACKEND_API_URL = 'http://localhost:8000/api/v1';

let cityImages = {};
let chatHistory = []; // Mantener historial para el sistema de swipe

// --- Load city images ---
fetch('/city-images.json')
    .then(response => {
        if (!response.ok) throw new Error('No se pudieron cargar las imágenes');
        return response.json();
    })
    .then(data => {
        cityImages = data;
        console.log('✅ Imágenes cargadas:', Object.keys(cityImages).length);
    })
    .catch(error => {
        console.error('❌ Error cargando imágenes:', error);
        cityImages = {};
    });

// --- Initialize app ---
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 NomadMatch iniciado (Langflow mode)');
    checkLangflowHealth();
    checkBackendHealth();
    setupEventListeners();
});

function setupEventListeners() {
    const matchButton = document.getElementById('matchButton');
    if (matchButton) {
        console.log('✅ Botón encontrado');
        matchButton.addEventListener('click', findMatches);
    } else {
        console.error('❌ Botón matchButton no encontrado');
    }
}

// --- Health checks ---
async function checkLangflowHealth() {
    try {
        const response = await fetch(`${LANGFLOW_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Langflow conectado');
            updateStatus('connected', 'Conectado a Langflow');
        } else {
            console.warn('⚠️ Langflow responde pero con error');
            updateStatus('disconnected', 'Langflow error');
        }
    } catch (error) {
        console.error('❌ Langflow no disponible:', error.message);
        updateStatus('disconnected', 'Sin conexión a Langflow');
    }
}

async function checkBackendHealth() {
    try {
        const response = await fetch(`${BACKEND_API_URL}/health`);
        const data = await response.json();
        if (data.status === 'healthy') {
            console.log('✅ Backend FastAPI conectado (admin/ingesta)');
        }
    } catch (error) {
        console.warn('⚠️ Backend FastAPI no disponible (solo afecta admin)');
    }
}

function updateStatus(state, text) {
    const statusEl = document.querySelector('.status-indicator');
    const statusDot = document.querySelector('.status-dot');
    if (statusEl && statusDot) {
        statusDot.className = `status-dot ${state}`;
        statusEl.innerHTML = `<span class="status-dot ${state}"></span>${text}`;
    }
}

// --- Main: Find Matches via Langflow ---
async function findMatches() {
    console.log('🎯 Buscando ciudades via Langflow...');

    const resultsContainer = document.getElementById('freeResults');
    if (!resultsContainer) {
        console.error('❌ resultsContainer no encontrado');
        return;
    }

    // Loading state
    resultsContainer.innerHTML = `
        <div class="loading-message">
            <span class="loading-icon">🔍</span>
            <p>Buscando tus ciudades ideales con IA...</p>
        </div>
    `;

    // Collect preferences from UI
    const preferences = collectPreferences();
    console.log('📋 Preferencias:', preferences);

    // Build the PROFILE message for Langflow prompt
    const profileMessage = buildProfileMessage(preferences);
    console.log('📨 Mensaje a Langflow:', profileMessage);

    try {
        const data = await callLangflow(profileMessage);
        console.log('📊 Respuesta Langflow:', data);

        // Parse the JSON response from the LLM
        const cities = parseLangflowResponse(data);
        console.log('🏆 Ciudades:', cities);

        if (cities.length === 0) {
            throw new Error('No se encontraron ciudades');
        }

        displayMatches(cities.slice(0, 3));

    } catch (error) {
        console.error('❌ Error:', error);
        resultsContainer.innerHTML = `
            <div class="loading-message">
                <span class="loading-icon">❌</span>
                <p>Error: ${error.message}</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">
                    Verifica que Langflow esté corriendo en puerto 7860
                    <br>
                    <button onclick="findMatches()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        🔄 Reintentar
                    </button>
                </p>
            </div>
        `;
    }
}

// --- Collect preferences from UI ---
function collectPreferences() {
    const budgetEl = document.querySelector('input[name="budget"]:checked');
    const climateEl = document.querySelector('input[name="climate"]:checked');
    const internetEl = document.querySelector('input[name="internet"]:checked');
    const visaEl = document.querySelector('input[name="visa"]:checked');
    const vibeEls = document.querySelectorAll('input[name="vibe"]:checked');

    return {
        budget: budgetEl ? budgetEl.value : 'moderate',
        climate: climateEl ? climateEl.value : 'warm',
        internet: internetEl ? internetEl.value : 'good',
        visa: visaEl ? visaEl.value === 'yes' : true,
        vibes: Array.from(vibeEls).map(cb => cb.value)
    };
}

// --- Build PROFILE message matching Langflow prompt format ---
function buildProfileMessage(preferences) {
    // Map frontend values to what the Langflow prompt expects
    const budgetMap = {
        'very_affordable': 'below 900',
        'affordable': '900 to 1200',
        'moderate': '1200 to 1600',
        'expensive': '1600 to 2000'
    };

    const climateMap = {
        'warm': 'warm',
        'mild': 'temperate',
        'cool': 'cool'
    };

    const vibeMap = {
        'beach': 'beach',
        'nightlife': 'nightlife',
        'historic': 'historical',
        'nature': 'nature',
        'tech': 'tech_hub',
        'foodie': 'foodie',
        'art': 'art',
        'sports': 'sports'
    };

    const vibes = preferences.vibes.map(v => vibeMap[v] || v);

    // Format: PROFILE: tier=free, budget_range=X, climate=Y, visa_needed=Z, vibes=[a,b,c]
    const profile = `PROFILE: tier=free, budget_range=${budgetMap[preferences.budget] || '1200 to 1600'}, climate=${climateMap[preferences.climate] || 'warm'}, visa_needed=${preferences.visa}, vibes=[${vibes.join(',')}], nationality=EU, tax_optimization=false`;

    return profile;
}

// --- Call Langflow API ---
async function callLangflow(message) {
    // Langflow API endpoint for running a flow
    const url = `${LANGFLOW_BASE_URL}/api/v1/run/${LANGFLOW_FLOW_ID}`;

    const payload = {
        input_value: message,
        output_type: "chat",
        input_type: "chat",
        tweaks: {}
    };

    console.log('📡 POST', url);

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ Langflow error response:', errorText);
        throw new Error(`Langflow error ${response.status}: ${errorText.substring(0, 200)}`);
    }

    return await response.json();
}

// --- Parse Langflow response ---
function parseLangflowResponse(data) {
    try {
        // Langflow returns nested structure
        // outputs[0].outputs[0].results.message.text contains the LLM response
        let text = '';

        if (data.outputs && data.outputs[0] && data.outputs[0].outputs) {
            const output = data.outputs[0].outputs[0];
            if (output.results && output.results.message) {
                text = output.results.message.text || output.results.message.data?.text || '';
            } else if (output.messages && output.messages[0]) {
                text = output.messages[0].message || output.messages[0].text || '';
            }
        }

        if (!text) {
            // Try alternative paths
            if (typeof data === 'string') text = data;
            else if (data.result) text = data.result;
            else if (data.message) text = data.message;
        }

        console.log('📝 Raw LLM text (first 500 chars):', text.substring(0, 500));

        if (!text) {
            throw new Error('Respuesta vacía de Langflow');
        }

        // Clean the text - remove markdown code blocks if present
        let cleanText = text.trim();
        cleanText = cleanText.replace(/^```json\s*/i, '').replace(/^```\s*/i, '').replace(/\s*```$/i, '');
        cleanText = cleanText.trim();

        // Parse JSON
        const parsed = JSON.parse(cleanText);

        // Store for swipe history
        if (parsed.cities && Array.isArray(parsed.cities)) {
            return parsed.cities.map(city => ({
                card: city.card || city,
                detail: city.detail || {},
                // Keep the full structure for display
                _raw: city
            }));
        }

        // If it's an array directly
        if (Array.isArray(parsed)) {
            return parsed;
        }

        console.warn('⚠️ Estructura inesperada:', Object.keys(parsed));
        return [];

    } catch (e) {
        console.error('❌ Error parsing Langflow response:', e);
        console.error('Raw data:', JSON.stringify(data).substring(0, 1000));
        throw new Error('Error al procesar la respuesta de Langflow. Revisa los logs.');
    }
}

// --- Display matches (updated for Langflow JSON format) ---
function displayMatches(cities) {
    const resultsContainer = document.getElementById('freeResults');

    if (!cities || cities.length === 0) {
        resultsContainer.innerHTML = `
            <div class="loading-message">
                <span class="loading-icon">😕</span>
                <p>No encontramos ciudades con esos criterios.</p>
                <p style="font-size: 0.9rem;">Prueba con otras preferencias</p>
            </div>
        `;
        return;
    }

    let html = '';
    cities.forEach((cityData, index) => {
        const card = cityData.card || cityData;
        const detail = cityData.detail || {};

        const cityName = card.city || 'Ciudad';
        const country = card.country || '';
        const matchPct = card.match_percentage || 0;
        const monthlyCost = card.monthly_cost_eur || 0;
        const heroDesc = card.hero_description || '';
        const topReasons = card.top_reasons || [];
        const vibeTags = card.vibe_tags || [];

        // Image lookup
        const imageKey = cityName.toLowerCase().replace(/\s+/g, '');
        const imageUrl = cityImages[imageKey] || `https://images.unsplash.com/photo-1449824913935-59a10c8d2000?w=600`;

        // Detail fields
        const climate = detail.climate || '';
        const internet = detail.internet ? `${detail.internet} Mbps` : '';
        const community = detail.community || '';
        const safety = detail.safety || '';
        const costBreakdown = detail.cost_breakdown || {};
        const neighbourhoods = detail.best_neighbourhoods || [];
        const coworkingSpaces = detail.coworking_spaces || [];

        // Visa/Tax (premium vs locked)
        const visaSection = detail.visa_section || 'locked_premium';
        const taxSection = detail.tax_section || 'locked_premium';
        const isPremiumLocked = visaSection === 'locked_premium';

        html += `
            <div class="city-card" data-city="${cityName}">
                <img class="city-image" src="${imageUrl}" alt="${cityName}" loading="lazy"
                     onerror="this.src='https://images.unsplash.com/photo-1449824913935-59a10c8d2000?w=600'">
                <div class="city-info">
                    <div class="city-header">
                        <div>
                            <span class="city-name">${cityName}</span>
                            <span class="city-country">${country}</span>
                        </div>
                        <span class="city-score">${matchPct}%</span>
                    </div>

                    ${heroDesc ? `<p class="city-hero">${heroDesc}</p>` : ''}

                    <div class="city-details">
                        <div class="city-detail">
                            <span class="detail-label">💰 Coste mensual</span>
                            <span class="detail-value">${monthlyCost ? monthlyCost + '€' : 'N/A'}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">🌡️ Clima</span>
                            <span class="detail-value">${climate || 'N/A'}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">📶 Internet</span>
                            <span class="detail-value">${internet || 'N/A'}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">👥 Comunidad</span>
                            <span class="detail-value">${community || 'N/A'}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">🛡️ Seguridad</span>
                            <span class="detail-value">${safety || 'N/A'}</span>
                        </div>
                    </div>

                    ${topReasons.length > 0 ? `
                        <div class="city-reasons">
                            ${topReasons.map(r => `<p class="reason">✓ ${r}</p>`).join('')}
                        </div>
                    ` : ''}

                    <div class="city-tags">
                        ${vibeTags.slice(0, 5).map(tag => `<span class="city-tag">${tag}</span>`).join('')}
                    </div>

                    ${isPremiumLocked ? `
                        <div class="premium-lock">
                            🔒 Visa y fiscalidad disponibles en Premium
                        </div>
                    ` : `
                        <div class="premium-info">
                            <p>🛂 ${visaSection}</p>
                            <p>💼 ${taxSection}</p>
                        </div>
                    `}

                    <div class="swipe-buttons">
                        <button class="btn-match" onclick="swipeCity('${cityName}', 'MATCHED')">❤️ Match</button>
                        <button class="btn-skip" onclick="swipeCity('${cityName}', 'SKIPPED')">✕ Skip</button>
                    </div>
                </div>
            </div>
        `;
    });

    resultsContainer.innerHTML = html;
    console.log('✅ Resultados mostrados:', cities.length, 'ciudades');
}

// --- Swipe system (Match/Skip) ---
async function swipeCity(cityName, action) {
    console.log(`👆 ${action}: ${cityName}`);

    const resultsContainer = document.getElementById('freeResults');
    resultsContainer.innerHTML = `
        <div class="loading-message">
            <span class="loading-icon">🔄</span>
            <p>Procesando tu ${action === 'MATCHED' ? 'match' : 'skip'}...</p>
        </div>
    `;

    const message = `${action}: ${cityName}`;

    try {
        const data = await callLangflow(message);
        const cities = parseLangflowResponse(data);

        if (cities.length === 0) {
            throw new Error('No se encontraron más ciudades');
        }

        displayMatches(cities.slice(0, 3));

    } catch (error) {
        console.error('❌ Error en swipe:', error);
        resultsContainer.innerHTML = `
            <div class="loading-message">
                <span class="loading-icon">⚠️</span>
                <p>Error al procesar. ${error.message}</p>
                <button onclick="findMatches()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    🔄 Buscar de nuevo
                </button>
            </div>
        `;
    }
}

// --- Health check auto-refresh ---
setInterval(checkLangflowHealth, 30000);
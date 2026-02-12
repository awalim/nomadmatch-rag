// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';
let cityImages = {};

// Load city images
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
        // Imágenes por defecto
        cityImages = {
            'lisbon': 'https://images.unsplash.com/photo-1585208798174-6cedd86e019a?w=600',
            'barcelona': 'https://images.unsplash.com/photo-1583422409516-2895a77efded?w=600',
            'berlin': 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=600'
        };
    });

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 NomadMatch iniciado');
    checkHealth();
    setupEventListeners();
    checkCollections();
});

function setupEventListeners() {
    const matchButton = document.getElementById('matchButton');
    if (matchButton) {
        console.log('✅ Botón encontrado, añadiendo evento');
        matchButton.addEventListener('click', findMatches);
    } else {
        console.error('❌ Botón no encontrado');
    }
}

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        const data = await response.json();
        console.log('🏥 Health check:', data);
        
        if (response.ok && data.status === 'healthy') {
            updateStatus('connected', 'Conectado');
        } else {
            updateStatus('disconnected', 'API Error');
        }
    } catch (error) {
        console.error('❌ Error de conexión:', error);
        updateStatus('disconnected', 'Sin conexión');
    }
}

async function checkCollections() {
    try {
        const response = await fetch(`${API_BASE_URL}/collections`);
        const data = await response.json();
        console.log('📚 Colecciones:', data);
        
        const collectionInfo = document.getElementById('collectionInfo');
        if (collectionInfo) {
            if (data.collections && data.collections.length > 0) {
                collectionInfo.innerHTML = `
                    <p><strong>Base de datos:</strong> ${data.collections[0]}</p>
                    <p><strong>Estado:</strong> ✅ Lista para consultas</p>
                `;
            } else {
                collectionInfo.innerHTML = `
                    <p><strong>Base de datos:</strong> Vacía</p>
                    <p class="small">⚠️ Sube un archivo CSV primero</p>
                `;
            }
        }
    } catch (error) {
        console.error('❌ Error checking collections:', error);
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

async function findMatches() {
    console.log('🎯 Buscando ciudades...');
    
    // Show loading state
    const resultsContainer = document.getElementById('resultsContainer');
    if (!resultsContainer) {
        console.error('❌ resultsContainer no encontrado');
        return;
    }
    
    resultsContainer.innerHTML = `
        <div class="loading-message">
            <span class="loading-icon">🔍</span>
            <p>Buscando tus ciudades ideales...</p>
        </div>
    `;

    // Get preferences
    const budgetElement = document.querySelector('input[name="budget"]:checked');
    const climateElement = document.querySelector('input[name="climate"]:checked');
    const internetElement = document.querySelector('input[name="internet"]:checked');
    const visaElement = document.querySelector('input[name="visa"]:checked');
    const vibeElements = document.querySelectorAll('input[name="vibe"]:checked');
    
    const preferences = {
        budget: budgetElement ? budgetElement.value : 'moderate',
        climate: climateElement ? climateElement.value : 'warm',
        internet: internetElement ? internetElement.value : 'good',
        visa: visaElement ? visaElement.value === 'yes' : true,
        vibes: Array.from(vibeElements).map(cb => cb.value)
    };
    
    console.log('📋 Preferencias:', preferences);

    try {
        // Convert preferences to search query
        const query = buildQuery(preferences);
        console.log('🔍 Query:', query);
        
        // Search cities
        console.log('📡 Enviando petición a:', `${API_BASE_URL}/query`);
        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: query,
                num_results: 15
            })
        });

        console.log('📥 Respuesta status:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }
        
        const data = await response.json();
        console.log('📊 Resultados:', data);
        
        if (!data.results || data.results.length === 0) {
            throw new Error('No se encontraron resultados');
        }
        
        // Filter and rank cities
        const matches = rankCities(data.results, preferences);
        console.log('🏆 Top matches:', matches.slice(0, 3));
        
        // Display top 3 matches
        displayMatches(matches.slice(0, 3));
        
    } catch (error) {
        console.error('❌ Error en findMatches:', error);
        resultsContainer.innerHTML = `
            <div class="loading-message">
                <span class="loading-icon">❌</span>
                <p>Error: ${error.message}</p>
                <p style="font-size: 0.9rem; margin-top: 1rem;">
                    ¿Has subido el archivo CSV? 
                    <br>
                    <button onclick="location.reload()" style="margin-top: 0.5rem; padding: 0.5rem 1rem; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer;">
                        🔄 Reintentar
                    </button>
                </p>
            </div>
        `;
    }
}

function buildQuery(preferences) {
    let query = 'European city for digital nomads';
    
    // Add budget
    const budgetMap = {
        'very_affordable': ' very affordable budget under 900 euros',
        'affordable': ' affordable budget 900 to 1200 euros',
        'moderate': ' moderate budget 1200 to 1600 euros',
        'expensive': ' higher budget 1600 to 2000 euros'
    };
    query += budgetMap[preferences.budget] || '';
    
    // Add climate
    const climateMap = {
        'warm': ' warm climate southern europe',
        'mild': ' mild climate central europe',
        'cool': ' cool climate northern europe'
    };
    query += climateMap[preferences.climate] || '';
    
    // Add internet
    if (preferences.internet === 'excellent') query += ' excellent fast internet 200+ Mbps';
    if (preferences.internet === 'good') query += ' good reliable internet';
    
    // Add visa
    if (preferences.visa) query += ' digital nomad visa available';
    
    // Add vibes
    preferences.vibes.forEach(vibe => {
        const vibeMap = {
            'beach': ' beach coastal city',
            'nightlife': ' vibrant nightlife party scene',
            'historic': ' historic old town culture',
            'nature': ' nature mountains outdoors',
            'tech': ' tech hub startup scene'
        };
        query += vibeMap[vibe] || '';
    });
    
    return query;
}

function rankCities(results, preferences) {
    return results
        .map(result => {
            const metadata = result.metadata || {};
            let score = result.similarity_score || 0.5;
            
            // Boost score based on preference matches
            if (preferences.visa && metadata.Digital_Nomad_Visa === 'Yes') score += 0.3;
            if (preferences.internet === 'excellent' && metadata.Internet_Reliability_Score === 'Excellent') score += 0.3;
            if (preferences.budget === 'very_affordable' && metadata.Monthly_Budget_Single === 'Very Affordable') score += 0.3;
            if (preferences.budget === 'affordable' && metadata.Monthly_Budget_Single === 'Affordable') score += 0.2;
            if (preferences.climate === 'warm' && metadata.Region === 'Southern Europe') score += 0.2;
            if (preferences.climate === 'mild' && metadata.Region === 'Central Europe') score += 0.2;
            if (preferences.climate === 'cool' && metadata.Region === 'Northern Europe') score += 0.2;
            
            return {
                ...result,
                score: score
            };
        })
        .sort((a, b) => b.score - a.score);
}

function displayMatches(cities) {
    const resultsContainer = document.getElementById('resultsContainer');
    
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
    cities.forEach((city, index) => {
        const metadata = city.metadata || {};
        const cityName = metadata.city || 'Ciudad';
        const country = metadata.country || metadata.Country || '';
        const imageKey = cityName.toLowerCase();
        const imageUrl = cityImages[imageKey] || 'https://images.unsplash.com/photo-1449824913935-59a10c8d2000?w=600';
        
        const budget = metadata.Monthly_Budget_Single || 'Moderate';
        const internet = metadata.Internet_Reliability_Score || 'Good';
        const visa = metadata.Digital_Nomad_Visa === 'Yes' ? '✅ Sí' : '❌ No';
        const temp = metadata.Summer_Temperature || 'Warm';
        const vibeTags = metadata.Vibe_Tags ? metadata.Vibe_Tags.split(',').map(t => t.trim()) : ['Europe'];
        
        html += `
            <div class="city-card">
                <img class="city-image" src="${imageUrl}" alt="${cityName}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1449824913935-59a10c8d2000?w=600'">
                <div class="city-info">
                    <div class="city-header">
                        <div>
                            <span class="city-name">${cityName}</span>
                            <span class="city-country">${country}</span>
                        </div>
                        <span class="city-score">#${index + 1}</span>
                    </div>
                    
                    <div class="city-details">
                        <div class="city-detail">
                            <span class="detail-label">💰 Presupuesto</span>
                            <span class="detail-value">${budget}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">🌡️ Clima</span>
                            <span class="detail-value">${temp}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">📶 Internet</span>
                            <span class="detail-value">${internet}</span>
                        </div>
                        <div class="city-detail">
                            <span class="detail-label">🛂 Visa</span>
                            <span class="detail-value">${visa}</span>
                        </div>
                    </div>
                    
                    <div class="city-tags">
                        ${vibeTags.slice(0, 4).map(tag => `<span class="city-tag">${tag.trim()}</span>`).join('')}
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
    console.log('✅ Resultados mostrados');
}

// Auto-refresh health check
setInterval(checkHealth, 30000);

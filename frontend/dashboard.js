const API_BASE = 'http://localhost:5000/api';
let forecastChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadCities();
});

async function loadCities() {
    try {
        const response = await fetch(`${API_BASE}/cities`);
        const data = await response.json();
        
        const select = document.getElementById('citySelect');
        select.innerHTML = '';
        
        data.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            select.appendChild(option);
        });
        
        select.value = 'Delhi';
        updateCity();
    } catch (error) {
        console.error('Error:', error);
    }
}

async function updateCity() {
    const city = document.getElementById('citySelect').value;
    if (city) {
        await loadCurrentData(city);
        await loadForecast(city);
    }
}

async function loadCurrentData(city) {
    try {
        const response = await fetch(`${API_BASE}/current/${city}`);
        const data = await response.json();
        
        if (response.ok) {
            displayCurrentData(data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayCurrentData(data) {
    const aqi = data.aqi || 0;
    const aqiLevel = getAQILevel(aqi);
    
    const html = `
        <h2>${data.city}</h2>
        <div class="aqi-value aqi-${aqiLevel.class}">${Math.round(aqi)}</div>
        <p style="font-size: 1.2em;">${aqiLevel.text}</p>
        <div class="health-alert ${data.health_alert.severity === 'critical' ? 'critical' : ''}">
            <strong>${data.health_alert.level}</strong><br>
            ${data.health_alert.message}
        </div>
        <div class="pollutants-grid">
            <div class="pollutant-item">
                <strong>PM2.5</strong><br>${data.pollutants.PM2_5?.toFixed(1) || 'N/A'}
            </div>
            <div class="pollutant-item">
                <strong>PM10</strong><br>${data.pollutants.PM10?.toFixed(1) || 'N/A'}
            </div>
        </div>
    `;
    
    document.getElementById('currentCard').innerHTML = html;
}

async function loadForecast(city) {
    try {
        const response = await fetch(`${API_BASE}/forecast/${city}?hours=48`);
        const data = await response.json();
        
        if (response.ok) {
            displayForecast(data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function displayForecast(data) {
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    const hours = data.forecasts.map(f => `H${f.hour}`);
    const aqiValues = data.forecasts.map(f => f.predicted_aqi);
    
    if (forecastChart) {
        forecastChart.destroy();
    }
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [{
                label: 'Predicted AQI',
                data: aqiValues,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

function getAQILevel(aqi) {
    if (aqi <= 50) return { text: 'Good', class: 'good' };
    if (aqi <= 100) return { text: 'Moderate', class: 'moderate' };
    if (aqi <= 150) return { text: 'Unhealthy for Sensitive Groups', class: 'unhealthy' };
    if (aqi <= 200) return { text: 'Unhealthy', class: 'very-unhealthy' };
    if (aqi <= 300) return { text: 'Very Unhealthy', class: 'very-unhealthy' };
    return { text: 'Hazardous', class: 'hazardous' };
}
